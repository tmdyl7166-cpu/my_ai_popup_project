/**
 * Main Application Module
 * Coordinates all modules and manages application lifecycle
 */
window.ProjectMonitor = {
    // Application state
    state: {
        connection: {
            status: 'disconnected',
            lastUpdate: null
        },
        project: {
            status: 'unknown',
            components: {},
            healthScore: 0
        },
        scripts: [],
        deployment: {},
        config: {},
        logs: {}
    },

    // Module references
    modules: {},

    /**
     * Initialize application
     */
    async init() {
        console.log('Initializing Project Monitor...');

        try {
            // Initialize core modules
            StateManager.init();
            WebSocketManager.init();
            NotificationsManager.info('正在初始化应用...');

            // Load navigation
            await this.loadComponent('navigation-container', '/static/templates/components/navigation.html');
            NavigationModule.init();

            // Load sidebar
            await this.loadComponent('sidebar-container', '/static/templates/components/sidebar.html');
            SidebarModule.init();

            // Load main content
            await this.loadComponent('main-content', '/static/templates/components/main-tabs.html');
            await this.loadComponent('dashboard-content', '/static/templates/components/dashboard.html');
            await this.loadComponent('scripts-content', '/static/templates/components/scripts.html');
            await this.loadComponent('deployment-content', '/static/templates/components/deployment.html');
            await this.loadComponent('config-content', '/static/templates/components/config.html');
            await this.loadComponent('logs-content', '/static/templates/components/logs.html');

            // Load modals
            await this.loadComponent('modals-container', '/static/templates/components/modals.html');

            // Initialize feature modules
            DashboardModule.init();
            ScriptsModule.init();
            DeploymentModule.init();
            ConfigModule.init();
            LogsModule.init();
            ModalsModule.init();

            // Connect to WebSocket
            WebSocketManager.connect();

            // Load initial data
            await this.loadInitialData();

            NotificationsManager.success('应用初始化完成');
            console.log('Project Monitor initialized successfully');

        } catch (error) {
            console.error('Failed to initialize application:', error);
            NotificationsManager.error('应用初始化失败: ' + error.message);
        }
    },

    /**
     * Load HTML component
     */
    async loadComponent(containerId, templatePath) {
        try {
            const response = await fetch(templatePath);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const html = await response.text();
            document.getElementById(containerId).innerHTML = html;
        } catch (error) {
            console.error(`Failed to load component ${containerId}:`, error);
            throw error;
        }
    },

    /**
     * Load initial application data
     */
    async loadInitialData() {
        try {
            // Load project status
            await DashboardModule.loadProjectStatus();

            // Load scripts
            await ScriptsModule.loadScripts();

            // Load deployment progress
            await DeploymentModule.loadDeploymentProgress();

            // Load config list
            await ConfigModule.loadConfigList();

        } catch (error) {
            console.error('Failed to load initial data:', error);
            NotificationsManager.error('加载初始数据失败');
        }
    },

    /**
     * Get current application state
     */
    getState() {
        return this.state;
    },

    /**
     * Update application state
     */
    updateState(newState) {
        this.state = { ...this.state, ...newState };
        StateManager.notifyStateChange(this.state);
    },

    /**
     * Register module
     */
    registerModule(name, module) {
        this.modules[name] = module;
    },

    /**
     * Get registered module
     */
    getModule(name) {
        return this.modules[name];
    }
};
