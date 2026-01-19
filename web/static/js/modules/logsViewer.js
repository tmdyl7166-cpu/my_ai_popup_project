/**
 * Logs Viewer Module - 日志查看模块
 * 负责日志文件的查看和管理
 * 单一职责：日志显示和过滤
 */

const LogsViewer = {
    // 状态
    state: {
        container: null,
        currentLog: null,
        logs: {},
        filters: {
            level: 'all',
            module: 'all',
            dateRange: 'today'
        },
        updateInterval: null,
        autoRefresh: true
    },

    // 配置
    config: {
        refreshInterval: 30000, // 30秒
        logsEndpoint: '/api/logs',
        maxLines: 1000,
        logTypes: ['web_app', 'health_monitor', 'system_diagnostic', 'config_validation']
    },

    /**
     * 初始化日志查看模块
     */
    init: function() {
        console.log('Logs Viewer initializing...');
        this.state.container = document.getElementById('logsViewerContent');

        if (!this.state.container) {
            console.error('Logs Viewer container not found');
            return;
        }

        this.loadLogs();
        this.startAutoRefresh();
    },

    /**
     * 加载日志
     */
    loadLogs: async function() {
        try {
            // 加载所有日志类型
            const logs = {};

            for (const logType of this.config.logTypes) {
                try {
                    const response = await fetch(`${this.config.logsEndpoint}/${logType}?lines=${this.config.maxLines}`);
                    if (response.ok) {
                        logs[logType] = await response.json();
                    } else {
                        logs[logType] = { status: 'error', message: 'Failed to load logs' };
                    }
                } catch (error) {
                    logs[logType] = { status: 'error', message: error.message };
                }
            }

            this.state.logs = logs;
            this.render();
        } catch (error) {
            console.error('Failed to load logs:', error);
            this.showError(error.message);
        }
    },

    /**
     * 渲染内容
     */
    render: function() {
        const html = this.buildHtml();
        this.state.container.innerHTML = html;
        this.bindEvents();
    },

    /**
     * 构建HTML
     */
    buildHtml: function() {
        const logs = this.state.logs;

        if (Object.keys(logs).length === 0) {
            return `
                <div class="text-center py-5">
                    <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">暂无日志</h5>
                    <p class="text-muted">日志数据未加载</p>
                </div>
            `;
        }

        return `
            <div class="logs-viewer-container">
                <!-- 日志导航 -->
                <div class="logs-nav mb-4">
                    <div class="nav nav-tabs" id="logsTabs" role="tablist">
                        ${this.buildLogTabsHtml(logs)}
                    </div>
                </div>

                <!-- 日志过滤器 -->
                <div class="logs-filters mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="filter-controls">
                            <select class="form-select form-select-sm me-2" id="levelFilter">
                                <option value="all">所有级别</option>
                                <option value="ERROR">错误</option>
                                <option value="WARNING">警告</option>
                                <option value="INFO">信息</option>
                                <option value="DEBUG">调试</option>
                            </select>
                            <select class="form-select form-select-sm me-2" id="moduleFilter">
                                <option value="all">所有模块</option>
                                <option value="web">Web模块</option>
                                <option value="backend">后端模块</option>
                                <option value="ai">AI模块</option>
                                <option value="system">系统模块</option>
                            </select>
                            <select class="form-select form-select-sm" id="dateFilter">
                                <option value="today">今天</option>
                                <option value="yesterday">昨天</option>
                                <option value="week">本周</option>
                                <option value="month">本月</option>
                            </select>
                        </div>
                        <div class="action-buttons">
                            <button class="btn btn-sm btn-outline-primary" onclick="logsViewer.applyFilters()">
                                <i class="fas fa-filter me-1"></i>应用过滤
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="logsViewer.clearFilters()">
                                <i class="fas fa-times me-1"></i>清除过滤
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 日志内容 -->
                <div class="tab-content" id="logsTabContent">
                    ${this.buildLogContentHtml(logs)}
                </div>
            </div>
        `;
    },

    /**
     * 构建日志标签页HTML
     */
    buildLogTabsHtml: function(logs) {
        const tabs = Object.entries(logs).map(([type, logData], index) => {
            const errorCount = this.countErrors(logData);
            const hasErrors = errorCount > 0;

            return `
                <button class="nav-link ${index === 0 ? 'active' : ''}"
                        id="${type}-tab"
                        data-bs-toggle="tab"
                        data-bs-target="#${type}-pane"
                        type="button"
                        role="tab"
                        aria-controls="${type}-pane"
                        aria-selected="${index === 0 ? 'true' : 'false'}">
                    <i class="fas ${this.getLogIcon(type)} me-1"></i>
                    ${this.getLogDisplayName(type)}
                    ${hasErrors ? `<span class="badge bg-danger ms-1">${errorCount}</span>` : ''}
                </button>
            `;
        }).join('');

        return tabs;
    },

    /**
     * 构建日志内容HTML
     */
    buildLogContentHtml: function(logs) {
        const contents = Object.entries(logs).map(([type, logData], index) => `
            <div class="tab-pane fade ${index === 0 ? 'show active' : ''}"
                 id="${type}-pane"
                 role="tabpanel"
                 aria-labelledby="${type}-tab"
                 tabindex="0">
                <div class="log-content">
                    ${this.buildLogEntriesHtml(type, logData)}
                </div>
            </div>
        `).join('');

        return contents;
    },

    /**
     * 构建日志条目HTML
     */
    buildLogEntriesHtml: function(type, logData) {
        if (logData.status === 'error') {
            return `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    加载日志失败: ${logData.message}
                </div>
            `;
        }

        if (!logData.logs || !Array.isArray(logData.logs) || logData.logs.length === 0) {
            return `
                <div class="text-center py-4">
                    <i class="fas fa-info-circle fa-2x text-muted mb-2"></i>
                    <p class="text-muted">暂无日志条目</p>
                </div>
            `;
        }

        // 解析和过滤日志
        const parsedLogs = this.parseLogs(logData.logs);
        const filteredLogs = this.filterLogs(parsedLogs);

        if (filteredLogs.length === 0) {
            return `
                <div class="text-center py-4">
                    <i class="fas fa-search fa-2x text-muted mb-2"></i>
                    <p class="text-muted">没有符合过滤条件的日志</p>
                </div>
            `;
        }

        return `
            <div class="log-entries">
                <div class="log-stats mb-3">
                    <small class="text-muted">
                        显示 ${filteredLogs.length} / ${parsedLogs.length} 条日志
                        (总共 ${logData.total_lines || parsedLogs.length} 行)
                    </small>
                </div>
                <div class="log-list">
                    ${filteredLogs.map(log => `
                        <div class="log-entry log-${log.level?.toLowerCase() || 'unknown'}">
                            <div class="log-time">${log.timestamp || '--'}</div>
                            <div class="log-level">
                                <span class="badge bg-${this.getLevelColor(log.level)}">${log.level || 'UNKNOWN'}</span>
                            </div>
                            <div class="log-module">${log.module || 'Unknown'}</div>
                            <div class="log-message">${this.escapeHtml(log.message || '')}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 过滤器变化事件
        const filters = ['levelFilter', 'moduleFilter', 'dateFilter'];
        filters.forEach(filterId => {
            const element = document.getElementById(filterId);
            if (element) {
                element.addEventListener('change', () => {
                    this.updateFilters();
                });
            }
        });

        // 标签页切换事件
        const tabs = this.state.container.querySelectorAll('[data-bs-toggle="tab"]');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (event) => {
                const targetType = event.target.id.replace('-tab', '');
                this.state.currentLog = targetType;
            });
        });
    },

    /**
     * 解析日志
     */
    parseLogs: function(logLines) {
        return logLines.map(line => {
            // 尝试解析常见的日志格式
            const logPattern = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.+)$/;
            const match = line.match(logPattern);

            if (match) {
                return {
                    timestamp: match[1],
                    level: match[2],
                    message: match[3],
                    module: this.extractModule(match[3])
                };
            }

            // 如果无法解析，返回原始行
            return {
                timestamp: null,
                level: 'UNKNOWN',
                message: line,
                module: 'Unknown'
            };
        });
    },

    /**
     * 过滤日志
     */
    filterLogs: function(logs) {
        const filters = this.state.filters;

        return logs.filter(log => {
            // 级别过滤
            if (filters.level !== 'all' && log.level !== filters.level) {
                return false;
            }

            // 模块过滤
            if (filters.module !== 'all' && log.module !== filters.module) {
                return false;
            }

            // 日期范围过滤
            if (filters.dateRange !== 'all' && log.timestamp) {
                const logDate = new Date(log.timestamp);
                const now = new Date();
                let startDate;

                switch (filters.dateRange) {
                    case 'today':
                        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                        break;
                    case 'yesterday':
                        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
                        const endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                        return logDate >= startDate && logDate < endDate;
                    case 'week':
                        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                        break;
                    case 'month':
                        startDate = new Date(now.getFullYear(), now.getMonth(), 1);
                        break;
                    default:
                        return true;
                }

                if (logDate < startDate) {
                    return false;
                }
            }

            return true;
        });
    },

    /**
     * 更新过滤器
     */
    updateFilters: function() {
        const levelFilter = document.getElementById('levelFilter');
        const moduleFilter = document.getElementById('moduleFilter');
        const dateFilter = document.getElementById('dateFilter');

        this.state.filters = {
            level: levelFilter ? levelFilter.value : 'all',
            module: moduleFilter ? moduleFilter.value : 'all',
            dateRange: dateFilter ? dateFilter.value : 'today'
        };

        this.render();
    },

    /**
     * 应用过滤器
     */
    applyFilters: function() {
        this.updateFilters();
    },

    /**
     * 清除过滤器
     */
    clearFilters: function() {
        this.state.filters = {
            level: 'all',
            module: 'all',
            dateRange: 'today'
        };

        // 重置选择器
        const levelFilter = document.getElementById('levelFilter');
        const moduleFilter = document.getElementById('moduleFilter');
        const dateFilter = document.getElementById('dateFilter');

        if (levelFilter) levelFilter.value = 'all';
        if (moduleFilter) moduleFilter.value = 'all';
        if (dateFilter) dateFilter.value = 'today';

        this.render();
    },

    /**
     * 提取模块信息
     */
    extractModule: function(message) {
        // 从消息中提取模块信息
        const modulePatterns = {
            'web': /web|frontend|dashboard/i,
            'backend': /backend|api|server/i,
            'ai': /ai|model|neural/i,
            'system': /system|os|hardware/i
        };

        for (const [module, pattern] of Object.entries(modulePatterns)) {
            if (pattern.test(message)) {
                return module;
            }
        }

        return 'Unknown';
    },

    /**
     * 计算错误数量
     */
    countErrors: function(logData) {
        if (!logData.logs || !Array.isArray(logData.logs)) return 0;

        return logData.logs.filter(line =>
            line.toLowerCase().includes('error') ||
            line.toLowerCase().includes('exception') ||
            line.toLowerCase().includes('failed')
        ).length;
    },

    /**
     * 获取日志图标
     */
    getLogIcon: function(type) {
        const icons = {
            'web_app': 'fa-globe',
            'health_monitor': 'fa-heartbeat',
            'system_diagnostic': 'fa-stethoscope',
            'config_validation': 'fa-check-circle'
        };
        return icons[type] || 'fa-file-alt';
    },

    /**
     * 获取日志显示名称
     */
    getLogDisplayName: function(type) {
        const names = {
            'web_app': 'Web应用日志',
            'health_monitor': '健康监控日志',
            'system_diagnostic': '系统诊断日志',
            'config_validation': '配置验证日志'
        };
        return names[type] || type;
    },

    /**
     * 获取级别颜色
     */
    getLevelColor: function(level) {
        const colors = {
            'ERROR': 'danger',
            'WARNING': 'warning',
            'INFO': 'info',
            'DEBUG': 'secondary'
        };
        return colors[level] || 'secondary';
    },

    /**
     * HTML转义
     */
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * 显示错误
     */
    showError: function(message) {
        this.state.container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                加载日志失败: ${message}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="logsViewer.refresh()">
                    <i class="fas fa-redo me-1"></i>重试
                </button>
            </div>
        `;
    },

    /**
     * 开始自动刷新
     */
    startAutoRefresh: function() {
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
        }

        this.state.updateInterval = setInterval(() => {
            if (this.state.autoRefresh) {
                this.loadLogs();
            }
        }, this.config.refreshInterval);
    },

    /**
     * 停止自动刷新
     */
    stopAutoRefresh: function() {
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
            this.state.updateInterval = null;
        }
    },

    /**
     * 刷新数据
     */
    refresh: function() {
        return this.loadLogs();
    },

    /**
     * 更新数据
     */
    update: function(newData) {
        this.state.logs = newData;
        this.render();
    },

    /**
     * 销毁日志查看模块
     */
    destroy: function() {
        console.log('Logs Viewer destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.logsViewer = LogsViewer;
