/**
 * Cache Manager Module - 缓存管理器
 * 负责管理所有缓存，防止缓存冲突
 * 单一职责：缓存存储、清理和冲突避免
 */

const CacheManager = {
    // 状态
    state: {
        cacheStore: new Map(),
        cachePrefix: 'app_',
        maxCacheSize: 50,
        expirationTimes: new Map()
    },

    // 配置
    config: {
        defaultExpiration: 300000, // 5分钟
        longExpiration: 3600000,   // 1小时
        checkInterval: 60000       // 1分钟检查一次过期
    },

    /**
     * 初始化缓存管理器
     */
    init: function() {
        console.log('Cache Manager initializing...');
        this.startExpirationChecker();
    },

    /**
     * 设置缓存
     */
    set: function(key, value, expiration = null) {
        const cacheKey = this.state.cachePrefix + key;
        const expiresAt = expiration || Date.now() + this.config.defaultExpiration;

        const cacheData = {
            value: value,
            expiresAt: expiresAt,
            createdAt: Date.now(),
            key: key
        };

        // 检查缓存大小
        if (this.state.cacheStore.size >= this.state.maxCacheSize) {
            this.evictOldest();
        }

        this.state.cacheStore.set(cacheKey, cacheData);
        this.state.expirationTimes.set(cacheKey, expiresAt);

        console.log(`Cache set: ${key}, expires in: ${(expiresAt - Date.now()) / 1000}s`);
        return true;
    },

    /**
     * 获取缓存
     */
    get: function(key) {
        const cacheKey = this.state.cachePrefix + key;
        const data = this.state.cacheStore.get(cacheKey);

        if (!data) {
            console.log(`Cache miss: ${key}`);
            return null;
        }

        // 检查是否过期
        if (Date.now() > data.expiresAt) {
            this.remove(key);
            console.log(`Cache expired: ${key}`);
            return null;
        }

        console.log(`Cache hit: ${key}`);
        return data.value;
    },

    /**
     * 删除缓存
     */
    remove: function(key) {
        const cacheKey = this.state.cachePrefix + key;
        this.state.cacheStore.delete(cacheKey);
        this.state.expirationTimes.delete(cacheKey);
        console.log(`Cache removed: ${key}`);
        return true;
    },

    /**
     * 检查缓存是否存在
     */
    has: function(key) {
        const cacheKey = this.state.cachePrefix + key;
        return this.state.cacheStore.has(cacheKey);
    },

    /**
     * 清空所有缓存
     */
    clear: function() {
        this.state.cacheStore.clear();
        this.state.expirationTimes.clear();
        console.log('All cache cleared');
    },

    /**
     * 清空指定前缀的缓存
     */
    clearByPrefix: function(prefix) {
        const keysToDelete = [];
        this.state.cacheStore.forEach((data, key) => {
            if (key.startsWith(this.state.cachePrefix + prefix)) {
                keysToDelete.push(key.replace(this.state.cachePrefix, ''));
            }
        });

        keysToDelete.forEach(key => this.remove(key));
        console.log(`Cleared cache with prefix: ${prefix}`);
        return keysToDelete.length;
    },

    /**
     * 获取缓存大小
     */
    size: function() {
        return this.state.cacheStore.size;
    },

    /**
     * 清理过期缓存
     */
    cleanup: function() {
        const now = Date.now();
        const expiredKeys = [];

        this.state.cacheStore.forEach((data, key) => {
            if (now > data.expiresAt) {
                expiredKeys.push(key);
            }
        });

        expiredKeys.forEach(key => {
            const actualKey = key.replace(this.state.cachePrefix, '');
            this.remove(actualKey);
        });

        console.log(`Cleaned up ${expiredKeys.length} expired cache items`);
        return expiredKeys.length;
    },

    /**
     * 驱逐最旧的缓存项
     */
    evictOldest: function() {
        let oldestKey = null;
        let oldestTime = Infinity;

        this.state.cacheStore.forEach((data, key) => {
            if (data.createdAt < oldestTime) {
                oldestTime = data.createdAt;
                oldestKey = key;
            }
        });

        if (oldestKey) {
            const actualKey = oldestKey.replace(this.state.cachePrefix, '');
            this.remove(actualKey);
            console.log(`Evicted oldest cache: ${actualKey}`);
        }
    },

    /**
     * 启动过期检查器
     */
    startExpirationChecker: function() {
        if (this.state.expirationTimer) {
            clearInterval(this.state.expirationTimer);
        }

        this.state.expirationTimer = setInterval(() => {
            this.cleanup();
        }, this.config.checkInterval);
    },

    /**
     * 停止过期检查器
     */
    stopExpirationChecker: function() {
        if (this.state.expirationTimer) {
            clearInterval(this.state.expirationTimer);
            this.state.expirationTimer = null;
        }
    },

    /**
     * 缓存API响应
     */
    cacheApiResponse: async function(endpoint, fetchFn, expiration = null) {
        const cacheKey = `api_${endpoint}`;
        const cached = this.get(cacheKey);
        
        if (cached) {
            return cached;
        }

        const data = await fetchFn();
        this.set(cacheKey, data, expiration);
        return data;
    },

    /**
     * 获取所有缓存键
     */
    keys: function() {
        const keys = [];
        this.state.cacheStore.forEach((data, key) => {
            keys.push(key.replace(this.state.cachePrefix, ''));
        });
        return keys;
    },

    /**
     * 获取缓存统计
     */
    getStats: function() {
        return {
            totalItems: this.state.cacheStore.size,
            maxSize: this.state.maxCacheSize,
            prefix: this.state.cachePrefix,
            activeTimers: !!this.state.expirationTimer
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('Cache Manager destroying...');
        this.stopExpirationChecker();
        this.clear();
    }
};

// 导出到全局
window.CacheManager = CacheManager;
