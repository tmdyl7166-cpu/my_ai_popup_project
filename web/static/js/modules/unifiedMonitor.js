/**
 * Unified Monitor Module - 统一监控面板模块
 * 负责前后端统一监控部署页面，战损风格主题图形文结构
 * 单一职责：系统状态统一监控和可视化展示
 */

const UnifiedMonitor = {
    // 状态
    state: {
        container: null,
        updateInterval: null,
        autoRefresh: true,
        systemStatus: {},
        serviceStatus: {},
        moduleStatus: {},
        resourceUsage: {},
        uptime: 0,
        startTime: Date.now()
    },

    // 配置
    config: {
        refreshInterval: 5000, // 5秒
        apiEndpoints: {
            system: '/api/monitor/system',
            services: '/api/monitor/services',
            modules: '/api/monitor/modules',
            resources: '/api/monitor/resources',
            logs: '/api/monitor/logs'
        },
        themes: {
            warzone: {
                primary: '#2d3436',
                secondary: '#636e72',
                accent: '#d63031',
                warning: '#fdcb6e',
                success: '#00b894',
                text: '#dfe6e9',
                border: '1px solid #636e72'
            }
        }
    },

    /**
     * 初始化统一监控面板
     */
    init: function(containerId = 'unifiedMonitorContainer') {
        console.log('Unified Monitor initializing...');

        this.state.container = document.getElementById(containerId);
        if (!this.state.container) {
            console.error('Unified Monitor container not found');
            return;
        }

        this.createMonitorStructure();
        this.startMonitoring();
        this.bindEvents();
    },

    /**
     * 创建监控面板结构
     */
    createMonitorStructure: function() {
        const html = `
            <div class="unified-monitor warzone-theme">
                <!-- 顶部状态栏 -->
                <div class="monitor-header">
                    <div class="status-bar">
                        <div class="system-status">
                            <span class="status-led" id="systemLed"></span>
                            <span class="status-text" id="systemStatusText">系统正常</span>
                        </div>
                        <div class="uptime-display">
                            <i class="fas fa-clock"></i>
                            <span id="uptimeText">00:00:00</span>
                        </div>
                        <div class="resource-gauges">
                            <div class="gauge cpu-gauge">
                                <span class="gauge-label">CPU</span>
                                <div class="gauge-bar">
                                    <div class="gauge-fill" id="cpuFill"></div>
                                </div>
                                <span class="gauge-value" id="cpuValue">0%</span>
                            </div>
                            <div class="gauge memory-gauge">
                                <span class="gauge-label">内存</span>
                                <div class="gauge-bar">
                                    <div class="gauge-fill" id="memoryFill"></div>
                                </div>
                                <span class="gauge-value" id="memoryValue">0%</span>
                            </div>
                            <div class="gauge disk-gauge">
                                <span class="gauge-label">磁盘</span>
                                <div class="gauge-bar">
                                    <div class="gauge-fill" id="diskFill"></div>
                                </div>
                                <span class="gauge-value" id="diskValue">0%</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 主监控区域 -->
                <div class="monitor-main">
                    <div class="monitor-grid">
                        <!-- 后端服务状态 -->
                        <div class="monitor-panel backend-services">
                            <div class="panel-header">
                                <h6><i class="fas fa-server"></i> 后端服务</h6>
                                <div class="panel-controls">
                                    <button class="btn btn-sm btn-outline-secondary" onclick="unifiedMonitor.refreshServices()">
                                        <i class="fas fa-sync"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="panel-body">
                                <div class="service-list" id="backendServiceList">
                                    <div class="service-item loading">
                                        <div class="service-icon">
                                            <i class="fas fa-spinner fa-spin"></i>
                                        </div>
                                        <div class="service-info">
                                            <div class="service-name">加载中...</div>
                                            <div class="service-status">检测中</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 前端模块状态 -->
                        <div class="monitor-panel frontend-modules">
                            <div class="panel-header">
                                <h6><i class="fas fa-cubes"></i> 前端模块</h6>
                                <div class="panel-controls">
                                    <button class="btn btn-sm btn-outline-secondary" onclick="unifiedMonitor.refreshModules()">
                                        <i class="fas fa-sync"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="panel-body">
                                <div class="module-list" id="frontendModuleList">
                                    <div class="module-item loading">
                                        <div class="module-icon">
                                            <i class="fas fa-spinner fa-spin"></i>
                                        </div>
                                        <div class="module-info">
                                            <div class="module-name">加载中...</div>
                                            <div class="module-status">检测中</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 数据库连接 -->
                        <div class="monitor-panel database-connections">
                            <div class="panel-header">
                                <h6><i class="fas fa-database"></i> 数据库</h6>
                                <div class="panel-controls">
                                    <button class="btn btn-sm btn-outline-secondary" onclick="unifiedMonitor.refreshDatabase()">
                                        <i class="fas fa-sync"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="panel-body">
                                <div class="connection-list" id="databaseConnectionList">
                                    <div class="connection-item loading">
                                        <div class="connection-icon">
                                            <i class="fas fa-spinner fa-spin"></i>
                                        </div>
                                        <div class="connection-info">
                                            <div class="connection-name">检测中...</div>
                                            <div class="connection-status">连接中</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 缓存状态 -->
                        <div class="monitor-panel cache-status">
                            <div class="panel-header">
                                <h6><i class="fas fa-memory"></i> 缓存</h6>
                                <div class="panel-controls">
                                    <button class="btn btn-sm btn-outline-secondary" onclick="unifiedMonitor.refreshCache()">
                                        <i class="fas fa-sync"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="panel-body">
                                <div class="cache-stats" id="cacheStats">
                                    <div class="stat-item">
                                        <span class="stat-label">命中率</span>
                                        <span class="stat-value" id="cacheHitRate">0%</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">使用量</span>
                                        <span class="stat-value" id="cacheUsage">0MB</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">条目数</span>
                                        <span class="stat-value" id="cacheEntries">0</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 底部日志区 -->
                <div class="monitor-footer">
                    <div class="log-stream">
                        <div class="log-header">
                            <h6><i class="fas fa-terminal"></i> 实时日志</h6>
                            <div class="log-controls">
                                <button class="btn btn-sm btn-outline-secondary" onclick="unifiedMonitor.clearLogs()">
                                    <i class="fas fa-trash"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="unifiedMonitor.toggleAutoScroll()">
                                    <i class="fas fa-scroll"></i>
                                </button>
                            </div>
                        </div>
                        <div class="log-content" id="logContent">
                            <div class="log-entry">
                                <span class="log-time">00:00:00</span>
                                <span class="log-level">INFO</span>
                                <span class="log-message">监控系统已启动</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.state.container.innerHTML = html;
    },

    /**
     * 开始监控
     */
    startMonitoring: function() {
        // 立即执行一次
        this.refreshAll();

        // 设置定时刷新
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
        }

        this.state.updateInterval = setInterval(() => {
            if (this.state.autoRefresh) {
                this.refreshAll();
            }
        }, this.config.refreshInterval);

        // 启动运行时间计时器
        this.startUptimeTimer();
    },

    /**
     * 刷新所有数据
     */
    refreshAll: async function() {
        try {
            await Promise.all([
                this.refreshSystemStatus(),
                this.refreshServices(),
                this.refreshModules(),
                this.refreshResources(),
                this.refreshDatabase(),
                this.refreshCache()
            ]);

            this.updateOverallStatus();
        } catch (error) {
            console.error('Failed to refresh monitor data:', error);
            this.showError('数据刷新失败: ' + error.message);
        }
    },

    /**
     * 刷新系统状态
     */
    refreshSystemStatus: async function() {
        try {
            const response = await fetch(this.config.apiEndpoints.system);
            if (!response.ok) throw new Error('Failed to fetch system status');

            const data = await response.json();
            this.state.systemStatus = data;

            this.updateSystemDisplay();
        } catch (error) {
            console.error('Failed to refresh system status:', error);
            this.state.systemStatus = { status: 'error', message: error.message };
        }
    },

    /**
     * 刷新服务状态
     */
    refreshServices: async function() {
        try {
            const response = await fetch(this.config.apiEndpoints.services);
            if (!response.ok) throw new Error('Failed to fetch services');

            const data = await response.json();
            this.state.serviceStatus = data.services || {};

            this.updateServicesDisplay();
        } catch (error) {
            console.error('Failed to refresh services:', error);
            this.state.serviceStatus = {};
        }
    },

    /**
     * 刷新模块状态
     */
    refreshModules: async function() {
        try {
            const response = await fetch(this.config.apiEndpoints.modules);
            if (!response.ok) throw new Error('Failed to fetch modules');

            const data = await response.json();
            this.state.moduleStatus = data.modules || {};

            this.updateModulesDisplay();
        } catch (error) {
            console.error('Failed to refresh modules:', error);
            this.state.moduleStatus = {};
        }
    },

    /**
     * 刷新资源使用情况
     */
    refreshResources: async function() {
        try {
            const response = await fetch(this.config.apiEndpoints.resources);
            if (!response.ok) throw new Error('Failed to fetch resources');

            const data = await response.json();
            this.state.resourceUsage = data.resources || {};

            this.updateResourcesDisplay();
        } catch (error) {
            console.error('Failed to refresh resources:', error);
            this.state.resourceUsage = { cpu: 0, memory: 0, disk: 0 };
        }
    },

    /**
     * 刷新数据库状态
     */
    refreshDatabase: async function() {
        try {
            // 模拟数据库状态检查
            const dbStatus = {
                main: { status: 'connected', connections: 5, latency: 2 },
                cache: { status: 'connected', connections: 2, latency: 1 }
            };

            this.state.databaseStatus = dbStatus;
            this.updateDatabaseDisplay();
        } catch (error) {
            console.error('Failed to refresh database:', error);
        }
    },

    /**
     * 刷新缓存状态
     */
    refreshCache: async function() {
        try {
            // 模拟缓存状态
            const cacheStats = {
                hitRate: 85,
                usage: 128,
                entries: 1024
            };

            this.state.cacheStatus = cacheStats;
            this.updateCacheDisplay();
        } catch (error) {
            console.error('Failed to refresh cache:', error);
        }
    },

    /**
     * 更新系统显示
     */
    updateSystemDisplay: function() {
        const status = this.state.systemStatus;
        const led = document.getElementById('systemLed');
        const text = document.getElementById('systemStatusText');

        if (led && text) {
            const isHealthy = status.status === 'healthy' || status.status === 'running';
            led.className = `status-led ${isHealthy ? 'healthy' : 'error'}`;
            text.textContent = isHealthy ? '系统正常' : '系统异常';
        }
    },

    /**
     * 更新服务显示
     */
    updateServicesDisplay: function() {
        const services = this.state.serviceStatus;
        const container = document.getElementById('backendServiceList');

        if (!container) return;

        const serviceItems = Object.entries(services).map(([name, info]) => {
            const status = info.status || 'unknown';
            const statusClass = this.getStatusClass(status);
            const statusIcon = this.getStatusIcon(status);

            return `
                <div class="service-item ${statusClass}">
                    <div class="service-icon">
                        <i class="fas ${statusIcon}"></i>
                    </div>
                    <div class="service-info">
                        <div class="service-name">${name}</div>
                        <div class="service-status">${this.getStatusText(status)}</div>
                        ${info.uptime ? `<div class="service-uptime">${info.uptime}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = serviceItems || '<div class="no-data">暂无服务数据</div>';
    },

    /**
     * 更新模块显示
     */
    updateModulesDisplay: function() {
        const modules = this.state.moduleStatus;
        const container = document.getElementById('frontendModuleList');

        if (!container) return;

        const moduleItems = Object.entries(modules).map(([name, info]) => {
            const status = info.status || 'unknown';
            const statusClass = this.getStatusClass(status);
            const statusIcon = this.getStatusIcon(status);

            return `
                <div class="module-item ${statusClass}">
                    <div class="module-icon">
                        <i class="fas ${statusIcon}"></i>
                    </div>
                    <div class="module-info">
                        <div class="module-name">${name}</div>
                        <div class="module-status">${this.getStatusText(status)}</div>
                        ${info.version ? `<div class="module-version">v${info.version}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = moduleItems || '<div class="no-data">暂无模块数据</div>';
    },

    /**
     * 更新资源显示
     */
    updateResourcesDisplay: function() {
        const resources = this.state.resourceUsage;

        // 更新CPU
        const cpuFill = document.getElementById('cpuFill');
        const cpuValue = document.getElementById('cpuValue');
        if (cpuFill && cpuValue) {
            const cpuPercent = resources.cpu || 0;
            cpuFill.style.width = `${cpuPercent}%`;
            cpuValue.textContent = `${cpuPercent}%`;
        }

        // 更新内存
        const memoryFill = document.getElementById('memoryFill');
        const memoryValue = document.getElementById('memoryValue');
        if (memoryFill && memoryValue) {
            const memoryPercent = resources.memory || 0;
            memoryFill.style.width = `${memoryPercent}%`;
            memoryValue.textContent = `${memoryPercent}%`;
        }

        // 更新磁盘
        const diskFill = document.getElementById('diskFill');
        const diskValue = document.getElementById('diskValue');
        if (diskFill && diskValue) {
            const diskPercent = resources.disk || 0;
            diskFill.style.width = `${diskPercent}%`;
            diskValue.textContent = `${diskPercent}%`;
        }
    },

    /**
     * 更新数据库显示
     */
    updateDatabaseDisplay: function() {
        const dbStatus = this.state.databaseStatus;
        const container = document.getElementById('databaseConnectionList');

        if (!container || !dbStatus) return;

        const connectionItems = Object.entries(dbStatus).map(([name, info]) => {
            const status = info.status || 'unknown';
            const statusClass = this.getStatusClass(status);
            const statusIcon = this.getStatusIcon(status);

            return `
                <div class="connection-item ${statusClass}">
                    <div class="connection-icon">
                        <i class="fas ${statusIcon}"></i>
                    </div>
                    <div class="connection-info">
                        <div class="connection-name">${name}</div>
                        <div class="connection-status">${this.getStatusText(status)}</div>
                        ${info.connections ? `<div class="connection-count">${info.connections} 连接</div>` : ''}
                        ${info.latency ? `<div class="connection-latency">${info.latency}ms</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = connectionItems || '<div class="no-data">暂无数据库数据</div>';
    },

    /**
     * 更新缓存显示
     */
    updateCacheDisplay: function() {
        const cacheStats = this.state.cacheStatus;

        if (!cacheStats) return;

        const hitRate = document.getElementById('cacheHitRate');
        const usage = document.getElementById('cacheUsage');
        const entries = document.getElementById('cacheEntries');

        if (hitRate) hitRate.textContent = `${cacheStats.hitRate || 0}%`;
        if (usage) usage.textContent = `${cacheStats.usage || 0}MB`;
        if (entries) entries.textContent = cacheStats.entries || 0;
    },

    /**
     * 更新整体状态
     */
    updateOverallStatus: function() {
        const services = Object.values(this.state.serviceStatus);
        const modules = Object.values(this.state.moduleStatus);

        const totalServices = services.length;
        const healthyServices = services.filter(s => s.status === 'healthy' || s.status === 'running').length;

        const totalModules = modules.length;
        const healthyModules = modules.filter(m => m.status === 'loaded' || m.status === 'active').length;

        const overallHealth = (healthyServices + healthyModules) / (totalServices + totalModules);

        // 更新全局状态指示器
        const globalStatus = document.getElementById('globalStatus');
        if (globalStatus) {
            const isHealthy = overallHealth >= 0.8;
            globalStatus.innerHTML = `
                <i class="fas fa-circle text-${isHealthy ? 'success' : 'danger'} me-1"></i>
                ${isHealthy ? '系统正常' : '系统异常'}
            `;
        }
    },

    /**
     * 启动运行时间计时器
     */
    startUptimeTimer: function() {
        setInterval(() => {
            this.state.uptime = Math.floor((Date.now() - this.state.startTime) / 1000);
            this.updateUptimeDisplay();
        }, 1000);
    },

    /**
     * 更新运行时间显示
     */
    updateUptimeDisplay: function() {
        const uptimeText = document.getElementById('uptimeText');
        if (uptimeText) {
            uptimeText.textContent = this.formatUptime(this.state.uptime);
        }
    },

    /**
     * 格式化运行时间
     */
    formatUptime: function(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },

    /**
     * 获取状态样式类
     */
    getStatusClass: function(status) {
        const classes = {
            'healthy': 'status-healthy',
            'running': 'status-healthy',
            'connected': 'status-healthy',
            'loaded': 'status-healthy',
            'active': 'status-healthy',
            'warning': 'status-warning',
            'error': 'status-error',
            'failed': 'status-error',
            'disconnected': 'status-error',
            'unknown': 'status-unknown'
        };
        return classes[status] || 'status-unknown';
    },

    /**
     * 获取状态图标
     */
    getStatusIcon: function(status) {
        const icons = {
            'healthy': 'check-circle',
            'running': 'play-circle',
            'connected': 'link',
            'loaded': 'check-circle',
            'active': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle',
            'failed': 'times-circle',
            'disconnected': 'unlink',
            'unknown': 'question-circle'
        };
        return icons[status] || 'question-circle';
    },

    /**
     * 获取状态文本
     */
    getStatusText: function(status) {
        const texts = {
            'healthy': '正常',
            'running': '运行中',
            'connected': '已连接',
            'loaded': '已加载',
            'active': '活跃',
            'warning': '警告',
            'error': '错误',
            'failed': '失败',
            'disconnected': '断开',
            'unknown': '未知'
        };
        return texts[status] || status;
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 自动刷新切换
        const autoRefreshToggle = document.getElementById('autoRefreshToggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.state.autoRefresh = e.target.checked;
            });
        }
    },

    /**
     * 添加日志条目
     */
    addLogEntry: function(level, message, source = 'monitor') {
        const logContent = document.getElementById('logContent');
        if (!logContent) return;

        const now = new Date();
        const timeStr = now.toLocaleTimeString('zh-CN', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${level.toLowerCase()}`;
        logEntry.innerHTML = `
            <span class="log-time">${timeStr}</span>
            <span class="log-level">${level}</span>
            <span class="log-source">[${source}]</span>
            <span class="log-message">${message}</span>
        `;

        logContent.appendChild(logEntry);

        // 自动滚动到底部
        logContent.scrollTop = logContent.scrollHeight;

        // 限制日志条目数量
        while (logContent.children.length > 100) {
            logContent.removeChild(logContent.firstChild);
        }
    },

    /**
     * 清空日志
     */
    clearLogs: function() {
        const logContent = document.getElementById('logContent');
        if (logContent) {
            logContent.innerHTML = '';
        }
    },

    /**
     * 切换自动滚动
     */
    toggleAutoScroll: function() {
        this.state.autoScroll = !this.state.autoScroll;
        const button = document.querySelector('[onclick="unifiedMonitor.toggleAutoScroll()"]');
        if (button) {
            button.classList.toggle('active', this.state.autoScroll);
        }
    },

    /**
     * 显示错误信息
     */
    showError: function(message) {
        this.addLogEntry('ERROR', message, 'monitor');
        Notifications.show('监控错误', message, 'error');
    },

    /**
     * 显示警告信息
     */
    showWarning: function(message) {
        this.addLogEntry('WARN', message, 'monitor');
        Notifications.show('监控警告', message, 'warning');
    },

    /**
     * 显示信息
     */
    showInfo: function(message) {
        this.addLogEntry('INFO', message, 'monitor');
        Notifications.show('监控信息', message, 'info');
    },

    /**
     * 导出监控报告
     */
    exportReport: function(format = 'json') {
        const report = {
            timestamp: new Date().toISOString(),
            system: this.state.systemStatus,
            services: this.state.serviceStatus,
            modules: this.state.moduleStatus,
            resources: this.state.resourceUsage,
            database: this.state.databaseStatus,
            cache: this.state.cacheStatus,
            uptime: this.state.uptime
        };

        if (format === 'json') {
            const blob = new Blob([JSON.stringify(report, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `monitor-report-${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.showInfo('监控报告已导出');
        }
    },

    /**
     * 获取监控数据
     */
    getMonitorData: function() {
        return {
            system: this.state.systemStatus,
            services: this.state.serviceStatus,
            modules: this.state.moduleStatus,
            resources: this.state.resourceUsage,
            database: this.state.databaseStatus,
            cache: this.state.cacheStatus,
            uptime: this.state.uptime
        };
    },

    /**
     * 停止监控
     */
    stopMonitoring: function() {
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
            this.state.updateInterval = null;
        }
        this.state.autoRefresh = false;
    },

    /**
     * 销毁监控面板
     */
    destroy: function() {
        console.log('Unified Monitor destroying...');
        this.stopMonitoring();

        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.unifiedMonitor = UnifiedMonitor;
