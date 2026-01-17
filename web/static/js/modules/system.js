/**
 * 系统资源模块
 * 功能: 获取系统资源使用情况 (CPU、内存、磁盘)
 * API: GET /api/system/resources
 */

class SystemResourcesModule {
    constructor(api) {
        this.api = api;
        this.isActive = false;
        this.data = null;
        this.history = {
            cpu: [],
            memory: [],
            timestamps: []
        };
        this.maxHistoryPoints = 20;
        this.intervalId = null;
    }

    /**
     * 初始化模块
     */
    init() {
        this.isActive = true;
        console.log('[SystemResourcesModule] 初始化完成');
    }

    /**
     * 获取系统资源数据
     * @returns {Promise<Object>} 资源数据
     */
    async fetch() {
        try {
            const response = await this.api.get('/api/system/resources');
            this.data = response;
            this.updateHistory(response);
            return response;
        } catch (error) {
            console.error('[SystemResourcesModule] 获取资源数据失败:', error);
            this.data = { error: error.message };
            return this.data;
        }
    }

    /**
     * 更新历史数据
     * @param {Object} data - 资源数据
     */
    updateHistory(data) {
        if (data.error) return;

        const now = new Date();
        const timeStr = now.toLocaleTimeString();

        this.history.timestamps.push(timeStr);
        this.history.cpu.push(data.cpu_percent);
        this.history.memory.push(data.memory?.percent || 0);

        // 限制历史点数量
        if (this.history.timestamps.length > this.maxHistoryPoints) {
            this.history.timestamps.shift();
            this.history.cpu.shift();
            this.history.memory.shift();
        }
    }

    /**
     * 启动自动刷新
     * @param {number} interval - 刷新间隔 (毫秒)
     */
    startAutoRefresh(interval = 5000) {
        this.stopAutoRefresh();
        this.intervalId = setInterval(() => this.fetch(), interval);
        console.log('[SystemResourcesModule] 启动自动刷新');
    }

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            console.log('[SystemResourcesModule] 停止自动刷新');
        }
    }

    /**
     * 获取 CPU 使用率
     * @returns {number}
     */
    getCpuPercent() {
        return this.data?.cpu_percent || 0;
    }

    /**
     * 获取内存使用率
     * @returns {number}
     */
    getMemoryPercent() {
        return this.data?.memory?.percent || 0;
    }

    /**
     * 获取磁盘使用率
     * @returns {number}
     */
    getDiskPercent() {
        return this.data?.disk?.percent || 0;
    }

    /**
     * 获取历史数据
     * @returns {Object}
     */
    getHistory() {
        return { ...this.history };
    }

    /**
     * 渲染资源卡片到 DOM
     * @param {string} containerId - 容器元素 ID
     */
    renderCards(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[SystemResourcesModule] 容器 ${containerId} 不存在`);
            return;
        }

        const data = this.data || { 
            cpu_percent: 0, 
            memory: { percent: 0 }, 
            disk: { percent: 0 } 
        };

        container.innerHTML = `
            <div class="resource-cards">
                ${this.renderResourceCard('cpu', 'CPU 使用率', data.cpu_percent, '%', 'primary')}
                ${this.renderResourceCard('memory', '内存使用率', data.memory?.percent || 0, '%', 'success')}
                ${this.renderResourceCard('disk', '磁盘使用率', data.disk?.percent || 0, '%', 'warning')}
            </div>
        `;
    }

    /**
     * 渲染单个资源卡片
     * @param {string} id - 资源 ID
     * @param {string} label - 标签
     * @param {number} value - 值
     * @param {string} unit - 单位
     * @param {string} type - 类型 (primary, success, warning, danger)
     * @returns {string}
     */
    renderResourceCard(id, label, value, unit, type) {
        const percent = Math.min(100, Math.max(0, value));
        const colorClass = this.getColorClass(percent, type);
        
        return `
            <div class="resource-card resource-${id}">
                <div class="resource-header">
                    <span class="resource-label">${this.escapeHtml(label)}</span>
                    <span class="resource-value">${value.toFixed(1)}${unit}</span>
                </div>
                <div class="progress">
                    <div class="progress-bar bg-${colorClass}" 
                         style="width: ${percent}%" 
                         role="progressbar">
                    </div>
                </div>
                <div class="resource-details">
                    ${this.getResourceDetails(id)}
                </div>
            </div>
        `;
    }

    /**
     * 获取资源详细信息
     * @param {string} id - 资源 ID
     * @returns {string}
     */
    getResourceDetails(id) {
        if (!this.data || this.data.error) return '';

        if (id === 'memory' && this.data.memory) {
            const used = this.formatBytes(this.data.memory.used || 0);
            const total = this.formatBytes(this.data.memory.total || 0);
            return `<small>${used} / ${total}</small>`;
        }

        if (id === 'disk' && this.data.disk) {
            const used = this.formatBytes(this.data.disk.used || 0);
            const total = this.formatBytes(this.data.disk.total || 0);
            return `<small>${used} / ${total}</small>`;
        }

        return '';
    }

    /**
     * 根据百分比获取颜色类
     * @param {number} percent - 百分比
     * @param {string} defaultType - 默认类型
     * @returns {string}
     */
    getColorClass(percent, defaultType) {
        if (percent >= 90) return 'danger';
        if (percent >= 70) return 'warning';
        if (percent >= 50) return 'info';
        return defaultType || 'success';
    }

    /**
     * 格式化字节数
     * @param {number} bytes - 字节数
     * @returns {string}
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
        this.stopAutoRefresh();
        this.isActive = false;
        this.data = null;
        this.history = { cpu: [], memory: [], timestamps: [] };
        console.log('[SystemResourcesModule] 已销毁');
    }
}

// 导出模块
window.SystemResourcesModule = SystemResourcesModule;

