/**
 * Logger utility
 */

import * as vscode from 'vscode';

export class Logger {
    private static outputChannel: vscode.OutputChannel | undefined;

    static init(): void {
        if (!this.outputChannel) {
            this.outputChannel = vscode.window.createOutputChannel('LLM Spend Tracker');
        }
    }

    static info(message: string, ...args: any[]): void {
        this.log('INFO', message, ...args);
    }

    static warn(message: string, ...args: any[]): void {
        this.log('WARN', message, ...args);
    }

    static error(message: string, ...args: any[]): void {
        this.log('ERROR', message, ...args);
    }

    static debug(message: string, ...args: any[]): void {
        this.log('DEBUG', message, ...args);
    }

    private static log(level: string, message: string, ...args: any[]): void {
        if (!this.outputChannel) {
            this.init();
        }

        const timestamp = new Date().toISOString();
        const formattedArgs = args.length > 0 ? ` ${JSON.stringify(args)}` : '';
        const logMessage = `[${timestamp}] [${level}] ${message}${formattedArgs}`;

        this.outputChannel?.appendLine(logMessage);
    }

    static show(): void {
        this.outputChannel?.show();
    }

    static dispose(): void {
        this.outputChannel?.dispose();
        this.outputChannel = undefined;
    }
}
