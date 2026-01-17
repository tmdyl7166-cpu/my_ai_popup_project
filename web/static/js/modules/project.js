/**
 * 项目状态模块
 * 功能: 获取项目整体运行状态
 * API: GET /api/project/status
 */

class ProjectModule {
    constructor(api) {
        this.api = api;
        this.isActive = false;
        this.status = null;
    }

    /**
     * 初始化模块
     */
    init() {
        this.isActive = true;
        console.log('[ProjectModule] 初始化完成');
    }

    /**
     * 获取项目状态
     * @returns {Promise<Object>} 项目状态
     */
    async getStatus() {
        try {
            const response = await this.api.get('/api/project/status');
            this.status = response;
            return response;
        } catch (error) {
            console.error('[ProjectModule] 获取状态失败:', error);
            this.status = { error: error.message };
            return this.status;
        }
    }

    /**
     * 获取项目名称
     * @returns {string}
     */
    getName() {
        return this.status?.project_name || '未知项目';
    }

    /**
     * 获取版本号
     * @returns {string}
     */
    getVersion() {
        return this.status?.version || 'v0.0.0';
    }

    /**
     * 获取整体状态
     * @returns {string}
     */
    getOverallStatus() {
        return this.status?.status || 'unknown';
    }

    /**
     * 获取组件状态
     * @returns {Object}
     */
    getComponents() {
        return this.status?.components || {};
    }

    /**
     * 渲染项目信息到 DOM
     * @param {string} containerId - 容器元素 ID
     */
    render(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[ProjectModule] 容器 ${containerId} 不存在`);
            return;
        }

        const status = this.status || { 
            project_name: '加载中...', 
            version: 'v0.0.0',
            status: 'loading',
            last_updated: null
        };

        container.innerHTML = `
            <div class="project-info">
                <div class="project-header">
                    <h2 class="project-name">${this.escapeHtml(status.project_name)}</h2>
                    <span class="project-version badge badge-info">${this.escapeHtml(status.version)}</span>
                </div>
                <div class="project-status">
                    <span class="status-indicator status-${status.status}"></span>
                    <span class="status-text">${this.getStatusText(status.status)}</span>
                </div>
                <div class="project-timestamp">
                    最后更新: ${status.last_updated || 'N/A'}
                </div>
                <div class="project-components">
                    ${this.renderComponents(status.components)}
                </div>
            </div>
        `;
    }

    /**
     * 渲染组件状态
     * @param {Object} components - 组件状态
     * @returns {string}
     */
    renderComponents(components) {
        if (!components || Object.keys(components).length === 0) {
            return '<div class="no-components">暂无组件信息</div>';
        }

        let html = '<div class="components-grid">';
        Object.entries(components).forEach(([name, info]) => {
            html += `
                <div class="component-card">
                    <div class="component-name">${this.escapeHtml(name)}</div>
                    <div class="component-status status-${info.status || 'unknown'}">
                        ${this.getStatusText(info.status)}
                    </div>
                    ${info.message ? `<div class="component-message">${this.escapeHtml(info.message)}</div>` : ''}
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    /**
     * 获取状态显示文本
     * @param {string} status - 状态值
     * @returns {string}
     */
    getStatusText(status) {
        const textMap = {
            'running': '运行中',
            'stopped': '已停止',
            'error': '错误',
            'warning': '警告',
            'loading': '加载中',
            'healthy': '健康',
            'unknown': '未知'
        };
        return textMap[status] || status || '未知';
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
        this.status = null;
        console.log('[ProjectModule] 已销毁');
    }
}

// 导出模块
window.ProjectModule = ProjectModule;

