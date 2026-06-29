/**
 * Budget repository for API calls
 */

import { ApiClient } from '../client';
import type { Budget } from '../../types';

export class BudgetRepository {
    private client: ApiClient;

    constructor(client: ApiClient) {
        this.client = client;
    }

    /**
     * Get budget information
     */
    async getBudget(): Promise<Budget> {
        return this.client.get<Budget>('/me/budget');
    }
}
