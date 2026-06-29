/**
 * API key manager for authentication
 */

import * as vscode from 'vscode';
import { Logger } from '../utils/logger';

const API_KEY_STORAGE_KEY = 'llmSpend.apiKey';

export class ApiKeyManager {
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    /**
     * Get stored API key
     */
    async getApiKey(): Promise<string | undefined> {
        try {
            const apiKey = await this.context.secrets.get(API_KEY_STORAGE_KEY);
            return apiKey;
        } catch (error) {
            Logger.error('Failed to retrieve API key', error);
            return undefined;
        }
    }

    /**
     * Store API key
     */
    async setApiKey(apiKey: string): Promise<void> {
        try {
            await this.context.secrets.store(API_KEY_STORAGE_KEY, apiKey);
            Logger.info('API key stored successfully');
        } catch (error) {
            Logger.error('Failed to store API key', error);
            throw error;
        }
    }

    /**
     * Remove stored API key
     */
    async removeApiKey(): Promise<void> {
        try {
            await this.context.secrets.delete(API_KEY_STORAGE_KEY);
            Logger.info('API key removed successfully');
        } catch (error) {
            Logger.error('Failed to remove API key', error);
            throw error;
        }
    }

    /**
     * Prompt user for API key
     */
    async promptForApiKey(): Promise<string | undefined> {
        const apiKey = await vscode.window.showInputBox({
            prompt: 'Enter your LiteLLM API key',
            placeHolder: 'sk-...',
            password: true,
            ignoreFocusOut: true,
            validateInput: value => {
                if (!value || value.trim().length === 0) {
                    return 'API key is required';
                }
                return null;
            },
        });

        if (apiKey) {
            await this.setApiKey(apiKey.trim());
            return apiKey.trim();
        }

        return undefined;
    }

    /**
     * Ensure API key is available
     */
    async ensureApiKey(): Promise<string | undefined> {
        let apiKey = await this.getApiKey();

        if (!apiKey) {
            apiKey = await this.promptForApiKey();
        }

        return apiKey;
    }
}
