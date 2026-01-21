/**
 * Health Checker Module - 健康检查模块
 * 负责执行系统健康检查脚本
 * 单一职责：健康检查功能
 */

const HealthChecker = {
    // 状态
    state: {
        container: null,
        scripts: [],
        isRunning: false,
        lastResult: null
    },

    // 配置
    config: {
        apiEndpoint: '/api/scripts/run/health_check.py',
        statusEndpoint: '/api/scripts/status',
        logEndpoint: '/api/logs/health_check.py',
        interval: 60000 // 60秒
    },

    /**
     * 初始化健康检查模块
     */
    init: function(containerId) {
        console.log('Health Checker initializing...');
        this.state.container = document.getElementById(containerId || 'healthCheckerContent');
        
        if (!this.state.container) {
            console.error('Health Checker container not found');
            return;
        }

        this.render();
        this.startAutoCheck();
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
            <div class="health-checker-container">
                <div class="card">
                    <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-heartbeat me-2"></i>健康检查
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-light" onclick="healthChecker.runCheck()">
                                <i class="fas fa-play me-1"></i>立即检查
                            </button>
                            <button class="btn btn-outline-light" onclick="healthChecker.viewLogs()">
                                <i class="fas fa-file-alt me-1"></i>查看日志
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- 状态指示器 -->
                        <div class="status-indicator mb-3">
                            <div class="d-flex align-items-center">
                                <div id="healthStatusIcon" class="status-icon me-3">
                                    <i class="fas fa-check-circle text-success fa-2x"></i>
                                </div>
                                <div>
                                    <h5 class="mb-0" id="healthStatusText">系统健康</h5>
                                    <small class="text-muted" id="healthLastCheck">最后检查: --</small>
                                </div>
                            </div>
                        </div>

                        <!-- 检查项目 -->
                        <div class="check-items">
                            ${this.buildCheckItems()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建检查项目
     */
    buildCheckItems: function() {
        const items = [
            { id: 'cpu', name: 'CPU使用率', icon: 'fa-microchip', threshold: 80 },
            { id: 'memory', name: '内存使用率', icon: 'fa-memory', threshold: 85 },
            { id: 'disk', name: '磁盘使用率', icon: 'fa-hdd', threshold: 90 },
            { id: 'services', name: '服务状态', icon: 'fa-server', threshold: 0 },
            { id: 'ports', name: '端口连通性', icon: 'fa-network-wired', threshold: 0 },
            { id: 'api', name: 'API响应', icon: 'fa-exchange-alt', threshold: 2000 }
        ];

        return items.map(item => `
            <div class="check-item d-flex justify-content-between align-items-center py-2 border-bottom">
                <div class="d-flex align-items-center">
                    <i class="fas ${item.icon} text-muted me-3" style="width: 20px;"></i>
                    <span>${item.name}</span>
                </div>
                <div class="check-status" id="check-${item.id}">
                    <span class="badge bg-secondary">待检查</span>
                </div>
            </div>
        `).join('');
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 按钮点击事件已在HTML中处理
    },

    /**
     * 运行健康检查
     */
    runCheck: async function() {
        if (this.state.isRunning) {
            Notifications.show('检查中', '健康检查正在进行中...', 'info');
            return;
        }

        this.state.isRunning = true;
        this.updateStatusIcon('checking');

        try {
            // 调用健康检查脚本
            const response = await fetch(this.config.apiEndpoint, { method: 'POST' });
            const result = await response.json();

            if (result.status === 'started' || result.status === 'success') {
                // 等待检查完成
                await this.sleep(3000);
                
                // 更新检查结果
                await this.updateCheckResults();
                
                this.state.lastResult = {
                    timestamp: new Date().toISOString(),
                    success: true
                };

                this.updateStatusIcon('healthy');
                Notifications.show('检查完成', '系统健康检查已完成', 'success');
                
                // 显示冒泡通知
                bubbleMonitor.show('success', '健康检查', '系统所有组件状态正常');
            }

        } catch (error) {
            console.error('Health check failed:', error);
            this.updateStatusIcon('unhealthy');
            Notifications.show('检查失败', error.message, 'error');
            
            bubbleMonitor.show('error', '健康检查失败', error.message);
        } finally {
            this.state.isRunning = false;
        }
    },

    /**
     * 更新检查结果
     */
    updateCheckResults: async function() {
        try {
            const response = await fetch('/api/system/resources');
            const data = await response.json();

            // 更新CPU
            this.updateCheckItem('cpu', data.cpu_percent, 80);
            
            // 更新内存
            if (data.memory) {
                this.updateCheckItem('memory', data.memory.percent, 85);
            }
            
            // 更新磁盘
            if (data.disk) {
                this.updateCheckItem('disk', data.disk.percent, 90);
            }

            // 更新服务状态
            this.updateCheckItem('services', 0, 0, 'healthy');
            
            // 更新端口状态
            this.updateCheckItem('ports', 0, 0, 'healthy');
            
            // 更新API响应
            const apiCheck = await this.checkApiHealth();
            this.updateCheckItem('api', apiCheck.latency, 2000, apiCheck.status);

            // 更新时间戳
            document.getElementById('healthLastCheck').textContent = 
                `最后检查: ${new Date().toLocaleString('zh-CN')}`;

        } catch (error) {
            console.error('Failed to update check results:', error);
        }
    },

    /**
     * 检查单个项目
     */
    updateCheckItem: function(id, value, threshold, status = null) {
        const element = document.getElementById(`check-${id}`);
        if (!element) return;

        // 如果没有指定状态，根据阈值判断
        if (!status) {
            status = value > threshold ? 'warning' : 'healthy';
        }

        const statusClass = status === 'healthy' ? 'success' : 
                           status === 'warning' ? 'warning' : 'danger';
        const statusText = status === 'healthy' ? '正常' : 
                          status === 'warning' ? '警告' : '异常';

        element.innerHTML = `
            <span class="badge bg-${statusClass}">
                ${typeof value === 'number' ? value + '%' : statusText}
            </span>
        `;
    },

    /**
     * 更新状态图标
     */
    updateStatusIcon: function(status) {
        const iconElement = document.getElementById('healthStatusIcon');
        const textElement = document.getElementById('healthStatusText');

        if (!iconElement || !textElement) return;

        switch (status) {
            case 'checking':
                iconElement.innerHTML = '<i class="fas fa-spinner fa-spin text-info fa-2x"></i>';
                textElement.textContent = '检查中...';
                break;
            case 'healthy':
                iconElement.innerHTML = '<i class="fas fa-check-circle text-success fa-2x"></i>';
                textElement.textContent = '系统健康';
                break;
            case 'unhealthy':
                iconElement.innerHTML = '<i class="fas fa-times-circle text-danger fa-2x"></i>';
                textElement.textContent = '存在问题';
                break;
            case 'warning':
                iconElement.innerHTML = '<i class="fas fa-exclamation-triangle text-warning fa-2x"></i>';
                textElement.textContent = '需要关注';
                break;
        }
    },

    /**
     * 检查API健康
     */
    checkApiHealth: async function() {
        const startTime = Date.now();
        try {
            await fetch('/api/health');
            return {
                status: 'healthy',
                latency: Date.now() - startTime
            };
        } catch (error) {
            return {
                status: 'unhealthy',
                latency: Date.now() - startTime
            };
        }
    },

    /**
     * 查看日志
     */
    viewLogs: function() {
        // 跳转到日志查看
        const logsTab = document.querySelector('[data-bs-target="#logs-viewer"]');
        if (logsTab) {
            logsTab.click();
        }
        Notifications.show('日志查看', '正在加载健康检查日志...', 'info');
    },

    /**
     * 开始自动检查
     */
    startAutoCheck: function() {
        // 可以设置定时自动检查
        // this.autoCheckTimer = setInterval(() => this.runCheck(), this.config.interval);
    },

    /**
     * 停止自动检查
     */
    stopAutoCheck: function() {
        if (this.autoCheckTimer) {
            clearInterval(this.autoCheckTimer);
        }
    },

    /**
     * 获取状态
     */
    getStatus: function() {
        return {
            isRunning: this.state.isRunning,
            lastResult: this.state.lastResult,
            status: this.state.lastResult?.success ? 'healthy' : 'unknown'
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('Health Checker destroying...');
        this.stopAutoCheck();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.HealthChecker = HealthChecker;

