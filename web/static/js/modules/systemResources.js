/**
 * System Resources Module - 系统资源监控模块
 * 负责监控CPU、内存、磁盘等系统资源使用情况
 * 单一职责：系统资源实时监控
 */

const SystemResources = {
    // 状态
    state: {
        container: null,
        resources: {},
        history: {
            cpu: [],
            memory: [],
            disk: []
        },
        updateInterval: null,
        maxHistory: 60 // 保留60个数据点
    },

    // 配置
    config: {
        apiEndpoint: '/api/system/resources',
        refreshInterval: 2000, // 2秒
        chartUpdateInterval: 5000 // 5秒更新图表
    },

    /**
     * 初始化系统资源模块
     */
    init: function(containerId) {
        console.log('System Resources initializing...');
        this.state.container = document.getElementById(containerId || 'systemResourcesContent');
        
        if (!this.state.container) {
            console.error('System Resources container not found');
            return;
        }

        this.loadResources();
        this.startAutoRefresh();
    },

    /**
     * 加载资源数据
     */
    loadResources: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            if (!response.ok) throw new Error('Failed to fetch resources');

            const data = await response.json();
            this.updateResources(data);
            this.render();
        } catch (error) {
            console.error('Failed to load resources:', error);
            this.render();
        }
    },

    /**
     * 更新资源数据
     */
    updateResources: function(data) {
        this.state.resources = data;

        // 更新历史记录
        if (data.cpu_percent !== undefined) {
            this.state.history.cpu.push({
                time: new Date(),
                value: data.cpu_percent
            });
        }

        if (data.memory?.percent !== undefined) {
            this.state.history.memory.push({
                time: new Date(),
                value: data.memory.percent
            });
        }

        if (data.disk?.percent !== undefined) {
            this.state.history.disk.push({
                time: new Date(),
                value: data.disk.percent
            });
        }

        // 限制历史记录长度
        Object.keys(this.state.history).forEach(key => {
            if (this.state.history[key].length > this.state.maxHistory) {
                this.state.history[key] = this.state.history[key].slice(-this.state.maxHistory);
            }
        });
    },

    /**
     * 渲染界面
     */
    render: function() {
        const html = this.buildHtml();
        this.state.container.innerHTML = html;
        this.bindEvents();
        
        // 渲染图表
        this.renderCharts();
    },

    /**
     * 构建HTML
     */
    buildHtml: function() {
        const resources = this.state.resources;
        const cpu = resources.cpu_percent || 0;
        const memory = resources.memory?.percent || 0;
        const disk = resources.disk?.percent || 0;

        return `
            <div class="system-resources-container">
                <!-- 资源概览卡片 -->
                <div class="resource-cards mb-4">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="resource-card cpu-card">
                                <div class="resource-icon">
                                    <i class="fas fa-microchip"></i>
                                </div>
                                <div class="resource-info">
                                    <div class="resource-value">${cpu.toFixed(1)}%</div>
                                    <div class="resource-label">CPU 使用率</div>
                                </div>
                                <div class="progress mt-2" style="height: 8px;">
                                    <div class="progress-bar ${this.getProgressColor(cpu)}" 
                                         style="width: ${cpu}%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="resource-card memory-card">
                                <div class="resource-icon">
                                    <i class="fas fa-memory"></i>
                                </div>
                                <div class="resource-info">
                                    <div class="resource-value">${memory.toFixed(1)}%</div>
                                    <div class="resource-label">内存使用率</div>
                                </div>
                                <div class="progress mt-2" style="height: 8px;">
                                    <div class="progress-bar ${this.getProgressColor(memory)}" 
                                         style="width: ${memory}%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="resource-card disk-card">
                                <div class="resource-icon">
                                    <i class="fas fa-hdd"></i>
                                </div>
                                <div class="resource-info">
                                    <div class="resource-value">${disk.toFixed(1)}%</div>
                                    <div class="resource-label">磁盘使用率</div>
                                </div>
                                <div class="progress mt-2" style="height: 8px;">
                                    <div class="progress-bar ${this.getProgressColor(disk)}" 
                                         style="width: ${disk}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 详细信息 -->
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>资源详情
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="detail-section">
                                    <h6>CPU 信息</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td>当前使用率</td>
                                            <td><strong>${cpu.toFixed(1)}%</strong></td>
                                        </tr>
                                        <tr>
                                            <td>核心数</td>
                                            <td><strong>${navigator.hardwareConcurrency || '未知'}</strong></td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="detail-section">
                                    <h6>内存信息</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td>总内存</td>
                                            <td><strong>${this.formatBytes(resources.memory?.total)}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>可用内存</td>
                                            <td><strong>${this.formatBytes(resources.memory?.available)}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>使用率</td>
                                            <td><strong>${memory.toFixed(1)}%</strong></td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <div class="detail-section">
                                    <h6>磁盘信息</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td>总容量</td>
                                            <td><strong>${this.formatBytes(resources.disk?.total)}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>可用空间</td>
                                            <td><strong>${this.formatBytes(resources.disk?.free)}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>使用率</td>
                                            <td><strong>${disk.toFixed(1)}%</strong></td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="detail-section">
                                    <h6>更新时间</h6>
                                    <p class="text-muted">${this.formatTimestamp(resources.timestamp)}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 实时图表 -->
                <div class="card mt-4">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>资源使用趋势
                        </h6>
                    </div>
                    <div class="card-body">
                        <canvas id="resourcesChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 渲染图表
     */
    renderCharts: function() {
        const canvas = document.getElementById('resourcesChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const history = this.state.history;

        // 简化的图表绘制
        this.drawSimpleChart(ctx, history.cpu, 'CPU', '#0d6efd');
        this.drawSimpleChart(ctx, history.memory, '内存', '#198754');
        this.drawSimpleChart(ctx, history.disk, '磁盘', '#ffc107');
    },

    /**
     * 绘制简化的折线图
     */
    drawSimpleChart: function(ctx, data, label, color) {
        if (data.length < 2) return;

        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        const padding = 40;

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();

        const step = (width - padding * 2) / Math.max(data.length - 1, 1);

        data.forEach((point, index) => {
            const x = padding + index * step;
            const y = height - padding - (point.value / 100) * (height - padding * 2);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();

        // 绘制标签
        ctx.fillStyle = color;
        ctx.font = '12px sans-serif';
        ctx.fillText(label, 10, 20);
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 可以添加刷新按钮事件
    },

    /**
     * 获取进度条颜色
     */
    getProgressColor: function(value) {
        if (value < 60) return 'bg-success';
        if (value < 80) return 'bg-warning';
        return 'bg-danger';
    },

    /**
     * 格式化字节
     */
    formatBytes: function(bytes) {
        if (!bytes) return '--';
        const gb = bytes / (1024 * 1024 * 1024);
        return gb.toFixed(2) + ' GB';
    },

    /**
     * 格式化时间戳
     */
    formatTimestamp: function(timestamp) {
        if (!timestamp) return '--';
        try {
            return new Date(timestamp).toLocaleString('zh-CN');
        } catch (error) {
            return timestamp;
        }
    },

    /**
     * 开始自动刷新
     */
    startAutoRefresh: function() {
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
        }

        this.state.updateInterval = setInterval(() => {
            this.loadResources();
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
        return this.loadResources();
    },

    /**
     * 获取当前资源状态
     */
    getStatus: function() {
        return {
            ...this.state.resources,
            history: this.state.history
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('System Resources destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.SystemResources = SystemResources;

