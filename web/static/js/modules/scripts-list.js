/**
 * 脚本列表模块
 * 功能: 获取所有可用脚本的列表
 * API: GET /api/scripts/list
 */

class ScriptsListModule {
    constructor(api) {
        this.api = api;
        this.isActive = false;
        this.scripts = [];
        this.onScriptsUpdated = null;
    }

    /**
     * 初始化模块
     */
    init() {
        this.isActive = true;
        console.log('[ScriptsListModule] 初始化完成');
    }

    /**
     * 获取脚本列表
     * @returns {Promise<Array>} 脚本列表
     */
    async fetch() {
        try {
            const response = await this.api.get('/api/scripts/list');
            this.scripts = response.scripts || [];
            if (this.onScriptsUpdated) {
                this.onScriptsUpdated(this.scripts);
            }
            return this.scripts;
        } catch (error) {
            console.error('[ScriptsListModule] 获取脚本列表失败:', error);
            this.scripts = [];
            return this.scripts;
        }
    }

    /**
     * 根据名称查找脚本
     * @param {string} name - 脚本名称
     * @returns {Object|null}
     */
    findByName(name) {
        return this.scripts.find(s => s.name === name) || null;
    }

    /**
     * 获取脚本显示名称
     * @param {Object} script - 脚本对象
     * @returns {string}
     */
    getDisplayName(script) {
        return script.display_name || script.name || '未命名脚本';
    }

    /**
     * 获取脚本描述
     * @param {Object} script - 脚本对象
     * @returns {string}
     */
    getDescription(script) {
        return script.description || '暂无描述';
    }

    /**
     * 获取脚本状态
     * @param {Object} script - 脚本对象
     * @returns {string}
     */
    getStatus(script) {
        return script.status || 'unknown';
    }

    /**
     * 获取状态显示文本
     * @param {string} status - 状态值
     * @returns {string}
     */
    getStatusText(status) {
        const textMap = {
            'running': '运行中',
            'completed': '已完成',
            'failed': '失败',
            'idle': '空闲',
            'stopped': '已停止',
            'pending': '等待中',
            'unknown': '未知'
        };
        return textMap[status] || status || '未知';
    }

    /**
     * 获取状态图标
     * @param {string} status - 状态值
     * @returns {string}
     */
    getStatusIcon(status) {
        const iconMap = {
            'running': '🔄',
            'completed': '✅',
            'failed': '❌',
            'idle': '⏸️',
            'stopped': '🛑',
            'pending': '⏳',
            'unknown': '❓'
        };
        return iconMap[status] || '❓';
    }

    /**
     * 获取状态颜色类
     * @param {string} status - 状态值
     * @returns {string}
     */
    getStatusClass(status) {
        const classMap = {
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'idle': 'secondary',
            'stopped': 'warning',
            'pending': 'info'
        };
        return classMap[status] || 'secondary';
    }

    /**
     * 渲染脚本列表到 DOM
     * @param {string} containerId - 容器元素 ID
     */
    render(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[ScriptsListModule] 容器 ${containerId} 不存在`);
            return;
        }

        if (this.scripts.length === 0) {
            container.innerHTML = '<div class="no-scripts">暂无脚本</div>';
            return;
        }

        let html = '<div class="scripts-list">';
        this.scripts.forEach(script => {
            html += this.renderScriptItem(script);
        });
        html += '</div>';
        container.innerHTML = html;
    }

    /**
     * 渲染单个脚本项
     * @param {Object} script - 脚本对象
     * @returns {string}
     */
    renderScriptItem(script) {
        const name = this.getDisplayName(script);
        const description = this.getDescription(script);
        const status = this.getStatus(script);
        const statusText = this.getStatusText(status);
        const statusIcon = this.getStatusIcon(status);
        const statusClass = this.getStatusClass(status);
        const lastRun = script.last_run || '从未运行';
        const frequency = script.frequency || '按需';

        return `
            <div class="script-item" data-script="${this.escapeHtml(script.name)}">
                <div class="script-header">
                    <span class="script-icon">${statusIcon}</span>
                    <span class="script-name">${this.escapeHtml(name)}</span>
                    <span class="badge badge-${statusClass}">${statusText}</span>
                </div>
                <div class="script-info">
                    <div class="script-description">${this.escapeHtml(description)}</div>
                    <div class="script-meta">
                        <span class="meta-item">最后运行: ${this.escapeHtml(lastRun)}</span>
                        <span class="meta-item">频率: ${this.escapeHtml(frequency)}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 渲染脚本表格到 DOM
     * @param {string} containerId - 容器元素 ID
     */
    renderTable(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[ScriptsListModule] 容器 ${containerId} 不存在`);
            return;
        }

        if (this.scripts.length === 0) {
            container.innerHTML = '<div class="no-scripts">暂无脚本</div>';
            return;
        }

        let html = `
            <table class="scripts-table">
                <thead>
                    <tr>
                        <th>状态</th>
                        <th>脚本名称</th>
                        <th>描述</th>
                        <th>执行频率</th>
                        <th>最后运行</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
        `;

        this.scripts.forEach(script => {
            html += `
                <tr data-script="${this.escapeHtml(script.name)}">
                    <td>
                        <span class="status-badge badge-${this.getStatusClass(script.status)}">
                            ${this.getStatusIcon(script.status)} ${this.getStatusText(script.status)}
                        </span>
                    </td>
                    <td>${this.escapeHtml(this.getDisplayName(script))}</td>
                    <td>${this.escapeHtml(this.getDescription(script))}</td>
                    <td>${this.escapeHtml(script.frequency || '按需')}</td>
                    <td>${this.escapeHtml(script.last_run || '从未运行')}</td>
                    <td class="script-actions">
                        <button class="btn-run btn-sm" data-action="run" data-script="${this.escapeHtml(script.name)}">
                            运行
                        </button>
                        <button class="btn-stop btn-sm" data-action="stop" data-script="${this.escapeHtml(script.name)}">
                            停止
                        </button>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    /**
     * HTML 转义
     * @param {string} text - 原始文本
     * @returns {string}
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 销毁模块
     */
    destroy() {
        this.isActive = false;
        this.scripts = [];
        this.onScriptsUpdated = null;
        console.log('[ScriptsListModule] 已销毁');
    }
}

// 导出模块
window.ScriptsListModule = ScriptsListModule;

