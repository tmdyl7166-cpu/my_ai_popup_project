/**
 * Config Management Module - 配置管理模块
 * 负责配置信息的查看、编辑和管理
 * 单一职责：配置管理
 */

const ConfigManagement = {
    // 状态
    state: {
        container: null,
        configs: {},
        currentConfig: null,
        updateInterval: null,
        autoRefresh: false
    },

    // 配置
    config: {
        refreshInterval: 30000, // 30秒
        configEndpoint: '/api/config',
        updateEndpoint: '/api/config'
    },

    /**
     * 初始化配置管理模块
     */
    init: function() {
        console.log('Config Management initializing...');
        this.state.container = document.getElementById('configManagementContent');

        if (!this.state.container) {
            console.error('Config Management container not found');
            return;
        }

        this.loadConfigs();
        this.startAutoRefresh();
    },

    /**
     * 加载配置列表
     */
    loadConfigs: async function() {
        try {
            // 加载所有配置
            const configTypes = ['project', 'frontend', 'backend', 'scripts'];
            const configs = {};

            for (const type of configTypes) {
                try {
                    const response = await fetch(`${this.config.configEndpoint}/${type}`);
                    if (response.ok) {
                        configs[type] = await response.json();
                    } else {
                        configs[type] = { error: 'Failed to load config' };
                    }
                } catch (error) {
                    configs[type] = { error: error.message };
                }
            }

            this.state.configs = configs;
            this.render();
        } catch (error) {
            console.error('Failed to load configs:', error);
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
        const configs = this.state.configs;

        if (Object.keys(configs).length === 0) {
            return `
                <div class="text-center py-5">
                    <i class="fas fa-cog fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">暂无配置</h5>
                    <p class="text-muted">未找到配置文件</p>
                </div>
            `;
        }

        return `
            <div class="config-management-container">
                <!-- 配置导航 -->
                <div class="config-nav mb-4">
                    <div class="nav nav-tabs" id="configTabs" role="tablist">
                        ${this.buildConfigTabsHtml(configs)}
                    </div>
                </div>

                <!-- 配置内容 -->
                <div class="tab-content" id="configTabContent">
                    ${this.buildConfigContentHtml(configs)}
                </div>

                <!-- 配置操作面板 -->
                <div class="config-actions mt-4">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <small class="text-muted">
                                <i class="fas fa-info-circle me-1"></i>
                                修改配置后请点击保存按钮
                            </small>
                        </div>
                        <div class="action-buttons">
                            <button class="btn btn-secondary btn-sm" onclick="configManagement.reset()">
                                <i class="fas fa-undo me-1"></i>重置
                            </button>
                            <button class="btn btn-primary btn-sm" onclick="configManagement.save()">
                                <i class="fas fa-save me-1"></i>保存
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建配置标签页HTML
     */
    buildConfigTabsHtml: function(configs) {
        const tabs = Object.keys(configs).map((type, index) => `
            <button class="nav-link ${index === 0 ? 'active' : ''}"
                    id="${type}-tab"
                    data-bs-toggle="tab"
                    data-bs-target="#${type}-pane"
                    type="button"
                    role="tab"
                    aria-controls="${type}-pane"
                    aria-selected="${index === 0 ? 'true' : 'false'}">
                <i class="fas ${this.getConfigIcon(type)} me-1"></i>
                ${this.getConfigDisplayName(type)}
            </button>
        `).join('');

        return tabs;
    },

    /**
     * 构建配置内容HTML
     */
    buildConfigContentHtml: function(configs) {
        const contents = Object.entries(configs).map(([type, config], index) => `
            <div class="tab-pane fade ${index === 0 ? 'show active' : ''}"
                 id="${type}-pane"
                 role="tabpanel"
                 aria-labelledby="${type}-tab"
                 tabindex="0">
                <div class="config-editor">
                    ${this.buildConfigEditorHtml(type, config)}
                </div>
            </div>
        `).join('');

        return contents;
    },

    /**
     * 构建配置编辑器HTML
     */
    buildConfigEditorHtml: function(type, config) {
        if (config.error) {
            return `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    加载配置失败: ${config.error}
                </div>
            `;
        }

        // JSON 编辑器
        return `
            <div class="config-json-editor">
                <div class="editor-header mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-code me-2"></i>JSON 配置编辑器
                        </h6>
                        <div class="editor-actions">
                            <button class="btn btn-sm btn-outline-secondary" onclick="configManagement.formatJson('${type}')">
                                <i class="fas fa-magic me-1"></i>格式化
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="configManagement.validateJson('${type}')">
                                <i class="fas fa-check me-1"></i>验证
                            </button>
                        </div>
                    </div>
                </div>
                <div class="editor-content">
                    <textarea class="form-control config-textarea"
                              id="config-editor-${type}"
                              rows="20"
                              spellcheck="false">${JSON.stringify(config, null, 2)}</textarea>
                </div>
                <div class="editor-footer mt-3">
                    <div class="validation-result" id="validation-${type}"></div>
                </div>
            </div>
        `;
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 配置内容变化监听
        const textareas = this.state.container.querySelectorAll('.config-textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', (event) => {
                this.markConfigChanged(event.target.id.replace('config-editor-', ''));
            });
        });

        // 标签页切换事件
        const tabs = this.state.container.querySelectorAll('[data-bs-toggle="tab"]');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (event) => {
                const targetType = event.target.id.replace('-tab', '');
                this.state.currentConfig = targetType;
            });
        });
    },

    /**
     * 标记配置已修改
     */
    markConfigChanged: function(type) {
        const tab = this.state.container.querySelector(`#${type}-tab`);
        if (tab && !tab.classList.contains('text-warning')) {
            tab.classList.add('text-warning');
            tab.innerHTML += ' <i class="fas fa-circle text-warning"></i>';
        }
    },

    /**
     * 保存配置
     */
    save: async function() {
        if (!this.state.currentConfig) {
            Notifications.show('保存失败', '请先选择要保存的配置', 'warning');
            return;
        }

        const textarea = document.getElementById(`config-editor-${this.state.currentConfig}`);
        if (!textarea) {
            Notifications.show('保存失败', '找不到配置编辑器', 'error');
            return;
        }

        try {
            const configData = JSON.parse(textarea.value);

            const response = await fetch(`${this.config.updateEndpoint}/${this.state.currentConfig}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configData)
            });

            if (!response.ok) throw new Error('Failed to save config');

            const result = await response.json();

            // 移除修改标记
            const tab = this.state.container.querySelector(`#${this.state.currentConfig}-tab`);
            if (tab) {
                tab.classList.remove('text-warning');
                const icon = tab.querySelector('.fa-circle');
                if (icon) icon.remove();
            }

            Notifications.show('保存成功', `配置 ${this.getConfigDisplayName(this.state.currentConfig)} 已保存`, 'success');

        } catch (error) {
            console.error('Failed to save config:', error);
            if (error instanceof SyntaxError) {
                Notifications.show('保存失败', 'JSON 格式错误，请检查语法', 'error');
            } else {
                Notifications.show('保存失败', error.message, 'error');
            }
        }
    },

    /**
     * 重置配置
     */
    reset: function() {
        ModalManager.confirm({
            title: '确认重置',
            content: '这将放弃所有未保存的修改，恢复到最后保存的配置。确定要继续吗？',
            onConfirm: () => {
                this.loadConfigs();
                Notifications.show('已重置', '配置已恢复到最后保存的状态', 'info');
            }
        });
    },

    /**
     * 格式化JSON
     */
    formatJson: function(type) {
        const textarea = document.getElementById(`config-editor-${type}`);
        if (!textarea) return;

        try {
            const parsed = JSON.parse(textarea.value);
            textarea.value = JSON.stringify(parsed, null, 2);
            this.clearValidation(type);
        } catch (error) {
            this.showValidationError(type, 'JSON 格式错误，无法格式化');
        }
    },

    /**
     * 验证JSON
     */
    validateJson: function(type) {
        const textarea = document.getElementById(`config-editor-${type}`);
        if (!textarea) return;

        try {
            JSON.parse(textarea.value);
            this.showValidationSuccess(type, 'JSON 格式正确');
        } catch (error) {
            this.showValidationError(type, `JSON 格式错误: ${error.message}`);
        }
    },

    /**
     * 显示验证成功
     */
    showValidationSuccess: function(type, message) {
        const validationDiv = document.getElementById(`validation-${type}`);
        if (validationDiv) {
            validationDiv.innerHTML = `
                <div class="alert alert-success py-2">
                    <i class="fas fa-check me-1"></i>${message}
                </div>
            `;
        }
    },

    /**
     * 显示验证错误
     */
    showValidationError: function(type, message) {
        const validationDiv = document.getElementById(`validation-${type}`);
        if (validationDiv) {
            validationDiv.innerHTML = `
                <div class="alert alert-danger py-2">
                    <i class="fas fa-exclamation-triangle me-1"></i>${message}
                </div>
            `;
        }
    },

    /**
     * 清除验证结果
     */
    clearValidation: function(type) {
        const validationDiv = document.getElementById(`validation-${type}`);
        if (validationDiv) {
            validationDiv.innerHTML = '';
        }
    },

    /**
     * 获取配置图标
     */
    getConfigIcon: function(type) {
        const icons = {
            'project': 'fa-project-diagram',
            'frontend': 'fa-desktop',
            'backend': 'fa-server',
            'scripts': 'fa-terminal'
        };
        return icons[type] || 'fa-cog';
    },

    /**
     * 获取配置显示名称
     */
    getConfigDisplayName: function(type) {
        const names = {
            'project': '项目配置',
            'frontend': '前端配置',
            'backend': '后端配置',
            'scripts': '脚本配置'
        };
        return names[type] || type;
    },

    /**
     * 显示错误
     */
    showError: function(message) {
        this.state.container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                加载配置失败: ${message}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="configManagement.refresh()">
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
                this.loadConfigs();
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
        return this.loadConfigs();
    },

    /**
     * 更新数据
     */
    update: function(newData) {
        // 这里可以实现配置更新逻辑
        this.loadConfigs();
    },

    /**
     * 销毁配置管理模块
     */
    destroy: function() {
        console.log('Config Management destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.configManagement = ConfigManagement;
