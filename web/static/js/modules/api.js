/**
 * API通信模块
 * 负责所有与后端API的通信、请求处理和错误管理
 */

class APIModule {
    constructor(config) {
        this.config = config;
        this.baseURL = window.location.origin;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        this.isActive = false;

        this.init();
    }

    init() {
        console.log('初始化API通信模块');
        this.setupInterceptors();
    }

    setupInterceptors() {
        // 可以在这里设置请求/响应拦截器
        // 用于统一的错误处理、认证等
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: { ...this.defaultHeaders, ...options.headers },
            timeout: options.timeout || this.config.timeout || 30000,
            ...options
        };

        // 添加请求体
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            console.log(`API请求: ${config.method} ${url}`);
            const response = await fetch(url, config);

            // 检查响应状态
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // 解析响应
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                console.log(`API响应: ${config.method} ${endpoint}`, data);
                return data;
            } else {
                const text = await response.text();
                console.log(`API响应: ${config.method} ${endpoint}`, text);
                return text;
            }

        } catch (error) {
            console.error(`API请求失败: ${config.method} ${endpoint}`, error);

            // 网络错误重试逻辑
            if (this.shouldRetry(error, options.retryCount || 0)) {
                console.log(`重试请求: ${options.retryCount || 0 + 1}/${this.config.retryAttempts || 3}`);
                return this.request(endpoint, {
                    ...options,
                    retryCount: (options.retryCount || 0) + 1
                });
            }

            throw error;
        }
    }

    shouldRetry(error, retryCount) {
        const maxRetries = this.config.retryAttempts || 3;

        // 只对网络错误重试
        if (retryCount >= maxRetries) return false;
        if (error.name === 'TypeError' && error.message.includes('fetch')) return true;
        if (error.message.includes('NetworkError')) return true;
        if (error.message.includes('Failed to fetch')) return true;

        return false;
    }

    // 便捷方法
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    async post(endpoint, data, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', body: data });
    }

    async put(endpoint, data, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', body: data });
    }

    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    // 健康检查
    async healthCheck() {
        try {
            const response = await this.get('/api/health');
            return response.status === 'healthy';
        } catch (error) {
            console.error('健康检查失败:', error);
            return false;
        }
    }

    // 项目状态
    async getProjectStatus() {
        return this.get('/api/project/status');
    }

    // 脚本管理
    async getScriptsList() {
        return this.get('/api/scripts/list');
    }

    async getScriptsStatus() {
        return this.get('/api/scripts/status');
    }

    async runScript(scriptName) {
        return this.post(`/api/scripts/run/${scriptName}`);
    }

    async stopScript(scriptName) {
        return this.post(`/api/scripts/stop/${scriptName}`);
    }

    // 日志查看
    async getScriptLogs(scriptName, lines = 100) {
        return this.get(`/api/logs/${scriptName}?lines=${lines}`);
    }

    // 配置管理
    async getConfig(component) {
        return this.get(`/api/config/${component}`);
    }

    async updateConfig(component, config) {
        return this.post(`/api/config/${component}`, config);
    }

    // 部署进度
    async getDeploymentProgress() {
        return this.get('/api/deployment/progress');
    }

    // 系统资源
    async getSystemResources() {
        return this.get('/api/system/resources');
    }

    // 批量操作
    async batchRequest(requests) {
        const promises = requests.map(req =>
            this.request(req.endpoint, req.options).catch(error => ({
                error: error.message,
                endpoint: req.endpoint
            }))
        );

        return Promise.allSettled(promises);
    }

    // WebSocket连接管理
    connectWebSocket() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return this.ws;
        }

        const wsURL = `ws://${window.location.host}/ws/monitoring`;
        this.ws = new WebSocket(wsURL);

        this.ws.onopen = () => {
            console.log('WebSocket连接已建立');
            if (this.onConnect) this.onConnect();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (this.onMessage) this.onMessage(data);
            } catch (error) {
                console.error('WebSocket消息解析失败:', error);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket连接已关闭');
            if (this.onDisconnect) this.onDisconnect();

            // 自动重连
            setTimeout(() => this.connectWebSocket(), 5000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket错误:', error);
        };

        return this.ws;
    }

    disconnectWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    // 事件处理器
    onConnect(callback) {
        this.onConnect = callback;
    }

    onDisconnect(callback) {
        this.onDisconnect = callback;
    }

    onMessage(callback) {
        this.onMessage = callback;
    }

    // 发送WebSocket消息
    sendWebSocket(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket未连接，无法发送消息');
        }
    }

    destroy() {
        this.disconnectWebSocket();
        this.isActive = false;
        console.log('API通信模块已销毁');
    }
}

// 导出模块
window.APIModule = APIModule;
