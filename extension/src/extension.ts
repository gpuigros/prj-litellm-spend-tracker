/**
 * Extension entry point
 */

import * as vscode from 'vscode';
import { Logger } from './utils/logger';
import { ApiKeyManager } from './auth/apiKeyManager';
import { ApiClient } from './api/client';
import { SpendRepository } from './api/repositories/spendRepository';
import { BudgetRepository } from './api/repositories/budgetRepository';
import { Configuration } from './config/configuration';
import { SpendService } from './services/spendService';
import { BudgetService } from './services/budgetService';
import { RefreshService } from './services/refreshService';
import { SpendStateManager } from './state/spendState';
import { BudgetStateManager } from './state/budgetState';
import { SpendTreeProvider } from './ui/treeView/spendTreeProvider';
import { StatusBarManager } from './ui/statusBar/statusBarManager';
import { SpendWebviewProvider } from './ui/webview/spendWebviewProvider';
import { COMMANDS, VIEWS } from './constants';

let apiKeyManager: ApiKeyManager;
let apiClient: ApiClient;
let spendRepository: SpendRepository;
let budgetRepository: BudgetRepository;
let spendService: SpendService;
let budgetService: BudgetService;
let refreshService: RefreshService;
let spendStateManager: SpendStateManager;
let budgetStateManager: BudgetStateManager;
let treeProvider: SpendTreeProvider;
let statusBarManager: StatusBarManager;
let webviewProvider: SpendWebviewProvider;

export function activate(context: vscode.ExtensionContext): void {
    Logger.init();
    Logger.info('LLM Spend Tracker activating');

    // Initialize services
    apiKeyManager = new ApiKeyManager(context);
    apiClient = new ApiClient(apiKeyManager);
    spendRepository = new SpendRepository(apiClient);
    budgetRepository = new BudgetRepository(apiClient);
    spendService = new SpendService(spendRepository);
    budgetService = new BudgetService(budgetRepository);
    refreshService = new RefreshService();

    // Initialize state managers
    const config = Configuration.getConfig();
    spendStateManager = new SpendStateManager(config.defaultPeriod);
    budgetStateManager = new BudgetStateManager();

    // Initialize UI components
    treeProvider = new SpendTreeProvider(spendStateManager, budgetStateManager);
    statusBarManager = new StatusBarManager(spendStateManager, budgetStateManager);
    webviewProvider = new SpendWebviewProvider(context.extensionUri, spendStateManager, budgetStateManager);

    // Register tree view
    const treeView = vscode.window.createTreeView(VIEWS.TREE_VIEW, {
        treeDataProvider: treeProvider,
    });
    context.subscriptions.push(treeView);

    // Register webview provider
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(VIEWS.SIDEBAR, webviewProvider)
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand(COMMANDS.REFRESH, async () => {
            Logger.info('Refresh command executed');
            await refreshData(true);
            vscode.window.showInformationMessage('LLM Spend data refreshed');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(COMMANDS.OPEN_SIDEBAR, () => {
            Logger.info('Open sidebar command executed');
            vscode.commands.executeCommand('workbench.view.extension.llm-spend');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(COMMANDS.CONFIGURE, () => {
            Logger.info('Configure command executed');
            vscode.commands.executeCommand('workbench.action.openSettings', 'llmSpend');
        })
    );

    // Listen for configuration changes
    context.subscriptions.push(
        Configuration.onDidChange(config => {
            Logger.info('Configuration changed', config);
            apiClient.updateBaseUrl(config.apiBaseUrl);
            spendStateManager.setPeriod(config.defaultPeriod);
        })
    );

    // Listen for state changes to trigger refresh
    spendStateManager.onDidChangeState(async state => {
        if (state.period && !state.summary && !state.isLoading && !state.error) {
            await refreshData(false);
        }
    });

    // Start auto-refresh
    refreshService.start(async () => {
        await refreshData(false);
    });

    // Initial data load
    refreshData(false);

    Logger.info('LLM Spend Tracker activated');
}

/**
 * Refresh all spend and budget data
 */
async function refreshData(forceRefresh: boolean): Promise<void> {
    const period = spendStateManager.getState().period;

    spendStateManager.setLoading(true);
    budgetStateManager.setLoading(true);

    // Fetch all data in parallel — use allSettled so one failure
    // does not discard the rest
    const [summaryResult, byModelResult, byProjectResult, dailyResult, budgetResult] =
        await Promise.allSettled([
            spendService.getSummary(period, forceRefresh),
            spendService.getByModel(period, forceRefresh),
            spendService.getByProject(period, forceRefresh),
            spendService.getDaily(period, forceRefresh),
            budgetService.getBudget(forceRefresh),
        ]);

    // Collect errors for partial-failure reporting
    const errors: string[] = [];

    // Update state for each fulfilled result; collect rejections
    if (summaryResult.status === 'fulfilled') {
        spendStateManager.setSummary(summaryResult.value);
    } else {
        const msg = errorMessage(summaryResult.reason);
        errors.push(`summary: ${msg}`);
        Logger.error('Failed to fetch spend summary', summaryResult.reason);
    }

    if (byModelResult.status === 'fulfilled') {
        spendStateManager.setByModel(byModelResult.value);
    } else {
        const msg = errorMessage(byModelResult.reason);
        errors.push(`by-model: ${msg}`);
        Logger.error('Failed to fetch spend by model', byModelResult.reason);
    }

    if (byProjectResult.status === 'fulfilled') {
        spendStateManager.setByProject(byProjectResult.value);
    } else {
        const msg = errorMessage(byProjectResult.reason);
        errors.push(`by-project: ${msg}`);
        Logger.error('Failed to fetch spend by project', byProjectResult.reason);
    }

    if (dailyResult.status === 'fulfilled') {
        spendStateManager.setDaily(dailyResult.value);
    } else {
        const msg = errorMessage(dailyResult.reason);
        errors.push(`daily: ${msg}`);
        Logger.error('Failed to fetch daily spend', dailyResult.reason);
    }

    if (budgetResult.status === 'fulfilled') {
        budgetStateManager.setBudget(budgetResult.value);
    } else {
        const msg = errorMessage(budgetResult.reason);
        errors.push(`budget: ${msg}`);
        Logger.error('Failed to fetch budget', budgetResult.reason);
    }

    if (errors.length > 0) {
        const combined = errors.join('; ');
        Logger.warn('Partial refresh failure', { errors });
        spendStateManager.setError(combined);
    } else {
        Logger.info('Data refreshed successfully', { period });
    }
}

/**
 * Extract a human-readable message from an unknown error
 */
function errorMessage(error: unknown): string {
    if (error instanceof Error) {
        return error.message;
    }
    if (typeof error === 'object' && error !== null && 'message' in error) {
        return String((error as Record<string, unknown>).message);
    }
    return 'Unknown error';
}

export function deactivate(): void {
    Logger.info('LLM Spend Tracker deactivating');

    // Dispose services
    refreshService?.dispose();

    // Dispose state managers
    spendStateManager?.dispose();
    budgetStateManager?.dispose();

    // Dispose UI components
    treeProvider?.dispose();
    statusBarManager?.dispose();
    webviewProvider?.dispose();

    Logger.dispose();
}
