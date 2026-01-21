/**
 * AI弹窗项目 - 主应用入口
 * 负责协调所有模块和应用生命周期管理
 * 
 * 版本: 1.0.0
 * 更新日期: 2026-01-19
 */

// 全局应用命名空间
window.AIPopupApp = {
    // 应用状态
    state: {
        initialized: false,
        connected: false,
        currentPage: 'dashboard',
        user: null,
        settings: {}
    },

    // 模块引用
    modules: {},

    // 配置
    config: {
        autoRefresh: true,
        refreshInterval: 5000,
        wsReconnectDelay: 3000,
        maxRetries: 3
    }
};

/**
 * 初始化应用
 */
AIPopupApp.init = async function() {
    console.log('🚀 AI弹窗项目监控中心启动中...');
    
    try {
        // 1. 初始化基础模块
        this.initUtils();
        
        // 2. 加载配置
        await this.loadConfig();
        
        // 3. 初始化事件系统
        this.initEventSystem();
        
        // 4. 初始化API接口
        this.initAPI();
        
        // 5. 初始化UI组件
        this.initUI();
        
        // 6. 加载模板组件
        await this.loadTemplates();
        
        // 7. 初始化功能模块
        this.initModules();
        
        // 8. 建立WebSocket连接
        this.initWebSocket();
        
        // 9. 加载初始数据
        await this.loadInitialData();
        
        // 10. 启动定时任务
        this.startTimers();
        
        this.state.initialized = true;
        console.log('✅ 应用初始化完成');
        
    } catch (error) {
        console.error('❌ 应用初始化失败:', error);
        this.showError('应用初始化失败: ' + error.message);
    }
};

/**
 * 初始化工具模块
 */
AIPopupApp.initUtils = function() {
    console.log('初始化工具模块...');
    
    // 事件总线
    if (typeof EventBus !== 'undefined') {
        EventBus.init();
    }
    
    // 错误处理
    if (typeof ErrorHandler !== 'undefined') {
        ErrorHandler.init();
    }
    
    // API工具
    if (typeof API !== 'undefined') {
        API.init();
    }
    
    console.log('工具模块初始化完成');
};

/**
 * 加载配置
 */
AIPopupApp.loadConfig = async function() {
    console.log('加载配置...');
    
    try {
        // 加载本地配置
        const response = await fetch('/api/config/project');
        if (response.ok) {
            const config = await response.json();
            this.state.settings = config;
        }
    } catch (error) {
        console.warn('加载配置失败，使用默认配置:', error.message);
    }
    
    console.log('配置加载完成');
};

/**
 * 初始化事件系统
 */
AIPopupApp.initEventSystem = function() {
    console.log('初始化事件系统...');
    
    // 全局事件监听
    window.addEventListener('error', (event) => {
        console.error('全局错误:', event.error);
        this.showError('发生错误: ' + event.error.message);
    });
    
    // 窗口关闭前提示
    window.addEventListener('beforeunload', (event) => {
        if (this.state.connected) {
            event.preventDefault();
            event.returnValue = '';
        }
    });
    
    console.log('事件系统初始化完成');
};

/**
 * 初始化API接口
 */
AIPopupApp.initAPI = function() {
    console.log('初始化API接口...');
    
    if (typeof APIInterface !== 'undefined') {
        APIInterface.init();
        this.modules.api = APIInterface;
    }
    
    console.log('API接口初始化完成');
};

/**
 * 初始化UI组件
 */
AIPopupApp.initUI = function() {
    console.log('初始化UI组件...');
    
    // 初始化主题
    if (typeof ThemeManager !== 'undefined') {
        ThemeManager.init();
    }
    
    // 初始化通知
    if (typeof NotificationsManager !== 'undefined') {
        NotificationsManager.init();
    }
    
    // 初始化模态框
    if (typeof ModalsModule !== 'undefined') {
        ModalsModule.init();
    }
    
    console.log('UI组件初始化完成');
};

/**
 * 加载模板组件
 */
AIPopupApp.loadTemplates = async function() {
    console.log('加载模板组件...');
    
    const templates = [
        { id: 'navigation-container', path: '/static/templates/components/navigation.html' },
        { id: 'main-tabs', path: '/static/templates/components/main-tabs.html' },
        { id: 'dashboard-panel', path: '/static/templates/components/dashboard.html' },
        { id: 'scripts-panel', path: '/static/templates/components/scripts.html' },
        { id: 'config-panel', path: '/static/templates/components/config.html' },
        { id: 'modals-container', path: '/static/templates/components/modals.html' }
    ];
    
    for (const template of templates) {
        try {
            const response = await fetch(template.path);
            if (response.ok) {
                const html = await response.text();
                const container = document.getElementById(template.id);
                if (container) {
                    container.innerHTML = html;
                }
            }
        } catch (error) {
            console.warn(`加载模板 ${template.path} 失败:`, error.message);
        }
    }
    
    console.log('模板组件加载完成');
};

