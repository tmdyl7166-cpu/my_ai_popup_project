/**
 * 健康检查模块
 * 功能: 检查 Web 服务健康状态
 * API: GET /api/health
 */

class HealthModule {
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
        console.log('[HealthModule] 初始化完成');
    }

    /**
     * 执行健康检查
     * @returns {Promise<Object>} 健康状态
     */
    async check() {
        try {
            const response = await this.api.get('/api/health');
            this.status = response;
            return response;
        } catch (error) {
            console.error('[HealthModule] 健康检查失败:', error);
            this.status = { status: 'error', message: error.message };
            return this.status;
        }
    }

    /**
     * 获取当前状态
     * @returns {Object|null}
     */
    getStatus() {
        return this.status;
    }

    /**
     * 检查是否健康
     * @returns {boolean}
     */
    isHealthy() {
        return this.status?.status === 'healthy';
    }

    /**
     * 获取状态显示文本
     * @returns {string}
     */
    getStatusText() {
        const statusMap = {
            'healthy': '健康',
            'warning': '警告',
            'error': '错误',
            null: '未知'
        };
        return statusMap[this.status?.status] || '未知';
    }

    /**
     * 获取状态图标
     * @returns {string}
     */
    getStatusIcon() {
        const iconMap = {
            'healthy': '✅',
            'warning': '⚠️',
            'error': '❌'
        };
        return iconMap[this.status?.status] || '❓';
    }

    /**
     * 渲染状态到 DOM
     * @param {string} containerId - 容器元素 ID
     */
    render(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[HealthModule] 容器 ${containerId} 不存在`);
            return;
        }

        const status = this.status || { status: 'unknown', timestamp: new Date().toISOString() };
        
        container.innerHTML = `
            <div class="health-status" data-status="${status.status}">
                <div class="status-icon">${this.getStatusIcon()}</div>
                <div class="status-info">
                    <div class="status-label">服务状态</div>
                    <div class="status-value">${this.getStatusText()}</div>
                    <div class="status-time">${status.timestamp || 'N/A'}</div>
                </div>
            </div>
        `;
    }

    /**
     * 销毁模块
     */
    destroy() {
        this.isActive = false;
        this.status = null;
        console.log('[HealthModule] 已销毁');
    }
}

// 导出模块
window.HealthModule = HealthModule;

