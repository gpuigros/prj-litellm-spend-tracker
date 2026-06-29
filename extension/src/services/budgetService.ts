/**
 * Budget service for budget calculations
 */

import { BudgetRepository } from '../api/repositories/budgetRepository';
import { MemoryCache } from '../cache/memoryCache';
import { Logger } from '../utils/logger';
import type { Budget, BudgetState } from '../types';

const CACHE_TTL = 60; // 60 seconds

export class BudgetService {
    private repository: BudgetRepository;
    private cache: MemoryCache<Budget>;

    constructor(repository: BudgetRepository) {
        this.repository = repository;
        this.cache = new MemoryCache();
    }

    /**
     * Get budget information with caching
     */
    async getBudget(forceRefresh = false): Promise<Budget> {
        const cacheKey = 'budget';

        if (!forceRefresh) {
            const cached = this.cache.get<Budget>(cacheKey);
            if (cached) {
                Logger.debug('Returning cached budget');
                return cached;
            }
        }

        Logger.info('Fetching budget');
        const data = await this.repository.getBudget();
        this.cache.set(cacheKey, data, CACHE_TTL);
        return data;
    }

    /**
     * Check if budget is in warning state
     */
    async isWarning(): Promise<boolean> {
        const budget = await this.getBudget();
        return budget.state === 'warning' || budget.state === 'exceeded';
    }

    /**
     * Check if budget is exceeded
     */
    async isExceeded(): Promise<boolean> {
        const budget = await this.getBudget();
        return budget.state === 'exceeded';
    }

    /**
     * Get budget state
     */
    async getState(): Promise<BudgetState> {
        const budget = await this.getBudget();
        return budget.state;
    }

    /**
     * Get remaining budget
     */
    async getRemaining(): Promise<number> {
        const budget = await this.getBudget();
        return budget.remaining;
    }

    /**
     * Get usage percentage
     */
    async getUsagePercent(): Promise<number> {
        const budget = await this.getBudget();
        return budget.used_percent;
    }

    /**
     * Clear cached budget
     */
    clearCache(): void {
        this.cache.clear();
        Logger.info('Budget cache cleared');
    }
}
