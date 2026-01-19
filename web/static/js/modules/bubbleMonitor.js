/**
 * Bubble Monitor Module - 冒泡监测模块
 * 负责功能运行状态的冒泡式实时监测和展示
 * 单一职责：状态冒泡显示和告警
 */

const BubbleMonitor = {
    // 状态
    state: {
        container: null,
        bubbles: [],
        activeBubble: null,
        updateInterval: null,
        autoRefresh: true,
        bubbleQueue: []
    },

    // 配置
    config: {
        refreshInterval: 5000, // 5秒
        maxBubbles: 10,        // 最大同时显示的冒泡数
        displayDuration: 5000, // 冒泡显示时长
        apiEndpoint: '/api/bubbles',
        bubbleTypes: {
            'success': { icon: 'check-circle', color: 'success', sound: null },
            'error': { icon: 'times-circle', color: 'danger', sound: 'error' },
            'warning': { icon: 'exclamation-triangle', color: 'warning', sound: 'warning' },
            'info': { icon: 'info-circle', color: 'info', sound: null },
            'progress': { icon: 'spinner', color: 'primary', sound: null }
        }
    },

    /**
     * 初始化冒泡监测模块
     */
    init: function() {
        console.log('Bubble Monitor initializing...');
        this.createBubbleContainer();
        this.loadBubbles();
        this.startAutoRefresh();
    },

    /**
     * 创建冒泡容器
     */
    createBubbleContainer: function() {
        let container = document.getElementById('bubbleContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'bubbleContainer';
            container.className = 'bubble-container';
            document.body.appendChild(container);
        }
        this.state.container = container;
    },

    /**
     * 加载冒泡数据
     */
    loadBubbles: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            if (!response.ok) throw new Error('Failed to fetch bubbles');

            const data = await response.json();
            const bubbles = data.bubbles || [];

            // 处理新冒泡
            this.processNewBubbles(bubbles);

        } catch (error) {
            console.error('Failed to load bubbles:', error);
            // 生成模拟冒泡数据进行演示
            this.generateDemoBubbles();
        }
    },

    /**
     * 生成演示冒泡
     */
    generateDemoBubbles: function() {
        const demoEvents = [
            { type: 'success', title: '服务启动成功', message: 'Web监控中心已启动', source: 'system' },
            { type: 'info', title: '健康检查完成', message: '所有组件状态正常', source: 'health' },
            { type: 'success', title: '数据同步完成', message: '配置已同步到所有节点', source: 'sync' },
            { type: 'warning', title: '内存使用偏高', message: '当前使用率: 78%', source: 'monitor' },
            { type: 'info', title: '新连接', message: '客户端已连接', source: 'websocket' }
        ];

        // 随机生成一个冒泡
        if (Math.random() > 0.7) {
            const event = demoEvents[Math.floor(Math.random() * demoEvents.length)];
            this.addBubble(event);
        }
    },

    /**
     * 处理新冒泡
     */
    processNewBubbles: function(newBubbles) {
        newBubbles.forEach(bubble => {
            if (!this.isDuplicate(bubble)) {
                this.addBubble(bubble);
            }
        });
    },

    /**
     * 检查是否重复
     */
    isDuplicate: function(bubble) {
        return this.state.bubbleQueue.some(
            b => b.title === bubble.title &&
                 b.message === bubble.message &&
                 b.type === bubble.type
        );
    },

    /**
     * 添加冒泡
     */
    addBubble: function(bubbleData) {
        const bubble = {
            id: `bubble-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: bubbleData.type || 'info',
            title: bubbleData.title || '通知',
            message: bubbleData.message || '',
            source: bubbleData.source || 'system',
            timestamp: new Date().toISOString(),
            duration: bubbleData.duration || this.config.displayDuration
        };

        // 添加到队列
        this.state.bubbleQueue.push(bubble);

        // 限制队列大小
        if (this.state.bubbleQueue.length > this.config.maxBubbles * 2) {
            this.state.bubbleQueue = this.state.bubbleQueue.slice(-this.config.maxBubbles);
        }

        // 显示冒泡
        this.displayBubble(bubble);

        // 播放声音（如果配置）
        this.playSound(bubble.type);
    },

    /**
     * 显示冒泡
     */
    displayBubble: function(bubble) {
        const config = this.config.bubbleTypes[bubble.type] || this.config.bubbleTypes.info;

        const bubbleHtml = `
            <div class="bubble bubble-${config.color} fade-in"
                 id="${bubble.id}"
                 data-bubble-id="${bubble.id}">
                <div class="bubble-icon">
                    <i class="fas fa-${config.icon}"></i>
                </div>
                <div class="bubble-content">
                    <div class="bubble-title">${this.escapeHtml(bubble.title)}</div>
                    <div class="bubble-message">${this.escapeHtml(bubble.message)}</div>
                    <div class="bubble-meta">
                        <small class="text-muted">${this.formatTime(bubble.timestamp)}</small>
                        <small class="text-muted ms-2">${this.escapeHtml(bubble.source)}</small>
                    </div>
                </div>
                <button class="bubble-close" onclick="bubbleMonitor.dismiss('${bubble.id}')">
                    <i class="fas fa-times"></i>
                </button>
                <div class="bubble-progress">
                    <div class="bubble-progress-bar" style="animation-duration: ${bubble.duration}ms"></div>
                </div>
            </div>
        `;

        this.state.container.insertAdjacentHTML('beforeend', bubbleHtml);

        // 自动消失
        setTimeout(() => {
            this.dismiss(bubble.id);
        }, bubble.duration);

        // 更新统计
        this.updateBubbleStats();
    },

    /**
     * 关闭冒泡
     */
    dismiss: function(bubbleId) {
        const bubble = document.getElementById(bubbleId);
        if (bubble) {
            bubble.classList.add('fade-out');
            setTimeout(() => {
                bubble.remove();
                // 从队列中移除
                this.state.bubbleQueue = this.state.bubbleQueue.filter(b => b.id !== bubbleId);
                this.updateBubbleStats();
            }, 300);
        }
    },

    /**
     * 关闭所有冒泡
     */
    dismissAll: function() {
        const bubbles = this.state.container.querySelectorAll('.bubble');
        bubbles.forEach(bubble => {
            const id = bubble.getAttribute('data-bubble-id');
            this.dismiss(id);
        });
    },

    /**
     * 播放声音
     */
    playSound: function(type) {
        const config = this.config.bubbleTypes[type];
        if (config && config.sound) {
            // 这里可以添加声音播放逻辑
            // 使用 Audio API 播放不同的提示音
            console.log(`Playing ${config.sound} sound for ${type} bubble`);
        }
    },

    /**
     * 更新冒泡统计
     */
    updateBubbleStats: function() {
        const stats = {
            total: this.state.bubbleQueue.length,
            success: this.state.bubbleQueue.filter(b => b.type === 'success').length,
            error: this.state.bubbleQueue.filter(b => b.type === 'error').length,
            warning: this.state.bubbleQueue.filter(b => b.type === 'warning').length,
            info: this.state.bubbleQueue.filter(b => b.type === 'info').length
        };

        // 更新全局状态指示器
        const statusElement = document.getElementById('bubbleStatus');
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="badge bg-${stats.error > 0 ? 'danger' : 'success'}">
                    <i class="fas fa-bell me-1"></i>
                    ${stats.total} 个通知
                </span>
            `;
        }

        // 存储统计数据
        this.state.bubbleStats = stats;
    },

    /**
     * 创建状态指示器
     */
    createStatusIndicator: function() {
        const indicator = document.createElement('div');
        indicator.id = 'bubbleStatus';
        indicator.className = 'bubble-status';
        document.querySelector('.navbar-collapse')?.appendChild(indicator);
    },

    /**
     * 格式化时间
     */
    formatTime: function(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        } catch (error) {
            return '--:--:--';
        }
    },

    /**
     * HTML转义
     */
    escapeHtml: function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * 手动添加冒泡
     */
    show: function(type, title, message, source = 'manual') {
        this.addBubble({ type, title, message, source });
    },

    /**
     * 显示成功冒泡
     */
    success: function(title, message) {
        this.show('success', title, message);
    },

    /**
     * 显示错误冒泡
     */
    error: function(title, message) {
        this.show('error', title, message);
    },

    /**
     * 显示警告冒泡
     */
    warning: function(title, message) {
        this.show('warning', title, message);
    },

    /**
     * 显示信息冒泡
     */
    info: function(title, message) {
        this.show('info', title, message);
    },

    /**
     * 显示进度冒泡
     */
    progress: function(title, message) {
        this.show('progress', title, message);
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
                this.loadBubbles();
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
        return this.loadBubbles();
    },

    /**
     * 获取冒泡历史
     */
    getHistory: function() {
        return [...this.state.bubbleQueue];
    },

    /**
     * 获取冒泡统计
     */
    getStats: function() {
        return this.state.bubbleStats || { total: 0, success: 0, error: 0, warning: 0, info: 0 };
    },

    /**
     * 销毁冒泡监测模块
     */
    destroy: function() {
        console.log('Bubble Monitor destroying...');
        this.stopAutoRefresh();
        this.dismissAll();

        // 移除容器
        if (this.state.container && this.state.container.parentNode) {
            this.state.container.parentNode.removeChild(this.state.container);
        }

        // 移除状态指示器
        const statusIndicator = document.getElementById('bubbleStatus');
        if (statusIndicator) {
            statusIndicator.remove();
        }
    }
};

// 导出到全局
window.bubbleMonitor = BubbleMonitor;

