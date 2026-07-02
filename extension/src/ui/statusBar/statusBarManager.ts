/**
 * Status bar manager
 */

import * as vscode from 'vscode';
import { SpendStateManager } from '../../state/spendState';
import { BudgetStateManager } from '../../state/budgetState';
import { Configuration } from '../../config/configuration';
import { Logger } from '../../utils/logger';

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;

    constructor(
        private spendState: SpendStateManager,
        private budgetState: BudgetStateManager
    ) {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.command = 'llmSpend.openSidebar';

        // Update status bar when state changes
        spendState.onDidChangeState(() => this.update());
        budgetState.onDidChangeState(() => this.update());

        this.update();
        this.statusBarItem.show();
    }

    /**
     * Update status bar display
     */
    private update(): void {
        const spendState = this.spendState.getState();
        const budgetState = this.budgetState.getState();

        // Loading state
        if (spendState.isLoading) {
            this.statusBarItem.text = '$(sync~spin) LLM Spend';
            this.statusBarItem.tooltip = 'Loading spend data...';
            this.statusBarItem.backgroundColor = undefined;
            return;
        }

        // Error state
        if (spendState.error) {
            this.statusBarItem.text = '$(error) LLM Spend';
            this.statusBarItem.tooltip = `Error: ${spendState.error}`;
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            return;
        }

        // No data
        if (!spendState.summary) {
            this.statusBarItem.text = '$(circle-outline) LLM Spend';
            this.statusBarItem.tooltip = 'No spend data available';
            this.statusBarItem.backgroundColor = undefined;
            return;
        }

        const summary = spendState.summary;
        const budget = budgetState.budget;
        const format = Configuration.getStatusBarFormat();

        // Budget exceeded
        if (budget && budget.state === 'exceeded') {
            this.statusBarItem.text = `$(warning) ${this.formatDisplay(summary.spend, summary.budget_used_percent, format)}`;
            this.statusBarItem.tooltip = `Budget exceeded! Spent $${summary.spend.toFixed(2)} of $${summary.budget.toFixed(2)} (${summary.budget_used_percent.toFixed(1)}%)`;
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            return;
        }

        // Budget warning
        if (budget && budget.state === 'warning') {
            this.statusBarItem.text = `$(alert) ${this.formatDisplay(summary.spend, summary.budget_used_percent, format)}`;
            this.statusBarItem.tooltip = `Budget warning: ${summary.budget_used_percent.toFixed(1)}% used ($${summary.spend.toFixed(2)} of $${summary.budget.toFixed(2)})`;
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            return;
        }

        // Normal state
        this.statusBarItem.text = `$(coin) ${this.formatDisplay(summary.spend, summary.budget_used_percent, format)}`;
        this.statusBarItem.tooltip = `LLM Spend: $${summary.spend.toFixed(2)} of $${summary.budget.toFixed(2)} (${summary.budget_used_percent.toFixed(1)}%)`;
        this.statusBarItem.backgroundColor = undefined;
    }

    /**
     * Format the status bar text based on the user's preferred display format.
     */
    private formatDisplay(spend: number, percent: number, format: string): string {
        const amount = `$${spend.toFixed(2)}`;
        const pct = `${percent.toFixed(1)}%`;

        switch (format) {
            case 'percentage':
                return pct;
            case 'both':
                return `${amount} / ${pct}`;
            case 'amount':
            default:
                return amount;
        }
    }

    /**
     * Show status bar
     */
    show(): void {
        this.statusBarItem.show();
    }

    /**
     * Hide status bar
     */
    hide(): void {
        this.statusBarItem.hide();
    }

    /**
     * Dispose resources
     */
    dispose(): void {
        this.statusBarItem.dispose();
    }
}
