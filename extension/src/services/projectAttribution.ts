/**
 * Project attribution service
 */

import * as vscode from 'vscode';
import { Logger } from '../utils/logger';

export class ProjectAttributionService {
    /**
     * Get current project name from workspace
     */
    getCurrentProject(): string {
        const workspaceFolders = vscode.workspace.workspaceFolders;

        if (!workspaceFolders || workspaceFolders.length === 0) {
            Logger.debug('No workspace folder found');
            return 'unknown';
        }

        // Use first workspace folder name
        const projectName = workspaceFolders[0].name;
        Logger.debug('Current project', { projectName });
        return projectName;
    }

    /**
     * Get workspace folder path
     */
    getWorkspacePath(): string | undefined {
        const workspaceFolders = vscode.workspace.workspaceFolders;

        if (!workspaceFolders || workspaceFolders.length === 0) {
            return undefined;
        }

        return workspaceFolders[0].uri.fsPath;
    }

    /**
     * Check if workspace is open
     */
    hasWorkspace(): boolean {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        return !!(workspaceFolders && workspaceFolders.length > 0);
    }
}
