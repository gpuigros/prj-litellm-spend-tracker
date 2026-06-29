/**
 * Type definitions for budget data
 */

export type BudgetState = 'normal' | 'warning' | 'exceeded';

export interface Budget {
    user_id: string;
    monthly_budget: number;
    currency: string;
    spent: number;
    remaining: number;
    used_percent: number;
    state: BudgetState;
    warning_threshold: number;
    exceeded_threshold: number;
}
