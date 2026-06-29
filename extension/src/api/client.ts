/**
 * API client for communicating with the backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { Configuration } from '../config/configuration';
import { ApiKeyManager } from '../auth/apiKeyManager';
import { Logger } from '../utils/logger';
import type { ApiError } from '../types';

export class ApiClient {
    private axiosInstance: AxiosInstance;
    private apiKeyManager: ApiKeyManager;

    constructor(apiKeyManager: ApiKeyManager) {
        this.apiKeyManager = apiKeyManager;

        this.axiosInstance = axios.create({
            baseURL: Configuration.getApiBaseUrl(),
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Request interceptor to add authentication
        this.axiosInstance.interceptors.request.use(
            async config => {
                const apiKey = await this.apiKeyManager.ensureApiKey();
                if (apiKey) {
                    config.headers.Authorization = `Bearer ${apiKey}`;
                }
                return config;
            },
            error => {
                return Promise.reject(error);
            }
        );

        // Response interceptor for error handling
        this.axiosInstance.interceptors.response.use(
            response => response,
            (error: AxiosError<ApiError>) => {
                if (error.response) {
                    const apiError = error.response.data;
                    Logger.error('API error', {
                        status: error.response.status,
                        detail: apiError.detail,
                        url: error.config?.url,
                    });

                    // Handle 401 Unauthorized
                    if (error.response.status === 401) {
                        Logger.warn('Authentication failed, clearing API key');
                        this.apiKeyManager.removeApiKey();
                    }
                } else if (error.request) {
                    Logger.error('No response from API', { url: error.config?.url });
                } else {
                    Logger.error('Request setup error', error.message);
                }

                return Promise.reject(error);
            }
        );
    }

    /**
     * Make GET request
     */
    async get<T>(url: string, params?: any): Promise<T> {
        const response = await this.axiosInstance.get<T>(url, { params });
        return response.data;
    }

    /**
     * Update base URL
     */
    updateBaseUrl(baseUrl: string): void {
        this.axiosInstance.defaults.baseURL = baseUrl;
        Logger.info('API base URL updated', { baseUrl });
    }
}
