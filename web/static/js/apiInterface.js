/**
 * API Interface Module - API接口管理模块
 * 负责统一管理所有前端API调用
 * 单一职责：API请求封装、错误处理、接口健康检测
 */

const APIInterface = {
    // 状态
    state: {
        baseUrl: '',
        headers: {
            'Content-Type': 'application/json'
        },
        timeout: 30000,
        retryCount: 3,
        retryDelay: 1000,
        endpoints: {},
        healthStatus: {},
        requestQueue: []
    },

    // 配置
    config: {
        healthCheckInterval: 30000, // 30秒
        defaultEndpoints: {
            // 健康检查
            'health': { method: 'GET', path: '/api/health', description: '系统健康检查' },
            
            // 项目状态
            'projectStatus': { method: 'GET', path: '/api/project/status', description: '项目整体状态' },
            
            // 脚本相关
            'scriptsList': { method: 'GET', path: '/api/scripts/list', description: '脚本列表' },
            'scriptsStatus': { method: 'GET', path: '/api/scripts/status', description: '脚本运行状态' },
            'scriptExecute': { method: 'POST', path: '/api/scripts/run/{script_name}', description: '执行脚本' },
            'scriptStop': { method: 'POST', path: '/api/scripts/stop/{script_name}', description: '停止脚本' },
            'scriptLogs': { method: 'GET', path: '/api/logs/{script_name}', description: '获取脚本日志' },
            
            // 配置相关
            'configGet': { method: 'GET', path: '/api/config/{component}', description: '获取配置' },
            'configUpdate': { method: 'POST', path: '/api/config/{component}', description: '更新配置' },
            
            // 系统资源
            'systemResources': { method: 'GET', path: '/api/system/resources', description: '系统资源使用' },
            
            // 端口相关
            'ports': { method: 'GET', path: '/api/ports', description: '端口状态列表' },
            
            // 子项目
            'subprojects': { method: 'GET', path: '/api/subprojects', description: '子项目状态' },
            'subprojectDetail': { method: 'GET', path: '/api/subprojects/{name}', description: '子项目详情' },
            
            // 部署进度
            'deploymentProgress': { method: 'GET', path: '/api/deployment/progress', description: '部署进度' },
            
            // 冒泡数据
            'bubbles': { method: 'GET', path: '/api/bubbles', description: '冒泡数据' },
            'bubblesHistory': { method: 'GET', path: '/api/bubbles/history', description: '历史冒泡' }
        }
    },

    /**
     * 初始化API接口管理模块
     */
    init: function() {
        console.log('API Interface initializing...');
        
        // 设置基础URL
        this.state.baseUrl = this.getBaseUrl();
        
        // 加载端点配置
        this.loadEndpoints();
        
        // 启动健康检查
        this.startHealthCheck();
    },

    /**
     * 获取基础URL
     */
    getBaseUrl: function() {
        return window.location.origin;
    },

    /**
     * 加载端点配置
     */
    loadEndpoints: function() {
        // 合并默认配置和自定义配置
        this.state.endpoints = { ...this.config.defaultEndpoints };
        
        // 从服务器加载额外配置（如果有）
        this.loadEndpointsFromServer();
    },

    /**
     * 从服务器加载端点配置
     */
    loadEndpointsFromServer: async function() {
        try {
            const response = await fetch('/api/mapping');
            if (response.ok) {
                const mapping = await response.json();
                // 可以在这里添加额外的端点配置
                console.log('Loaded API mapping:', mapping);
            }
        } catch (error) {
            // 忽略错误，使用默认配置
            console.warn('Failed to load API mapping, using defaults');
        }
    },

    /**
     * 发起HTTP请求
     */
    request: async function(endpoint, options = {}) {
        const config = this.state.endpoints[endpoint];
        if (!config) {
            throw new Error(`Unknown endpoint: ${endpoint}`);
        }

        // 构建URL
        let url = this.state.baseUrl + config.path;
        
        // 替换路径参数
        if (options.pathParams) {
            Object.keys(options.pathParams).forEach(key => {
                url = url.replace(`{${key}}`, options.pathParams[key]);
            });
        }

        // 构建查询参数
        const queryParams = new URLSearchParams();
        if (options.queryParams) {
            Object.keys(options.queryParams).forEach(key => {
                queryParams.append(key, options.queryParams[key]);
            });
        }
        
        if (queryParams.toString()) {
            url += `?${queryParams.toString()}`;
        }

        // 构建请求选项
        const requestOptions = {
            method: options.method || config.method || 'GET',
            headers: {
                ...this.state.headers,
                ...options.headers
            },
            timeout: options.timeout || this.state.timeout
        };

        // 添加请求体
        if (requestOptions.method !== 'GET' && requestOptions.method !== 'HEAD' && options.body) {
            requestOptions.body = JSON.stringify(options.body);
        }

        // 执行请求（带重试）
        return this.executeWithRetry(url, requestOptions);
    },

    /**
     * 带重试的请求执行
     */
    executeWithRetry: async function(url, options, retryCount = null) {
        if (retryCount === null) {
            retryCount = this.state.retryCount;
        }

        for (let attempt = 1; attempt <= retryCount; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), options.timeout);
                
                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);

                // 解析响应
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    return data;
                } else {
                    const text = await response.text();
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return text;
                }

            } catch (error) {
                // 检查是否是最后一次尝试
                if (attempt === retryCount) {
                    this.handleError(endpoint, error);
                    throw error;
                }

                // 等待后重试
                await this.sleep(this.state.retryDelay * attempt);
            }
        }
    },

    /**
     * 睡眠函数
     */
    sleep: function(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * 错误处理
     */
    handleError: function(endpoint, error) {
        console.error(`API Error [${endpoint}]:`, error);
        
        // 显示错误通知
        const config = this.state.endpoints[endpoint];
        Notifications.show('API错误', `${config?.description || endpoint}: ${error.message}`, 'error');
    },

    // ========== 快捷方法 ==========

    /**
     * 健康检查
     */
    async healthCheck() {
        return this.request('health');
    },

    /**
     * 获取项目状态
     */
    async getProjectStatus() {
        return this.request('projectStatus');
    },

    /**
     * 获取脚本列表
     */
    async getScriptsList() {
        return this.request('scriptsList');
    },

    /**
     * 获取脚本状态
     */
    async getScriptsStatus() {
        return this.request('scriptsStatus');
    },

    /**
     * 执行脚本
     */
    async executeScript(scriptName) {
        return this.request('scriptExecute', {
            method: 'POST',
            pathParams: { script_name: scriptName }
        });
    },

    /**
     * 停止脚本
     */
    async stopScript(scriptName) {
        return this.request('scriptStop', {
            method: 'POST',
            pathParams: { script_name: scriptName }
        });
    },

    /**
     * 获取脚本日志
     */
    async getScriptLogs(scriptName, lines = 100) {
        return this.request('scriptLogs', {
            pathParams: { script_name: scriptName },
            queryParams: { lines }
        });
    },

    /**
     * 获取配置
     */
    async getConfig(component) {
        return this.request('configGet', {
            pathParams: { component }
        });
    },

    /**
     * 更新配置
     */
    async updateConfig(component, config) {
        return this.request('configUpdate', {
            method: 'POST',
            pathParams: { component },
            body: config
        });
    },

    /**
     * 获取系统资源
     */
    async getSystemResources() {
        return this.request('systemResources');
    },

    /**
     * 获取端口状态
     */
    async getPorts() {
        return this.request('ports');
    },

    /**
     * 获取子项目状态
     */
    async getSubProjects() {
        return this.request('subprojects');
    },

    /**
     * 获取子项目详情
     */
    async getSubProjectDetail(name) {
        return this.request('subprojectDetail', {
            pathParams: { name }
        });
    },

    /**
     * 获取部署进度
     */
    async getDeploymentProgress() {
        return this.request('deploymentProgress');
    },

    /**
     * 获取冒泡数据
     */
    async getBubbles() {
        return this.request('bubbles');
    },

    /**
     * 获取历史冒泡
     */
    async getBubblesHistory() {
        return this.request('bubblesHistory');
    },

    // ========== 健康检测 ==========

    /**
     * 启动健康检查
     */
    startHealthCheck: function() {
        // 立即执行一次
        this.checkAllEndpoints();
        
        // 定期检查
        this.healthCheckTimer = setInterval(() => {
            this.checkAllEndpoints();
        }, this.config.healthCheckInterval);
    },

    /**
     * 检查所有端点健康状态
     */
    checkAllEndpoints: async function() {
        const endpoints = ['health', 'projectStatus', 'systemResources'];
        
        for (const endpoint of endpoints) {
            try {
                const startTime = Date.now();
                await this.request(endpoint);
                const responseTime = Date.now() - startTime;
                
                this.state.healthStatus[endpoint] = {
                    status: 'healthy',
                    responseTime,
                    lastCheck: new Date().toISOString()
                };
            } catch (error) {
                this.state.healthStatus[endpoint] = {
                    status: 'unhealthy',
                    error: error.message,
                    lastCheck: new Date().toISOString()
                };
            }
        }
    },

    /**
     * 获取端点健康状态
     */
    getEndpointHealth: function(endpoint) {
        return this.state.healthStatus[endpoint] || { status: 'unknown' };
    },

    /**
     * 获取所有健康状态
     */
    getAllHealthStatus: function() {
        return { ...this.state.healthStatus };
    },

    /**
     * 获取健康统计
     */
    getHealthStats: function() {
        const statuses = Object.values(this.state.healthStatus);
        const healthy = statuses.filter(s => s.status === 'healthy').length;
        const unhealthy = statuses.filter(s => s.status === 'unhealthy').length;
        
        return {
            total: statuses.length,
            healthy,
            unhealthy,
            avgResponseTime: this.calculateAvgResponseTime()
        };
    },

    /**
     * 计算平均响应时间
     */
    calculateAvgResponseTime: function() {
        const healthyStatuses = Object.values(this.state.healthStatus)
            .filter(s => s.status === 'healthy' && s.responseTime);
        
        if (healthyStatuses.length === 0) return 0;
        
        const total = healthyStatuses.reduce((sum, s) => sum + s.responseTime, 0);
        return Math.round(total / healthyStatuses.length);
    },

    // ========== 端点管理 ==========

    /**
     * 添加自定义端点
     */
    addEndpoint: function(key, config) {
        this.state.endpoints[key] = {
            method: 'GET',
            ...config
        };
    },

    /**
     * 移除端点
     */
    removeEndpoint: function(key) {
        delete this.state.endpoints[key];
    },

    /**
     * 获取所有端点
     */
    getEndpoints: function() {
        return { ...this.state.endpoints };
    },

    /**
     * 获取端点配置
     */
    getEndpoint: function(key) {
        return this.state.endpoints[key];
    },

    // ========== 工具方法 ==========

    /**
     * 生成API文档
     */
    generateApiDocs: function() {
        const endpoints = Object.entries(this.state.endpoints);
        
        const docs = endpoints.map(([key, config]) => {
            return {
                name: key,
                method: config.method,
                path: config.path,
                description: config.description
            };
        });

        return {
            title: 'AI弹窗项目 API 文档',
            version: '1.0.0',
            baseUrl: this.state.baseUrl,
            generatedAt: new Date().toISOString(),
            endpoints: docs
        };
    },

    /**
     * 导出API配置
     */
    exportConfig: function() {
        const config = {
            baseUrl: this.state.baseUrl,
            headers: this.state.headers,
            timeout: this.state.timeout,
            retryCount: this.state.retryCount,
            endpoints: this.state.endpoints,
            healthStatus: this.state.healthStatus
        };

        const blob = new Blob([JSON.stringify(config, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `api-config-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        Notifications.show('导出成功', 'API配置已导出', 'success');
    },

    /**
     * 销毁API接口管理模块
     */
    destroy: function() {
        console.log('API Interface destroying...');
        
        // 停止健康检查
        if (this.healthCheckTimer) {
            clearInterval(this.healthCheckTimer);
        }
        
        // 清空状态
        this.state.endpoints = {};
        this.state.healthStatus = {};
    }
};

// 导出到全局
window.APIInterface = APIInterface;

