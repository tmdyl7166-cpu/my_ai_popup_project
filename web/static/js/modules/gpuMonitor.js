/**
 * GPU Monitor Module - GPU监控模块
 * 负责监控GPU使用情况、温度和内存
 * 单一职责：GPU资源监控
 */

const GPUMonitor = {
    // 状态
    state: {
        container: null,
        gpuData: null,
        isRunning: false,
        interval: null
    },

    // 配置
    config: {
        apiEndpoint: '/api/system/gpu',
        refreshInterval: 5000, // 5秒刷新
        warningTemp: 70,
        criticalTemp: 85,
        warningUsage: 80,
        criticalUsage: 95
    },

    /**
     * 初始化GPU监控模块
     */
    init: function(containerId) {
        console.log('GPU Monitor initializing...');
        this.state.container = document.getElementById(containerId || 'gpuMonitorContent');
        
        if (!this.state.container) {
            console.error('GPU Monitor container not found');
            return;
        }

        this.render();
        this.startAutoRefresh();
        this.fetchGPUData();
    },

    /**
     * 渲染界面
     */
    render: function() {
        const html = this.buildHtml();
        this.state.container.innerHTML = html;
    },

    /**
     * 构建HTML
     */
    buildHtml: function() {
        return `
            <div class="gpu-monitor-container">
                <div class="card">
                    <div class="card-header bg-gradient-dark text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-microchip me-2"></i>GPU监控
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-light" onclick="GPUMonitor.refresh()">
                                <i class="fas fa-sync me-1"></i>刷新
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- GPU状态概览 -->
                        <div id="gpuOverview" class="mb-3">
                            ${this.buildGPUOverview()}
                        </div>
                        
                        <!-- 详细指标 -->
                        <div id="gpuMetrics" class="row">
                            ${this.buildGPUMetrics()}
                        </div>
                        
                        <!-- GPU内存使用 -->
                        <div id="gpuMemory" class="mt-3">
                            ${this.buildGPUMemoryBar()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建GPU概览
     */
    buildGPUOverview: function() {
        return `
            <div class="d-flex align-items-center justify-content-between p-3 bg-light rounded">
                <div class="d-flex align-items-center">
                    <div id="gpuStatusIcon" class="me-3">
                        <i class="fas fa-check-circle text-success fa-2x"></i>
                    </div>
                    <div>
                        <h6 class="mb-0" id="gpuName">检测GPU中...</h6>
                        <small class="text-muted" id="gpuStatusText">等待数据...</small>
                    </div>
                </div>
                <div class="text-end">
                    <small class="text-muted">最后更新</small>
                    <div id="gpuLastUpdate" class="fw-bold">--:--:--</div>
                </div>
            </div>
        `;
    },

    /**
     * 构建GPU指标
     */
    buildGPUMetrics: function() {
        return `
            <!-- GPU使用率 -->
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-percentage text-primary fa-2x mb-2"></i>
                        <h6>GPU使用率</h6>
                        <h4 id="gpuUsagePercent" class="text-primary">--%</h4>
                        <div class="progress mt-2" style="height: 10px;">
                            <div id="gpuUsageBar" class="progress-bar bg-primary" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- GPU温度 -->
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-thermometer-half text-warning fa-2x mb-2"></i>
                        <h6>GPU温度</h6>
                        <h4 id="gpuTemp" class="text-warning">--°C</h4>
                        <small class="text-muted" id="gpuTempStatus">正常</small>
                    </div>
                </div>
            </div>
            
            <!-- GPU风扇转速 -->
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-fan text-info fa-2x mb-2"></i>
                        <h6>风扇转速</h6>
                        <h4 id="gpuFanSpeed" class="text-info">--%</h4>
                        <small class="text-muted">转速</small>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建GPU内存条
     */
    buildGPUMemoryBar: function() {
        return `
            <div class="mt-3">
                <div class="d-flex justify-content-between mb-1">
                    <small><i class="fas fa-memory me-1"></i>显存使用</small>
                    <small id="gpuMemoryUsage">0 MB / 0 MB</small>
                </div>
                <div class="progress" style="height: 20px;">
                    <div id="gpuMemoryBar" class="progress-bar bg-success" style="width: 0%"></div>
                </div>
                <div class="d-flex justify-content-between mt-1">
                    <small class="text-muted" id="gpuMemoryUsed">已用: -- MB</small>
                    <small class="text-muted" id="gpuMemoryTotal">总计: -- MB</small>
                </div>
            </div>
        `;
    },

    /**
     * 获取GPU数据
     */
    fetchGPUData: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            if (!response.ok) {
                throw new Error('GPU API响应失败');
            }
            const data = await response.json();
            this.updateGPUDisplay(data);
        } catch (error) {
            console.warn('获取GPU数据失败:', error);
            this.showGPUNotAvailable();
        }
    },

    /**
     * 更新GPU显示
     */
    updateGPUDisplay: function(data) {
        this.state.gpuData = data;
        
        // 更新概览
        const nameElement = document.getElementById('gpuName');
        const statusElement = document.getElementById('gpuStatusText');
        const statusIcon = document.getElementById('gpuStatusIcon');
        
        if (nameElement) {
            nameElement.textContent = data.name || 'NVIDIA GPU';
        }
        if (statusElement) {
            statusElement.textContent = data.status || '正常';
        }
        if (statusIcon) {
            const status = data.status?.toLowerCase();
            if (status === 'healthy' || status === '正常') {
                statusIcon.innerHTML = '<i class="fas fa-check-circle text-success fa-2x"></i>';
            } else if (status === 'warning' || status === '警告') {
                statusIcon.innerHTML = '<i class="fas fa-exclamation-triangle text-warning fa-2x"></i>';
            } else {
                statusIcon.innerHTML = '<i class="fas fa-exclamation-circle text-danger fa-2x"></i>';
            }
        }

        // 更新指标
        this.updateMetric('gpuUsagePercent', 'gpuUsageBar', 
            data.utilization || 0, this.config.warningUsage, this.config.criticalUsage, '%');
        this.updateMetric('gpuTemp', null, 
            data.temperature || 0, this.config.warningTemp, this.config.criticalTemp, '°C');
        
        // 风扇转速
        const fanElement = document.getElementById('gpuFanSpeed');
        if (fanElement) {
            fanElement.textContent = (data.fan_speed || 0) + '%';
        }

        // 内存使用
        const memoryUsed = data.memory_used || 0;
        const memoryTotal = data.memory_total || 0;
        const memoryPercent = memoryTotal > 0 ? (memoryUsed / memoryTotal * 100) : 0;
        
        document.getElementById('gpuMemoryUsage').textContent = 
            `${this.formatBytes(memoryUsed * 1024 * 1024)} / ${this.formatBytes(memoryTotal * 1024 * 1024)}`;
        document.getElementById('gpuMemoryUsed').textContent = `已用: ${this.formatBytes(memoryUsed * 1024 * 1024)}`;
        document.getElementById('gpuMemoryTotal').textContent = `总计: ${this.formatBytes(memoryTotal * 1024 * 1024)}`;
        
        const memoryBar = document.getElementById('gpuMemoryBar');
        if (memoryBar) {
            memoryBar.style.width = memoryPercent + '%';
            memoryBar.className = this.getStatusClass(memoryPercent, 70, 90);
        }

        // 更新时间
        document.getElementById('gpuLastUpdate').textContent = 
            new Date().toLocaleString('zh-CN');

        // 温度状态
        const tempStatus = document.getElementById('gpuTempStatus');
        if (tempStatus) {
            const temp = data.temperature || 0;
            if (temp >= this.config.criticalTemp) {
                tempStatus.textContent = '过热！';
                tempStatus.className = 'text-danger fw-bold';
            } else if (temp >= this.config.warningTemp) {
                tempStatus.textContent = '高温';
                tempStatus.className = 'text-warning fw-bold';
            } else {
                tempStatus.textContent = '正常';
                tempStatus.className = 'text-muted';
            }
        }

        // 检查是否需要告警
        this.checkAlerts(data);
    },

    /**
     * 更新单个指标
     */
    updateMetric: function(valueId, barId, value, warningThreshold, criticalThreshold, suffix) {
        const valueElement = document.getElementById(valueId);
        if (valueElement) {
            valueElement.textContent = value + suffix;
        }
        
        if (barId) {
            const barElement = document.getElementById(barId);
            if (barElement) {
                barElement.style.width = Math.min(value, 100) + '%';
                barElement.className = `progress-bar ${this.getStatusClass(value, warningThreshold, criticalThreshold)}`;
            }
        }
    },

    /**
     * 获取状态样式类
     */
    getStatusClass: function(value, warning, critical) {
        if (value >= critical) return 'bg-danger';
        if (value >= warning) return 'bg-warning';
        return 'bg-success';
    },

    /**
     * 显示GPU不可用
     */
    showGPUNotAvailable: function() {
        const overview = document.getElementById('gpuOverview');
        const metrics = document.getElementById('gpuMetrics');
        
        if (overview) {
            overview.innerHTML = `
                <div class="d-flex align-items-center justify-content-between p-3 bg-light rounded">
                    <div class="d-flex align-items-center">
                        <div class="me-3">
                            <i class="fas fa-microchip text-muted fa-2x"></i>
                        </div>
                        <div>
                            <h6 class="mb-0">GPU未检测到</h6>
                            <small class="text-muted">系统无可用GPU或GPU监控未安装</small>
                        </div>
                    </div>
                </div>
            `;
        }
        
        if (metrics) {
            metrics.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="fas fa-plug text-muted fa-3x mb-3"></i>
                    <p class="text-muted">未检测到兼容的GPU设备</p>
                    <small class="text-muted">
                        提示: 请确保已安装NVIDIA驱动和nvidia-smi工具
                    </small>
                </div>
            `;
        }
    },

    /**
     * 检查告警
     */
    checkAlerts: function(data) {
        // 温度告警
        if (data.temperature >= this.config.criticalTemp) {
            bubbleMonitor.show('error', 'GPU温度过高', 
                `GPU温度达到 ${data.temperature}°C，请及时检查散热！`);
        } else if (data.temperature >= this.config.warningTemp) {
            bubbleMonitor.show('warning', 'GPU温度偏高', 
                `GPU温度达到 ${data.temperature}°C`);
        }

        // 使用率告警
        if (data.utilization >= this.config.criticalUsage) {
            bubbleMonitor.show('error', 'GPU负载过高', 
                `GPU使用率达到 ${data.utilization}%`);
        }
    },

    /**
     * 格式化字节
     */
    formatBytes: function(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * 刷新数据
     */
    refresh: function() {
        this.fetchGPUData();
    },

    /**
     * 开始自动刷新
     */
    startAutoRefresh: function() {
        this.state.interval = setInterval(() => {
            this.fetchGPUData();
        }, this.config.refreshInterval);
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
            hasGPU: this.state.gpuData !== null,
            data: this.state.gpuData,
            isRunning: this.state.isRunning
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('GPU Monitor destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.GPUMonitor = GPUMonitor;

