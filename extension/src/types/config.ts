/**
 * Type definitions for configuration
 */

import type { Period } from './spend';

export interface ExtensionConfig {
    apiBaseUrl: string;
    refreshInterval: number;
    defaultPeriod: Period;
}
