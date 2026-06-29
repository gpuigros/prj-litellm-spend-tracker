/**
 * Spend state management
 */

import * as vscode from 'vscode';
import type { Period, SpendSummary, SpendByModel, SpendByProject, SpendDaily } from '../types';
import { Logger } from '../utils/logger';

export interface SpendState {
    period: Period;
    summary: SpendSummary | null;
    byModel: SpendByModel | null;
    byProject: SpendByProject | null;
    daily: SpendDaily | null;
    isLoading: boolean;
    error: string | null;
    lastUpdated: Date | null;
}

export class SpendStateManager {
    private state: SpendState;
    private _onDidChangeState = new vscode.EventEmitter<SpendState>();
    readonly onDidChangeState = this._onDidChangeState.event;

    constructor(defaultPeriod: Period) {
        this.state = {
            period: defaultPeriod,
            summary: null,
            byModel: null,
            byProject: null,
            daily: null,
            isLoading: false,
            error: null,
            lastUpdated: null,
        };
    }

    /**
     * Get current state
     */
    getState(): SpendState {
        return { ...this.state };
    }

    /**
     * Set period
     */
    setPeriod(period: Period): void {
        this.state = {
            ...this.state,
            period,
            summary: null,
            byModel: null,
            byProject: null,
            daily: null,
            error: null,
        };
        this.emitChange();
        Logger.debug('Period changed', { period });
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
     * Update summary data
     */
    setSummary(summary: SpendSummary): void {
        this.state = {
            ...this.state,
            summary,
            isLoading: false,
            error: null,
            lastUpdated: new Date(),
        };
        this.emitChange();
    }

    /**
     * Update model breakdown
     */
    setByModel(byModel: SpendByModel): void {
        this.state = { ...this.state, byModel };
        this.emitChange();
    }

    /**
     * Update project breakdown
     */
    setByProject(byProject: SpendByProject): void {
        this.state = { ...this.state, byProject };
        this.emitChange();
    }

    /**
     * Update daily spend
     */
    setDaily(daily: SpendDaily): void {
        this.state = { ...this.state, daily };
        this.emitChange();
    }

    /**
     * Clear all data
     */
    clear(): void {
        this.state = {
            ...this.state,
            summary: null,
            byModel: null,
            byProject: null,
            daily: null,
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
