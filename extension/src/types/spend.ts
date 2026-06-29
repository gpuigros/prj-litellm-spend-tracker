/**
 * Type definitions for spend data
 */

export type Period = 'today' | 'week' | 'month';

export interface SpendSummary {
    user_id: string;
    period: Period;
    currency: string;
    spend: number;
    budget: number;
    remaining: number;
    budget_used_percent: number;
}

export interface ModelSpend {
    model: string;
    spend: number;
    percentage: number;
    requests: number;
    tokens: number;
}

export interface SpendByModel {
    period: Period;
    currency: string;
    models: ModelSpend[];
}

export interface ProjectSpend {
    project: string;
    spend: number;
    percentage: number;
    requests: number;
}

export interface SpendByProject {
    period: Period;
    currency: string;
    projects: ProjectSpend[];
}

export interface DailySpend {
    date: string;
    spend: number;
    requests: number;
    tokens: number;
}

export interface SpendDaily {
    period: Period;
    currency: string;
    days: DailySpend[];
}
