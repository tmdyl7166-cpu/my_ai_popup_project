/**
 * 监控管理器 - 实时监控自动轮询
 * 实现前后端热交互的监控功能
 */

class MonitorManager {
    constructor() {
        this.isRunning = false;
        this.pollingInterval = 5000; // 默认5秒轮询
        this.maxRetries = 3;
        this.retryCount = 0;
        this.websocket = null;
        this.lastUpdate = null;
        this.updateCallbacks = [];
        this.statusCallbacks = [];
        this.errorCallbacks = [];
        
        this.init();
    }
    
    init() {
        // 从配置读取轮询间隔
        const config = window.AppConfig?.monitoring?.polling || {};
        this.pollingInterval = config.interval || 5000;
        this.maxRetries = config.maxRetries || 3;
    }
    
    /**
     * 启动监控
     */
    start() {
        if (this.isRunning) {
            console.warn('监控已在运行中');
            return;
        }
        
        this.isRunning = true;
        this.retryCount = 0;
        console.log('监控管理器已启动');
        
        // 启动WebSocket连接
        this.connectWebSocket();
        
        // 启动轮询
        this.startPolling();
        
        // 通知状态变化
        this._notifyStatusChange('running');
    }
    
    /**
     * 停止监控
     */
    stop() {
        if (!this.isRunning) {
            return;
        }
        
        this.isRunning = false;
        
        // 停止轮询
        this.stopPolling();
        
        // 关闭WebSocket
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        console.log('监控管理器已停止');
        this._notifyStatusChange('stopped');
    }
    
    /**
     * 连接WebSocket
     */
    connectWebSocket() {
        const wsUrl = this._getWebSocketUrl();
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = (event) => {
                console.log('WebSocket连接已建立');
                this.retryCount = 0;
                this._notifyStatusChange('connected');
                
                // 发送订阅请求
                this._sendMessage({
                    action: 'subscribe',
                    channels: ['status', 'scripts', 'system', 'deployment']
                });
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this._handleWebSocketMessage(data);
                } catch (e) {
                    console.error('解析WebSocket消息失败:', e);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('WebSocket连接已关闭:', event.code, event.reason);
                
                if (this.isRunning) {
                    // 尝试重新连接
                    setTimeout(() => this.connectWebSocket(), 5000);
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this._notifyError('websocket_error', error);
            };
            
        } catch (e) {
            console.error('创建WebSocket连接失败:', e);
            this._notifyError('websocket_connection_failed', e);
        }
    }
    
    /**
     * 启动轮询
     */
    startPolling() {
        this._pollingTimer = setInterval(() => {
            this._performPoll();
        }, this.pollingInterval);
        
        // 立即执行一次
        this._performPoll();
    }
    
    /**
     * 停止轮询
     */
    stopPolling() {
        if (this._pollingTimer) {
            clearInterval(this._pollingTimer);
            this._pollingTimer = null;
        }
    }
    
    /**
     * 执行轮询
     */
    async _performPoll() {
        try {
            // 获取系统资源
            await this._pollSystemResources();
            
            // 获取脚本状态
            await this._pollScriptsStatus();
            
            // 获取部署进度
            await this._pollDeploymentProgress();
            
            // 获取项目状态
            await this._pollProjectStatus();
            
            this.retryCount = 0;
            this.lastUpdate = new Date();
            this._notifyUpdate();
            
        } catch (e) {
            console.error('轮询执行失败:', e);
            this.retryCount++;
            
            if (this.retryCount >= this.maxRetries) {
                this._notifyError('polling_failed', e);
                this.retryCount = 0;
            }
        }
    }
    
    /**
     * 轮询系统资源
     */
    async _pollSystemResources() {
        try {
            const response = await fetch('/api/system/resources');
            if (response.ok) {
                const data = await response.json();
                window.AppState.systemResources = data;
            }
        } catch (e) {
            console.warn('获取系统资源失败:', e);
        }
    }
    
    /**
     * 轮询脚本状态
     */
    async _pollScriptsStatus() {
        try {
            const response = await fetch('/api/scripts/status');
            if (response.ok) {
                const data = await response.json();
                window.AppState.scriptsStatus = data;
            }
        } catch (e) {
            console.warn('获取脚本状态失败:', e);
        }
    }
    
    /**
     * 轮询部署进度
     */
    async _pollDeploymentProgress() {
        try {
            const response = await fetch('/api/deployment/progress');
            if (response.ok) {
                const data = await response.json();
                window.AppState.deploymentProgress = data;
            }
        } catch (e) {
            console.warn('获取部署进度失败:', e);
        }
    }
    
    /**
     * 轮询项目状态
     */
    async _pollProjectStatus() {
        try {
            const response = await fetch('/api/project/status');
            if (response.ok) {
                const data = await response.json();
                window.AppState.projectStatus = data;
            }
        } catch (e) {
            console.warn('获取项目状态失败:', e);
        }
    }
    
    /**
     * 处理WebSocket消息
     */
    _handleWebSocketMessage(data) {
        const { type, payload } = data;
        
        switch (type) {
            case 'status_update':
                window.AppState.scriptsStatus = payload;
                this._notifyUpdate();
                break;
                
            case 'script_result':
            case 'script_completed':
                // 刷新脚本列表
                this._pollScriptsStatus();
                this._notifyUpdate();
                break;
                
            case 'script_error':
                this._notifyError('script_error', payload);
                break;
                
            case 'deployment_update':
                window.AppState.deploymentProgress = payload;
                this._notifyUpdate();
                break;
                
            case 'system_alert':
                this._notifyError('system_alert', payload);
                break;
                
            default:
                console.log('未知消息类型:', type);
        }
    }
    
    /**
     * 获取WebSocket URL
     */
    _getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/monitoring`;
    }
    
    /**
     * 发送WebSocket消息
     */
    _sendMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }
    
    /**
     * 注册更新回调
     */
    onUpdate(callback) {
        this.updateCallbacks.push(callback);
    }
    
    /**
     * 注册状态变化回调
     */
    onStatusChange(callback) {
        this.statusCallbacks.push(callback);
    }
    
    /**
     * 注册错误回调
     */
    onError(callback) {
        this.errorCallbacks.push(callback);
    }
    
    /**
     * 通知更新
     */
    _notifyUpdate() {
        const data = {
            timestamp: new Date(),
            lastUpdate: this.lastUpdate,
            systemResources: window.AppState.systemResources,
            scriptsStatus: window.AppState.scriptsStatus,
            deploymentProgress: window.AppState.deploymentProgress
        };
        
        this.updateCallbacks.forEach(callback => {
            try {
                callback(data);
            } catch (e) {
                console.error('更新回调执行失败:', e);
            }
        });
    }
    
    /**
     * 通知状态变化
     */
    _notifyStatusChange(status) {
        this.statusCallbacks.forEach(callback => {
            try {
                callback(status);
            } catch (e) {
                console.error('状态回调执行失败:', e);
            }
        });
    }
    
    /**
     * 通知错误
     */
    _notifyError(type, error) {
        const data = {
            type,
            error,
            timestamp: new Date()
        };
        
        this.errorCallbacks.forEach(callback => {
            try {
                callback(data);
            } catch (e) {
                console.error('错误回调执行失败:', e);
            }
        });
    }
    
    /**
     * 获取监控状态
     */
    getStatus() {
        return {
            isRunning: this.isRunning,
            pollingInterval: this.pollingInterval,
            lastUpdate: this.lastUpdate,
            retryCount: this.retryCount
        };
    }
}

// 导出到全局
window.MonitorManager = MonitorManager;

