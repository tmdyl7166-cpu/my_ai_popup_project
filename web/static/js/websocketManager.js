/**
 * WebSocket Manager Module - WebSocket管理模块
 * 负责WebSocket连接管理和消息处理
 * 单一职责：管理WebSocket连接
 */

const WebSocketManager = {
    // 连接状态
    state: {
        connected: false,
        reconnecting: false,
        reconnectAttempts: 0,
        socket: null
    },

    // 配置
    config: {
        url: `ws://${window.location.host}/ws/monitoring`,
        maxReconnectAttempts: 5,
        reconnectInterval: 3000,
        heartbeatInterval: 30000
    },

    // 事件处理器
    handlers: {},

    /**
     * 初始化WebSocket管理器
     */
    init: function() {
        console.log('WebSocket Manager initializing...');
        this.connect();
    },

    /**
     * 连接WebSocket
     */
    connect: function() {
        if (this.state.socket && this.state.socket.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            this.state.socket = new WebSocket(this.config.url);

            this.state.socket.onopen = (event) => {
                console.log('WebSocket connected');
                this.state.connected = true;
                this.state.reconnecting = false;
                this.state.reconnectAttempts = 0;
                this.startHeartbeat();
                this.emit('connected', event);
                this.updateConnectionStatus();
            };

            this.state.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.state.socket.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                this.state.connected = false;
                this.stopHeartbeat();
                this.emit('disconnected', event);
                this.updateConnectionStatus();

                if (!this.state.reconnecting && this.state.reconnectAttempts < this.config.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };

            this.state.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.scheduleReconnect();
        }
    },

    /**
     * 断开连接
     */
    disconnect: function() {
        if (this.state.socket) {
            this.state.socket.close();
            this.state.socket = null;
        }
        this.state.connected = false;
        this.stopHeartbeat();
    },

    /**
     * 发送消息
     */
    send: function(data) {
        if (this.state.connected && this.state.socket) {
            try {
                const message = JSON.stringify(data);
                this.state.socket.send(message);
            } catch (error) {
                console.error('Failed to send WebSocket message:', error);
            }
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    },

    /**
     * 处理接收到的消息
     */
    handleMessage: function(data) {
        console.log('WebSocket message received:', data);

        // 根据消息类型分发
        if (data.type) {
            this.emit(data.type, data);
        } else {
            this.emit('message', data);
        }
    },

    /**
     * 注册事件处理器
     */
    on: function(event, handler) {
        if (!this.handlers[event]) {
            this.handlers[event] = [];
        }
        this.handlers[event].push(handler);
    },

    /**
     * 移除事件处理器
     */
    off: function(event, handler) {
        if (this.handlers[event]) {
            const index = this.handlers[event].indexOf(handler);
            if (index > -1) {
                this.handlers[event].splice(index, 1);
            }
        }
    },

    /**
     * 触发事件
     */
    emit: function(event, data) {
        if (this.handlers[event]) {
            this.handlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in ${event} handler:`, error);
                }
            });
        }
    },

    /**
     * 计划重连
     */
    scheduleReconnect: function() {
        if (this.state.reconnectAttempts >= this.config.maxReconnectAttempts) {
            console.error('Max reconnect attempts reached');
            return;
        }

        this.state.reconnecting = true;
        this.state.reconnectAttempts++;

        console.log(`Scheduling reconnect attempt ${this.state.reconnectAttempts}/${this.config.maxReconnectAttempts}`);

        setTimeout(() => {
            this.connect();
        }, this.config.reconnectInterval);
    },

    /**
     * 开始心跳
     */
    startHeartbeat: function() {
        this.heartbeatTimer = setInterval(() => {
            if (this.state.connected) {
                this.send({ type: 'heartbeat', timestamp: Date.now() });
            }
        }, this.config.heartbeatInterval);
    },

    /**
     * 停止心跳
     */
    stopHeartbeat: function() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    },

    /**
     * 更新连接状态显示
     */
    updateConnectionStatus: function() {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            const icon = statusElement.querySelector('i');
            const text = statusElement.querySelector('small');

            if (this.state.connected) {
                icon.className = 'fas fa-wifi text-success';
                text.textContent = '已连接';
            } else if (this.state.reconnecting) {
                icon.className = 'fas fa-wifi text-warning';
                text.textContent = '重连中...';
            } else {
                icon.className = 'fas fa-wifi text-danger';
                text.textContent = '已断开';
            }
        }
    },

    /**
     * 获取连接状态
     */
    getStatus: function() {
        return {
            connected: this.state.connected,
            reconnecting: this.state.reconnecting,
            attempts: this.state.reconnectAttempts
        };
    },

    /**
     * 销毁WebSocket管理器
     */
    destroy: function() {
        console.log('WebSocket Manager destroying...');
        this.disconnect();
        this.handlers = {};
    }
};

// 导出到全局
window.WebSocketManager = WebSocketManager;
