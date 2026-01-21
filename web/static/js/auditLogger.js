/**
 * Audit Logger Module - 审计日志模块
 * 记录所有安全相关操作和系统事件
 * 单一职责：审计日志记录和查询
 */

const AuditLogger = {
    // 状态
    state: {
        logs: [],
        maxLogs: 1000,
        isEnabled: true,
        autoRefresh: true
    },

    // 配置
    config: {
        apiEndpoint: '/api/audit/logs',
        exportEndpoint: '/api/audit/export',
        refreshInterval: 10000, // 10秒
        levels: ['info', 'warning', 'error', 'critical']
    },

    // 事件类型
    eventTypes: {
        AUTH: '认证',
        API_ACCESS: 'API访问',
        SCRIPT_EXECUTION: '脚本执行',
        CONFIG_CHANGE: '配置变更',
        SECURITY: '安全事件',
        SYSTEM: '系统事件',
        DEPLOYMENT: '部署事件'
    },

    /**
     * 初始化审计日志模块
     */
    init: function(containerId) {
        console.log('Audit Logger initializing...');
        this.state.container = document.getElementById(containerId || 'auditLoggerContent');
        
        if (!this.state.container) {
            console.error('Audit Logger container not found');
            return;
        }

        this.render();
        this.loadLogs();
        this.startAutoRefresh();
    },

    /**
     * 渲染界面
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
        return `
            <div class="audit-logger-container">
                <div class="card">
                    <div class="card-header bg-gradient-dark text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-history me-2"></i>审计日志
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-light" onclick="AuditLogger.loadLogs()">
                                <i class="fas fa-sync me-1"></i>刷新
                            </button>
                            <button class="btn btn-outline-light" onclick="AuditLogger.exportLogs()">
                                <i class="fas fa-download me-1"></i>导出
                            </button>
                            <button class="btn btn-outline-light" onclick="AuditLogger.clearLogs()">
                                <i class="fas fa-trash me-1"></i>清空
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- 过滤器 -->
                        <div class="filter-section mb-3">
                            <div class="row">
                                <div class="col-md-3">
                                    <select class="form-select form-select-sm" id="auditLevelFilter" onchange="AuditLogger.filterLogs()">
                                        <option value="">所有级别</option>
                                        <option value="info">信息</option>
                                        <option value="warning">警告</option>
                                        <option value="error">错误</option>
                                        <option value="critical">严重</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <select class="form-select form-select-sm" id="auditTypeFilter" onchange="AuditLogger.filterLogs()">
                                        <option value="">所有类型</option>
                                        ${Object.entries(this.eventTypes).map(([key, value]) => 
                                            `<option value="${key}">${value}</option>`
                                        ).join('')}
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <input type="text" class="form-control form-control-sm" 
                                        id="auditSearchInput" placeholder="搜索日志内容..."
                                        onkeyup="AuditLogger.filterLogs()">
                                </div>
                                <div class="col-md-2">
                                    <span class="badge bg-secondary" id="logCount">0 条记录</span>
                                </div>
                            </div>
                        </div>

                        <!-- 日志表格 -->
                        <div class="log-table-container" style="max-height: 400px; overflow-y: auto;">
                            <table class="table table-sm table-hover" id="auditLogTable">
                                <thead class="table-light sticky-top">
                                    <tr>
                                        <th style="width: 60px;">级别</th>
                                        <th style="width: 80px;">时间</th>
                                        <th style="width: 80px;">类型</th>
                                        <th>事件</th>
                                        <th style="width: 100px;">来源</th>
                                        <th style="width: 60px;">详情</th>
                                    </tr>
                                </thead>
                                <tbody id="auditLogBody">
                                    ${this.buildLogRows()}
                                </tbody>
                            </table>
                        </div>

                        <!-- 统计信息 -->
                        <div class="mt-3">
                            <div class="row text-center">
                                <div class="col-md-3">
                                    <div class="badge bg-info fs-6">信息: <span id="countInfo">0</span></div>
                                </div>
                                <div class="col-md-3">
                                    <div class="badge bg-warning fs-6">警告: <span id="countWarning">0</span></div>
                                </div>
                                <div class="col-md-3">
                                    <div class="badge bg-danger fs-6">错误: <span id="countError">0</span></div>
                                </div>
                                <div class="col-md-3">
                                    <div class="badge bg-dark fs-6">总计: <span id="countTotal">0</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建日志行
     */
    buildLogRows: function() {
        if (this.state.logs.length === 0) {
            return `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p class="mb-0">暂无日志记录</p>
                    </td>
                </tr>
            `;
        }

        return this.state.logs.slice(0, 100).map(log => `
            <tr class="log-row" data-level="${log.level}" data-type="${log.event_type}">
                <td>
                    <span class="badge ${this.getLevelClass(log.level)}">
                        ${this.getLevelIcon(log.level)}
                    </span>
                </td>
                <td><small>${this.formatTime(log.timestamp)}</small></td>
                <td><small>${this.eventTypes[log.event_type] || log.event_type}</small></td>
                <td>
                    <div class="log-message">${this.escapeHtml(log.message)}</div>
                    ${log.details ? `<small class="text-muted">${this.escapeHtml(log.details)}</small>` : ''}
                </td>
                <td><small>${log.source || '-'}</small></td>
                <td>
                    ${log.metadata ? `
                        <button class="btn btn-sm btn-link" onclick="AuditLogger.showDetails('${log.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    ` : '-'}
                </td>
            </tr>
        `).join('');
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 事件已在HTML中处理
    },

    /**
     * 加载日志
     */
    loadLogs: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.state.logs = data.logs || [];
                this.updateDisplay();
            }
        } catch (error) {
            console.error('加载审计日志失败:', error);
            // 使用模拟数据
            this.state.logs = this.getMockLogs();
            this.updateDisplay();
        }
    },

    /**
     * 更新显示
     */
    updateDisplay: function() {
        const tbody = document.getElementById('auditLogBody');
        if (tbody) {
            tbody.innerHTML = this.buildLogRows();
        }
        
        this.updateStats();
        this.updateLogCount();
    },

    /**
     * 更新统计
     */
    updateStats: function() {
        const counts = {
            info: 0,
            warning: 0,
            error: 0,
            critical: 0
        };
        
        this.state.logs.forEach(log => {
            if (counts[log.level] !== undefined) {
                counts[log.level]++;
            }
        });
        
        document.getElementById('countInfo').textContent = counts.info;
        document.getElementById('countWarning').textContent = counts.warning;
        document.getElementById('countError').textContent = counts.error + counts.critical;
        document.getElementById('countTotal').textContent = this.state.logs.length;
    },

    /**
     * 更新日志计数
     */
    updateLogCount: function() {
        const element = document.getElementById('logCount');
        if (element) {
            element.textContent = `${this.state.logs.length} 条记录`;
        }
    },

    /**
     * 过滤日志
     */
    filterLogs: function() {
        const level = document.getElementById('auditLevelFilter')?.value || '';
        const type = document.getElementById('auditTypeFilter')?.value || '';
        const search = document.getElementById('auditSearchInput')?.value.toLowerCase() || '';
        
        let filteredLogs = this.state.logs;
        
        if (level) {
            filteredLogs = filteredLogs.filter(log => log.level === level);
        }
        
        if (type) {
            filteredLogs = filteredLogs.filter(log => log.event_type === type);
        }
        
        if (search) {
            filteredLogs = filteredLogs.filter(log => 
                log.message.toLowerCase().includes(search) ||
                (log.details && log.details.toLowerCase().includes(search))
            );
        }
        
        // 临时更新显示
        const originalLogs = this.state.logs;
        this.state.logs = filteredLogs;
        this.updateDisplay();
        this.state.logs = originalLogs;
    },

    /**
     * 导出日志
     */
    exportLogs: function() {
        const logs = this.state.logs;
        const csv = this.convertToCSV(logs);
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `audit_logs_${new Date().toISOString().slice(0,10)}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        bubbleMonitor.show('success', '导出成功', `已导出 ${logs.length} 条日志记录`);
    },

    /**
     * 清空日志
     */
    clearLogs: function() {
        if (confirm('确定要清空所有日志吗？此操作不可撤销。')) {
            this.state.logs = [];
            this.updateDisplay();
            bubbleMonitor.show('info', '日志已清空', '所有审计日志已被清除');
        }
    },

    /**
     * 显示详情
     */
    showDetails: function(logId) {
        const log = this.state.logs.find(l => l.id === logId);
        if (!log) return;
        
        const details = JSON.stringify(log, null, 2);
        
        ModalManager.show({
            title: '日志详情',
            content: `<pre class="bg-light p-3 rounded">${this.escapeHtml(details)}</pre>`,
            size: 'lg'
        });
    },

    /**
     * 获取级别样式类
     */
    getLevelClass: function(level) {
        const classes = {
            info: 'bg-info',
            warning: 'bg-warning',
            error: 'bg-danger',
            critical: 'bg-dark'
        };
        return classes[level] || 'bg-secondary';
    },

    /**
     * 获取级别图标
     */
    getLevelIcon: function(level) {
        const icons = {
            info: 'ℹ',
            warning: '⚠',
            error: '✕',
            critical: '⚡'
        };
        return icons[level] || '?';
    },

    /**
     * 格式化时间
     */
    formatTime: function(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
    },

    /**
     * 转义HTML
     */
    escapeHtml: function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * 转换为CSV
     */
    convertToCSV: function(logs) {
        const headers = ['时间', '级别', '类型', '事件', '来源', '详情'];
        const rows = logs.map(log => [
            log.timestamp,
            log.level,
            log.event_type,
            log.message,
            log.source || '',
            log.details || ''
        ]);
        
        return [headers, ...rows]
            .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
            .join('\n');
    },

    /**
     * 获取模拟数据
     */
    getMockLogs: function() {
        return [
            {
                id: 'log-1',
                timestamp: new Date().toISOString(),
                level: 'info',
                event_type: 'SYSTEM',
                message: '系统启动完成',
                source: 'app.py',
                details: 'Web监控服务已成功启动',
                metadata: { port: 8080, environment: 'development' }
            },
            {
                id: 'log-2',
                timestamp: new Date(Date.now() - 60000).toISOString(),
                level: 'info',
                event_type: 'API_ACCESS',
                message: '健康检查API调用',
                source: '192.168.1.1',
                details: 'GET /api/health',
                metadata: { method: 'GET', path: '/api/health' }
            },
            {
                id: 'log-3',
                timestamp: new Date(Date.now() - 120000).toISOString(),
                level: 'warning',
                event_type: 'SECURITY',
                message: 'API密钥验证失败',
                source: '192.168.1.100',
                details: '无效的API密钥尝试',
                metadata: { attempted_key: '***', reason: 'invalid_key' }
            },
            {
                id: 'log-4',
                timestamp: new Date(Date.now() - 180000).toISOString(),
                level: 'info',
                event_type: 'AUTH',
                message: '用户认证成功',
                source: 'web',
                details: 'API密钥验证通过',
                metadata: { user_role: 'admin' }
            }
        ];
    },

    /**
     * 记录日志
     */
    log: function(level, eventType, message, details = null, source = null) {
        const logEntry = {
            id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date().toISOString(),
            level: level,
            event_type: eventType,
            message: message,
            details: details,
            source: source,
            metadata: null
        };
        
        this.state.logs.unshift(logEntry);
        
        // 保持日志数量限制
        if (this.state.logs.length > this.state.maxLogs) {
            this.state.logs = this.state.logs.slice(0, this.state.maxLogs);
        }
        
        // 更新显示
        if (this.state.container) {
            this.updateDisplay();
        }
        
        return logEntry;
    },

    /**
     * 便捷方法
     */
    info: function(message, details, source) {
        return this.log('info', 'SYSTEM', message, details, source);
    },
    
    warning: function(message, details, source) {
        return this.log('warning', 'SECURITY', message, details, source);
    },
    
    error: function(message, details, source) {
        return this.log('error', 'SYSTEM', message, details, source);
    },
    
    security: function(message, details, source) {
        return this.log('warning', 'SECURITY', message, details, source);
    },

    /**
     * 开始自动刷新
     */
    startAutoRefresh: function() {
        if (this.config.autoRefresh) {
            this.state.interval = setInterval(() => {
                this.loadLogs();
            }, this.config.refreshInterval);
        }
    },

    /**
     * 停止自动刷新
     */
    stopAutoRefresh: function() {
        if (this.state.interval) {
            clearInterval(this.state.interval);
            this.state.interval = null;
        }
    },

    /**
     * 获取状态
     */
    getStatus: function() {
        return {
            isEnabled: this.state.isEnabled,
            logCount: this.state.logs.length,
            autoRefresh: this.state.autoRefresh
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('Audit Logger destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.AuditLogger = AuditLogger;

