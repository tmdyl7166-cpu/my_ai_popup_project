/**
 * Performance Monitor Module - 性能监控模块
 * 监控和优化Web应用性能，提供实时性能指标和优化建议
 * 单一职责：性能监控和优化
 */

const PerformanceMonitor = {
    // 状态
    state: {
        metrics: {},
        thresholds: {},
        alerts: [],
        isMonitoring: false
    },

    // 配置
    config: {
        apiEndpoint: '/api/performance',
        metricsEndpoint: '/api/performance/metrics',
        optimizeEndpoint: '/api/performance/optimize',
        refreshInterval: 30000, // 30秒
        alertThresholds: {
            responseTime: 1000, // 1秒
            memoryUsage: 80, // 80%
            cpuUsage: 70, // 70%
            errorRate: 5 // 5%
        }
    },

    // 性能指标类型
    metricTypes: [
        { id: 'response_time', name: '响应时间', unit: 'ms', icon: 'fa-clock' },
        { id: 'memory_usage', name: '内存使用', unit: '%', icon: 'fa-memory' },
        { id: 'cpu_usage', name: 'CPU使用', unit: '%', icon: 'fa-microchip' },
        { id: 'error_rate', name: '错误率', unit: '%', icon: 'fa-exclamation-triangle' },
        { id: 'throughput', name: '吞吐量', unit: 'req/s', icon: 'fa-chart-line' },
        { id: 'active_connections', name: '活跃连接', unit: '个', icon: 'fa-users' }
    ],

    /**
     * 初始化性能监控
     */
    init: function(containerId) {
        console.log('Performance Monitor initializing...');
        this.state.container = document.getElementById(containerId || 'performanceMonitorContent');

        if (!this.state.container) {
            console.error('Performance Monitor container not found');
            return;
        }

        this.render();
        this.loadMetrics();
        this.startMonitoring();
    },

    /**
     * 渲染界面
     */
    render: function() {
        const html = this.buildHtml();
        this.state.container.innerHTML = html;
        this.bindEvents();
        this.renderCharts();
    },

    /**
     * 构建HTML
     */
    buildHtml: function() {
        return `
            <div class="performance-monitor-container">
                <div class="card">
                    <div class="card-header bg-gradient-success text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-tachometer-alt me-2"></i>性能监控
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-light" onclick="PerformanceMonitor.loadMetrics()">
                                <i class="fas fa-sync me-1"></i>刷新
                            </button>
                            <button class="btn btn-outline-light" onclick="PerformanceMonitor.showOptimization()">
                                <i class="fas fa-wrench me-1"></i>优化
                            </button>
                            <button class="btn btn-outline-light" onclick="PerformanceMonitor.showAlerts()">
                                <i class="fas fa-bell me-1"></i>告警
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- 性能概览 -->
                        <div class="row mb-3">
                            ${this.metricTypes.map(metric => `
                                <div class="col-md-4 mb-3">
                                    <div class="card h-100">
                                        <div class="card-body text-center">
                                            <div class="metric-icon mb-2">
                                                <i class="fas ${metric.icon} fa-2x text-primary"></i>
                                            </div>
                                            <h5 class="metric-value" id="${metric.id}Value">--</h5>
                                            <small class="text-muted">${metric.name}</small>
                                            <div class="progress mt-2" style="height: 6px;">
                                                <div class="progress-bar" id="${metric.id}Bar" style="width: 0%"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>

                        <!-- 性能图表 -->
                        <div class="performance-charts mb-3">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">响应时间趋势</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="responseTimeChart" height="200"></canvas>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">资源使用趋势</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="resourceUsageChart" height="200"></canvas>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 优化建议 -->
                        <div class="optimization-suggestions" id="optimizationContainer" style="display: none;">
                            <div class="card">
                                <div class="card-header bg-warning">
                                    <h6 class="mb-0">
                                        <i class="fas fa-lightbulb me-2"></i>性能优化建议
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div id="optimizationList">
                                        <div class="text-center text-muted py-3">
                                            <i class="fas fa-spinner fa-spin fa-2x mb-2"></i>
                                            <p>分析中...</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 性能告警 -->
                        <div class="performance-alerts" id="alertsContainer" style="display: none;">
                            <div class="card">
                                <div class="card-header bg-danger text-white">
                                    <h6 class="mb-0">
                                        <i class="fas fa-exclamation-triangle me-2"></i>性能告警
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div id="alertsList">
                                        <div class="alert alert-info">
                                            <i class="fas fa-info-circle me-2"></i>
                                            暂无性能告警
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 事件已在HTML中处理
    },

    /**
     * 渲染图表
     */
    renderCharts: function() {
        // 响应时间图表
        const responseCtx = document.getElementById('responseTimeChart');
        if (responseCtx) {
            this.state.responseChart = new Chart(responseCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '响应时间 (ms)',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // 资源使用图表
        const resourceCtx = document.getElementById('resourceUsageChart');
        if (resourceCtx) {
            this.state.resourceChart = new Chart(resourceCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU使用率 (%)',
                            data: [],
                            borderColor: 'rgb(255, 99, 132)',
                            tension: 0.1
                        },
                        {
                            label: '内存使用率 (%)',
                            data: [],
                            borderColor: 'rgb(54, 162, 235)',
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    },

    /**
     * 加载性能指标
     */
    loadMetrics: async function() {
        try {
            const response = await fetch(this.config.metricsEndpoint);
            const data = await response.json();

            if (data.status === 'success') {
                this.state.metrics = data.metrics || {};
                this.updateDisplay();
                this.checkThresholds();
            }
        } catch (error) {
            console.warn('加载性能指标失败，使用模拟数据:', error);
            this.state.metrics = this.getMockMetrics();
            this.updateDisplay();
        }
    },

    /**
     * 更新显示
     */
    updateDisplay: function() {
        // 更新指标数值
        this.metricTypes.forEach(metric => {
            const value = this.state.metrics[metric.id] || 0;
            const element = document.getElementById(metric.id + 'Value');
            const bar = document.getElementById(metric.id + 'Bar');

            if (element) {
                element.textContent = value + ' ' + metric.unit;
            }

            if (bar) {
                let percentage = 0;
                if (metric.unit === '%') {
                    percentage = Math.min(value, 100);
                } else if (metric.id === 'response_time') {
                    percentage = Math.min((value / 2000) * 100, 100); // 2秒为满
                } else if (metric.id === 'throughput') {
                    percentage = Math.min((value / 100) * 100, 100); // 100 req/s为满
                } else if (metric.id === 'active_connections') {
                    percentage = Math.min((value / 1000) * 100, 100); // 1000连接为满
                }

                bar.style.width = percentage + '%';
                bar.className = 'progress-bar ' + this.getProgressClass(percentage);
            }
        });

        // 更新图表
        this.updateCharts();
    },

    /**
     * 更新图表数据
     */
    updateCharts: function() {
        const now = new Date().toLocaleTimeString();

        // 响应时间图表
        if (this.state.responseChart) {
            const responseData = this.state.responseChart.data;
            if (responseData.labels.length > 20) {
                responseData.labels.shift();
                responseData.datasets[0].data.shift();
            }
            responseData.labels.push(now);
            responseData.datasets[0].data.push(this.state.metrics.response_time || 0);
            this.state.responseChart.update();
        }

        // 资源使用图表
        if (this.state.resourceChart) {
            const resourceData = this.state.resourceChart.data;
            if (resourceData.labels.length > 20) {
                resourceData.labels.shift();
                resourceData.datasets[0].data.shift();
                resourceData.datasets[1].data.shift();
            }
            resourceData.labels.push(now);
            resourceData.datasets[0].data.push(this.state.metrics.cpu_usage || 0);
            resourceData.datasets[1].data.push(this.state.metrics.memory_usage || 0);
            this.state.resourceChart.update();
        }
    },

    /**
     * 获取进度条样式类
     */
    getProgressClass: function(percentage) {
        if (percentage < 50) return 'bg-success';
        if (percentage < 80) return 'bg-warning';
        return 'bg-danger';
    },

    /**
     * 检查阈值
     */
    checkThresholds: function() {
        const alerts = [];

        // 检查各项指标
        if (this.state.metrics.response_time > this.config.alertThresholds.responseTime) {
            alerts.push({
                type: 'warning',
                metric: 'response_time',
                message: `响应时间过高: ${this.state.metrics.response_time}ms`,
                suggestion: '考虑优化API查询或添加缓存'
            });
        }

        if (this.state.metrics.memory_usage > this.config.alertThresholds.memoryUsage) {
            alerts.push({
                type: 'danger',
                metric: 'memory_usage',
                message: `内存使用率过高: ${this.state.metrics.memory_usage}%`,
                suggestion: '检查内存泄漏或增加服务器内存'
            });
        }

        if (this.state.metrics.cpu_usage > this.config.alertThresholds.cpuUsage) {
            alerts.push({
                type: 'warning',
                metric: 'cpu_usage',
                message: `CPU使用率过高: ${this.state.metrics.cpu_usage}%`,
                suggestion: '考虑优化算法或增加服务器CPU核心'
            });
        }

        if (this.state.metrics.error_rate > this.config.alertThresholds.errorRate) {
            alerts.push({
                type: 'danger',
                metric: 'error_rate',
                message: `错误率过高: ${this.state.metrics.error_rate}%`,
                suggestion: '检查应用错误日志并修复bug'
            });
        }

        this.state.alerts = alerts;
    },

    /**
     * 显示优化建议
     */
    showOptimization: function() {
        const container = document.getElementById('optimizationContainer');
        const list = document.getElementById('optimizationList');

        if (!container || !list) return;

        const suggestions = this.generateOptimizationSuggestions();

        list.innerHTML = suggestions.length > 0 ?
            suggestions.map(suggestion => `
                <div class="alert alert-${suggestion.type} d-flex align-items-start">
                    <div class="me-3">
                        <i class="fas ${suggestion.icon} fa-lg"></i>
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${suggestion.title}</h6>
                        <p class="mb-1">${suggestion.description}</p>
                        <small class="text-muted">${suggestion.impact}</small>
                    </div>
                </div>
            `).join('') :
            '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>性能表现良好，无需优化</div>';

        container.style.display = 'block';

        // 滚动到优化建议区域
        container.scrollIntoView({ behavior: 'smooth' });
    },

    /**
     * 显示告警
     */
    showAlerts: function() {
        const container = document.getElementById('alertsContainer');
        const list = document.getElementById('alertsList');

        if (!container || !list) return;

        list.innerHTML = this.state.alerts.length > 0 ?
            this.state.alerts.map(alert => `
                <div class="alert alert-${alert.type} d-flex align-items-start">
                    <div class="me-3">
                        <i class="fas fa-exclamation-triangle fa-lg"></i>
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${alert.message}</h6>
                        <p class="mb-0">${alert.suggestion}</p>
                    </div>
                </div>
            `).join('') :
            '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>暂无性能告警</div>';

        container.style.display = 'block';

        // 滚动到告警区域
        container.scrollIntoView({ behavior: 'smooth' });
    },

    /**
     * 生成优化建议
     */
    generateOptimizationSuggestions: function() {
        const suggestions = [];

        // 基于当前指标生成建议
        const metrics = this.state.metrics;

        if (metrics.response_time > 500) {
            suggestions.push({
                type: 'warning',
                icon: 'fa-database',
                title: '数据库查询优化',
                description: '响应时间较慢，建议优化数据库查询和添加适当索引',
                impact: '预计可提升响应速度 30-50%'
            });
        }

        if (metrics.memory_usage > 70) {
            suggestions.push({
                type: 'danger',
                icon: 'fa-memory',
                title: '内存优化',
                description: '内存使用率较高，建议检查内存泄漏并优化数据结构',
                impact: '预计可减少内存占用 20-40%'
            });
        }

        if (metrics.cpu_usage > 60) {
            suggestions.push({
                type: 'warning',
                icon: 'fa-microchip',
                title: 'CPU优化',
                description: 'CPU使用率较高，建议优化算法复杂度或增加服务器核心',
                impact: '预计可降低CPU使用率 25-35%'
            });
        }

        if (metrics.error_rate > 2) {
            suggestions.push({
                type: 'danger',
                icon: 'fa-bug',
                title: '错误处理优化',
                description: '错误率较高，建议改进错误处理和异常捕获机制',
                impact: '预计可降低错误率 50%以上'
            });
        }

        // 通用优化建议
        suggestions.push({
            type: 'info',
            icon: 'fa-server',
            title: '缓存策略优化',
            description: '实施适当的缓存策略可以显著提升性能',
            impact: '预计可提升响应速度 40-60%'
        });

        suggestions.push({
            type: 'info',
            icon: 'fa-code',
            title: '代码性能优化',
            description: '优化热点代码路径，减少不必要的计算',
            impact: '预计可提升整体性能 15-25%'
        });

        return suggestions;
    },

    /**
     * 获取模拟指标数据
     */
    getMockMetrics: function() {
        return {
            response_time: Math.floor(Math.random() * 500) + 100,
            memory_usage: Math.floor(Math.random() * 40) + 30,
            cpu_usage: Math.floor(Math.random() * 50) + 20,
            error_rate: Math.floor(Math.random() * 3),
            throughput: Math.floor(Math.random() * 50) + 10,
            active_connections: Math.floor(Math.random() * 200) + 50
        };
    },

    /**
     * 开始监控
     */
    startMonitoring: function() {
        if (this.state.isMonitoring) return;

        this.state.isMonitoring = true;
        this.state.interval = setInterval(() => {
            this.loadMetrics();
        }, this.config.refreshInterval);

        console.log('Performance monitoring started');
    },

    /**
     * 停止监控
     */
    stopMonitoring: function() {
        if (!this.state.isMonitoring) return;

        this.state.isMonitoring = false;
        if (this.state.interval) {
            clearInterval(this.state.interval);
            this.state.interval = null;
        }

        console.log('Performance monitoring stopped');
    },

    /**
     * 获取状态
     */
    getStatus: function() {
        return {
            isMonitoring: this.state.isMonitoring,
            metrics: this.state.metrics,
            alertsCount: this.state.alerts.length,
            lastUpdate: new Date().toISOString()
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('Performance Monitor destroying...');
        this.stopMonitoring();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.PerformanceMonitor = PerformanceMonitor;