/**
 * 初始化功能模块
 */
AIPopupApp.initModules = function() {
    console.log('初始化功能模块...');
    
    // 仪表板模块
    if (typeof DashboardModule !== 'undefined') {
        this.modules.dashboard = new DashboardModule({
            autoRefresh: this.config.autoRefresh,
            refreshInterval: this.config.refreshInterval
        });
    }
    
    // 脚本控制模块
    if (typeof ScriptControl !== 'undefined') {
        this.modules.scriptControl = ScriptControl;
        ScriptControl.init();
    }
    
    // 配置管理模块
    if (typeof ConfigManagement !== 'undefined') {
        this.modules.config = ConfigManagement;
        ConfigManagement.init();
    }
    
    // 日志查看模块
    if (typeof LogsModule !== 'undefined') {
        this.modules.logs = LogsModule;
        LogsModule.init();
    }
    
    // 全局监控模块
    if (typeof GlobalMonitor !== 'undefined') {
        this.modules.monitor = GlobalMonitor;
        GlobalMonitor.init();
    }
    
    // 部署进度模块
    if (typeof DeploymentProgress !== 'undefined') {
        this.modules.deployment = DeploymentProgress;
        DeploymentProgress.init();
    }
    
    // WebSocket管理器
    if (typeof WebSocketManager !== 'undefined') {
        this.modules.ws = WebSocketManager;
        WebSocketManager.init();
    }
    
    console.log('功能模块初始化完成');
};

/**
 * 初始化WebSocket连接
 */
AIPopupApp.initWebSocket = function() {
    console.log('初始化WebSocket连接...');
    
    if (this.modules.ws) {
        this.modules.ws.connect();
        
        this.modules.ws.on('connect', () => {
            this.state.connected = true;
            console.log('WebSocket已连接');
            this.showNotification('已连接到服务器', 'success');
        });
        
        this.modules.ws.on('disconnect', () => {
            this.state.connected = false;
            console.log('WebSocket已断开');
            this.showNotification('与服务器断开连接', 'warning');
        });
        
        this.modules.ws.on('status_update', (data) => {
            if (this.modules.dashboard) {
                this.modules.dashboard.updateFromSocket(data);
            }
        });
        
        this.modules.ws.on('script_result', (data) => {
            this.showNotification(`脚本 ${data.script} 执行完成`, 'info');
        });
    }
    
    console.log('WebSocket初始化完成');
};

/**
 * 加载初始数据
 */
AIPopupApp.loadInitialData = async function() {
    console.log('加载初始数据...');
    
    try {
        // 并行加载多个数据源
        await Promise.all([
            this.loadProjectStatus(),
            this.loadSystemResources(),
            this.loadScriptsStatus(),
            this.loadDeploymentProgress()
        ]);
        
        console.log('初始数据加载完成');
        
    } catch (error) {
        console.error('加载初始数据失败:', error);
    }
};

/**
 * 加载项目状态
 */
AIPopupApp.loadProjectStatus = async function() {
    try {
        if (this.modules.api) {
            const status = await this.modules.api.getProjectStatus();
            this.updateProjectStatus(status);
        }
    } catch (error) {
        console.error('加载项目状态失败:', error);
    }
};

/**
 * 加载系统资源
 */
AIPopupApp.loadSystemResources = async function() {
    try {
        if (this.modules.api) {
            const resources = await this.modules.api.getSystemResources();
            this.updateSystemResources(resources);
        }
    } catch (error) {
        console.error('加载系统资源失败:', error);
    }
};

/**
 * 加载脚本状态
 */
AIPopupApp.loadScriptsStatus = async function() {
    try {
        if (this.modules.api) {
            const status = await this.modules.api.getScriptsStatus();
            if (this.modules.scriptControl) {
                this.modules.scriptControl.updateStatus(status);
            }
        }
    } catch (error) {
        console.error('加载脚本状态失败:', error);
    }
};

/**
 * 加载部署进度
 */
AIPopupApp.loadDeploymentProgress = async function() {
    try {
        if (this.modules.api) {
            const progress = await this.modules.api.getDeploymentProgress();
            if (this.modules.deployment) {
                this.modules.deployment.update(progress);
            }
        }
    } catch (error) {
        console.error('加载部署进度失败:', error);
    }
};

/**
 * 启动定时任务
 */
AIPopupApp.startTimers = function() {
    console.log('启动定时任务...');
    
    // 系统资源监控
    this.resourceTimer = setInterval(() => {
        if (this.config.autoRefresh) {
            this.loadSystemResources();
        }
    }, this.config.refreshInterval);
    
    // 脚本状态监控
    this.scriptTimer = setInterval(() => {
        if (this.config.autoRefresh) {
            this.loadScriptsStatus();
        }
    }, this.config.refreshInterval * 2);
    
    console.log('定时任务启动完成');
};

/**
 * 停止定时任务
 */
