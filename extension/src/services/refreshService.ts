/**
 * Refresh service for automatic data updates
 */

import * as vscode from 'vscode';
import { Configuration } from '../config/configuration';
import { Logger } from '../utils/logger';

export class RefreshService {
    private intervalId: NodeJS.Timeout | undefined;
    private onRefreshCallback: (() => Promise<void>) | undefined;
    private isRefreshing = false;

    /**
     * Start auto-refresh with configured interval
     */
    start(callback: () => Promise<void>): void {
        this.stop(); // Clear any existing interval

        this.onRefreshCallback = callback;
        const intervalSeconds = Configuration.getRefreshInterval();

        if (intervalSeconds <= 0) {
            Logger.info('Auto-refresh disabled');
            return;
        }

        const intervalMs = intervalSeconds * 1000;
        Logger.info('Starting auto-refresh', { intervalSeconds });

        this.intervalId = setInterval(async () => {
            await this.refresh();
        }, intervalMs);
    }

    /**
     * Stop auto-refresh
     */
    stop(): void {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = undefined;
            Logger.info('Auto-refresh stopped');
        }
    }

    /**
     * Manually trigger refresh
     */
    async refresh(): Promise<void> {
        if (this.isRefreshing) {
            Logger.debug('Refresh already in progress');
            return;
        }

        if (!this.onRefreshCallback) {
            Logger.warn('No refresh callback registered');
            return;
        }

        this.isRefreshing = true;
        try {
            Logger.info('Refreshing data');
            await this.onRefreshCallback();
            Logger.info('Data refreshed successfully');
        } catch (error) {
            Logger.error('Refresh failed', error);
            throw error;
        } finally {
            this.isRefreshing = false;
        }
    }

    /**
     * Check if currently refreshing
     */
    getIsRefreshing(): boolean {
        return this.isRefreshing;
    }

    /**
     * Dispose resources
     */
    dispose(): void {
        this.stop();
        this.onRefreshCallback = undefined;
    }
}
