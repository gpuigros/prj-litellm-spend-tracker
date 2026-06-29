/**
 * Budget state management
 */

import * as vscode from 'vscode';
import type { Budget } from '../types';
import { Logger } from '../utils/logger';

export interface BudgetState {
    budget: Budget | null;
    isLoading: boolean;
    error: string | null;
    lastUpdated: Date | null;
}

export class BudgetStateManager {
    private state: BudgetState;
    private _onDidChangeState = new vscode.EventEmitter<BudgetState>();
    readonly onDidChangeState = this._onDidChangeState.event;

    constructor() {
        this.state = {
            budget: null,
            isLoading: false,
            error: null,
            lastUpdated: null,
        };
    }

    /**
     * Get current state
     */
    getState(): BudgetState {
        return { ...this.state };
    }

    /**
     * Set loading state
     */
    setLoading(isLoading: boolean): void {
        this.state = { ...this.state, isLoading };
        this.emitChange();
    }

    /**
     * Set error
     */
    setError(error: string | null): void {
        this.state = { ...this.state, error, isLoading: false };
        this.emitChange();
    }

    /**
     * Update budget data
     */
    setBudget(budget: Budget): void {
        this.state = {
            ...this.state,
            budget,
            isLoading: false,
            error: null,
            lastUpdated: new Date(),
        };
        this.emitChange();
        Logger.debug('Budget updated', {
            spent: budget.spent,
            remaining: budget.remaining,
            state: budget.state
        });
    }

    /**
     * Clear budget data
     */
    clear(): void {
        this.state = {
            ...this.state,
            budget: null,
            error: null,
            lastUpdated: null,
        };
        this.emitChange();
    }

    /**
     * Emit state change event
     */
    private emitChange(): void {
        this._onDidChangeState.fire(this.getState());
    }

    /**
     * Dispose resources
     */
    dispose(): void {
        this._onDidChangeState.dispose();
    }
}
