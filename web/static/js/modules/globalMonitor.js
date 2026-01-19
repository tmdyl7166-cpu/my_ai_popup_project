/**
 * Global Monitor Module - 全局监控模块
 * 负责全局内容部署实时监控
 * 单一职责：全局监控显示和更新
 */

const GlobalMonitor = {
    // 状态
    state: {
        container: null,
        data: null,
        updateInterval: null,
        autoRefresh: true
    },

    // 配置
    config: {
        refreshInterval: 30000, // 30秒
        apiEndpoint: '/api/project/status'
    },

    /**
     * 初始化全局监控模块
     */
    init: function() {
        console.log('Global Monitor initializing...');
        this.state.container = document.getElementById('globalMonitorContent');

        if (!this.state.container) {
            console.error('Global Monitor container not found');
            return;
        }

        this.loadData();
        this.startAutoRefresh();
    },

    /**
     * 加载数据
     */
    loadData: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            if (!response.ok) throw new Error('Failed to fetch data');

            this.state.data = await response.json();
            this.render();
        } catch (error) {
            console.error('Failed to load global monitor data:', error);
            this.showError(error.message);
        }
    },

    /**
     * 渲染内容
     */
    render: function() {
        if (!this.state.data) return;

        const html = this.buildHtml();
        this.state.container.innerHTML = html;
        this.bindEvents();
    },

    /**
     * 构建HTML
     */
    buildHtml: function() {
        const data = this.state.data;

        return `
            <div class="global-monitor-grid">
                <!-- 项目概览 -->
                <div class="monitor-card">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-project-diagram me-2"></i>项目概览
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="metric-item">
                                    <div class="metric-label">项目名称</div>
                                    <div class="metric-value">${data.project_name || '未知'}</div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="metric-item">
                                    <div class="metric-label">版本</div>
                                    <div class="metric-value">${data.version || '未知'}</div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="metric-item">
                                    <div class="metric-label">状态</div>
                                    <div class="metric-value">
                                        <span class="badge bg-${this.getStatusColor(data.status)}">${this.getStatusText(data.status)}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="metric-item">
                                    <div class="metric-label">最后更新</div>
                                    <div class="metric-value">${this.formatTimestamp(data.last_updated)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 组件状态 -->
                <div class="monitor-card">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-cubes me-2"></i>组件状态
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="components-grid">
                            ${this.buildComponentsHtml(data.components)}
                        </div>
                    </div>
                </div>

                <!-- 系统资源 -->
                <div class="monitor-card">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-server me-2"></i>系统资源
                        </h6>
                    </div>
                    <div class="card-body">
                        ${this.buildSystemResourcesHtml()}
                    </div>
                </div>

                <!-- 实时指标 -->
                <div class="monitor-card">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>实时指标
                        </h6>
                    </div>
                    <div class="card-body">
                        <canvas id="globalMonitorChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建组件HTML
     */
    buildComponentsHtml: function(components) {
        if (!components) return '<div class="text-muted">暂无组件数据</div>';

        return Object.entries(components).map(([name, component]) => `
            <div class="component-item">
                <div class="component-name">${name}</div>
                <div class="component-status">
                    <span class="badge bg-${this.getStatusColor(component.status)}">${this.getStatusText(component.status)}</span>
                </div>
                <div class="component-time">${this.formatTimestamp(component.last_check)}</div>
            </div>
        `).join('');
    },

    /**
     * 构建系统资源HTML
     */
    buildSystemResourcesHtml: function() {
        // 这里可以从系统监控模块获取数据
        return `
            <div class="resource-metrics">
                <div class="resource-item">
                    <div class="resource-label">CPU使用率</div>
                    <div class="resource-value" id="globalCpuUsage">--%</div>
                    <div class="progress mt-1" style="height: 6px;">
                        <div class="progress-bar bg-info" id="globalCpuBar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="resource-item">
                    <div class="resource-label">内存使用率</div>
                    <div class="resource-value" id="globalMemoryUsage">--%</div>
                    <div class="progress mt-1" style="height: 6px;">
                        <div class="progress-bar bg-success" id="globalMemoryBar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="resource-item">
                    <div class="resource-label">磁盘使用率</div>
                    <div class="resource-value" id="globalDiskUsage">--%</div>
                    <div class="progress mt-1" style="height: 6px;">
                        <div class="progress-bar bg-warning" id="globalDiskBar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 组件点击事件
        const componentItems = this.state.container.querySelectorAll('.component-item');
        componentItems.forEach(item => {
            item.addEventListener('click', () => {
                const componentName = item.querySelector('.component-name').textContent;
                this.showComponentDetails(componentName);
            });
        });
    },

    /**
     * 显示组件详情
     */
    showComponentDetails: function(componentName) {
        if (!this.state.data || !this.state.data.components) return;

        const component = this.state.data.components[componentName];
        if (!component) return;

        const content = `
            <div class="component-details">
                <h6>${componentName} 组件详情</h6>
                <div class="row">
                    <div class="col-md-6">
                        <strong>状态:</strong> <span class="badge bg-${this.getStatusColor(component.status)}">${this.getStatusText(component.status)}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>最后检查:</strong> ${this.formatTimestamp(component.last_check)}
                    </div>
                </div>
                ${component.details ? `<pre class="mt-3">${JSON.stringify(component.details, null, 2)}</pre>` : ''}
            </div>
        `;

        ModalManager.alert({
            title: `${componentName} 详情`,
            content: content,
            size: 'lg'
        });
    },

    /**
     * 更新系统资源显示
     */
    updateSystemResources: function(resources) {
        if (!resources) return;

        // 更新CPU
        const cpuUsage = document.getElementById('globalCpuUsage');
        const cpuBar = document.getElementById('globalCpuBar');
        if (cpuUsage && cpuBar) {
            cpuUsage.textContent = `${resources.cpu_percent?.toFixed(1) || 0}%`;
            cpuBar.style.width = `${resources.cpu_percent || 0}%`;
        }

        // 更新内存
        const memoryUsage = document.getElementById('globalMemoryUsage');
        const memoryBar = document.getElementById('globalMemoryBar');
        if (memoryUsage && memoryBar) {
            const memoryPercent = resources.memory?.percent || 0;
            memoryUsage.textContent = `${memoryPercent.toFixed(1)}%`;
            memoryBar.style.width = `${memoryPercent}%`;
        }

        // 更新磁盘
        const diskUsage = document.getElementById('globalDiskUsage');
        const diskBar = document.getElementById('globalDiskBar');
        if (diskUsage && diskBar) {
            const diskPercent = resources.disk?.percent || 0;
            diskUsage.textContent = `${diskPercent.toFixed(1)}%`;
            diskBar.style.width = `${diskPercent}%`;
        }
    },

    /**
     * 获取状态颜色
     */
    getStatusColor: function(status) {
        const colors = {
            'healthy': 'success',
            'running': 'success',
            'warning': 'warning',
            'error': 'danger',
            'failed': 'danger',
            'stopped': 'secondary'
        };
        return colors[status] || 'secondary';
    },

    /**
     * 获取状态文本
     */
    getStatusText: function(status) {
        const texts = {
            'healthy': '正常',
            'running': '运行中',
            'warning': '警告',
            'error': '错误',
            'failed': '失败',
            'stopped': '已停止'
        };
        return texts[status] || status;
    },

    /**
     * 格式化时间戳
     */
    formatTimestamp: function(timestamp) {
        if (!timestamp) return '--';
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('zh-CN');
        } catch (error) {
            return timestamp;
        }
    },

    /**
     * 显示错误
     */
    showError: function(message) {
        this.state.container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                加载失败: ${message}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="globalMonitor.refresh()">
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
                this.loadData();
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
        return this.loadData();
    },

    /**
     * 更新数据
     */
    update: function(newData) {
        this.state.data = newData;
        this.render();
    },

    /**
     * 销毁全局监控模块
     */
    destroy: function() {
        console.log('Global Monitor destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.globalMonitor = GlobalMonitor;
