/**
 * Test suite for extension
 */

import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('your-github-username.litellm-spend-tracker'));
    });

    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('your-github-username.litellm-spend-tracker');
        assert.ok(extension);
        await extension?.activate();
        assert.ok(extension?.isActive);
    });

    test('Commands should be registered', async () => {
        const commands = await vscode.commands.getCommands();
        assert.ok(commands.includes('llmSpend.refresh'));
        assert.ok(commands.includes('llmSpend.openSidebar'));
        assert.ok(commands.includes('llmSpend.configure'));
    });
});
