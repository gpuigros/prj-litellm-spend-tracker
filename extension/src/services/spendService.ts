/**
 * Spend service for data orchestration
 */

import { SpendRepository } from '../api/repositories/spendRepository';
import { MemoryCache } from '../cache/memoryCache';
import { Logger } from '../utils/logger';
import type { Period, SpendSummary, SpendByModel, SpendByProject, SpendDaily } from '../types';

const CACHE_TTL = 60; // 60 seconds

export class SpendService {
    private repository: SpendRepository;
    private cache: MemoryCache<any>;

    constructor(repository: SpendRepository) {
        this.repository = repository;
        this.cache = new MemoryCache();
    }

    /**
     * Get spend summary with caching
     */
    async getSummary(period: Period, forceRefresh = false): Promise<SpendSummary> {
        const cacheKey = `summary:${period}`;

        if (!forceRefresh) {
            const cached = this.cache.get<SpendSummary>(cacheKey);
            if (cached) {
                Logger.debug('Returning cached summary', { period });
                return cached;
            }
        }

        Logger.info('Fetching spend summary', { period });
        const data = await this.repository.getSummary(period);
        this.cache.set(cacheKey, data, CACHE_TTL);
        return data;
    }

    /**
     * Get spend by model with caching
     */
    async getByModel(period: Period, forceRefresh = false): Promise<SpendByModel> {
        const cacheKey = `byModel:${period}`;

        if (!forceRefresh) {
            const cached = this.cache.get<SpendByModel>(cacheKey);
            if (cached) {
                Logger.debug('Returning cached model breakdown', { period });
                return cached;
            }
        }

        Logger.info('Fetching spend by model', { period });
        const data = await this.repository.getByModel(period);
        this.cache.set(cacheKey, data, CACHE_TTL);
        return data;
    }

    /**
     * Get spend by project with caching
     */
    async getByProject(period: Period, forceRefresh = false): Promise<SpendByProject> {
        const cacheKey = `byProject:${period}`;

        if (!forceRefresh) {
            const cached = this.cache.get<SpendByProject>(cacheKey);
            if (cached) {
                Logger.debug('Returning cached project breakdown', { period });
                return cached;
            }
        }

        Logger.info('Fetching spend by project', { period });
        const data = await this.repository.getByProject(period);
        this.cache.set(cacheKey, data, CACHE_TTL);
        return data;
    }

    /**
     * Get daily spend with caching
     */
    async getDaily(period: Period, forceRefresh = false): Promise<SpendDaily> {
        const cacheKey = `daily:${period}`;

        if (!forceRefresh) {
            const cached = this.cache.get<SpendDaily>(cacheKey);
            if (cached) {
                Logger.debug('Returning cached daily spend', { period });
                return cached;
            }
        }

        Logger.info('Fetching daily spend', { period });
        const data = await this.repository.getDaily(period);
        this.cache.set(cacheKey, data, CACHE_TTL);
        return data;
    }

    /**
     * Clear all cached data
     */
    clearCache(): void {
        this.cache.clear();
        Logger.info('Spend cache cleared');
    }
}
