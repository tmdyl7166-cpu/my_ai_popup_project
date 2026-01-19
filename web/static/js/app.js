/**
 * Main Application - 主应用
 * 负责初始化所有模块和应用启动
 */

const App = {
  // 状态
  state: {
    initialized: false,
    modules: {},
    components: {},
    utils: {},
    startTime: null,
  },

  // 配置
  config: {
    initTimeout: 10000, // 初始化超时时间
    heartbeatInterval: 30000, // 心跳间隔
    initOrder: [
      // 第一阶段：工具模块（无依赖）
      "utils/eventBus",
      "utils/safeUtils",
      "utils/errorHandler",
      // 第二阶段：基础组件
      "components/charting",
      "components/progress",
      "components/spinner",
      "components/toast",
      // 第三阶段：核心工具
      "utils/api",
      "utils/modalStack",
      "utils/themeManager",
      "utils/dynamicMenu",
      // 第四阶段：WebSocket
      "components/ws",
    ],
  },

  /**
   * 应用初始化
   */
  init: function () {
    console.log("AI弹窗项目监控中心 - 应用初始化开始...");

    if (this.state.initialized) {
      console.warn("应用已经初始化");
      return;
    }

    this.state.startTime = Date.now();

    try {
      // 显示全局加载器
      this.showGlobalLoader("正在初始化应用...");

      // 初始化工具模块
      this.initUtils();

      // 初始化组件
      this.initComponents();

      // 初始化核心模块
      this.initCoreModules();

      // 初始化功能模块
      this.initFeatureModules();

      // 设置全局事件监听器
      this.setupGlobalEventListeners();

      // 启动心跳
      this.startHeartbeat();

      // 隐藏全局加载器
      this.hideGlobalLoader();

      this.state.initialized = true;
      console.log("AI弹窗项目监控中心 - 应用初始化完成");

      // 触发初始化完成事件
      this.emit("app:initialized");
    } catch (error) {
      console.error("应用初始化失败:", error);
      this.showInitError(error);
    }
  },

  /**
   * 初始化工具模块
   */
  initUtils: function () {
    console.log("初始化工具模块...");

    // 事件总线
    if (typeof EventBus !== "undefined") {
      EventBus.init();
      this.state.utils.eventBus = EventBus;
    }

    // 安全工具
    if (typeof SafeUtils !== "undefined") {
      SafeUtils.init && SafeUtils.init();
      this.state.utils.safeUtils = SafeUtils;
    }

    // 错误处理器
    if (typeof ErrorHandler !== "undefined") {
      ErrorHandler.init();
      this.state.utils.errorHandler = ErrorHandler;
    }

    // API封装
    if (typeof API !== "undefined") {
      API.init();
      this.state.utils.api = API;
    }

    // 弹窗堆栈
    if (typeof ModalStack !== "undefined") {
      ModalStack.init();
      this.state.utils.modalStack = ModalStack;
    }

    // 主题管理
    if (typeof ThemeManager !== "undefined") {
      ThemeManager.init();
      this.state.utils.themeManager = ThemeManager;
    }

    // 动态菜单
    if (typeof DynamicMenu !== "undefined") {
      DynamicMenu.init();
      this.state.utils.dynamicMenu = DynamicMenu;
    }

    console.log("工具模块初始化完成");
  },

  /**
   * 初始化组件
   */
  initComponents: function () {
    console.log("初始化组件...");

    // 图表组件
    if (typeof Charting !== "undefined") {
      Charting.init && Charting.init();
      this.state.components.charting = Charting;
    }

    // 进度条组件
    if (typeof Progress !== "undefined") {
      Progress.init && Progress.init();
      this.state.components.progress = Progress;
    }

    // 加载动画
    if (typeof Spinner !== "undefined") {
      Spinner.init && Spinner.init();
      this.state.components.spinner = Spinner;
    }

    // 通知提示
    if (typeof Toast !== "undefined") {
      Toast.init && Toast.init();
      this.state.components.toast = Toast;
    }

    // WebSocket
    if (typeof WS !== "undefined") {
      WS.init && WS.init();
      this.state.components.ws = WS;
    }

    console.log("组件初始化完成");
  },

  /**
   * 初始化核心模块
   */
  initCoreModules: function () {
    console.log("初始化核心模块...");

    // WebSocket管理器
    if (typeof WebSocketManager !== "undefined") {
      WebSocketManager.init();
      this.state.modules.websocketManager = WebSocketManager;
    } else {
      throw new Error("WebSocketManager 模块未加载");
    }

    // 模态框管理器
    if (typeof ModalManager !== "undefined") {
      ModalManager.init();
      this.state.modules.modalManager = ModalManager;
    } else {
      throw new Error("ModalManager 模块未加载");
    }

    // 通知管理器
    if (typeof Notifications !== "undefined") {
      Notifications.init();
      this.state.modules.notifications = Notifications;
    } else {
      throw new Error("Notifications 模块未加载");
    }

    // 全局操作
    if (typeof GlobalActions !== "undefined") {
      GlobalActions.init();
      this.state.modules.globalActions = GlobalActions;
    } else {
      throw new Error("GlobalActions 模块未加载");
    }

    console.log("核心模块初始化完成");
  },

  /**
   * 初始化功能模块
   */
  initFeatureModules: function () {
    console.log("初始化功能模块...");

    // API接口管理（依赖WebSocket）
    if (typeof APIInterface !== "undefined") {
      APIInterface.init();
      this.state.modules.apiInterface = APIInterface;
    }

    // 全局监控
    if (typeof GlobalMonitor !== "undefined") {
      GlobalMonitor.init();
      this.state.modules.globalMonitor = GlobalMonitor;
    }

    // 部署进度
    if (typeof DeploymentProgress !== "undefined") {
      DeploymentProgress.init();
      this.state.modules.deploymentProgress = DeploymentProgress;
    }

    // 模块状态
    if (typeof ModuleStatus !== "undefined") {
      ModuleStatus.init();
      this.state.modules.moduleStatus = ModuleStatus;
    }

    // 脚本控制
    if (typeof ScriptControl !== "undefined") {
      ScriptControl.init();
      this.state.modules.scriptControl = ScriptControl;
    }

    // 脚本运行器
    if (typeof ScriptRunner !== "undefined") {
      ScriptRunner.init();
      this.state.modules.scriptRunner = ScriptRunner;
    }

    // 配置管理
    if (typeof ConfigManagement !== "undefined") {
      ConfigManagement.init();
      this.state.modules.configManagement = ConfigManagement;
    }

    // 日志查看
    if (typeof LogsViewer !== "undefined") {
      LogsViewer.init();
      this.state.modules.logsViewer = LogsViewer;
    }

    // 端口映射
    if (typeof PortMapping !== "undefined") {
      PortMapping.init();
      this.state.modules.portMapping = PortMapping;
    }

    // 冒泡监测
    if (typeof BubbleMonitor !== "undefined") {
      BubbleMonitor.init();
      this.state.modules.bubbleMonitor = BubbleMonitor;
    }

    // 视频流监控
    if (typeof VideoStreamMonitor !== "undefined") {
      VideoStreamMonitor.init();
      this.state.modules.videoStreamMonitor = VideoStreamMonitor;
    }

    // 备份恢复监控
    if (typeof BackupRecoveryMonitor !== "undefined") {
      BackupRecoveryMonitor.init();
      this.state.modules.backupRecoveryMonitor = BackupRecoveryMonitor;
    }

    // 子项目监测
    if (typeof SubProjectMonitor !== "undefined") {
      SubProjectMonitor.init();
      this.state.modules.subProjectMonitor = SubProjectMonitor;
    }

    console.log("功能模块初始化完成");
  },

  /**
   * 设置全局事件监听器
   */
  setupGlobalEventListeners: function () {
    console.log("设置全局事件监听器...");

    // 窗口错误处理
    window.addEventListener("error", (event) => {
      console.error("全局错误:", event.error);
      this.handleGlobalError(event.error);
    });

    // 未处理的Promise拒绝
    window.addEventListener("unhandledrejection", (event) => {
      console.error("未处理的Promise拒绝:", event.reason);
      this.handleGlobalError(event.reason);
    });

    // 页面可见性变化
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        console.log("页面变为不可见");
        this.pauseAutoRefresh();
      } else {
        console.log("页面变为可见");
        this.resumeAutoRefresh();
      }
    });

    // 键盘快捷键
    document.addEventListener("keydown", (event) => {
      this.handleKeyboardShortcut(event);
    });

    // 网络状态变化
    window.addEventListener("online", () => {
      console.log("网络连接恢复");
      Notifications.show("网络状态", "网络连接已恢复", "success");
      this.resumeAutoRefresh();
    });

    window.addEventListener("offline", () => {
      console.log("网络连接断开");
      Notifications.show("网络状态", "网络连接已断开", "warning");
      this.pauseAutoRefresh();
    });
  },

  /**
   * 处理全局错误
   */
  handleGlobalError: function (error) {
    const errorMessage = error.message || "未知错误";
    console.error("全局错误处理:", error);

    // 显示错误通知
    Notifications.show("应用错误", errorMessage, "error");

    // 如果是严重错误，显示模态框
    if (error.name === "TypeError" || error.name === "ReferenceError") {
      ModalManager.alert({
        title: "应用错误",
        content: `发生严重错误: ${errorMessage}<br><br>建议刷新页面重新加载应用。`,
        size: "lg",
      });
    }
  },

  /**
   * 处理键盘快捷键
   */
  handleKeyboardShortcut: function (event) {
    // Ctrl+R: 刷新所有
    if (event.ctrlKey && event.key === "r") {
      event.preventDefault();
      GlobalActions.refreshAll();
    }

    // Ctrl+H: 健康检查
    if (event.ctrlKey && event.key === "h") {
      event.preventDefault();
      GlobalActions.runHealthCheck();
    }

    // Ctrl+S: 保存配置
    if (event.ctrlKey && event.key === "s") {
      event.preventDefault();
      if (typeof ConfigManagement !== "undefined") {
        ConfigManagement.save();
      }
    }
  },

  /**
   * 显示全局加载器
   */
  showGlobalLoader: function (message = "加载中...") {
    const loader = document.getElementById("globalLoader");
    if (loader) {
      const messageElement = loader.querySelector("h5");
      if (messageElement) {
        messageElement.textContent = message;
      }
      loader.style.display = "flex";
    }
  },

  /**
   * 隐藏全局加载器
   */
  hideGlobalLoader: function () {
    const loader = document.getElementById("globalLoader");
    if (loader) {
      loader.style.display = "none";
    }
  },

  /**
   * 显示初始化错误
   */
  showInitError: function (error) {
    this.hideGlobalLoader();

    const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <h4 class="alert-heading">
                    <i class="fas fa-exclamation-triangle me-2"></i>应用初始化失败
                </h4>
                <p>抱歉，应用初始化过程中发生错误。</p>
                <hr>
                <p class="mb-0">
                    <strong>错误信息:</strong> ${error.message || "未知错误"}
                </p>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>
            </div>
            <div class="text-center mt-3">
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-redo me-2"></i>刷新页面重试
                </button>
            </div>
        `;

    const container = document.querySelector(".container-fluid");
    if (container) {
      container.insertAdjacentHTML("afterbegin", errorHtml);
    }
  },

  /**
   * 启动心跳
   */
  startHeartbeat: function () {
    this.heartbeatTimer = setInterval(() => {
      this.checkHealth();
    }, this.config.heartbeatInterval);
  },

  /**
   * 健康检查
   */
  checkHealth: async function () {
    try {
      const response = await fetch("/api/health");
      if (response.ok) {
        // 健康检查通过
        this.updateHealthStatus(true);
      } else {
        throw new Error("Health check failed");
      }
    } catch (error) {
      console.warn("健康检查失败:", error);
      this.updateHealthStatus(false);
    }
  },

  /**
   * 更新健康状态
   */
  updateHealthStatus: function (healthy) {
    const statusElement = document.getElementById("globalStatus");
    if (statusElement) {
      const icon = statusElement.querySelector("i");
      const text = statusElement.querySelector("small");

      if (healthy) {
        statusElement.className = "badge bg-success";
        if (icon) icon.className = "fas fa-circle me-1";
        if (text) text.textContent = "系统正常";
      } else {
        statusElement.className = "badge bg-danger";
        if (icon) icon.className = "fas fa-circle me-1";
        if (text) text.textContent = "系统异常";
      }
    }
  },

  /**
   * 暂停自动刷新
   */
  pauseAutoRefresh: function () {
    Object.values(this.state.modules).forEach((module) => {
      if (module.stopAutoRefresh) {
        module.stopAutoRefresh();
      }
    });
  },

  /**
   * 恢复自动刷新
   */
  resumeAutoRefresh: function () {
    Object.values(this.state.modules).forEach((module) => {
      if (module.startAutoRefresh) {
        module.startAutoRefresh();
      }
    });
  },

  /**
   * 注册事件处理器
   */
  on: function (event, handler) {
    if (!this.eventHandlers) {
      this.eventHandlers = {};
    }
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = [];
    }
    this.eventHandlers[event].push(handler);
  },

  /**
   * 触发事件
   */
  emit: function (event, data) {
    if (this.eventHandlers && this.eventHandlers[event]) {
      this.eventHandlers[event].forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in ${event} handler:`, error);
        }
      });
    }
  },

  /**
   * 获取应用状态
   */
  getStatus: function () {
    return {
      initialized: this.state.initialized,
      startTime: this.state.startTime,
      uptime: this.state.startTime ? Date.now() - this.state.startTime : 0,
      modules: Object.keys(this.state.modules),
      components: Object.keys(this.state.components),
      utils: Object.keys(this.state.utils),
    };
  },

  /**
   * 获取组件
   */
  getComponent: function (name) {
    return this.state.components[name] || null;
  },

  /**
   * 获取工具
   */
  getUtil: function (name) {
    return this.state.utils[name] || null;
  },

  /**
   * 销毁应用
   */
  destroy: function () {
    console.log("应用销毁...");

    // 停止心跳
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    // 销毁所有模块
    Object.values(this.state.modules).forEach((module) => {
      if (module.destroy) {
        module.destroy();
      }
    });

    // 清除事件处理器
    this.eventHandlers = {};

    this.state.initialized = false;
    console.log("应用已销毁");
  },
};

// 页面加载完成后初始化应用
document.addEventListener("DOMContentLoaded", function () {
  // 设置初始化超时
  const initTimeout = setTimeout(() => {
    console.error("应用初始化超时");
    App.showInitError(new Error("初始化超时"));
  }, App.config.initTimeout);

  try {
    App.init();
    clearTimeout(initTimeout);
  } catch (error) {
    clearTimeout(initTimeout);
    App.showInitError(error);
  }
});

// 页面卸载时销毁应用
window.addEventListener("beforeunload", function () {
  App.destroy();
});

// 导出到全局
window.App = App;
