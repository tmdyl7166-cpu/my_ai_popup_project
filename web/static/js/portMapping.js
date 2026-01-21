/**
 * Port Mapping Module - 端口映射表模块
 * 负责统一前后端口映射表显示和监控
 * 单一职责：端口状态监控和配置管理
 */

const PortMapping = {
    // 状态
    state: {
        container: null,
        ports: [],
        updateInterval: null,
        autoRefresh: true,
        editingPort: null
    },

    // 配置
    config: {
        refreshInterval: 30000, // 30秒
        apiEndpoint: '/api/ports',
        portMapping: {
            'web': { port: 8080, name: 'Web监控中心', protocol: 'http', description: '主监控界面' },
            'api': { port: 8000, name: 'API服务', protocol: 'http', description: 'REST API服务' },
            'websocket': { port: 8080, name: 'WebSocket', protocol: 'ws', description: '实时通信服务' },
            'gpu': { port: None, name: 'GPU监控', protocol: 'internal', description: 'GPU状态监控' },
            'database': { port: None, name: '数据库', protocol: 'sqlite', description: 'SQLite数据存储' }
        }
    },

    /**
     * 初始化端口映射表模块
     */
    init: function() {
        console.log('Port Mapping initializing...');
        this.state.container = document.getElementById('portMappingContent');

        if (!this.state.container) {
            console.error('Port Mapping container not found');
            return;
        }

        this.loadPorts();
        this.startAutoRefresh();
    },

    /**
     * 加载端口数据
     */
    loadPorts: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            if (!response.ok) throw new Error('Failed to fetch ports');

            const data = await response.json();
            this.state.ports = data.ports || [];
            this.render();
        } catch (error) {
            console.error('Failed to load ports:', error);
            // 使用默认端口映射
            this.state.ports = this.getDefaultPorts();
            this.render();
        }
    },

    /**
     * 获取默认端口列表
     */
    getDefaultPorts: function() {
        return [
            {
                key: 'web',
                name: 'Web监控中心',
                port: 8080,
                protocol: 'http',
                status: 'running',
                description: '主监控界面',
                host: '0.0.0.0'
            },
            {
                key: 'api',
                name: 'API服务',
                port: 8000,
                protocol: 'http',
                status: 'stopped',
                description: 'REST API服务',
                host: '0.0.0.0'
            },
            {
                key: 'websocket',
                name: 'WebSocket',
                port: 8080,
                protocol: 'ws',
                status: 'running',
                description: '实时通信服务',
                host: '0.0.0.0'
            },
            {
                key: 'health',
                name: '健康检查',
                port: 8080,
                protocol: 'http',
                status: 'running',
                description: '健康检查端点',
                host: '0.0.0.0'
            }
        ];
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
        const ports = this.state.ports;
        const summary = this.getPortSummary(ports);

        return `
            <div class="port-mapping-container">
                <!-- 端口统计 -->
                <div class="port-summary mb-4">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-primary">
                                    <i class="fas fa-network-wired fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.total}</div>
                                    <div class="summary-label">总端口数</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-success">
                                    <i class="fas fa-check-circle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.running}</div>
                                    <div class="summary-label">运行中</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-warning">
                                    <i class="fas fa-pause-circle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.stopped}</div>
                                    <div class="summary-label">已停止</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-danger">
                                    <i class="fas fa-exclamation-circle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.error}</div>
                                    <div class="summary-label">异常</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 端口列表 -->
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-list me-2"></i>端口映射表
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="portMapping.refresh()">
                                <i class="fas fa-sync me-1"></i>刷新
                            </button>
                            <button class="btn btn-outline-secondary" onclick="portMapping.export()">
                                <i class="fas fa-download me-1"></i>导出
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover port-table">
                                <thead>
                                    <tr>
                                        <th>服务名称</th>
                                        <th>端口</th>
                                        <th>协议</th>
                                        <th>状态</th>
                                        <th>描述</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${this.buildPortRows(ports)}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- 端口映射说明 -->
                <div class="card mt-4">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>端口映射说明
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="config-section">
                                    <h6><i class="fas fa-server me-2"></i>前端服务</h6>
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>服务</th>
                                                <th>端口</th>
                                                <th>访问地址</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>Web监控中心</td>
                                                <td>8080</td>
                                                <td><code>http://localhost:8080</code></td>
                                            </tr>
                                            <tr>
                                                <td>健康检查</td>
                                                <td>8080</td>
                                                <td><code>http://localhost:8080/api/health</code></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="config-section">
                                    <h6><i class="fas fa-code me-2"></i>API接口</h6>
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>接口</th>
                                                <th>端点</th>
                                                <th>方法</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>项目状态</td>
                                                <td><code>/api/project/status</code></td>
                                                <td><span class="badge bg-info">GET</span></td>
                                            </tr>
                                            <tr>
                                                <td>脚本列表</td>
                                                <td><code>/api/scripts/list</code></td>
                                                <td><span class="badge bg-info">GET</span></td>
                                            </tr>
                                            <tr>
                                                <td>系统资源</td>
                                                <td><code>/api/system/resources</code></td>
                                                <td><span class="badge bg-info">GET</span></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建端口行HTML
     */
    buildPortRows: function(ports) {
        if (!ports || ports.length === 0) {
            return `
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <i class="fas fa-info-circle fa-2x text-muted mb-2"></i>
                        <p class="text-muted">暂无端口数据</p>
                    </td>
                </tr>
            `;
        }

        return ports.map(port => `
            <tr data-port="${port.key}">
                <td>
                    <strong>${this.escapeHtml(port.name)}</strong>
                    <br>
                    <small class="text-muted">${this.escapeHtml(port.key)}</small>
                </td>
                <td>
                    <code class="port-number">${port.port || '--'}</code>
                </td>
                <td>
                    <span class="badge bg-secondary">${port.protocol.toUpperCase()}</span>
                </td>
                <td>
                    <span class="badge bg-${this.getStatusColor(port.status)}">
                        <i class="fas fa-${this.getStatusIcon(port.status)} me-1"></i>
                        ${this.getStatusText(port.status)}
                    </span>
                </td>
                <td>
                    <small>${this.escapeHtml(port.description || '--')}</small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary"
                                onclick="portMapping.checkPort('${port.key}')"
                                title="检查端口状态">
                            <i class="fas fa-search"></i>
                        </button>
                        <button class="btn btn-outline-info"
                                onclick="portMapping.showDetails('${port.key}')"
                                title="查看详情">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${port.status !== 'running' ? `
                            <button class="btn btn-outline-success"
                                    onclick="portMapping.startPort('${port.key}')"
                                    title="启动服务">
                                <i class="fas fa-play"></i>
                            </button>
                        ` : `
                            <button class="btn btn-outline-warning"
                                    onclick="portMapping.stopPort('${port.key}')"
                                    title="停止服务">
                                <i class="fas fa-stop"></i>
                            </button>
                        `}
                    </div>
                </td>
            </tr>
        `).join('');
    },

    /**
     * 获取端口统计
     */
    getPortSummary: function(ports) {
        const total = ports.length;
        const running = ports.filter(p => p.status === 'running').length;
        const stopped = ports.filter(p => p.status === 'stopped').length;
        const error = ports.filter(p => p.status === 'error').length;

        return { total, running, stopped, error };
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 端口行点击事件
        const rows = this.state.container.querySelectorAll('.port-table tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', (event) => {
                // 避免按钮点击时触发
                if (event.target.tagName === 'BUTTON' || event.target.closest('button')) return;

                const portKey = row.getAttribute('data-port');
                this.showDetails(portKey);
            });
        });
    },

    /**
     * 检查端口状态
     */
    checkPort: function(portKey) {
        const port = this.state.ports.find(p => p.key === portKey);
        if (!port) return;

        ModalManager.alert({
            title: `${port.name} 状态检查`,
            content: `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">检查中...</span>
                    </div>
                    <p class="mt-2">正在检查端口 ${port.port}...</p>
                </div>
            `,
            size: 'sm'
        });

        // 模拟检查过程
        setTimeout(() => {
            const isRunning = port.status === 'running';
            ModalManager.update(this.getLastModalId(), {
                content: `
                    <div class="port-check-result">
                        <div class="text-center mb-3">
                            <i class="fas ${isRunning ? 'fa-check-circle text-success' : 'fa-times-circle text-danger'} fa-3x"></i>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <strong>服务名称:</strong> ${port.name}
                            </div>
                            <div class="col-md-6">
                                <strong>端口:</strong> ${port.port}
                            </div>
                            <div class="col-md-6">
                                <strong>协议:</strong> ${port.protocol.toUpperCase()}
                            </div>
                            <div class="col-md-6">
                                <strong>状态:</strong>
                                <span class="badge bg-${this.getStatusColor(port.status)}">${this.getStatusText(port.status)}</span>
                            </div>
                        </div>
                        <div class="mt-3">
                            <strong>描述:</strong> ${port.description || '无'}
                        </div>
                        <div class="mt-3">
                            <strong>访问地址:</strong>
                            <code>${port.protocol}://localhost:${port.port}</code>
                        </div>
                    </div>
                `
            });
        }, 1500);
    },

    /**
     * 显示端口详情
     */
    showDetails: function(portKey) {
        const port = this.state.ports.find(p => p.key === portKey);
        if (!port) return;

        const content = `
            <div class="port-details">
                <div class="row">
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>服务Key:</strong> ${port.key}
                        </div>
                        <div class="detail-item">
                            <strong>服务名称:</strong> ${port.name}
                        </div>
                        <div class="detail-item">
                            <strong>端口:</strong> ${port.port || '未配置'}
                        </div>
                        <div class="detail-item">
                            <strong>协议:</strong>
                            <span class="badge bg-secondary">${port.protocol.toUpperCase()}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>状态:</strong>
                            <span class="badge bg-${this.getStatusColor(port.status)}">${this.getStatusText(port.status)}</span>
                        </div>
                        <div class="detail-item">
                            <strong>主机:</strong> ${port.host || '0.0.0.0'}
                        </div>
                        <div class="detail-item">
                            <strong>描述:</strong> ${port.description || '无'}
                        </div>
                        <div class="detail-item">
                            <strong>访问地址:</strong>
                            <code>${port.protocol}://${port.host || 'localhost'}:${port.port}</code>
                        </div>
                    </div>
                </div>
            </div>
        `;

        ModalManager.alert({
            title: `${port.name} 详情`,
            content: content,
            size: 'lg'
        });
    },

    /**
     * 启动端口服务
     */
    startPort: function(portKey) {
        ModalManager.confirm({
            title: '确认启动',
            content: `确定要启动 ${portKey} 服务吗？`,
            onConfirm: () => {
                Notifications.show('启动中', `正在启动 ${portKey} 服务...`, 'info');
                // 模拟启动过程
                setTimeout(() => {
                    const port = this.state.ports.find(p => p.key === portKey);
                    if (port) {
                        port.status = 'running';
                        this.render();
                    }
                    Notifications.show('启动成功', `${portKey} 服务已启动`, 'success');
                }, 2000);
            }
        });
    },

    /**
     * 停止端口服务
     */
    stopPort: function(portKey) {
        ModalManager.confirm({
            title: '确认停止',
            content: `确定要停止 ${portKey} 服务吗？`,
            onConfirm: () => {
                Notifications.show('停止中', `正在停止 ${portKey} 服务...`, 'info');
                // 模拟停止过程
                setTimeout(() => {
                    const port = this.state.ports.find(p => p.key === portKey);
                    if (port) {
                        port.status = 'stopped';
                        this.render();
                    }
                    Notifications.show('已停止', `${portKey} 服务已停止`, 'warning');
                }, 2000);
            }
        });
    },

    /**
     * 导出端口配置
     */
    export: function() {
        const data = {
            timestamp: new Date().toISOString(),
            project: 'AI弹窗项目',
            version: '1.0.0',
            ports: this.state.ports
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `port-mapping-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        Notifications.show('导出成功', '端口配置已导出', 'success');
    },

    /**
     * 获取状态颜色
     */
    getStatusColor: function(status) {
        const colors = {
            'running': 'success',
            'active': 'success',
            'stopped': 'warning',
            'inactive': 'warning',
            'error': 'danger',
            'failed': 'danger',
            'unknown': 'secondary'
        };
        return colors[status] || 'secondary';
    },

    /**
     * 获取状态图标
     */
    getStatusIcon: function(status) {
        const icons = {
            'running': 'check-circle',
            'active': 'check-circle',
            'stopped': 'pause-circle',
            'inactive': 'pause-circle',
            'error': 'exclamation-circle',
            'failed': 'times-circle',
            'unknown': 'question-circle'
        };
        return icons[status] || 'question-circle';
    },

    /**
     * 获取状态文本
     */
    getStatusText: function(status) {
        const texts = {
            'running': '运行中',
            'active': '活跃',
            'stopped': '已停止',
            'inactive': '未激活',
            'error': '错误',
            'failed': '失败',
            'unknown': '未知'
        };
        return texts[status] || status;
    },

    /**
     * HTML转义
     */
    escapeHtml: function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * 获取最后一个模态框ID
     */
    getLastModalId: function() {
        const modals = document.querySelectorAll('.modal');
        return modals[modals.length - 1]?.id;
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
                this.loadPorts();
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
        return this.loadPorts();
    },

    /**
     * 更新数据
     */
    update: function(newData) {
        this.state.ports = newData.ports || [];
        this.render();
    },

    /**
     * 销毁端口映射表模块
     */
    destroy: function() {
        console.log('Port Mapping destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.portMapping = PortMapping;

