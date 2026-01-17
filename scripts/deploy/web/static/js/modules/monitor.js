/**
 * 监控面板模块
 * 实时显示系统状态和监控数据
 */

class MonitorPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('监控面板容器不存在:', containerId);
            return;
        }
        
        this.charts = {};
        this.metrics = {
            cpu: [],
            memory: [],
            disk: [],
            timestamps: []
        };
        this.maxDataPoints = 60; // 最多保存60个数据点
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        this.render();
        this.setupEventListeners();
        this.startAutoRefresh();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="monitor-panel">
                <div class="monitor-header">
                    <h3><i class="fas fa-chart-line"></i> 实时监控</h3>
                    <div class="monitor-controls">
                        <button class="btn btn-sm btn-outline-secondary" id="pauseMonitor">
                            <i class="fas fa-pause"></i> 暂停
                        </button>
                        <button class="btn btn-sm btn-outline-primary" id="refreshMonitor">
                            <i class="fas fa-sync-alt"></i> 刷新
                        </button>
                    </div>
                </div>
                
                <div class="monitor-stats">
                    <div class="stat-card cpu">
                        <div class="stat-icon">
                            <i class="fas fa-microchip"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value" id="cpuValue">--</div>
                            <div class="stat-label">CPU 使用率</div>
                            <div class="progress">
                                <div class="progress-bar" id="cpuProgress" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="stat-card memory">
                        <div class="stat-icon">
                            <i class="fas fa-memory"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value" id="memoryValue">--</div>
                            <div class="stat-label">内存使用率</div>
                            <div class="progress">
                                <div class="progress-bar" id="memoryProgress" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="stat-card disk">
                        <div class="stat-icon">
                            <i class="fas fa-hdd"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value" id="diskValue">--</div>
                            <div class="stat-label">磁盘使用率</div>
                            <div class="progress">
                                <div class="progress-bar" id="diskProgress" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="stat-card network">
                        <div class="stat-icon">
                            <i class="fas fa-network-wired"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value" id="networkStatus">--</div>
                            <div class="stat-label">网络状态</div>
                            <div class="status-badge" id="networkBadge">--</div>
                        </div>
                    </div>
                </div>
                
                <div class="monitor-charts">
                    <div class="chart-container">
                        <canvas id="metricsChart"></canvas>
                    </div>
                </div>
                
                <div class="monitor-details">
                    <div class="detail-section">
                        <h4>运行服务</h4>
                        <div id="servicesList" class="services-list">
                            <div class="loading">加载中...</div>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h4>最近事件</h4>
                        <div id="eventsList" class="events-list">
                            <div class="loading">加载中...</div>
                        </div>
                    </div>
                </div>
                
                <div class="monitor-footer">
                    <span class="last-update">最后更新: <span id="lastUpdateTime">--</span></span>
                    <span class="update-frequency">更新频率: 5秒</span>
                </div>
            </div>
        `;
        
        // 初始化Chart
        this.initChart();
    }
    
    initChart() {
        const canvas = document.getElementById('metricsChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        this.charts.metrics = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'CPU',
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        data: [],
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '内存',
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        data: [],
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                animation: {
                    duration: 0
                }
            }
        });
    }
    
    setupEventListeners() {
        // 暂停/继续监控
        const pauseBtn = document.getElementById('pauseMonitor');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.togglePause());
        }
        
        // 手动刷新
        const refreshBtn = document.getElementById('refreshMonitor');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }
    }
    
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.refresh();
        }, 5000);
        
        // 立即刷新一次
        this.refresh();
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    async refresh() {
        try {
            // 获取系统资源数据
            const response = await fetch('/api/system/resources');
            if (response.ok) {
                const data = await response.json();
                this.updateStats(data);
                this.updateChart(data);
                this.updateTimestamp();
            }
            
            // 获取服务状态
            await this.loadServices();
            
        } catch (e) {
            console.error('刷新监控数据失败:', e);
        }
    }
    
    updateStats(data) {
        if (!data) return;
        
        // CPU
        const cpuPercent = data.cpu_percent || 0;
        document.getElementById('cpuValue').textContent = `${cpuPercent.toFixed(1)}%`;
        document.getElementById('cpuProgress').style.width = `${cpuPercent}%`;
        this._setProgressBarColor('cpuProgress', cpuPercent);
        
        // 内存
        const memoryPercent = data.memory?.percent || 0;
        const memoryUsed = this._formatBytes(data.memory?.available || 0);
        const memoryTotal = this._formatBytes(data.memory?.total || 0);
        document.getElementById('memoryValue').textContent = `${memoryPercent.toFixed(1)}%`;
        document.getElementById('memoryProgress').style.width = `${memoryPercent}%`;
        this._setProgressBarColor('memoryProgress', memoryPercent);
        
        // 磁盘
        const diskPercent = data.disk?.percent || 0;
        document.getElementById('diskValue').textContent = `${diskPercent.toFixed(1)}%`;
        document.getElementById('diskProgress').style.width = `${diskPercent}%`;
        this._setProgressBarColor('diskProgress', diskPercent);
        
        // 网络状态
        const networkBadge = document.getElementById('networkBadge');
        const networkStatus = document.getElementById('networkStatus');
        if (cpuPercent > 0) {
            networkStatus.textContent = '正常';
            networkBadge.textContent = '在线';
            networkBadge.className = 'status-badge badge-success';
        } else {
            networkStatus.textContent = '空闲';
            networkBadge.textContent = '空闲';
            networkBadge.className = 'status-badge badge-secondary';
        }
    }
    
    updateChart(data) {
        if (!data || !this.charts.metrics) return;
        
        const now = new Date().toLocaleTimeString();
        const cpuPercent = data.cpu_percent || 0;
        const memoryPercent = data.memory?.percent || 0;
        
        // 添加新数据
        this.metrics.cpu.push(cpuPercent);
        this.metrics.memory.push(memoryPercent);
        this.metrics.timestamps.push(now);
        
        // 保持数据点数量
        if (this.metrics.cpu.length > this.maxDataPoints) {
            this.metrics.cpu.shift();
            this.metrics.memory.shift();
            this.metrics.timestamps.shift();
        }
        
        // 更新图表
        this.charts.metrics.data.labels = [...this.metrics.timestamps];
        this.charts.metrics.data.datasets[0].data = [...this.metrics.cpu];
        this.charts.metrics.data.datasets[1].data = [...this.metrics.memory];
        this.charts.metrics.update();
    }
    
    async loadServices() {
        const container = document.getElementById('servicesList');
        if (!container) return;
        
        try {
            const response = await fetch('/api/scripts/list');
            if (response.ok) {
                const services = await response.json();
                
                if (services.length === 0) {
                    container.innerHTML = '<div class="empty">暂无运行的服务</div>';
                    return;
                }
                
                container.innerHTML = services.map(service => `
                    <div class="service-item">
                        <div class="service-info">
                            <span class="service-name">${service.display_name || service.name}</span>
                            <span class="service-status badge badge-${this._getStatusClass(service.status)}">
                                ${service.status}
                            </span>
                        </div>
                        <div class="service-meta">
                            <span>频率: ${service.frequency || 'manual'}</span>
                        </div>
                    </div>
                `).join('');
            }
        } catch (e) {
            container.innerHTML = '<div class="error">加载服务列表失败</div>';
        }
    }
    
    updateTimestamp() {
        const now = new Date().toLocaleString();
        document.getElementById('lastUpdateTime').textContent = now;
    }
    
    togglePause() {
        const btn = document.getElementById('pauseMonitor');
        if (this.refreshInterval) {
            this.stopAutoRefresh();
            btn.innerHTML = '<i class="fas fa-play"></i> 继续';
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-outline-success');
        } else {
            this.startAutoRefresh();
            btn.innerHTML = '<i class="fas fa-pause"></i> 暂停';
            btn.classList.remove('btn-outline-success');
            btn.classList.add('btn-outline-secondary');
        }
    }
    
    _setProgressBarColor(elementId, value) {
        const element = document.getElementById(elementId);
        if (value >= 90) {
            element.className = 'progress-bar bg-danger';
        } else if (value >= 70) {
            element.className = 'progress-bar bg-warning';
        } else {
            element.className = 'progress-bar bg-success';
        }
    }
    
    _getStatusClass(status) {
        const statusMap = {
            'running': 'success',
            'completed': 'info',
            'failed': 'danger',
            'idle': 'secondary',
            'stopped': 'warning'
        };
        return statusMap[status] || 'secondary';
    }
    
    _formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    destroy() {
        this.stopAutoRefresh();
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
}

// 导出到全局
window.MonitorPanel = MonitorPanel;

