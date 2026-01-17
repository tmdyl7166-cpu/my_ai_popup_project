/**
 * Scripts Module
 * Handles script monitoring and management
 */
const ScriptsModule = {
    currentScripts: [],

    /**
     * Initialize scripts module
     */
    init() {
        console.log('ScriptsModule initialized');
        this.bindEvents();
    },

    /**
     * Bind event handlers
     */
    bindEvents() {
        // Bind tab change events
        const scriptsTab = document.getElementById('scripts-tab');
        if (scriptsTab) {
            scriptsTab.addEventListener('shown.bs.tab', () => {
                this.onTabActivated();
            });
        }
    },

    /**
     * Handle tab activation
     */
    async onTabActivated() {
        await this.loadScripts();
    },

    /**
     * Load scripts list
     */
    async loadScripts() {
        try {
            const response = await fetch('/api/scripts/list');
            const scripts = await response.json();

            this.currentScripts = scripts;
            this.renderScripts(scripts);
            this.updateLogScriptSelect(scripts);

            // Update global state
            StateManager.set('scripts', scripts);

        } catch (error) {
            console.error('Failed to load scripts:', error);
            this.showError('scripts-container', '加载脚本列表失败');
        }
    },

    /**
     * Refresh scripts
     */
    async refresh() {
        await this.loadScripts();
        NotificationsManager.success('脚本列表已刷新');
    },

    /**
     * Render scripts list
     */
    renderScripts(scripts) {
        const container = document.getElementById('scripts-container');

        if (!scripts || scripts.length === 0) {
            container.innerHTML = '<div class="alert alert-info">暂无脚本配置</div>';
            return;
        }

        const scriptCards = scripts.map(script => {
            const statusClass = this.getStatusClass(script.status);
            const statusIcon = this.getStatusIcon(script.status);

            return `
                <div class="card mb-3 card-hover">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="card-title">
                                    <i class="fas fa-terminal me-2"></i>${script.display_name}
                                </h6>
                                <p class="card-text text-muted small">${script.description}</p>
                                <div class="d-flex align-items-center">
                                    <span class="badge ${statusClass} me-2">
                                        ${statusIcon} ${script.status}
                                    </span>
                                    <small class="text-muted">
                                        频率: ${script.frequency}
                                        ${script.last_run ? ` | 上次运行: ${new Date(script.last_run * 1000).toLocaleString()}` : ''}
                                    </small>
                                </div>
                            </div>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-outline-primary" onclick="ScriptsModule.runScript('${script.name}')">
                                    <i class="fas fa-play"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-info" onclick="ScriptsModule.showDetails('${script.name}')">
                                    <i class="fas fa-info"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="ScriptsModule.viewLogs('${script.name}')">
                                    <i class="fas fa-file-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = scriptCards;
    },

    /**
     * Run script
     */
    async runScript(scriptName) {
        try {
            NotificationsManager.info(`正在启动脚本 ${scriptName}...`);

            const response = await fetch(`/api/scripts/run/${scriptName}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.status === 'started') {
                NotificationsManager.success(`脚本 ${scriptName} 已开始运行`);
                this.updateScriptStatus(scriptName, 'running');
                // Refresh after a delay
                setTimeout(() => this.loadScripts(), 2000);
            } else {
                NotificationsManager.error(`启动脚本失败: ${result.message}`);
            }

        } catch (error) {
            console.error('Failed to run script:', error);
            NotificationsManager.error('运行脚本失败');
        }
    },

    /**
     * Show script details
     */
    showDetails(scriptName) {
        const script = this.currentScripts.find(s => s.name === scriptName);
        if (!script) {
            NotificationsManager.error('脚本信息未找到');
            return;
        }

        ModalsModule.showScriptDetails(script);
    },

    /**
     * View script logs
     */
    viewLogs(scriptName) {
        // Switch to logs tab and load logs for this script
        const logsTab = document.getElementById('logs-tab');
        if (logsTab) {
            logsTab.click();
            LogsModule.loadLogsForScript(scriptName);
        }
    },

    /**
     * Update script status display
     */
    updateScriptStatus(scriptName, status) {
        const scriptCards = document.querySelectorAll('.card');
        scriptCards.forEach(card => {
            const title = card.querySelector('.card-title');
            if (title && title.textContent.includes(scriptName)) {
                const badge = card.querySelector('.badge');
                if (badge) {
                    badge.className = `badge ${this.getStatusClass(status)} me-2`;
                    badge.innerHTML = `${this.getStatusIcon(status)} ${status}`;
                }
            }
        });
    },

    /**
     * Get status CSS class
     */
    getStatusClass(status) {
        switch (status) {
            case 'running': return 'bg-primary';
            case 'completed': return 'bg-success';
            case 'failed': return 'bg-danger';
            case 'idle': return 'bg-secondary';
            default: return 'bg-warning';
        }
    },

    /**
     * Get status icon
     */
    getStatusIcon(status) {
        switch (status) {
            case 'running': return '<i class="fas fa-spinner fa-spin"></i>';
            case 'completed': return '<i class="fas fa-check"></i>';
            case 'failed': return '<i class="fas fa-times"></i>';
            case 'idle': return '<i class="fas fa-pause"></i>';
            default: return '<i class="fas fa-question"></i>';
        }
    },

    /**
     * Update log script select dropdown
     */
    updateLogScriptSelect(scripts) {
        // This will be handled by LogsModule
        if (window.LogsModule) {
            LogsModule.updateScriptSelect(scripts);
        }
    },

    /**
     * Show error message
     */
    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                </div>
            `;
        }
    }
};
