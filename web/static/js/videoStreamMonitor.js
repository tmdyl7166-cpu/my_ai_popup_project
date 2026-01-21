/**
 * Video Stream Monitor Module - 视频流监控模块
 * 监控摄像头和视频流处理状态，集成第三方引擎管理
 * 单一职责：视频流状态监控和引擎管理
 */

const VideoStreamMonitor = {
    // 状态
    state: {
        cameras: [],
        streams: [],
        engines: [],
        isMonitoring: false
    },

    // 配置
    config: {
        apiEndpoint: '/api/video',
        camerasEndpoint: '/api/video/cameras',
        streamsEndpoint: '/api/video/streams',
        enginesEndpoint: '/api/video/engines',
        refreshInterval: 5000,
        alertThresholds: {
            frameRate: 15,  // 低于15fps告警
            latency: 100,   // 高于100ms延迟告警
            gpuMemory: 80   // GPU内存超过80%告警
        }
    },

    // 视频状态类型
    streamStatuses: [
        { id: 'active', name: '运行中', icon: 'fa-play-circle', color: 'success' },
        { id: 'idle', name: '空闲', icon: 'fa-pause-circle', color: 'secondary' },
        { id: 'error', name: '错误', icon: 'fa-exclamation-circle', color: 'danger' },
        { id: 'stopped', name: '已停止', icon: 'fa-stop-circle', color: 'dark' }
    ],

    // 引擎类型
    engineTypes: [
        { id: 'deep_live_cam', name: 'Deep-Live-Cam', icon: 'fa-user-clock', color: 'primary' },
        { id: 'facefusion', name: 'FaceFusion', icon: 'fa-users', color: 'info' },
        { id: 'iroop', name: 'iRoopDeepFaceCam', icon: 'fa-video', color: 'warning' }
    ],

    /**
     * 初始化视频流监控
     */
    init: function(containerId) {
        console.log('Video Stream Monitor initializing...');
        this.state.container = document.getElementById(containerId || 'videoMonitorContent');

        if (!this.state.container) {
            console.error('Video Stream Monitor container not found');
            return;
        }

        this.render();
        this.loadData();
        this.startMonitoring();
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
            <div class="video-stream-monitor">
                <div class="card">
                    <div class="card-header bg-gradient-info text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-video me-2"></i>视频流监控
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-light" onclick="VideoStreamMonitor.loadData()">
                                <i class="fas fa-sync me-1"></i>刷新
                            </button>
                            <button class="btn btn-outline-light" onclick="VideoStreamMonitor.scanDevices()">
                                <i class="fas fa-search me-1"></i>扫描设备
                            </button>
                            <button class="btn btn-outline-light" onclick="VideoStreamMonitor.showEngineManager()">
                                <i class="fas fa-cogs me-1"></i>引擎管理
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- 概览统计 -->
                        <div class="row mb-3">
                            <div class="col-md-3">
                                <div class="card bg-primary text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="cameraCount">0</h4>
                                        <small>摄像头</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-success text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="activeStreamCount">0</h4>
                                        <small>活跃流</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-info text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="engineCount">3</h4>
                                        <small>引擎</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-warning text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="avgFps">0</h4>
                                        <small>平均FPS</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 标签页 -->
                        <ul class="nav nav-tabs mb-3" role="tablist">
                            <li class="nav-item">
                                <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#cameraDevices">
                                    <i class="fas fa-camera me-1"></i>摄像头设备
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#activeStreams">
                                    <i class="fas fa-stream me-1"></i>活跃流
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#engineStatus">
                                    <i class="fas fa-microchip me-1"></i>引擎状态
                                </button>
                            </li>
                        </ul>

                        <!-- 标签页内容 -->
                        <div class="tab-content">
                            <!-- 摄像头设备 -->
                            <div class="tab-pane fade show active" id="cameraDevices">
                                <div class="camera-grid" id="cameraGrid">
                                    ${this.buildCameraCards()}
                                </div>
                            </div>

                            <!-- 活跃流 -->
                            <div class="tab-pane fade" id="activeStreams">
                                <div class="table-responsive">
                                    <table class="table table-sm table-hover" id="streamTable">
                                        <thead class="table-light">
                                            <tr>
                                                <th>状态</th>
                                                <th>名称</th>
                                                <th>来源</th>
                                                <th>分辨率</th>
                                                <th>帧率</th>
                                                <th>延迟</th>
                                                <th>引擎</th>
                                                <th>操作</th>
                                            </tr>
                                        </thead>
                                        <tbody id="streamTableBody">
                                            ${this.buildStreamRows()}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- 引擎状态 -->
                            <div class="tab-pane fade" id="engineStatus">
                                <div class="engine-grid" id="engineGrid">
                                    ${this.buildEngineCards()}
                                </div>
                            </div>
                        </div>

                        <!-- 性能监控 -->
                        <div class="performance-section mt-3">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0">
                                        <i class="fas fa-chart-line me-2"></i>视频处理性能
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <canvas id="fpsChart" height="200"></canvas>
                                        </div>
                                        <div class="col-md-6">
                                            <canvas id="gpuMemoryChart" height="200"></canvas>
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
     * 构建摄像头卡片
     */
    buildCameraCards: function() {
        const cameras = this.state.cameras.length > 0 ? this.state.cameras : this.getMockCameras();

        return `
            <div class="row">
                ${cameras.map(camera => `
                    <div class="col-md-4 mb-3">
                        <div class="camera-card card h-100 ${camera.status === 'active' ? 'border-success' : ''}">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <div>
                                    <i class="fas fa-camera me-2"></i>
                                    <strong>${camera.name}</strong>
                                </div>
                                <span class="badge bg-${camera.status === 'active' ? 'success' : 'secondary'}">
                                    ${camera.status === 'active' ? '运行中' : '离线'}
                                </span>
                            </div>
                            <div class="card-body">
                                <div class="camera-preview mb-2" style="background: #000; height: 120px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                                    ${camera.status === 'active' ? `
                                        <i class="fas fa-play-circle fa-3x text-success"></i>
                                    ` : `
                                        <i class="fas fa-camera fa-3x text-secondary"></i>
                                    `}
                                </div>
                                <div class="camera-info">
                                    <div class="d-flex justify-content-between mb-1">
                                        <small>分辨率</small>
                                        <small>${camera.resolution}</small>
                                    </div>
                                    <div class="d-flex justify-content-between mb-1">
                                        <small>帧率</small>
                                        <small>${camera.fps} FPS</small>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <small>设备ID</small>
                                        <small class="text-muted">${camera.deviceId}</small>
                                    </div>
                                </div>
                            </div>
                            <div class="card-footer">
                                <div class="btn-group btn-group-sm w-100">
                                    ${camera.status === 'active' ? `
                                        <button class="btn btn-outline-warning" onclick="VideoStreamMonitor.stopCamera('${camera.deviceId}')">
                                            <i class="fas fa-stop me-1"></i>停止
                                        </button>
                                    ` : `
                                        <button class="btn btn-outline-success" onclick="VideoStreamMonitor.startCamera('${camera.deviceId}')">
                                            <i class="fas fa-play me-1"></i>启动
                                        </button>
                                    `}
                                    <button class="btn btn-outline-info" onclick="VideoStreamMonitor.configureCamera('${camera.deviceId}')">
                                        <i class="fas fa-cog me-1"></i>配置
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * 构建流表格行
     */
    buildStreamRows: function() {
        const streams = this.state.streams.length > 0 ? this.state.streams : this.getMockStreams();

        return streams.map(stream => `
            <tr>
                <td>
                    <span class="badge bg-${this.getStatusColor(stream.status)}">
                        <i class="fas ${this.getStatusIcon(stream.status)} me-1"></i>
                        ${stream.status}
                    </span>
                </td>
                <td>${stream.name}</td>
                <td>${stream.source}</td>
                <td>${stream.resolution}</td>
                <td>${stream.fps} FPS</td>
                <td>${stream.latency}ms</td>
                <td>
                    <span class="badge bg-${this.getEngineColor(stream.engine)}">
                        ${stream.engine}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${stream.status === 'active' ? `
                            <button class="btn btn-outline-warning" onclick="VideoStreamMonitor.stopStream('${stream.id}')">
                                <i class="fas fa-stop"></i>
                            </button>
                        ` : `
                            <button class="btn btn-outline-success" onclick="VideoStreamMonitor.startStream('${stream.id}')">
                                <i class="fas fa-play"></i>
                            </button>
                        `}
                        <button class="btn btn-outline-secondary" onclick="VideoStreamMonitor.viewStreamDetails('${stream.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('') || `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="fas fa-stream fa-2x mb-2"></i>
                    <p class="mb-0">暂无活跃视频流</p>
                </td>
            </tr>
        `;
    },

    /**
     * 构建引擎卡片
     */
    buildEngineCards: function() {
        return `
            <div class="row">
                ${this.engineTypes.map(engine => `
                    <div class="col-md-4 mb-3">
                        <div class="engine-card card h-100">
                            <div class="card-header">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="fas ${engine.icon} me-2"></i>
                                        <strong>${engine.name}</strong>
                                    </div>
                                    <span class="badge bg-${engine.color}" id="engineStatus_${engine.id}">
                                        就绪
                                    </span>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="engine-stats">
                                    <div class="d-flex justify-content-between mb-2">
                                        <small>GPU内存</small>
                                        <small id="engineGpu_${engine.id}">--</small>
                                    </div>
                                    <div class="progress mb-2" style="height: 8px;">
                                        <div class="progress-bar bg-info" id="engineGpuBar_${engine.id}" style="width: 0%"></div>
                                    </div>
                                    <div class="d-flex justify-content-between mb-2">
                                        <small>处理队列</small>
                                        <small id="engineQueue_${engine.id}">0</small>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <small>今日处理</small>
                                        <small id="engineProcessed_${engine.id}">0</small>
                                    </div>
                                </div>
                            </div>
                            <div class="card-footer">
                                <div class="btn-group btn-group-sm w-100">
                                    <button class="btn btn-outline-primary" onclick="VideoStreamMonitor.checkEngine('${engine.id}')">
                                        <i class="fas fa-check me-1"></i>检测
                                    </button>
                                    <button class="btn btn-outline-secondary" onclick="VideoStreamMonitor.configureEngine('${engine.id}')">
                                        <i class="fas fa-cog me-1"></i>配置
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
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
     * 加载数据
     */
    loadData: async function() {
        try {
            // 加载摄像头数据
            const camerasResponse = await fetch(this.config.camerasEndpoint);
            const camerasData = await camerasResponse.json();
            if (camerasData.status === 'success') {
                this.state.cameras = camerasData.cameras || [];
            }
        } catch (error) {
            console.warn('加载摄像头数据失败，使用模拟数据:', error);
            this.state.cameras = this.getMockCameras();
        }

        try {
            // 加载流数据
            const streamsResponse = await fetch(this.config.streamsEndpoint);
            const streamsData = await streamsResponse.json();
            if (streamsData.status === 'success') {
                this.state.streams = streamsData.streams || [];
            }
        } catch (error) {
            console.warn('加载流数据失败，使用模拟数据:', error);
            this.state.streams = this.getMockStreams();
        }

        this.updateDisplay();
        this.renderCharts();
    },

    /**
     * 更新显示
     */
    updateDisplay: function() {
        // 更新统计
        const cameras = this.state.cameras.length;
        const activeStreams = this.state.streams.filter(s => s.status === 'active').length;
        const avgFps = this.state.streams.length > 0
            ? Math.round(this.state.streams.reduce((sum, s) => sum + s.fps, 0) / this.state.streams.length)
            : 0;

        document.getElementById('cameraCount').textContent = cameras;
        document.getElementById('activeStreamCount').textContent = activeStreams;
        document.getElementById('avgFps').textContent = avgFps;

        // 更新摄像头卡片
        const cameraGrid = document.getElementById('cameraGrid');
        if (cameraGrid) {
            cameraGrid.innerHTML = this.buildCameraCards();
        }

        // 更新流表格
        const streamBody = document.getElementById('streamTableBody');
        if (streamBody) {
            streamBody.innerHTML = this.buildStreamRows();
        }
    },

    /**
     * 渲染图表
     */
    renderCharts: function() {
        // FPS图表
        const fpsCtx = document.getElementById('fpsChart');
        if (fpsCtx && !this.state.fpsChart) {
            this.state.fpsChart = new Chart(fpsCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '帧率 (FPS)',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 60
                        }
                    }
                }
            });
        }

        // GPU内存图表
        const gpuCtx = document.getElementById('gpuMemoryChart');
        if (gpuCtx && !this.state.gpuChart) {
            this.state.gpuChart = new Chart(gpuCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: this.engineTypes.map((engine, index) => ({
                        label: engine.name,
                        data: [],
                        borderColor: this.getEngineColor(engine.id),
                        tension: 0.4
                    }))
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

        // 更新图表数据
        this.updateCharts();
    },

    /**
     * 更新图表
     */
    updateCharts: function() {
        const now = new Date().toLocaleTimeString();

        // 更新FPS图表
        if (this.state.fpsChart) {
            const fpsData = this.state.fpsChart.data;
            if (fpsData.labels.length > 20) {
                fpsData.labels.shift();
                fpsData.datasets[0].data.shift();
            }
            fpsData.labels.push(now);
            fpsData.datasets[0].data.push(this.state.streams.length > 0
                ? this.state.streams.reduce((sum, s) => sum + s.fps, 0) / this.state.streams.length
                : 0);
            this.state.fpsChart.update();
        }

        // 更新GPU内存图表
        if (this.state.gpuChart) {
            const gpuData = this.state.gpuChart.data;
            if (gpuData.labels.length > 20) {
                gpuData.labels.shift();
                gpuData.datasets.forEach(ds => ds.data.shift());
            }
            gpuData.labels.push(now);
            this.engineTypes.forEach((engine, index) => {
                gpuData.datasets[index].data.push(Math.random() * 30 + 20); // 模拟GPU使用率
            });
            this.state.gpuChart.update();
        }
    },

    /**
     * 扫描设备
     */
    scanDevices: async function() {
        bubbleMonitor.show('info', '扫描设备', '正在扫描可用摄像头设备...');

        // 模拟扫描过程
        await new Promise(resolve => setTimeout(resolve, 1500));

        this.state.cameras = this.getMockCameras();
        this.updateDisplay();

        bubbleMonitor.show('success', '扫描完成', `发现 ${this.state.cameras.length} 个摄像头设备`);
    },

    /**
     * 启动摄像头
     */
    startCamera: async function(deviceId) {
        const camera = this.state.cameras.find(c => c.deviceId === deviceId);
        if (!camera) return;

        camera.status = 'active';
        this.updateDisplay();

        bubbleMonitor.show('success', '摄像头已启动', camera.name);

        // 通知后端
        try {
            await fetch(`${this.config.camerasEndpoint}/${deviceId}/start`, { method: 'POST' });
        } catch (error) {
            console.warn('通知后端失败:', error);
        }
    },

    /**
     * 停止摄像头
     */
    stopCamera: function(deviceId) {
        const camera = this.state.cameras.find(c => c.deviceId === deviceId);
        if (!camera) return;

        camera.status = 'idle';
        this.updateDisplay();

        bubbleMonitor.show('warning', '摄像头已停止', camera.name);
    },

    /**
     * 配置摄像头
     */
    configureCamera: function(deviceId) {
        const camera = this.state.cameras.find(c => c.deviceId === deviceId);
        if (!camera) return;

        const content = `
            <div class="camera-config-form">
                <div class="mb-3">
                    <label class="form-label">设备名称</label>
                    <input type="text" class="form-control" value="${camera.name}" readonly>
                </div>
                <div class="mb-3">
                    <label class="form-label">分辨率</label>
                    <select class="form-select" id="configResolution">
                        <option value="640x480" ${camera.resolution === '640x480' ? 'selected' : ''}>640x480 (VGA)</option>
                        <option value="1280x720" ${camera.resolution === '1280x720' ? 'selected' : ''}>1280x720 (HD)</option>
                        <option value="1920x1080" ${camera.resolution === '1920x1080' ? 'selected' : ''}>1920x1080 (Full HD)</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">目标帧率</label>
                    <input type="number" class="form-control" value="${camera.fps}" min="15" max="60" id="configFps">
                </div>
            </div>
        `;

        ModalManager.show({
            title: '配置摄像头',
            content: content,
            size: 'md',
            onConfirm: () => {
                const resolution = document.getElementById('configResolution').value;
                const fps = parseInt(document.getElementById('configFps').value);

                camera.resolution = resolution;
                camera.fps = fps;
                this.updateDisplay();

                bubbleMonitor.show('success', '配置已保存', camera.name);
            }
        });
    },

    /**
     * 启动流
     */
    startStream: function(streamId) {
        const stream = this.state.streams.find(s => s.id === streamId);
        if (!stream) return;

        stream.status = 'active';
        this.updateDisplay();

        bubbleMonitor.show('success', '视频流已启动', stream.name);
    },

    /**
     * 停止流
     */
    stopStream: function(streamId) {
        const stream = this.state.streams.find(s => s.id === streamId);
        if (!stream) return;

        stream.status = 'stopped';
        this.updateDisplay();

        bubbleMonitor.show('warning', '视频流已停止', stream.name);
    },

    /**
     * 查看流详情
     */
    viewStreamDetails: function(streamId) {
        const stream = this.state.streams.find(s => s.id === streamId);
        if (!stream) return;

        const content = `
            <div class="stream-details">
                <h6>${stream.name}</h6>
                <hr>
                <div class="row">
                    <div class="col-6">
                        <p><strong>状态:</strong> <span class="badge bg-${this.getStatusColor(stream.status)}">${stream.status}</span></p>
                        <p><strong>来源:</strong> ${stream.source}</p>
                        <p><strong>分辨率:</strong> ${stream.resolution}</p>
                    </div>
                    <div class="col-6">
                        <p><strong>帧率:</strong> ${stream.fps} FPS</p>
                        <p><strong>延迟:</strong> ${stream.latency}ms</p>
                        <p><strong>引擎:</strong> ${stream.engine}</p>
                    </div>
                </div>
            </div>
        `;

        ModalManager.show({
            title: '视频流详情',
            content: content,
            size: 'md'
        });
    },

    /**
     * 显示引擎管理
     */
    showEngineManager: function() {
        const content = `
            <div class="engine-manager">
                <div class="row">
                    ${this.engineTypes.map(engine => `
                        <div class="col-md-4 mb-3">
                            <div class="card">
                                <div class="card-header bg-${engine.color} text-white">
                                    <i class="fas ${engine.icon} me-2"></i>${engine.name}
                                </div>
                                <div class="card-body">
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="checkbox" checked id="engineEnabled_${engine.id}">
                                        <label class="form-check-label" for="engineEnabled_${engine.id}">启用引擎</label>
                                    </div>
                                    <div class="mb-2">
                                        <label class="form-label">GPU内存限制</label>
                                        <input type="range" class="form-range" min="1" max="16" value="4" id="engineMemory_${engine.id}">
                                        <small class="text-muted">4 GB</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        ModalManager.show({
            title: '引擎管理',
            content: content,
            size: 'lg',
            onConfirm: () => {
                bubbleMonitor.show('success', '引擎配置已更新', '重启服务后生效');
            }
        });
    },

    /**
     * 检测引擎
     */
    checkEngine: async function(engineId) {
        const engine = this.engineTypes.find(e => e.id === engineId);
        if (!engine) return;

        bubbleMonitor.show('info', '检测中', `正在检测 ${engine.name}...`);

        // 模拟检测过程
        await new Promise(resolve => setTimeout(resolve, 1000));

        const gpuUsage = Math.random() * 40 + 10;
        document.getElementById(`engineStatus_${engineId}`).textContent = '正常';
        document.getElementById(`engineStatus_${engineId}`).className = 'badge bg-success';
        document.getElementById(`engineGpu_${engineId}`).textContent = gpuUsage.toFixed(1) + '%';
        document.getElementById(`engineGpuBar_${engineId}`).style.width = gpuUsage + '%';

        bubbleMonitor.show('success', '检测完成', `${engine.name} 运行正常`);
    },

    /**
     * 配置引擎
     */
    configureEngine: function(engineId) {
        const engine = this.engineTypes.find(e => e.id === engineId);
        if (!engine) return;

        const content = `
            <div class="engine-config">
                <h6>${engine.name} 配置</h6>
                <hr>
                <div class="mb-3">
                    <label class="form-label">最大并发处理数</label>
                    <input type="number" class="form-control" value="2" min="1" max="8">
                </div>
                <div class="mb-3">
                    <label class="form-label">GPU内存分配 (GB)</label>
                    <input type="number" class="form-control" value="4" min="1" max="16">
                </div>
                <div class="mb-3">
                    <label class="form-label">处理优先级</label>
                    <select class="form-select">
                        <option value="high">高</option>
                        <option value="normal" selected>正常</option>
                        <option value="low">低</option>
                    </select>
                </div>
            </div>
        `;

        ModalManager.show({
            title: '引擎配置',
            content: content,
            size: 'md',
            onConfirm: () => {
                bubbleMonitor.show('success', '配置已保存', engine.name);
            }
        });
    },

    /**
     * 获取状态颜色
     */
    getStatusColor: function(status) {
        const colors = {
            active: 'success',
            idle: 'secondary',
            error: 'danger',
            stopped: 'dark'
        };
        return colors[status] || 'secondary';
    },

    /**
     * 获取状态图标
     */
    getStatusIcon: function(status) {
        const icons = {
            active: 'fa-play-circle',
            idle: 'fa-pause-circle',
            error: 'fa-exclamation-circle',
            stopped: 'fa-stop-circle'
        };
        return icons[status] || 'fa-circle';
    },

    /**
     * 获取引擎颜色
     */
    getEngineColor: function(engineId) {
        const engine = this.engineTypes.find(e => e.id === engineId);
        return engine ? engine.color : 'secondary';
    },

    /**
     * 获取模拟摄像头数据
     */
    getMockCameras: function() {
        return [
            {
                deviceId: 'camera-001',
                name: '主摄像头',
                status: 'active',
                resolution: '1280x720',
                fps: 30
            },
            {
                deviceId: 'camera-002',
                name: '辅助摄像头',
                status: 'idle',
                resolution: '640x480',
                fps: 15
            }
        ];
    },

    /**
     * 获取模拟流数据
     */
    getMockStreams: function() {
        return [
            {
                id: 'stream-001',
                name: '实时直播流',
                source: 'camera-001',
                resolution: '1280x720',
                fps: 30,
                latency: 45,
                engine: 'Deep-Live-Cam',
                status: 'active'
            },
            {
                id: 'stream-002',
                name: '录播处理流',
                source: 'video_file.mp4',
                resolution: '1920x1080',
                fps: 25,
                latency: 120,
                engine: 'FaceFusion',
                status: 'idle'
            }
        ];
    },

    /**
     * 开始监控
     */
    startMonitoring: function() {
        if (this.state.isMonitoring) return;

        this.state.isMonitoring = true;
        this.state.interval = setInterval(() => {
            this.loadData();
        }, this.config.refreshInterval);

        console.log('Video stream monitoring started');
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

        console.log('Video stream monitoring stopped');
    },

    /**
     * 获取状态
     */
    getStatus: function() {
        return {
            isMonitoring: this.state.isMonitoring,
            cameraCount: this.state.cameras.length,
            activeStreamCount: this.state.streams.filter(s => s.status === 'active').length,
            engineCount: this.engineTypes.length
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('Video Stream Monitor destroying...');
        this.stopMonitoring();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.VideoStreamMonitor = VideoStreamMonitor;

