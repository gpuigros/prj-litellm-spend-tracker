/**
 * Tree view provider for spend data
 */

import * as vscode from 'vscode';
import { SpendStateManager } from '../../state/spendState';
import { BudgetStateManager } from '../../state/budgetState';
import { Logger } from '../../utils/logger';
import type { ModelSpend, ProjectSpend } from '../../types';

type TreeItem = SummaryItem | ModelItem | ProjectItem | DailyItem;

class SummaryItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
    ) {
        super(label, collapsibleState);
        this.description = value;
        this.contextValue = 'summaryItem';
    }
}

class ModelItem extends vscode.TreeItem {
    constructor(
        public readonly model: ModelSpend,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
    ) {
        super(model.model, collapsibleState);
        this.description = `$${model.spend.toFixed(2)} (${model.percentage.toFixed(1)}%)`;
        this.tooltip = `${model.requests} requests, ${model.tokens} tokens`;
        this.contextValue = 'modelItem';
        this.iconPath = new vscode.ThemeIcon('symbol-misc');
    }
}

class ProjectItem extends vscode.TreeItem {
    constructor(
        public readonly project: ProjectSpend,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
    ) {
        super(project.project, collapsibleState);
        this.description = `$${project.spend.toFixed(2)} (${project.percentage.toFixed(1)}%)`;
        this.tooltip = `${project.requests} requests`;
        this.contextValue = 'projectItem';
        this.iconPath = new vscode.ThemeIcon('folder');
    }
}

class DailyItem extends vscode.TreeItem {
    constructor(
        public readonly date: string,
        public readonly spend: number,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
    ) {
        super(date, collapsibleState);
        this.description = `$${spend.toFixed(2)}`;
        this.contextValue = 'dailyItem';
        this.iconPath = new vscode.ThemeIcon('calendar');
    }
}

export class SpendTreeProvider implements vscode.TreeDataProvider<TreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<TreeItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor(
        private spendState: SpendStateManager,
        private budgetState: BudgetStateManager
    ) {
        // Refresh tree when state changes
        spendState.onDidChangeState(() => this.refresh());
        budgetState.onDidChangeState(() => this.refresh());
    }

    /**
     * Refresh tree view
     */
    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    /**
     * Get tree item
     */
    getTreeItem(element: TreeItem): vscode.TreeItem {
        return element;
    }

    /**
     * Get children for tree
     */
    getChildren(element?: TreeItem): Thenable<TreeItem[]> {
        if (!element) {
            return this.getRootItems();
        }

        if (element instanceof SummaryItem && element.label === 'Models') {
            return this.getModelItems();
        }

        if (element instanceof SummaryItem && element.label === 'Projects') {
            return this.getProjectItems();
        }

        if (element instanceof SummaryItem && element.label === 'Daily') {
            return this.getDailyItems();
        }

        return Promise.resolve([]);
    }

    /**
     * Get root level items
     */
    private getRootItems(): Thenable<TreeItem[]> {
        const items: TreeItem[] = [];
        const spendState = this.spendState.getState();
        const budgetState = this.budgetState.getState();

        // Summary section
        if (spendState.summary) {
            const summary = spendState.summary;
            items.push(new SummaryItem('Total Spend', `$${summary.spend.toFixed(2)}`));
            items.push(new SummaryItem('Budget', `$${summary.budget.toFixed(2)}`));
            items.push(new SummaryItem('Remaining', `$${summary.remaining.toFixed(2)}`));
            items.push(new SummaryItem('Usage', `${summary.budget_used_percent.toFixed(1)}%`));
        } else if (spendState.isLoading) {
            items.push(new SummaryItem('Loading...', ''));
        } else if (spendState.error) {
            items.push(new SummaryItem('Error', spendState.error));
        } else {
            items.push(new SummaryItem('No data', ''));
        }

        // Budget state
        if (budgetState.budget) {
            const budget = budgetState.budget;
            const stateIcon = budget.state === 'exceeded' ? '⚠️' : budget.state === 'warning' ? '⚡' : '✓';
            items.push(new SummaryItem('Budget State', `${stateIcon} ${budget.state}`));
        }

        // Collapsible sections
        if (spendState.byModel && spendState.byModel.models.length > 0) {
            items.push(new SummaryItem('Models', `${spendState.byModel.models.length}`, vscode.TreeItemCollapsibleState.Collapsed));
        }

        if (spendState.byProject && spendState.byProject.projects.length > 0) {
            items.push(new SummaryItem('Projects', `${spendState.byProject.projects.length}`, vscode.TreeItemCollapsibleState.Collapsed));
        }

        if (spendState.daily && spendState.daily.days.length > 0) {
            items.push(new SummaryItem('Daily', `${spendState.daily.days.length} days`, vscode.TreeItemCollapsibleState.Collapsed));
        }

        return Promise.resolve(items);
    }

    /**
     * Get model breakdown items
     */
    private getModelItems(): Thenable<TreeItem[]> {
        const state = this.spendState.getState();
        if (!state.byModel) {
            return Promise.resolve([]);
        }

        // Defensive: drop rows with empty model names so the tree never
        // shows a blank entry.
        const items = state.byModel.models
            .filter(model => model.model)
            .map(model => new ModelItem(model));
        return Promise.resolve(items);
    }

    /**
     * Get project breakdown items
     */
    private getProjectItems(): Thenable<TreeItem[]> {
        const state = this.spendState.getState();
        if (!state.byProject) {
            return Promise.resolve([]);
        }

        const items = state.byProject.projects.map(project => new ProjectItem(project));
        return Promise.resolve(items);
    }

    /**
     * Get daily spend items
     */
    private getDailyItems(): Thenable<TreeItem[]> {
        const state = this.spendState.getState();
        if (!state.daily) {
            return Promise.resolve([]);
        }

        const items = state.daily.days.map(day => {
            const date = new Date(day.date).toLocaleDateString();
            return new DailyItem(date, day.spend);
        });
        return Promise.resolve(items);
    }

    /**
     * Dispose resources
     */
    dispose(): void {
        this._onDidChangeTreeData.dispose();
    }
}
