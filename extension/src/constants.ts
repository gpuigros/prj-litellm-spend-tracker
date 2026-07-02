/**
 * Configuration keys and constants
 */

export const CONFIG_SECTION = 'llmSpend';
export const CONFIG_KEYS = {
    API_BASE_URL: 'apiBaseUrl',
    REFRESH_INTERVAL: 'refreshInterval',
    DEFAULT_PERIOD: 'defaultPeriod',
    STATUS_BAR_FORMAT: 'statusBarFormat',
} as const;

export const DEFAULTS = {
    API_BASE_URL: 'http://localhost:8000',
    REFRESH_INTERVAL: 300,
    DEFAULT_PERIOD: 'month' as const,
    STATUS_BAR_FORMAT: 'both' as const,
} as const;

export const COMMANDS = {
    REFRESH: 'llmSpend.refresh',
    OPEN_SIDEBAR: 'llmSpend.openSidebar',
    CONFIGURE: 'llmSpend.configure',
} as const;

export const VIEWS = {
    SIDEBAR: 'llmSpend.sidebar',
    TREE_VIEW: 'llmSpend.treeView',
} as const;