AIPopupApp.stopTimers = function() {
    if (this.resourceTimer) clearInterval(this.resourceTimer);
    if (this.scriptTimer) clearInterval(this.scriptTimer);
};

/**
 * 更新项目状态显示
 */
AIPopupApp.updateProjectStatus = function(status) {
    const statusBadge = document.getElementById('systemHealthBadge');
    const statusBar = document.getElementById('systemHealthBar');
    
    if (statusBadge) {
        statusBadge.textContent = status.status === 'running' ? '运行中' : status.status;
        statusBadge.className = `badge bg-${status.status === 'running' ? 'success' : 'warning'}`;
    }
    
    if (statusBar) {
        const healthScore = status.healthScore || 100;
        statusBar.style.width = `${healthScore}%`;
        statusBar.className = `progress-bar bg-${healthScore > 80 ? 'success' : healthScore > 60 ? 'warning' : 'danger'}`;
    }
};

/**
 * 更新系统资源显示
 */
AIPopupApp.updateSystemResources = function(resources) {
    // CPU
    const cpuUsage = document.getElementById('cpuUsage');
    const cpuBar = document.getElementById('cpuBar');
    if (cpuUsage) cpuUsage.textContent = `${resources.cpu_percent}%`;
    if (cpuBar) cpuBar.style.width = `${resources.cpu_percent}%`;
    
    // 内存
    const memoryUsage = document.getElementById('memoryUsage');
    const memoryBar = document.getElementById('memoryBar');
    if (memoryUsage) memoryUsage.textContent = `${resources.memory.percent}%`;
    if (memoryBar) memoryBar.style.width = `${resources.memory.percent}%`;
    
    // 磁盘
    const diskUsage = document.getElementById('diskUsage');
    const diskBar = document.getElementById('diskBar');
    if (diskUsage) diskUsage.textContent = `${resources.disk.percent}%`;
    if (diskBar) diskBar.style.width = `${resources.disk.percent}%`;
};

/**
 * 显示通知
 */
AIPopupApp.showNotification = function(message, type = 'info') {
    if (typeof NotificationsManager !== 'undefined') {
        NotificationsManager[type]?.(message) || NotificationsManager.info(message);
    }
};

/**
 * 显示错误
 */
AIPopupApp.showError = function(message) {
    this.showNotification(message, 'error');
    
    // 尝试显示模态框错误
    if (typeof ModalManager !== 'undefined') {
        ModalManager.showError(message);
    }
};

/**
 * 刷新所有数据
 */
AIPopupApp.refreshAll = async function() {
    this.showNotification('正在刷新数据...', 'info');
    await this.loadInitialData();
    this.showNotification('数据已刷新', 'success');
};

/**
 * 导出报告
 */
AIPopupApp.exportReport = function() {
    const report = {
        timestamp: new Date().toISOString(),
        project: this.state.settings,
        resources: {
            cpu: document.getElementById('cpuUsage')?.textContent,
            memory: document.getElementById('memoryUsage')?.textContent,
            disk: document.getElementById('diskUsage')?.textContent
        }
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    this.showNotification('报告已导出', 'success');
};

/**
 * 运行健康检查
 */
AIPopupApp.runHealthCheck = async function() {
    this.showNotification('正在运行健康检查...', 'info');
    
    try {
        if (this.modules.api) {
            await this.modules.api.healthCheck();
            this.showNotification('健康检查完成', 'success');
        }
    } catch (error) {
        this.showError('健康检查失败: ' + error.message);
    }
};

/**
 * 切换页面
 */
AIPopupApp.navigateTo = function(page) {
    this.state.currentPage = page;
    
    // 隐藏所有面板
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // 显示目标面板
    const targetPanel = document.getElementById(`${page}-section`);
    if (targetPanel) {
        targetPanel.style.display = 'block';
    }
    
    // 更新导航状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`[data-page="${page}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
};

/**
 * 获取当前状态
 */
AIPopupApp.getState = function() {
    return { ...this.state };
};

/**
 * 更新设置
 */
AIPopupApp.updateSettings = function(newSettings) {
    this.state.settings = { ...this.state.settings, ...newSettings };
};

/**
 * 销毁应用
 */
AIPopupApp.destroy = function() {
    console.log('销毁应用...');
    
    // 停止定时任务
    this.stopTimers();
    
    // 断开WebSocket
    if (this.modules.ws) {
        this.modules.ws.disconnect();
    }
    
    // 销毁模块
    Object.values(this.modules).forEach(module => {
        if (module.destroy) {
            module.destroy();
        }
    });
    
    this.state.initialized = false;
    console.log('应用已销毁');
};

// 全局快捷方法
window.globalActions = {
    refreshAll: () => AIPopupApp.refreshAll(),
    exportReport: () => AIPopupApp.exportReport(),
    runHealthCheck: () => AIPopupApp.runHealthCheck()
};

// DOM加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    AIPopupApp.init();
});

