/**
 * Simple in-memory cache with TTL
 */

export class MemoryCache<T> {
    private cache = new Map<string, { value: T; expires: number }>();

    /**
     * Get value from cache
     */
    get(key: string): T | undefined {
        const entry = this.cache.get(key);

        if (!entry) {
            return undefined;
        }

        if (Date.now() > entry.expires) {
            this.cache.delete(key);
            return undefined;
        }

        return entry.value;
    }

    /**
     * Set value in cache with TTL
     */
    set(key: string, value: T, ttlSeconds: number): void {
        const expires = Date.now() + ttlSeconds * 1000;
        this.cache.set(key, { value, expires });
    }

    /**
     * Check if key exists and is not expired
     */
    has(key: string): boolean {
        return this.get(key) !== undefined;
    }

    /**
     * Remove value from cache
     */
    delete(key: string): void {
        this.cache.delete(key);
    }

    /**
     * Clear all cached values
     */
    clear(): void {
        this.cache.clear();
    }

    /**
     * Get cache size
     */
    size(): number {
        return this.cache.size;
    }
}
