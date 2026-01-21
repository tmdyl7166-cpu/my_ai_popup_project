/**
 * 仪表板模块
 * 负责主仪表板的初始化、数据更新和用户交互
 */

class DashboardModule {
    constructor(config) {
        this.config = config;
        this.socket = null;
        this.charts = {};
        this.intervals = {};
        this.isActive = false;

        this.init();
    }

    init() {
        console.log('初始化仪表板模块');
        this.setupEventListeners();
        this.initializeCharts();
        this.startDataUpdates();
    }

    setupEventListeners() {
        // 刷新按钮
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // 自动刷新开关
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.config.autoRefresh = e.target.checked;
                if (e.target.checked) {
                    this.startDataUpdates();
                } else {
                    this.stopDataUpdates();
                }
            });
        }
    }

    initializeCharts() {
        // 初始化系统资源图表
        this.initializeResourceCharts();
        // 初始化脚本状态图表
        this.initializeScriptCharts();
    }

    initializeResourceCharts() {
        const ctx = document.getElementById('resource-chart');
        if (!ctx) return;

        this.charts.resources = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU使用率 (%)',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }, {
                    label: '内存使用率 (%)',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }, {
                    label: '磁盘使用率 (%)',
                    data: [],
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    initializeScriptCharts() {
        const ctx = document.getElementById('script-status-chart');
        if (!ctx) return;

        this.charts.scripts = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['运行中', '已完成', '失败', '空闲'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#dc3545',
                        '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    startDataUpdates() {
        if (!this.config.autoRefresh) return;

        // 停止现有更新
        this.stopDataUpdates();

        // 启动新的更新间隔
        this.intervals.resources = setInterval(() => {
            this.updateResourceData();
        }, this.config.refreshInterval || 5000);

        this.intervals.scripts = setInterval(() => {
            this.updateScriptData();
        }, this.config.refreshInterval || 5000);

        console.log('启动数据自动更新');
    }

    stopDataUpdates() {
        Object.values(this.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
        this.intervals = {};
        console.log('停止数据自动更新');
    }

    async updateResourceData() {
        try {
            const response = await fetch('/api/system/resources');
            const data = await response.json();

            if (data.error) {
                console.error('获取系统资源数据失败:', data.error);
                return;
            }

            this.updateResourceDisplay(data);
            this.updateResourceChart(data);

        } catch (error) {
            console.error('更新资源数据失败:', error);
        }
    }

    updateResourceDisplay(data) {
        // 更新进度条
        const cpuBar = document.getElementById('cpu-progress');
        const memoryBar = document.getElementById('memory-progress');
        const diskBar = document.getElementById('disk-progress');

        if (cpuBar) {
            cpuBar.style.width = `${data.cpu_percent}%`;
            cpuBar.textContent = `CPU: ${data.cpu_percent.toFixed(1)}%`;
        }

        if (memoryBar) {
            memoryBar.style.width = `${data.memory.percent}%`;
            memoryBar.textContent = `内存: ${data.memory.percent.toFixed(1)}%`;
        }

        if (diskBar) {
            diskBar.style.width = `${data.disk.percent}%`;
            diskBar.textContent = `磁盘: ${data.disk.percent.toFixed(1)}%`;
        }

        // 更新数值显示
        const cpuValue = document.getElementById('cpu-value');
        const memoryValue = document.getElementById('memory-value');
        const diskValue = document.getElementById('disk-value');

        if (cpuValue) cpuValue.textContent = `${data.cpu_percent.toFixed(1)}%`;
        if (memoryValue) memoryValue.textContent = `${data.memory.percent.toFixed(1)}%`;
        if (diskValue) diskValue.textContent = `${data.disk.percent.toFixed(1)}%`;
    }

    updateResourceChart(data) {
        if (!this.charts.resources) return;

        const chart = this.charts.resources;
        const now = new Date().toLocaleTimeString();

        // 添加新数据点
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(data.cpu_percent);
        chart.data.datasets[1].data.push(data.memory.percent);
        chart.data.datasets[2].data.push(data.disk.percent);

        // 限制数据点数量
        const maxPoints = 20;
        if (chart.data.labels.length > maxPoints) {
            chart.data.labels.shift();
            chart.data.datasets.forEach(dataset => dataset.data.shift());
        }

        chart.update('none');
    }

    async updateScriptData() {
        try {
            const response = await fetch('/api/scripts/status');
            const data = await response.json();

            this.updateScriptStatus(data);
            this.updateScriptChart(data);

        } catch (error) {
            console.error('更新脚本数据失败:', error);
        }
    }

    updateScriptStatus(data) {
        const statusContainer = document.getElementById('script-status-overview');
        if (!statusContainer) return;

        let html = '<div class="row">';

        // 统计各状态数量
        const stats = {
            running: 0,
            completed: 0,
            failed: 0,
            idle: 0
        };

        if (data.scripts) {
            Object.values(data.scripts).forEach(status => {
                stats[status] = (stats[status] || 0) + 1;
            });
        }

        // 生成状态卡片
        Object.entries(stats).forEach(([status, count]) => {
            const statusClass = this.getStatusClass(status);
            const statusIcon = this.getStatusIcon(status);
            const statusText = this.getStatusText(status);

            html += `
                <div class="col-md-3 mb-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <div class="status-indicator ${statusClass} mb-2"></div>
                            <h3 class="card-title">${count}</h3>
                            <p class="card-text">${statusText}</p>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        statusContainer.innerHTML = html;
    }

    updateScriptChart(data) {
        if (!this.charts.scripts) return;

        const stats = {
            running: 0,
            completed: 0,
            failed: 0,
            idle: 0
        };

        if (data.scripts) {
            Object.values(data.scripts).forEach(status => {
                stats[status] = (stats[status] || 0) + 1;
            });
        }

        this.charts.scripts.data.datasets[0].data = [
            stats.running,
            stats.completed,
            stats.failed,
            stats.idle
        ];

        this.charts.scripts.update('none');
    }

    getStatusClass(status) {
        const classes = {
            'running': 'running',
            'completed': 'healthy',
            'failed': 'error',
            'idle': ''
        };
        return classes[status] || '';
    }

    getStatusIcon(status) {
        const icons = {
            'running': 'fas fa-spinner fa-spin',
            'completed': 'fas fa-check',
            'failed': 'fas fa-times',
            'idle': 'fas fa-pause'
        };
        return icons[status] || 'fas fa-question';
    }

    getStatusText(status) {
        const texts = {
            'running': '运行中',
            'completed': '已完成',
            'failed': '失败',
            'idle': '空闲'
        };
        return texts[status] || status;
    }

    async refreshData() {
        console.log('手动刷新仪表板数据');
        await Promise.all([
            this.updateResourceData(),
            this.updateScriptData()
        ]);

        this.showNotification('数据已刷新', 'success');
    }

    showNotification(message, type = 'info') {
        // 使用全局通知系统
        if (window.NotificationSystem) {
            window.NotificationSystem.show(message, type);
        }
    }

    connectWebSocket(socket) {
        this.socket = socket;

        socket.on('status_update', (data) => {
            this.updateScriptStatus(data);
            this.updateScriptChart(data);
        });

        socket.on('resource_update', (data) => {
            this.updateResourceDisplay(data);
            this.updateResourceChart(data);
        });
    }

    disconnectWebSocket() {
        this.socket = null;
    }

    destroy() {
        this.stopDataUpdates();
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        this.isActive = false;
        console.log('仪表板模块已销毁');
    }
}

// 导出模块
window.DashboardModule = DashboardModule;
