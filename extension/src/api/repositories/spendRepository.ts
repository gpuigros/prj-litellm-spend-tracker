/**
 * Spend repository for API calls
 */

import { ApiClient } from '../client';
import type { Period, SpendSummary, SpendByModel, SpendByProject, SpendDaily } from '../../types';

export class SpendRepository {
    private client: ApiClient;

    constructor(client: ApiClient) {
        this.client = client;
    }

    /**
     * Get spend summary
     */
    async getSummary(period: Period): Promise<SpendSummary> {
        return this.client.get<SpendSummary>('/me/spend/summary', { period });
    }

    /**
     * Get spend by model
     */
    async getByModel(period: Period): Promise<SpendByModel> {
        return this.client.get<SpendByModel>('/me/spend/by-model', { period });
    }

    /**
     * Get spend by project
     */
    async getByProject(period: Period): Promise<SpendByProject> {
        return this.client.get<SpendByProject>('/me/spend/by-project', { period });
    }

    /**
     * Get daily spend
     */
    async getDaily(period: Period): Promise<SpendDaily> {
        return this.client.get<SpendDaily>('/me/spend/daily', { period });
    }
}
