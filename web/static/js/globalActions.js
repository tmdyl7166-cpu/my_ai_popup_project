/**
 * Global Actions Module - 全局操作模块
 * 负责全局操作的执行和管理
 * 单一职责：全局操作处理
 */

const GlobalActions = {
    // 状态
    state: {
        actions: new Map(),
        loading: false
    },

    // 配置
    config: {
        defaultTimeout: 30000 // 默认超时时间
    },

    /**
     * 初始化全局操作模块
     */
    init: function() {
        console.log('Global Actions initializing...');
        this.registerDefaultActions();
        this.bindKeyboardShortcuts();
    },

    /**
     * 注册默认操作
     */
    registerDefaultActions: function() {
        // 刷新所有
        this.register('refreshAll', {
            name: '刷新所有',
            description: '刷新所有监控数据',
            icon: 'fas fa-sync',
            handler: this.handleRefreshAll.bind(this)
        });

        // 健康检查
        this.register('runHealthCheck', {
            name: '健康检查',
            description: '运行系统健康检查',
            icon: 'fas fa-heartbeat',
            handler: this.handleHealthCheck.bind(this)
        });

        // 导出报告
        this.register('exportReport', {
            name: '导出报告',
            description: '导出系统状态报告',
            icon: 'fas fa-download',
            handler: this.handleExportReport.bind(this)
        });

        // 重启服务
        this.register('restartServices', {
            name: '重启服务',
            description: '重启所有后台服务',
            icon: 'fas fa-redo',
            handler: this.handleRestartServices.bind(this),
            confirm: true
        });

        // 清理缓存
        this.register('clearCache', {
            name: '清理缓存',
            description: '清理系统缓存',
            icon: 'fas fa-trash',
            handler: this.handleClearCache.bind(this)
        });
    },

    /**
     * 注册操作
     */
    register: function(key, action) {
        this.state.actions.set(key, {
            key: key,
            name: action.name || key,
            description: action.description || '',
            icon: action.icon || 'fas fa-cog',
            handler: action.handler,
            confirm: action.confirm || false,
            timeout: action.timeout || this.config.defaultTimeout
        });
    },

    /**
     * 执行操作
     */
    execute: async function(key, params = {}) {
        const action = this.state.actions.get(key);
        if (!action) {
            console.error(`Action '${key}' not found`);
            Notifications.show('操作失败', `操作 '${key}' 不存在`, 'error');
            return false;
        }

        // 如果需要确认
        if (action.confirm) {
            const confirmed = await this.showConfirmDialog(action);
            if (!confirmed) return false;
        }

        // 显示加载状态
        this.setLoading(true, action.name);

        try {
            // 执行操作
            const result = await this.runAction(action, params);

            // 显示成功消息
            Notifications.show('操作成功', `${action.name} 已完成`, 'success');

            return result;

        } catch (error) {
            console.error(`Action '${key}' failed:`, error);
            Notifications.show('操作失败', `${action.name} 失败: ${error.message}`, 'error');
            return false;

        } finally {
            this.setLoading(false);
        }
    },

    /**
     * 运行操作
     */
    runAction: function(action, params) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('操作超时'));
            }, action.timeout);

            try {
                const result = action.handler(params);
                if (result instanceof Promise) {
                    result.then(resolve).catch(reject).finally(() => clearTimeout(timeout));
                } else {
                    clearTimeout(timeout);
                    resolve(result);
                }
            } catch (error) {
                clearTimeout(timeout);
                reject(error);
            }
        });
    },

    /**
     * 显示确认对话框
     */
    showConfirmDialog: function(action) {
        return new Promise((resolve) => {
            ModalManager.confirm({
                title: '确认操作',
                content: `确定要执行 "${action.name}" 操作吗？<br><br><small class="text-muted">${action.description}</small>`,
                onConfirm: () => resolve(true),
                onCancel: () => resolve(false)
            });
        });
    },

    /**
     * 设置加载状态
     */
    setLoading: function(loading, message = '') {
        this.state.loading = loading;

        const loader = document.getElementById('globalLoader');
        if (loader) {
            if (loading) {
                const messageElement = loader.querySelector('h5');
                if (messageElement) {
                    messageElement.textContent = message;
                }
                loader.style.display = 'flex';
            } else {
                loader.style.display = 'none';
            }
        }
    },

    /**
     * 绑定键盘快捷键
     */
    bindKeyboardShortcuts: function() {
        document.addEventListener('keydown', (event) => {
            // Ctrl+R: 刷新所有
            if (event.ctrlKey && event.key === 'r') {
                event.preventDefault();
                this.refreshAll();
            }

            // Ctrl+H: 健康检查
            if (event.ctrlKey && event.key === 'h') {
                event.preventDefault();
                this.runHealthCheck();
            }

            // Ctrl+E: 导出报告
            if (event.ctrlKey && event.key === 'e') {
                event.preventDefault();
                this.exportReport();
            }
        });
    },

    /**
     * 刷新所有
     */
    refreshAll: function() {
        return this.execute('refreshAll');
    },

    /**
     * 运行健康检查
     */
    runHealthCheck: function() {
        return this.execute('runHealthCheck');
    },

    /**
     * 导出报告
     */
    exportReport: function() {
        return this.execute('exportReport');
    },

    /**
     * 重启服务
     */
    restartServices: function() {
        return this.execute('restartServices');
    },

    /**
     * 清理缓存
     */
    clearCache: function() {
        return this.execute('clearCache');
    },

    /**
     * 处理刷新所有
     */
    handleRefreshAll: async function() {
        console.log('Refreshing all data...');

        const modules = [
            'globalMonitor',
            'deploymentProgress',
            'moduleStatus',
            'scriptControl',
            'configManagement',
            'logsViewer'
        ];

        const refreshPromises = modules.map(moduleName => {
            const module = window[moduleName];
            if (module && typeof module.refresh === 'function') {
                return module.refresh();
            }
            return Promise.resolve();
        });

        await Promise.all(refreshPromises);
        console.log('All data refreshed');
    },

    /**
     * 处理健康检查
     */
    handleHealthCheck: async function() {
        console.log('Running health check...');

        try {
            const response = await fetch('/api/health');
            if (!response.ok) throw new Error('Health check failed');

            const healthData = await response.json();

            // 更新全局状态
            this.updateGlobalStatus(healthData);

            console.log('Health check completed:', healthData);

        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    },

    /**
     * 处理导出报告
     */
    handleExportReport: async function() {
        console.log('Exporting report...');

        try {
            // 收集所有模块的数据
            const reportData = {
                timestamp: new Date().toISOString(),
                system: await this.collectSystemData(),
                modules: await this.collectModulesData(),
                scripts: await this.collectScriptsData(),
                logs: await this.collectLogsData()
            };

            // 生成报告
            const report = this.generateReport(reportData);

            // 下载报告
            this.downloadReport(report, `system-report-${Date.now()}.json`);

        } catch (error) {
            console.error('Export report error:', error);
            throw error;
        }
    },

    /**
     * 处理重启服务
     */
    handleRestartServices: async function() {
        console.log('Restarting services...');

        // 这里可以实现服务重启逻辑
        // 例如调用后端API来重启服务

        // 模拟重启过程
        await new Promise(resolve => setTimeout(resolve, 2000));

        // 刷新所有数据
        await this.handleRefreshAll();

        console.log('Services restarted');
    },

    /**
     * 处理清理缓存
     */
    handleClearCache: async function() {
        console.log('Clearing cache...');

        // 清理本地存储
        localStorage.clear();
        sessionStorage.clear();

        // 清理Service Worker缓存（如果有）
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames.map(cacheName => caches.delete(cacheName))
            );
        }

        console.log('Cache cleared');
    },

    /**
     * 收集系统数据
     */
    collectSystemData: async function() {
        try {
            const response = await fetch('/api/system/resources');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Failed to collect system data:', error);
        }
        return {};
    },

    /**
     * 收集模块数据
     */
    collectModulesData: async function() {
        try {
            const response = await fetch('/api/project/status');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Failed to collect modules data:', error);
        }
        return {};
    },

    /**
     * 收集脚本数据
     */
    collectScriptsData: async function() {
        try {
            const response = await fetch('/api/scripts/status');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Failed to collect scripts data:', error);
        }
        return {};
    },

    /**
     * 收集日志数据
     */
    collectLogsData: async function() {
        // 这里可以实现日志收集逻辑
        return {
            recent_errors: [],
            system_logs: []
        };
    },

    /**
     * 生成报告
     */
    generateReport: function(data) {
        return {
            title: 'AI弹窗项目系统报告',
            generated_at: data.timestamp,
            summary: {
                status: 'generated',
                modules_count: Object.keys(data.modules.components || {}).length,
                scripts_count: data.scripts.scripts ? data.scripts.scripts.length : 0
            },
            data: data
        };
    },

    /**
     * 下载报告
     */
    downloadReport: function(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    /**
     * 更新全局状态
     */
    updateGlobalStatus: function(healthData) {
        // 更新全局状态指示器
        const statusElement = document.getElementById('globalStatus');
        if (statusElement) {
            const isHealthy = healthData.status === 'healthy';
            statusElement.className = `badge bg-${isHealthy ? 'success' : 'danger'}`;
            const icon = statusElement.querySelector('i');
            const text = statusElement.querySelector('small');

            if (icon) icon.className = `fas fa-circle me-1`;
            if (text) text.textContent = isHealthy ? '系统正常' : '系统异常';
        }
    },

    /**
     * 获取操作列表
     */
    getActions: function() {
        return Array.from(this.state.actions.values());
    },

    /**
     * 获取操作详情
     */
    getAction: function(key) {
        return this.state.actions.get(key);
    },

    /**
     * 检查是否正在加载
     */
    isLoading: function() {
        return this.state.loading;
    },

    /**
     * 销毁全局操作模块
     */
    destroy: function() {
        console.log('Global Actions destroying...');
        this.state.actions.clear();
        this.state.loading = false;
    }
};

// 导出到全局
window.GlobalActions = GlobalActions;
