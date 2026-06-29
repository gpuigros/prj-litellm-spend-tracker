/**
 * Configuration management service
 */

import * as vscode from 'vscode';
import { CONFIG_KEYS, CONFIG_SECTION, DEFAULTS } from '../constants';
import type { ExtensionConfig, Period } from '../types';

export class Configuration {
    /**
     * Get current configuration
     */
    static getConfig(): ExtensionConfig {
        const config = vscode.workspace.getConfiguration(CONFIG_SECTION);

        return {
            apiBaseUrl: config.get<string>(CONFIG_KEYS.API_BASE_URL, DEFAULTS.API_BASE_URL),
            refreshInterval: config.get<number>(CONFIG_KEYS.REFRESH_INTERVAL, DEFAULTS.REFRESH_INTERVAL),
            defaultPeriod: config.get<Period>(CONFIG_KEYS.DEFAULT_PERIOD, DEFAULTS.DEFAULT_PERIOD),
        };
    }

    /**
     * Get API base URL
     */
    static getApiBaseUrl(): string {
        return this.getConfig().apiBaseUrl;
    }

    /**
     * Get refresh interval in seconds
     */
    static getRefreshInterval(): number {
        return this.getConfig().refreshInterval;
    }

    /**
     * Get default period
     */
    static getDefaultPeriod(): Period {
        return this.getConfig().defaultPeriod;
    }

    /**
     * Listen for configuration changes
     */
    static onDidChange(callback: (config: ExtensionConfig) => void): vscode.Disposable {
        return vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration(CONFIG_SECTION)) {
                callback(this.getConfig());
            }
        });
    }
}
