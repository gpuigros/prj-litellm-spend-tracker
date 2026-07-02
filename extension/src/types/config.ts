/**
 * Type definitions for configuration
 */

import type { Period } from './spend';

export type StatusBarFormat = 'amount' | 'percentage' | 'both';

export interface ExtensionConfig {
    apiBaseUrl: string;
    refreshInterval: number;
    defaultPeriod: Period;
    statusBarFormat: StatusBarFormat;
}
