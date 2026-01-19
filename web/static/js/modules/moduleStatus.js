/**
 * Module Status Module - 模块状态模块
 * 负责各功能模块的部署说明、配置说明监控
 * 单一职责：模块状态显示和更新
 */

const ModuleStatus = {
    // 状态
    state: {
        container: null,
        modules: {},
        updateInterval: null,
        autoRefresh: true
    },

    // 配置
    config: {
        refreshInterval: 15000, // 15秒
        apiEndpoint: '/api/project/status'
    },

    /**
     * 初始化模块状态模块
     */
    init: function() {
        console.log('Module Status initializing...');
        this.state.container = document.getElementById('moduleStatusContent');

        if (!this.state.container) {
            console.error('Module Status container not found');
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
            if (!response.ok) throw new Error('Failed to fetch module status');

            const data = await response.json();
            this.state.modules = data.components || {};
            this.render();
        } catch (error) {
            console.error('Failed to load module status:', error);
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
        const modules = this.state.modules;

        if (Object.keys(modules).length === 0) {
            return `
                <div class="text-center py-5">
                    <i class="fas fa-cubes fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">暂无模块信息</h5>
                    <p class="text-muted">模块状态数据未加载</p>
                </div>
            `;
        }

        return `
            <div class="module-status-container">
                <!-- 模块网格 -->
                <div class="modules-grid">
                    ${this.buildModulesGridHtml(modules)}
                </div>

                <!-- 模块详情面板 -->
                <div class="module-details-panel mt-4" id="moduleDetailsPanel" style="display: none;">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-info-circle me-2"></i>模块详情
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="moduleDetailsContent"></div>
                        </div>
                    </div>
                </div>

                <!-- 配置说明 -->
                <div class="config-documentation mt-4">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-book me-2"></i>配置说明
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="config-sections">
                                ${this.buildConfigSectionsHtml()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建模块网格HTML
     */
    buildModulesGridHtml: function(modules) {
        return Object.entries(modules).map(([name, module]) => `
            <div class="module-card" data-module="${name}">
                <div class="module-header">
                    <div class="module-icon">
                        <i class="fas ${this.getModuleIcon(name)}"></i>
                    </div>
                    <div class="module-info">
                        <div class="module-name">${this.getModuleDisplayName(name)}</div>
                        <div class="module-status">
                            <span class="badge bg-${this.getStatusColor(module.status)}">${this.getStatusText(module.status)}</span>
                        </div>
                    </div>
                </div>
                <div class="module-description">
                    ${this.getModuleDescription(name)}
                </div>
                <div class="module-meta">
                    <small class="text-muted">
                        最后检查: ${this.formatTimestamp(module.last_check)}
                    </small>
                </div>
                <div class="module-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="moduleStatus.showDetails('${name}')">
                        <i class="fas fa-eye me-1"></i>详情
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="moduleStatus.showConfig('${name}')">
                        <i class="fas fa-cog me-1"></i>配置
                    </button>
                </div>
            </div>
        `).join('');
    },

    /**
     * 构建配置说明HTML
     */
    buildConfigSectionsHtml: function() {
        const sections = [
            {
                title: '环境配置',
                icon: 'fas fa-server',
                content: `
                    <ul>
                        <li>Python 3.8+ 环境</li>
                        <li>虚拟环境配置</li>
                        <li>依赖包管理</li>
                        <li>路径配置</li>
                    </ul>
                `
            },
            {
                title: '后端配置',
                icon: 'fas fa-code',
                content: `
                    <ul>
                        <li>FastAPI 框架</li>
                        <li>WebSocket 支持</li>
                        <li>API 路由配置</li>
                        <li>安全中间件</li>
                    </ul>
                `
            },
            {
                title: '前端配置',
                icon: 'fas fa-desktop',
                content: `
                    <ul>
                        <li>Bootstrap 5 UI</li>
                        <li>Chart.js 图表</li>
                        <li>Socket.IO 通信</li>
                        <li>模块化 JavaScript</li>
                    </ul>
                `
            },
            {
                title: '数据库配置',
                icon: 'fas fa-database',
                content: `
                    <ul>
                        <li>SQLite 默认</li>
                        <li>MySQL 可选</li>
                        <li>数据迁移</li>
                        <li>备份策略</li>
                    </ul>
                `
            }
        ];

        return sections.map(section => `
            <div class="config-section">
                <div class="config-section-header">
                    <i class="${section.icon} me-2"></i>
                    <strong>${section.title}</strong>
                </div>
                <div class="config-section-content">
                    ${section.content}
                </div>
            </div>
        `).join('');
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 模块卡片点击事件
        const moduleCards = this.state.container.querySelectorAll('.module-card');
        moduleCards.forEach(card => {
            card.addEventListener('click', (event) => {
                // 避免按钮点击时触发
                if (event.target.tagName === 'BUTTON') return;

                const moduleName = card.getAttribute('data-module');
                this.showDetails(moduleName);
            });
        });
    },

    /**
     * 显示模块详情
     */
    showDetails: function(moduleName) {
        const module = this.state.modules[moduleName];
        if (!module) return;

        const detailsPanel = document.getElementById('moduleDetailsPanel');
        const detailsContent = document.getElementById('moduleDetailsContent');

        if (detailsPanel && detailsContent) {
            const content = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>模块名称:</strong> ${this.getModuleDisplayName(moduleName)}
                        </div>
                        <div class="detail-item">
                            <strong>状态:</strong>
                            <span class="badge bg-${this.getStatusColor(module.status)}">${this.getStatusText(module.status)}</span>
                        </div>
                        <div class="detail-item">
                            <strong>最后检查:</strong> ${this.formatTimestamp(module.last_check)}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>描述:</strong> ${this.getModuleDescription(moduleName)}
                        </div>
                        <div class="detail-item">
                            <strong>依赖:</strong> ${this.getModuleDependencies(moduleName).join(', ')}
                        </div>
                    </div>
                </div>
                ${module.details ? `
                    <div class="mt-3">
                        <strong>详细信息:</strong>
                        <pre class="mt-2">${JSON.stringify(module.details, null, 2)}</pre>
                    </div>
                ` : ''}
            `;

            detailsContent.innerHTML = content;
            detailsPanel.style.display = 'block';
            detailsPanel.scrollIntoView({ behavior: 'smooth' });
        }
    },

    /**
     * 显示模块配置
     */
    showConfig: function(moduleName) {
        // 这里可以实现配置显示逻辑
        ModalManager.alert({
            title: `${this.getModuleDisplayName(moduleName)} 配置`,
            content: `<p>配置信息加载中...</p>`,
            size: 'lg'
        });
    },

    /**
     * 获取模块图标
     */
    getModuleIcon: function(moduleName) {
        const icons = {
            'frontend': 'fa-desktop',
            'backend': 'fa-server',
            'ai': 'fa-brain',
            'processing': 'fa-cogs',
            'integrations': 'fa-plug'
        };
        return icons[moduleName] || 'fa-cube';
    },

    /**
     * 获取模块显示名称
     */
    getModuleDisplayName: function(moduleName) {
        const names = {
            'frontend': '前端界面',
            'backend': '后端服务',
            'ai': 'AI 引擎',
            'processing': '数据处理',
            'integrations': '集成服务'
        };
        return names[moduleName] || moduleName;
    },

    /**
     * 获取模块描述
     */
    getModuleDescription: function(moduleName) {
        const descriptions = {
            'frontend': '用户界面和交互组件',
            'backend': 'API 服务和业务逻辑',
            'ai': '人工智能算法和模型',
            'processing': '数据处理和转换服务',
            'integrations': '第三方服务集成'
        };
        return descriptions[moduleName] || '模块功能描述';
    },

    /**
     * 获取模块依赖
     */
    getModuleDependencies: function(moduleName) {
        const dependencies = {
            'frontend': ['Bootstrap', 'Chart.js', 'Socket.IO'],
            'backend': ['FastAPI', 'Uvicorn', 'SQLAlchemy'],
            'ai': ['TensorFlow', 'OpenCV', 'NumPy'],
            'processing': ['Pandas', 'PIL', 'FFmpeg'],
            'integrations': ['Requests', 'WebSocket', 'AsyncIO']
        };
        return dependencies[moduleName] || [];
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
                加载模块状态失败: ${message}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="moduleStatus.refresh()">
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
        this.state.modules = newData.components || {};
        this.render();
    },

    /**
     * 销毁模块状态模块
     */
    destroy: function() {
        console.log('Module Status destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.moduleStatus = ModuleStatus;
