/**
 * Script Runner Module - 自动化脚本调用模块
 * 负责执行和管理自动化运行脚本
 * 单一职责：脚本执行和结果展示
 */

const ScriptRunner = {
    // 状态
    state: {
        container: null,
        scripts: [],
        runningScripts: new Map(),
        updateInterval: null,
        autoRefresh: true
    },

    // 配置
    config: {
        refreshInterval: 5000, // 5秒
        listEndpoint: '/api/scripts/list',
        statusEndpoint: '/api/scripts/status',
        executeEndpoint: '/api/scripts/execute',
        stopEndpoint: '/api/scripts/stop',
        logEndpoint: '/api/logs',
        scriptCategories: {
            'health': { name: '健康检查', icon: 'fa-heartbeat', color: 'success' },
            'deploy': { name: '部署脚本', icon: 'fa-rocket', color: 'primary' },
            'backup': { name: '备份脚本', icon: 'fa-save', color: 'info' },
            'maintain': { name: '维护脚本', icon: 'fa-tools', color: 'warning' },
            'test': { name: '测试脚本', icon: 'fa-vial', color: 'danger' }
        }
    },

    /**
     * 初始化脚本运行器模块
     */
    init: function() {
        console.log('Script Runner initializing...');
        this.state.container = document.getElementById('scriptRunnerContent');

        if (!this.state.container) {
            console.error('Script Runner container not found');
            return;
        }

        this.loadScripts();
        this.startAutoRefresh();
    },

    /**
     * 加载脚本列表
     */
    loadScripts: async function() {
        try {
            const response = await fetch(this.config.listEndpoint);
            if (!response.ok) throw new Error('Failed to fetch scripts');

            const data = await response.json();
            this.state.scripts = data.scripts || [];
            this.render();
        } catch (error) {
            console.error('Failed to load scripts:', error);
            this.state.scripts = this.getDefaultScripts();
            this.render();
        }
    },

    /**
     * 获取默认脚本列表
     */
    getDefaultScripts: function() {
        return [
            {
                name: 'health_check.py',
                display_name: '系统健康检查',
                description: '检查系统各组件运行状态',
                category: 'health',
                status: 'idle',
                last_run: null,
                frequency: '手动'
            },
            {
                name: 'system_diagnostic',
                display_name: '系统诊断',
                description: '诊断系统配置和依赖',
                category: 'health',
                status: 'idle',
                last_run: null,
                frequency: '手动'
            },
            {
                name: 'deploy.sh',
                display_name: '部署脚本',
                description: '执行项目部署流程',
                category: 'deploy',
                status: 'idle',
                last_run: null,
                frequency: '手动'
            },
            {
                name: 'unified_launcher.py',
                display_name: '统一启动器',
                description: '启动所有服务组件',
                category: 'deploy',
                status: 'idle',
                last_run: null,
                frequency: '手动'
            },
            {
                name: 'emergency_recovery.sh',
                display_name: '紧急恢复',
                description: '执行紧急恢复操作',
                category: 'maintain',
                status: 'idle',
                last_run: null,
                frequency: '手动'
            },
            {
                name: 'validate_configs.py',
                display_name: '配置验证',
                description: '验证配置文件正确性',
                category: 'test',
                status: 'idle',
                last_run: null,
                frequency: '手动'
            }
        ];
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
        const scripts = this.state.scripts;
        const summary = this.getScriptSummary(scripts);

        return `
            <div class="script-runner-container">
                <!-- 脚本统计 -->
                <div class="script-summary mb-4">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-primary">
                                    <i class="fas fa-code fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.total}</div>
                                    <div class="summary-label">脚本总数</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-success">
                                    <i class="fas fa-check-circle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.completed}</div>
                                    <div class="summary-label">执行成功</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-warning">
                                    <i class="fas fa-play-circle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.running}</div>
                                    <div class="summary-label">运行中</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="summary-card">
                                <div class="summary-icon text-danger">
                                    <i class="fas fa-exclamation-triangle fa-2x"></i>
                                </div>
                                <div class="summary-info">
                                    <div class="summary-value">${summary.failed}</div>
                                    <div class="summary-label">执行失败</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 脚本分类导航 -->
                <div class="script-categories mb-4">
                    <div class="nav nav-pills" id="scriptCategories" role="tablist">
                        <button class="nav-link active" data-category="all">
                            <i class="fas fa-list me-1"></i>全部
                        </button>
                        ${this.buildCategoryPills()}
                    </div>
                </div>

                <!-- 脚本列表 -->
                <div class="script-list">
                    ${this.buildScriptCards(scripts)}
                </div>

                <!-- 运行中脚本 -->
                ${this.buildRunningScriptsPanel()}
            </div>
        `;
    },

    /**
     * 构建分类导航HTML
     */
    buildCategoryPills: function() {
        return Object.entries(this.config.scriptCategories).map(([key, category]) => `
            <button class="nav-link" data-category="${key}">
                <i class="fas ${category.icon} me-1"></i>
                ${category.name}
            </button>
        `).join('');
    },

    /**
     * 构建脚本卡片HTML
     */
    buildScriptCards: function(scripts) {
        if (!scripts || scripts.length === 0) {
            return `
                <div class="text-center py-5">
                    <i class="fas fa-code fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">暂无脚本</h5>
                    <p class="text-muted">未找到可执行的脚本</p>
                </div>
            `;
        }

        return `
            <div class="row">
                ${scripts.map(script => this.buildScriptCard(script)).join('')}
            </div>
        `;
    },

    /**
     * 构建单个脚本卡片
     */
    buildScriptCard: function(script) {
        const category = this.config.scriptCategories[script.category] || { name: '其他', icon: 'fa-code', color: 'secondary' };
        const isRunning = script.status === 'running' || script.status === 'starting';

        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="script-card ${isRunning ? 'script-running' : ''}" data-script="${script.name}">
                    <div class="script-card-header bg-${category.color}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="script-info">
                                <div class="script-name">${script.display_name || script.name}</div>
                                <div class="script-category">
                                    <span class="badge bg-light text-${category.color}">
                                        <i class="fas ${category.icon} me-1"></i>
                                        ${category.name}
                                    </span>
                                </div>
                            </div>
                            <div class="script-status">
                                <span class="badge bg-light text-${this.getStatusColor(script.status)}">
                                    <i class="fas ${this.getStatusIcon(script.status)} me-1"></i>
                                    ${this.getStatusText(script.status)}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="script-card-body">
                        <div class="script-description">
                            ${script.description || '暂无描述'}
                        </div>
                        <div class="script-meta">
                            <small class="text-muted">
                                <i class="fas fa-clock me-1"></i>
                                最后运行: ${this.formatTimestamp(script.last_run) || '从未'}
                            </small>
                            <br>
                            <small class="text-muted">
                                <i class="fas fa-redo me-1"></i>
                                执行频率: ${script.frequency || '手动'}
                            </small>
                        </div>
                    </div>
                    <div class="script-card-footer">
                        <div class="btn-group w-100">
                            ${isRunning ? `
                                <button class="btn btn-outline-warning"
                                        onclick="scriptRunner.stopScript('${script.name}')"
                                        ${script.status === 'starting' ? 'disabled' : ''}>
                                    <i class="fas fa-stop me-1"></i>停止
                                </button>
                            ` : `
                                <button class="btn btn-outline-success"
                                        onclick="scriptRunner.runScript('${script.name}')">
                                    <i class="fas fa-play me-1"></i>执行
                                </button>
                            `}
                            <button class="btn btn-outline-primary"
                                    onclick="scriptRunner.showDetails('${script.name}')">
                                <i class="fas fa-eye me-1"></i>详情
                            </button>
                            <button class="btn btn-outline-info"
                                    onclick="scriptRunner.viewLogs('${script.name}')">
                                <i class="fas fa-file-alt me-1"></i>日志
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建运行中脚本面板
     */
    buildRunningScriptsPanel: function() {
        const runningScripts = Array.from(this.state.runningScripts.values());

        if (runningScripts.length === 0) {
            return '';
        }

        return `
            <div class="running-scripts-panel mt-4">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h6 class="mb-0">
                            <i class="fas fa-spinner fa-spin me-2"></i>
                            运行中的脚本
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="list-group">
                            ${runningScripts.map(script => `
                                <div class="list-group-item">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>${script.display_name || script.name}</strong>
                                            <br>
                                            <small class="text-muted">开始时间: ${this.formatTimestamp(script.start_time)}</small>
                                        </div>
                                        <div class="progress" style="width: 200px;">
                                            <div class="progress-bar progress-bar-striped progress-bar-animated"
                                                 style="width: ${script.progress || 0}%">
                                                ${script.progress || 0}%
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 获取脚本统计
     */
    getScriptSummary: function(scripts) {
        const total = scripts.length;
        const completed = scripts.filter(s => s.status === 'completed').length;
        const running = scripts.filter(s => s.status === 'running' || s.status === 'starting').length;
        const failed = scripts.filter(s => s.status === 'failed' || s.status === 'error').length;

        return { total, completed, running, failed };
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 分类切换
        const categoryButtons = this.state.container.querySelectorAll('[data-category]');
        categoryButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const category = event.currentTarget.getAttribute('data-category');
                this.filterScripts(category);
            });
        });
    },

    /**
     * 过滤脚本
     */
    filterScripts: function(category) {
        // 更新激活状态
        const buttons = this.state.container.querySelectorAll('[data-category]');
        buttons.forEach(btn => btn.classList.remove('active'));
        event.currentTarget.classList.add('active');

        // 过滤脚本
        const scripts = category === 'all'
            ? this.state.scripts
            : this.state.scripts.filter(s => s.category === category);

        // 重新渲染
        const scriptList = this.state.container.querySelector('.script-list');
        if (scriptList) {
            scriptList.innerHTML = this.buildScriptCards(scripts);
        }
    },

    /**
     * 执行脚本
     */
    runScript: async function(scriptName) {
        const script = this.state.scripts.find(s => s.name === scriptName);
        if (!script) return;

        // 检查是否已经在运行
        if (this.state.runningScripts.has(scriptName)) {
            Notifications.show('执行失败', `${script.display_name || scriptName} 已在运行中`, 'warning');
            return;
        }

        // 确认执行
        const confirmed = await this.showConfirmDialog(script);
        if (!confirmed) return;

        try {
            // 更新状态
            script.status = 'starting';
            this.state.runningScripts.set(scriptName, {
                ...script,
                start_time: new Date().toISOString(),
                progress: 0
            });
            this.render();

            Notifications.show('执行中', `正在启动 ${script.display_name || scriptName}...`, 'info');

            // 模拟执行过程
            this.simulateScriptExecution(scriptName);

        } catch (error) {
            console.error('Failed to run script:', error);
            Notifications.show('执行失败', error.message, 'error');
        }
    },

    /**
     * 模拟脚本执行
     */
    simulateScriptExecution: function(scriptName) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;

            const runningScript = this.state.runningScripts.get(scriptName);
            if (runningScript) {
                runningScript.progress = Math.round(progress);
            }

            // 更新UI
            const progressBar = document.querySelector(`[data-script="${scriptName}"] .progress-bar`);
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.textContent = `${Math.round(progress)}%`;
            }

            if (progress >= 100) {
                clearInterval(interval);
                this.completeScript(scriptName, true);
            }
        }, 1000);
    },

    /**
     * 完成脚本执行
     */
    completeScript: function(scriptName, success) {
        const script = this.state.scripts.find(s => s.name === scriptName);
        if (script) {
            script.status = success ? 'completed' : 'failed';
            script.last_run = new Date().toISOString();
        }

        this.state.runningScripts.delete(scriptName);
        this.render();

        const message = success ? '执行成功' : '执行失败';
        const type = success ? 'success' : 'error';
        Notifications.show(message, `${script?.display_name || scriptName} ${message}`, type);

        // 显示冒泡通知
        bubbleMonitor.show(success ? 'success' : 'error', '脚本执行', `${script?.display_name || scriptName} 已${message}`);
    },

    /**
     * 停止脚本
     */
    stopScript: async function(scriptName) {
        const script = this.state.scripts.find(s => s.name === scriptName);
        if (!script) return;

        ModalManager.confirm({
            title: '确认停止',
            content: `确定要停止 ${script.display_name || scriptName} 吗？`,
            onConfirm: () => {
                // 更新状态
                script.status = 'idle';
                this.state.runningScripts.delete(scriptName);
                this.render();

                Notifications.show('已停止', `${script.display_name || scriptName} 已停止`, 'warning');
            }
        });
    },

    /**
     * 显示脚本详情
     */
    showDetails: function(scriptName) {
        const script = this.state.scripts.find(s => s.name === scriptName);
        if (!script) return;

        const category = this.config.scriptCategories[script.category] || { name: '其他', icon: 'fa-code', color: 'secondary' };

        const content = `
            <div class="script-details">
                <div class="row">
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>脚本名称:</strong> ${script.name}
                        </div>
                        <div class="detail-item">
                            <strong>显示名称:</strong> ${script.display_name || script.name}
                        </div>
                        <div class="detail-item">
                            <strong>分类:</strong>
                            <span class="badge bg-${category.color}">
                                <i class="fas ${category.icon} me-1"></i>
                                ${category.name}
                            </span>
                        </div>
                        <div class="detail-item">
                            <strong>状态:</strong>
                            <span class="badge bg-${this.getStatusColor(script.status)}">${this.getStatusText(script.status)}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="detail-item">
                            <strong>执行频率:</strong> ${script.frequency || '手动'}
                        </div>
                        <div class="detail-item">
                            <strong>最后运行:</strong> ${this.formatTimestamp(script.last_run) || '从未'}
                        </div>
                        <div class="detail-item">
                            <strong>运行次数:</strong> ${script.run_count || 0}
                        </div>
                        <div class="detail-item">
                            <strong>成功率:</strong> ${script.success_rate || 0}%
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <strong>描述:</strong>
                    <p class="mt-1">${script.description || '暂无描述'}</p>
                </div>
            </div>
        `;

        ModalManager.alert({
            title: `${script.display_name || scriptName} 详情`,
            content: content,
            size: 'lg'
        });
    },

    /**
     * 查看脚本日志
     */
    viewLogs: function(scriptName) {
        // 跳转到日志查看页面
        const logsTab = document.querySelector('[data-bs-target="#logs-viewer"]');
        if (logsTab) {
            logsTab.click();
        }

        // 筛选相关日志
        setTimeout(() => {
            if (typeof LogsViewer !== 'undefined') {
                LogsViewer.filterByScript(scriptName);
            }
        }, 500);

        Notifications.show('日志查看', `正在加载 ${scriptName} 的日志...`, 'info');
    },

    /**
     * 批量执行脚本
     */
    runBatch: async function(category) {
        const scripts = category === 'all'
            ? this.state.scripts
            : this.state.scripts.filter(s => s.category === category);

        const idleScripts = scripts.filter(s => s.status === 'idle');

        if (idleScripts.length === 0) {
            Notifications.show('无可执行脚本', '没有处于就绪状态的脚本', 'warning');
            return;
        }

        const confirmed = await this.showConfirmDialog({
            name: '批量执行',
            display_name: `批量执行 ${idleScripts.length} 个脚本`
        });

        if (!confirmed) return;

        // 依次执行脚本
        for (const script of idleScripts) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            this.runScript(script.name);
        }
    },

    /**
     * 显示确认对话框
     */
    showConfirmDialog: function(script) {
        return new Promise((resolve) => {
            ModalManager.confirm({
                title: '确认执行',
                content: `确定要执行 <strong>${script.display_name || script.name}</strong> 吗？<br><br><small class="text-muted">${script.description || ''}</small>`,
                onConfirm: () => resolve(true),
                onCancel: () => resolve(false)
            });
        });
    },

    /**
     * 获取状态颜色
     */
    getStatusColor: function(status) {
        const colors = {
            'idle': 'secondary',
            'starting': 'info',
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'error': 'danger',
            'stopped': 'warning',
            'timeout': 'warning'
        };
        return colors[status] || 'secondary';
    },

    /**
     * 获取状态图标
     */
    getStatusIcon: function(status) {
        const icons = {
            'idle': 'clock',
            'starting': 'spinner',
            'running': 'play-circle',
            'completed': 'check-circle',
            'failed': 'times-circle',
            'error': 'exclamation-triangle',
            'stopped': 'stop-circle',
            'timeout': 'clock'
        };
        return icons[status] || 'question-circle';
    },

    /**
     * 获取状态文本
     */
    getStatusText: function(status) {
        const texts = {
            'idle': '就绪',
            'starting': '启动中',
            'running': '运行中',
            'completed': '已完成',
            'failed': '失败',
            'error': '错误',
            'stopped': '已停止',
            'timeout': '超时'
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
     * 开始自动刷新
     */
    startAutoRefresh: function() {
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
        }

        this.state.updateInterval = setInterval(() => {
            if (this.state.autoRefresh) {
                this.loadScripts();
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
        return this.loadScripts();
    },

    /**
     * 更新数据
     */
    update: function(newData) {
        this.state.scripts = newData.scripts || [];
        this.render();
    },

    /**
     * 销毁脚本运行器模块
     */
    destroy: function() {
        console.log('Script Runner destroying...');
        this.stopAutoRefresh();
        // 停止所有运行中的脚本
        this.state.runningScripts.forEach((_, scriptName) => {
            this.stopScript(scriptName);
        });
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.scriptRunner = ScriptRunner;

