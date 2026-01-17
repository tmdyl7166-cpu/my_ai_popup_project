/**
 * Config Module
 * Handles configuration management
 */
const ConfigModule = {
    currentConfig: null,

    /**
     * Initialize config module
     */
    init() {
        console.log('ConfigModule initialized');
        this.bindEvents();
    },

    /**
     * Bind event handlers
     */
    bindEvents() {
        // Bind tab change events
        const configTab = document.getElementById('config-tab');
        if (configTab) {
            configTab.addEventListener('shown.bs.tab', () => {
                this.onTabActivated();
            });
        }
    },

    /**
     * Handle tab activation
     */
    async onTabActivated() {
        await this.loadConfigList();
    },

    /**
     * Load configuration list
     */
    async loadConfigList() {
        const configList = [
            { id: 'project', name: '项目配置', icon: 'fas fa-project-diagram' },
            { id: 'frontend', name: '前端配置', icon: 'fas fa-desktop' },
            { id: 'backend', name: '后端配置', icon: 'fas fa-server' },
            { id: 'scripts', name: '脚本配置', icon: 'fas fa-terminal' },
            { id: 'ai', name: 'AI配置', icon: 'fas fa-brain' },
            { id: 'processing', name: '处理配置', icon: 'fas fa-cogs' }
        ];

        this.renderConfigList(configList);

        // Load default config (project)
        await this.loadConfig('project');
    },

    /**
     * Render configuration list
     */
    renderConfigList(configs) {
        const container = document.getElementById('config-list');

        const configItems = configs.map(config => `
            <a href="#" class="list-group-item list-group-item-action" onclick="ConfigModule.loadConfig('${config.id}')">
                <i class="${config.icon} me-2"></i>${config.name}
            </a>
        `).join('');

        container.innerHTML = configItems;
    },

    /**
     * Load specific configuration
     */
    async loadConfig(component) {
        try {
            // Update active state
            this.updateActiveConfig(component);

            const response = await fetch(`/api/config/${component}`);
            const config = await response.json();

            this.currentConfig = config;
            this.renderConfigEditor(component, config);

            // Update global state
            StateManager.set(`config.${component}`, config);

        } catch (error) {
            console.error('Failed to load config:', error);
            this.showConfigError('加载配置失败');
        }
    },

    /**
     * Render configuration editor
     */
    renderConfigEditor(component, config) {
        const container = document.getElementById('config-editor');

        if (config.error) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${config.error}
                </div>
            `;
            return;
        }

        const formattedJson = JSON.stringify(config, null, 2);

        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6>${component} 配置</h6>
                <div>
                    <button class="btn btn-sm btn-outline-primary me-2" onclick="ConfigModule.editConfig('${component}')">
                        <i class="fas fa-edit me-1"></i>编辑
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="ConfigModule.saveConfig('${component}')">
                        <i class="fas fa-save me-1"></i>保存
                    </button>
                </div>
            </div>
            <pre class="bg-light p-3 rounded" id="config-json-viewer" style="max-height: 500px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 0.85em;">${this.escapeHtml(formattedJson)}</pre>
        `;
    },

    /**
     * Update active configuration in list
     */
    updateActiveConfig(activeComponent) {
        const items = document.querySelectorAll('#config-list .list-group-item');
        items.forEach(item => {
            item.classList.remove('active');
            if (item.onclick.toString().includes(activeComponent)) {
                item.classList.add('active');
            }
        });
    },

    /**
     * Edit configuration
     */
    editConfig(component) {
        const jsonViewer = document.getElementById('config-json-viewer');
        if (!jsonViewer) return;

        const currentJson = jsonViewer.textContent;
        jsonViewer.innerHTML = `
            <textarea class="form-control" id="config-editor-textarea" rows="20" style="font-family: 'Courier New', monospace; font-size: 0.85em;">${currentJson}</textarea>
        `;

        // Focus on textarea
        const textarea = document.getElementById('config-editor-textarea');
        if (textarea) {
            textarea.focus();
        }
    },

    /**
     * Save configuration
     */
    async saveConfig(component) {
        const textarea = document.getElementById('config-editor-textarea');
        if (!textarea) {
            NotificationsManager.warning('请先进入编辑模式');
            return;
        }

        try {
            const newConfig = JSON.parse(textarea.value);

            const response = await fetch(`/api/config/${component}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newConfig)
            });

            const result = await response.json();

            if (result.success) {
                NotificationsManager.success('配置保存成功');
                this.currentConfig = newConfig;
                this.renderConfigEditor(component, newConfig);
            } else {
                NotificationsManager.error('配置保存失败: ' + (result.message || '未知错误'));
            }

        } catch (error) {
            if (error instanceof SyntaxError) {
                NotificationsManager.error('JSON格式错误，请检查配置内容');
            } else {
                console.error('Failed to save config:', error);
                NotificationsManager.error('保存配置失败');
            }
        }
    },

    /**
     * Refresh configuration
     */
    async refresh() {
        if (this.currentConfig) {
            await this.loadConfigList();
            NotificationsManager.success('配置列表已刷新');
        }
    },

    /**
     * Show configuration error
     */
    showConfigError(message) {
        const container = document.getElementById('config-editor');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                </div>
            `;
        }
    },

    /**
     * Escape HTML content
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
