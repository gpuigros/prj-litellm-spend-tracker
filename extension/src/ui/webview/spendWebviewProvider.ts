/**
 * Webview provider for spend dashboard
 */

import * as vscode from 'vscode';
import { SpendStateManager } from '../../state/spendState';
import { BudgetStateManager } from '../../state/budgetState';
import { Logger } from '../../utils/logger';
import type { Period } from '../../types';

export class SpendWebviewProvider implements vscode.WebviewViewProvider {
  private webviewView?: vscode.WebviewView;

  constructor(
    private readonly extensionUri: vscode.Uri,
    private spendState: SpendStateManager,
    private budgetState: BudgetStateManager
  ) {
    // Update webview when state changes
    spendState.onDidChangeState(() => this.updateWebview());
    budgetState.onDidChangeState(() => this.updateWebview());
  }

  /**
   * Resolve webview view
   */
  resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    token: vscode.CancellationToken
  ): void {
    this.webviewView = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.extensionUri],
    };

    // Handle messages from webview
    webviewView.webview.onDidReceiveMessage(
      message => {
        switch (message.command) {
          case 'changePeriod':
            this.spendState.setPeriod(message.period as Period);
            break;
          case 'refresh':
            vscode.commands.executeCommand('llmSpend.refresh');
            break;
        }
      },
      undefined,
      []
    );

    this.updateWebview();
  }

  /**
   * Update webview content
   */
  private updateWebview(): void {
    if (!this.webviewView) {
      return;
    }

    const spendState = this.spendState.getState();
    const budgetState = this.budgetState.getState();

    const html = this.getHtmlContent(spendState, budgetState);
    this.webviewView.webview.html = html;
  }

  /**
   * Generate HTML content for webview
   */
  private getHtmlContent(spendState: any, budgetState: any): string {
    const nonce = this.getNonce();

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${this.webviewView?.webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <title>LLM Spend Dashboard</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      padding: 10px;
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
    }
    .section {
      margin-bottom: 20px;
    }
    .section-title {
      font-weight: bold;
      margin-bottom: 10px;
      color: var(--vscode-textLink-foreground);
    }
    .stat {
      display: flex;
      justify-content: space-between;
      padding: 5px 0;
      border-bottom: 1px solid var(--vscode-panel-border);
    }
    .stat-label {
      color: var(--vscode-descriptionForeground);
    }
    .stat-value {
      font-weight: bold;
    }
    .warning {
      color: var(--vscode-editorWarning-foreground);
    }
    .error {
      color: var(--vscode-editorError-foreground);
    }
    .success {
      color: var(--vscode-testing-iconPassed);
    }
    select {
      width: 100%;
      padding: 5px;
      background-color: var(--vscode-input-background);
      color: var(--vscode-input-foreground);
      border: 1px solid var(--vscode-input-border);
      margin-bottom: 15px;
    }
    button {
      width: 100%;
      padding: 8px;
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      cursor: pointer;
      margin-top: 10px;
    }
    button:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
    .loading {
      text-align: center;
      padding: 20px;
      color: var(--vscode-descriptionForeground);
    }
    .error-message {
      padding: 10px;
      background-color: var(--vscode-inputValidation-errorBackground);
      border: 1px solid var(--vscode-inputValidation-errorBorder);
      color: var(--vscode-errorForeground);
    }
  </style>
</head>
<body>
  <div class="section">
    <label for="period">Period:</label>
    <select id="period">
      <option value="today" ${spendState.period === 'today' ? 'selected' : ''}>Today</option>
      <option value="week" ${spendState.period === 'week' ? 'selected' : ''}>This Week</option>
      <option value="month" ${spendState.period === 'month' ? 'selected' : ''}>This Month</option>
    </select>
  </div>

  ${spendState.isLoading ? '<div class="loading">Loading...</div>' : ''}
  
  ${spendState.error ? `<div class="error-message">${spendState.error}</div>` : ''}

  ${spendState.summary ? `
    <div class="section">
      <div class="section-title">Summary</div>
      <div class="stat">
        <span class="stat-label">Total Spend:</span>
        <span class="stat-value">$${spendState.summary.spend.toFixed(2)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Budget:</span>
        <span class="stat-value">$${spendState.summary.budget.toFixed(2)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Remaining:</span>
        <span class="stat-value">$${spendState.summary.remaining.toFixed(2)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Usage:</span>
        <span class="stat-value">${spendState.summary.budget_used_percent.toFixed(1)}%</span>
      </div>
    </div>
  ` : ''}

  ${budgetState.budget ? `
    <div class="section">
      <div class="section-title">Budget Status</div>
      <div class="stat">
        <span class="stat-label">State:</span>
        <span class="stat-value ${budgetState.budget.state === 'exceeded' ? 'error' : budgetState.budget.state === 'warning' ? 'warning' : 'success'}">
          ${budgetState.budget.state.toUpperCase()}
        </span>
      </div>
    </div>
  ` : ''}

  ${spendState.byModel && spendState.byModel.models.length > 0 ? `
    <div class="section">
      <div class="section-title">By Model</div>
      ${spendState.byModel.models
          .filter((model: any) => model.model)
          .map((model: any) => `
        <div class="stat">
          <span class="stat-label">${model.model}:</span>
          <span class="stat-value">$${model.spend.toFixed(2)} (${model.percentage.toFixed(1)}%)</span>
        </div>
      `).join('')}
    </div>
  ` : ''}

  ${spendState.byProject && spendState.byProject.projects.length > 0 ? `
    <div class="section">
      <div class="section-title">By Project</div>
      ${spendState.byProject.projects.map((project: any) => `
        <div class="stat">
          <span class="stat-label">${project.project}:</span>
          <span class="stat-value">$${project.spend.toFixed(2)} (${project.percentage.toFixed(1)}%)</span>
        </div>
      `).join('')}
    </div>
  ` : ''}

  <button id="refresh">Refresh Data</button>

  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();

    document.getElementById('period').addEventListener('change', (e) => {
      vscode.postMessage({
        command: 'changePeriod',
        period: e.target.value
      });
    });

    document.getElementById('refresh').addEventListener('click', () => {
      vscode.postMessage({
        command: 'refresh'
      });
    });
  </script>
</body>
</html>`;
  }

  /**
   * Generate nonce for CSP
   */
  private getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }

  /**
   * Dispose resources
   */
  dispose(): void {
    // Webview disposal handled by VS Code
  }
}
