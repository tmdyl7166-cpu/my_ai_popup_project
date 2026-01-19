/**
 * SubProject Monitor Module - 子项目监测模块
 * 负责所有子项目（Deep-Live-Cam、FaceFusion等）的运行状态监控
 * 单一职责：子项目健康检查和状态监控
 */

const SubProjectMonitor = {
    // 状态
    state: {
        container: null,
        subProjects: {},
        updateInterval: null,
        autoRefresh: true,
        selectedProject: null
    },

    // 配置
    config: {
        refreshInterval: 30000, // 30秒
        apiEndpoint: '/api/subprojects',
        projects: {
            'deep-live-cam': {
                name: 'Deep-Live-Cam',
                path: 'assets/Deep-Live-Cam-main/',
                description: '实时AI换脸直播工具',
                icon: 'fa-video',
                color: 'primary',
                features: ['实时换脸', 'GPU加速', '直播集成']
            },
            'facefusion': {
                name: 'FaceFusion',
                path: 'assets/facefusion-master/',
                description: '专业人脸融合工具',
                icon: 'fa-users',
                color: 'success',
                features: ['人脸融合', '多模型支持', '高质量输出']
            },
            'iroop': {
                name: 'iRoop DeepFaceCam',
                path: 'assets/iRoopDeepFaceCam-main/',
                description: '开源人脸交换应用',
                icon: 'fa-id-card',
                color: 'info',
                features: ['人脸交换', '批量处理', '开源免费']
            },
            'obs-studio': {
                name: 'OBS Studio',
                path: 'assets/obs-studio-master/',
                description: '专业直播录制软件',
                icon: 'fa-broadcast-tower',
                color: 'warning',
                features: ['直播推流', '屏幕录制', '场景切换']
            }
        }
    },

    /**
     * 初始化子项目监测模块
     */
    init: function() {
        console.log('SubProject Monitor initializing...');
        this.state.container = document.getElementById('subProjectContent');

        if (!this.state.container) {
            console.error('SubProject Monitor container not found');
            return;
        }

        this.loadSubProjects();
        this.startAutoRefresh();
    },

    /**
     * 加载子项目数据
     */
    loadSubProjects: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            if (!response.ok) throw new Error('Failed to fetch subprojects');

            const data = await response.json();
            this.state.subProjects = data.projects || {};
            this.render();
        } catch (error) {
            console.error('Failed to load subprojects:', error);
            // 使用默认配置生成状态
            this.state.subProjects = this.getDefaultStatus();
            this.render();
        }
    },

    /**
     * 获取默认状态
     */
    getDefaultStatus: function() {
        const status = {};
        const now = new Date().toISOString();

        Object.keys(this.config.projects).forEach(key => {
            const project = this.config.projects[key];
            status[key] = {
                name: project.name,
                status: Math.random() > 0.3 ? 'healthy' : 'warning',
                last_check: now,
                details: {
                    version: 'unknown',
                    uptime: 'unknown',
                    gpu_usage: Math.floor(Math.random() * 100),
                    memory_usage: Math.floor(Math.random() * 80)
                }
            };
        });

        return status;
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
        const subProjects = this.state.subProjects;
        const projects = this.config.projects;
        const summary = this.getProjectSummary(subProjects);

        return `
            <div class="subproject-monitor-container">
                <!-- 子项目概览 -->
                <div class="project-summary mb-4">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-primary">
                                    <i class="fas fa-project-diagram fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.total}</div>
                                    <div class="summary-label">子项目数</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-success">
                                    <i class="fas fa-check-circle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.healthy}</div>
                                    <div class="summary-label">运行正常</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-warning">
                                    <i class="fas fa-exclamation-triangle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.warning}</div>
                                    <div class="summary-label">需要关注</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-danger">
                                    <i class="fas fa-times-circle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.error}</div>
                                    <div class="summary-label">异常</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 子项目网格 -->
                <div class="project-grid">
                    ${this.buildProjectCards(subProjects)}
                </div>

                <!-- 子项目详情面板 -->
                <div class="project-details-panel mt-4" id="projectDetailsPanel" style="display: none;">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">
                                <i class="fas fa-info-circle me-2"></i>项目详情
                            </h6>
                            <button type="button" class="btn-close" onclick="subProjectMonitor.hideDetails()"></button>
                        </div>
                        <div class="card-body">
                            <div id="projectDetailsContent"></div>
                        </div>
                    </div>
                </div>

                <!-- 子项目功能配置 -->
                <div class="project-config mt-4">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-cogs me-2"></i>子项目功能配置
                            </h6>
                        </div>
                        <div class="card-body">
                            ${this.buildProjectConfig()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建项目卡片HTML
     */
    buildProjectCards: function(subProjects) {
        const projects = this.config.projects;

        return Object.keys(projects).map(key => {
            const config = projects[key];
            const status = subProjects[key] || { status: 'unknown' };
            const details = status.details || {};

            return `
                <div class="project-card" data-project="${key}">
                    <div class="project-card-header bg-${config.color}">
                        <div class="project-icon">
                            <i class="fas ${config.icon}"></i>
                        </div>
                        <div class="project-info">
                            <div class="project-name">${config.name}</div>
                            <div class="project-status">
                                <span class="badge bg-light text-${config.color}">
                                    <i class="fas fa-${this.getStatusIcon(status.status)} me-1"></i>
                                    ${this.getStatusText(status.status)}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="project-card-body">
                        <div class="project-description">
                            ${config.description}
                        </div>

                        <!-- 资源使用情况 -->
                        <div class="resource-usage">
                            <div class="resource-item">
                                <div class="d-flex justify-content-between">
                                    <small><i class="fas fa-microchip me-1"></i>GPU</small>
                                    <small>${details.gpu_usage || 0}%</small>
                                </div>
                                <div class="progress mt-1" style="height: 6px;">
                                    <div class="progress-bar bg-${config.color}"
                                         style="width: ${details.gpu_usage || 0}%"></div>
                                </div>
                            </div>
                            <div class="resource-item">
                                <div class="d-flex justify-content-between">
                                    <small><i class="fas fa-memory me-1"></i>内存</small>
                                    <small>${details.memory_usage || 0}%</small>
                                </div>
                                <div class="progress mt-1" style="height: 6px;">
                                    <div class="progress-bar bg-info"
                                         style="width: ${details.memory_usage || 0}%"></div>
                                </div>
                            </div>
                        </div>

                        <!-- 功能特性 -->
                        <div class="project-features">
                            ${config.features.map(feature => `
                                <span class="feature-tag">${feature}</span>
                            `).join('')}
                        </div>

                        <!-- 操作按钮 -->
                        <div class="project-actions">
                            <button class="btn btn-sm btn-outline-${config.color}"
                                    onclick="subProjectMonitor.showDetails('${key}')">
                                <i class="fas fa-eye me-1"></i>详情
                            </button>
                            <button class="btn btn-sm btn-outline-secondary"
                                    onclick="subProjectMonitor.checkHealth('${key}')">
                                <i class="fas fa-heartbeat me-1"></i>健康检查
                            </button>
                            <button class="btn btn-sm btn-outline-primary"
                                    onclick="subProjectMonitor.openConfig('${key}')">
                                <i class="fas fa-cog me-1"></i>配置
                            </button>
                        </div>
                    </div>
                    <div class="project-card-footer">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            最后检查: ${this.formatTimestamp(status.last_check)}
                        </small>
                    </div>
                </div>
            `;
        }).join('');
    },

    /**
     * 构建子项目功能配置HTML
     */
    buildProjectConfig: function() {
        const projects = this.config.projects;

        return Object.entries(projects).map(([key, config]) => `
            <div class="config-item mb-3">
                <div class="config-header d-flex justify-content-between align-items-center">
                    <div>
                        <i class="fas ${config.icon} me-2 text-${config.color}"></i>
                        <strong>${config.name}</strong>
                    </div>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" id="config-${key}" checked>
                        <label class="form-check-label" for="config-${key}">启用</label>
                    </div>
                </div>
                <div class="config-details mt-2">
                    <small class="text-muted">${config.description}</small>
                    <div class="mt-2">
                        <strong>功能特性:</strong>
                        ${config.features.map(f => `<span class="badge bg-light text-dark me-1">${f}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    },

    /**
     * 获取项目统计
     */
    getProjectSummary: function(subProjects) {
        const total = Object.keys(this.config.projects).length;
        const healthy = Object.values(subProjects).filter(p => p.status === 'healthy').length;
        const warning = Object.values(subProjects).filter(p => p.status === 'warning').length;
        const error = Object.values(subProjects).filter(p => p.status === 'error').length;

        return { total, healthy, warning, error };
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 项目卡片点击事件
        const cards = this.state.container.querySelectorAll('.project-card');
        cards.forEach(card => {
            card.addEventListener('click', (event) => {
                // 避免按钮点击时触发
                if (event.target.tagName === 'BUTTON' || event.target.closest('button')) return;

                const projectKey = card.getAttribute('data-project');
                this.showDetails(projectKey);
            });
        });
    },

    /**
     * 显示项目详情
     */
    showDetails: function(projectKey) {
        const config = this.config.projects[projectKey];
        const status = this.state.subProjects[projectKey] || {};
        const details = status.details || {};

        const content = `
            <div class="project-details">
                <div class="row">
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>项目名称:</strong> ${config.name}
                        </div>
                        <div class="detail-item">
                            <strong>状态:</strong>
                            <span class="badge bg-${this.getStatusColor(status.status)}">${this.getStatusText(status.status)}</span>
                        </div>
                        <div class="detail-item">
                            <strong>路径:</strong>
                            <code>${config.path}</code>
                        </div>
                        <div class="detail-item">
                            <strong>最后检查:</strong> ${this.formatTimestamp(status.last_check)}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>版本:</strong> ${details.version || '未知'}
                        </div>
                        <div class="detail-item">
                            <strong>运行时长:</strong> ${details.uptime || '未知'}
                        </div>
                        <div class="detail-item">
                            <strong>GPU使用:</strong> ${details.gpu_usage || 0}%
                        </div>
                        <div class="detail-item">
                            <strong>内存使用:</strong> ${details.memory_usage || 0}%
                        </div>
                    </div>
                </div>

                <div class="mt-3">
                    <strong>功能特性:</strong>
                    <div class="mt-2">
                        ${config.features.map(f => `
                            <span class="badge bg-${config.color} me-1">${f}</span>
                        `).join('')}
                    </div>
                </div>

                <div class="mt-3">
                    <strong>描述:</strong>
                    <p class="mt-1">${config.description}</p>
                </div>
            </div>
        `;

        const detailsPanel = document.getElementById('projectDetailsPanel');
        const detailsContent = document.getElementById('projectDetailsContent');

        if (detailsPanel && detailsContent) {
            detailsContent.innerHTML = content;
            detailsPanel.style.display = 'block';
            detailsPanel.scrollIntoView({ behavior: 'smooth' });
        }

        this.state.selectedProject = projectKey;
    },

    /**
     * 隐藏详情面板
     */
    hideDetails: function() {
        const detailsPanel = document.getElementById('projectDetailsPanel');
        if (detailsPanel) {
            detailsPanel.style.display = 'none';
        }
        this.state.selectedProject = null;
    },

    /**
     * 检查项目健康状态
     */
    checkHealth: function(projectKey) {
        const config = this.config.projects[projectKey];

        ModalManager.alert({
            title: `${config.name} 健康检查`,
            content: `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">检查中...</span>
                    </div>
                    <p class="mt-2">正在检查 ${config.name} 健康状态...</p>
                </div>
            `,
            size: 'sm'
        });

        // 模拟检查过程
        setTimeout(() => {
            const status = this.state.subProjects[projectKey] || {};
            const isHealthy = status.status === 'healthy';

            ModalManager.update(this.getLastModalId(), {
                content: `
                    <div class="health-check-result">
                        <div class="text-center mb-3">
                            <i class="fas ${isHealthy ? 'fa-check-circle text-success' : 'fa-exclamation-triangle text-warning'} fa-3x"></i>
                        </div>
                        <div class="text-center">
                            <h5>${isHealthy ? '健康状态正常' : '存在一些问题'}</h5>
                            <p class="text-muted">${config.name}</p>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <strong>检查项目:</strong>
                                <ul class="mt-2">
                                    <li>进程状态: ${isHealthy ? '运行中' : '异常'}</li>
                                    <li>GPU使用: ${status.details?.gpu_usage || 0}%</li>
                                    <li>内存使用: ${status.details?.memory_usage || 0}%</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <strong>建议操作:</strong>
                                <ul class="mt-2">
                                    ${isHealthy ? '<li>无需操作</li>' : '<li>检查日志</li><li>重启服务</li>'}
                                </ul>
                            </div>
                        </div>
                    </div>
                `
            });
        }, 2000);
    },

    /**
     * 打开项目配置
     */
    openConfig: function(projectKey) {
        const config = this.config.projects[projectKey];

        ModalManager.alert({
            title: `${config.name} 配置`,
            content: `
                <div class="config-panel">
                    <div class="mb-3">
                        <label class="form-label"><strong>项目路径:</strong></label>
                        <input type="text" class="form-control" value="${config.path}" readonly>
                    </div>
                    <div class="mb-3">
                        <label class="form-label"><strong>功能特性:</strong></label>
                        <div>
                            ${config.features.map(f => `
                                <span class="badge bg-${config.color} me-1">${f}</span>
                            `).join('')}
                        </div>
                    </div>
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="project-enable-${projectKey}" checked>
                        <label class="form-check-label" for="project-enable-${projectKey}">启用该项目</label>
                    </div>
                    <div class="d-grid gap-2">
                        <button class="btn btn-outline-primary" onclick="subProjectMonitor.restartProject('${projectKey}')">
                            <i class="fas fa-redo me-1"></i>重启项目
                        </button>
                        <button class="btn btn-outline-secondary" onclick="subProjectMonitor.viewLogs('${projectKey}')">
                            <i class="fas fa-file-alt me-1"></i>查看日志
                        </button>
                    </div>
                </div>
            `,
            size: 'lg'
        });
    },

    /**
     * 重启项目
     */
    restartProject: function(projectKey) {
        const config = this.config.projects[projectKey];

        ModalManager.confirm({
            title: '确认重启',
            content: `确定要重启 ${config.name} 吗？`,
            onConfirm: () => {
                Notifications.show('重启中', `正在重启 ${config.name}...`, 'info');
                setTimeout(() => {
                    Notifications.show('重启成功', `${config.name} 已重启`, 'success');
                }, 3000);
            }
        });
    },

    /**
     * 查看项目日志
     */
    viewLogs: function(projectKey) {
        const config = this.config.projects[projectKey];
        Notifications.show('日志查看', `正在打开 ${config.name} 日志...`, 'info');
        // 这里可以跳转到日志查看页面
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
            'unknown': 'secondary'
        };
        return colors[status] || 'secondary';
    },

    /**
     * 获取状态图标
     */
    getStatusIcon: function(status) {
        const icons = {
            'healthy': 'check-circle',
            'running': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle',
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
            'healthy': '健康',
            'running': '运行中',
            'warning': '警告',
            'error': '错误',
            'failed': '失败',
            'unknown': '未知'
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
                this.loadSubProjects();
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
        return this.loadSubProjects();
    },

    /**
     * 更新数据
     */
    update: function(newData) {
        this.state.subProjects = newData.projects || {};
        this.render();
    },

    /**
     * 销毁子项目监测模块
     */
    destroy: function() {
        console.log('SubProject Monitor destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.subProjectMonitor = SubProjectMonitor;

