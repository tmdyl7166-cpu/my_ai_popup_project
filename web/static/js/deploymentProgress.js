/**
 * Deployment Progress Module - 部署进度模块
 * 负责各类部署功能的部署进度百分比监控
 * 单一职责：部署进度显示和更新
 */

const DeploymentProgress = {
    // 状态
    state: {
        container: null,
        progress: {},
        updateInterval: null,
        autoRefresh: true
    },

    // 配置
    config: {
        refreshInterval: 10000, // 10秒
        apiEndpoint: '/api/deployment/progress'
    },

    /**
     * 初始化部署进度模块
     */
    init: function() {
        console.log('Deployment Progress initializing...');
        this.state.container = document.getElementById('deploymentProgressContent');

        if (!this.state.container) {
            console.error('Deployment Progress container not found');
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
            if (!response.ok) throw new Error('Failed to fetch deployment progress');

            this.state.progress = await response.json();
            this.render();
        } catch (error) {
            console.error('Failed to load deployment progress:', error);
            this.showError(error.message);
        }
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
        const progress = this.state.progress;

        if (!progress || progress.status === 'not_found') {
            return `
                <div class="text-center py-5">
                    <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">暂无部署进度</h5>
                    <p class="text-muted">部署进度数据未加载</p>
                </div>
            `;
        }

        return `
            <div class="deployment-progress-container">
                <!-- 总体进度 -->
                <div class="overall-progress mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-tachometer-alt me-2"></i>总体部署进度
                            </h6>
                        </div>
                        <div class="card-body">
                            ${this.buildOverallProgressHtml(progress)}
                        </div>
                    </div>
                </div>

                <!-- 进度详情 -->
                <div class="progress-details mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-tasks me-2"></i>部署任务详情
                            </h6>
                        </div>
                        <div class="card-body">
                            ${this.buildProgressDetailsHtml(progress)}
                        </div>
                    </div>
                </div>

                <!-- 进度趋势 -->
                <div class="progress-trend">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-chart-area me-2"></i>部署进度趋势
                            </h6>
                        </div>
                        <div class="card-body">
                            <canvas id="progressTrendChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建总体进度HTML
     */
    buildOverallProgressHtml: function(progress) {
        // 模拟总体进度数据
        const overallProgress = this.calculateOverallProgress(progress);

        return `
            <div class="overall-stats">
                <div class="row">
                    <div class="col-md-3">
                        <div class="stat-item">
                            <div class="stat-value">${overallProgress.completed}</div>
                            <div class="stat-label">已完成</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-item">
                            <div class="stat-value">${overallProgress.inProgress}</div>
                            <div class="stat-label">进行中</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-item">
                            <div class="stat-value">${overallProgress.pending}</div>
                            <div class="stat-label">待开始</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-item">
                            <div class="stat-value">${overallProgress.total}</div>
                            <div class="stat-label">总任务</div>
                        </div>
                    </div>
                </div>
                <div class="progress mt-3" style="height: 20px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated"
                         id="overallProgressBar"
                         style="width: ${overallProgress.percentage}%">
                        ${overallProgress.percentage}%
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建进度详情HTML
     */
    buildProgressDetailsHtml: function(progress) {
        // 模拟任务列表
        const tasks = this.getDeploymentTasks(progress);

        if (tasks.length === 0) {
            return '<div class="text-muted">暂无任务详情</div>';
        }

        return `
            <div class="tasks-list">
                ${tasks.map(task => `
                    <div class="task-item">
                        <div class="task-header">
                            <div class="task-name">${task.name}</div>
                            <div class="task-status">
                                <span class="badge bg-${this.getTaskStatusColor(task.status)}">${this.getTaskStatusText(task.status)}</span>
                            </div>
                        </div>
                        <div class="task-description">${task.description}</div>
                        <div class="task-progress">
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar bg-${this.getTaskStatusColor(task.status)}"
                                     style="width: ${task.progress}%"></div>
                            </div>
                            <small class="text-muted mt-1 d-block">${task.progress}% 完成</small>
                        </div>
                        <div class="task-meta">
                            <small class="text-muted">
                                开始时间: ${this.formatTimestamp(task.startTime)} |
                                预计完成: ${this.formatTimestamp(task.estimatedEnd)}
                            </small>
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
        // 任务项点击事件
        const taskItems = this.state.container.querySelectorAll('.task-item');
        taskItems.forEach(item => {
            item.addEventListener('click', () => {
                const taskName = item.querySelector('.task-name').textContent;
                this.showTaskDetails(taskName);
            });
        });
    },

    /**
     * 显示任务详情
     */
    showTaskDetails: function(taskName) {
        const tasks = this.getDeploymentTasks(this.state.progress);
        const task = tasks.find(t => t.name === taskName);

        if (!task) return;

        const content = `
            <div class="task-details">
                <h6>${task.name}</h6>
                <div class="row">
                    <div class="col-md-6">
                        <strong>状态:</strong>
                        <span class="badge bg-${this.getTaskStatusColor(task.status)} ms-2">${this.getTaskStatusText(task.status)}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>进度:</strong> ${task.progress}%
                    </div>
                </div>
                <div class="mt-3">
                    <strong>描述:</strong>
                    <p class="mt-2">${task.description}</p>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <strong>开始时间:</strong> ${this.formatTimestamp(task.startTime)}
                    </div>
                    <div class="col-md-6">
                        <strong>预计完成:</strong> ${this.formatTimestamp(task.estimatedEnd)}
                    </div>
                </div>
                ${task.logs ? `
                    <div class="mt-3">
                        <strong>最新日志:</strong>
                        <pre class="mt-2">${task.logs.join('\n')}</pre>
                    </div>
                ` : ''}
            </div>
        `;

        ModalManager.alert({
            title: `${taskName} 详情`,
            content: content,
            size: 'lg'
        });
    },

    /**
     * 计算总体进度
     */
    calculateOverallProgress: function(progress) {
        const tasks = this.getDeploymentTasks(progress);

        const completed = tasks.filter(t => t.status === 'completed').length;
        const inProgress = tasks.filter(t => t.status === 'in_progress').length;
        const pending = tasks.filter(t => t.status === 'pending').length;
        const total = tasks.length;

        const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

        return {
            completed,
            inProgress,
            pending,
            total,
            percentage
        };
    },

    /**
     * 获取部署任务
     */
    getDeploymentTasks: function(progress) {
        // 这里可以从实际的进度数据中解析任务
        // 暂时返回模拟数据
        return [
            {
                name: '环境配置',
                description: '配置Python环境和依赖包',
                status: 'completed',
                progress: 100,
                startTime: '2024-01-18T08:00:00Z',
                estimatedEnd: '2024-01-18T08:30:00Z',
                logs: ['环境配置完成', '依赖安装成功']
            },
            {
                name: '数据库初始化',
                description: '初始化数据库结构和基础数据',
                status: 'completed',
                progress: 100,
                startTime: '2024-01-18T08:30:00Z',
                estimatedEnd: '2024-01-18T09:00:00Z',
                logs: ['数据库创建成功', '基础数据导入完成']
            },
            {
                name: 'API服务部署',
                description: '部署后端API服务',
                status: 'in_progress',
                progress: 75,
                startTime: '2024-01-18T09:00:00Z',
                estimatedEnd: '2024-01-18T10:00:00Z',
                logs: ['服务启动中...', '路由配置完成']
            },
            {
                name: '前端界面部署',
                description: '部署Web前端界面',
                status: 'pending',
                progress: 0,
                startTime: null,
                estimatedEnd: '2024-01-18T11:00:00Z',
                logs: []
            },
            {
                name: '集成测试',
                description: '执行系统集成测试',
                status: 'pending',
                progress: 0,
                startTime: null,
                estimatedEnd: '2024-01-18T12:00:00Z',
                logs: []
            }
        ];
    },

    /**
     * 获取任务状态颜色
     */
    getTaskStatusColor: function(status) {
        const colors = {
            'completed': 'success',
            'in_progress': 'primary',
            'pending': 'secondary',
            'failed': 'danger'
        };
        return colors[status] || 'secondary';
    },

    /**
     * 获取任务状态文本
     */
    getTaskStatusText: function(status) {
        const texts = {
            'completed': '已完成',
            'in_progress': '进行中',
            'pending': '待开始',
            'failed': '失败'
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
                加载部署进度失败: ${message}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="deploymentProgress.refresh()">
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
        this.state.progress = newData;
        this.render();
    },

    /**
     * 销毁部署进度模块
     */
    destroy: function() {
        console.log('Deployment Progress destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.deploymentProgress = DeploymentProgress;
