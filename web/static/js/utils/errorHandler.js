/**
 * ErrorHandler - 全局错误捕获与上报
 * 统一处理前端错误并上报到后端
 */

const ErrorHandler = {
  // 配置
  config: {
    enabled: true,
    autoReport: true,
    reportEndpoint: "/api/audit/logs",
    maxErrors: 100,
    ignorePatterns: [/ResizeObserver/, /non-native-interactive/, /favicon.ico/],
    userInfo: null,
  },

  // 错误缓存
  errorCache: [],

  /**
   * 初始化
   */
  init: function (config = {}) {
    this.config = { ...this.config, ...config };
    console.log("[ErrorHandler] 初始化错误处理器");

    // 监听JavaScript错误
    window.addEventListener("error", (event) => this.handleError(event));

    // 监听Promise拒绝
    window.addEventListener("unhandledrejection", (event) =>
      this.handlePromiseRejection(event),
    );

    // 监听资源加载错误
    window.addEventListener(
      "error",
      (event) => {
        if (
          event.target.tagName === "IMG" ||
          event.target.tagName === "SCRIPT" ||
          event.target.tagName === "LINK"
        ) {
          this.handleResourceError(event);
        }
      },
      true,
    );

    // 恢复缓存的错误
    this.recoverCachedErrors();
  },

  /**
   * 处理JavaScript错误
   */
  handleError: function (event) {
    const error = event.error;

    // 忽略某些错误
    if (this.shouldIgnore(error)) {
      return;
    }

    const errorInfo = {
      type: "javascript",
      message: error?.message || "Unknown error",
      stack: error?.stack || "",
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    };

    this.logError(errorInfo);

    if (this.config.autoReport) {
      this.reportError(errorInfo);
    }
  },

  /**
   * 处理Promise拒绝
   */
  handlePromiseRejection: function (event) {
    const reason = event.reason;

    const errorInfo = {
      type: "promise",
      message: reason?.message || String(reason),
      stack: reason?.stack || "",
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    };

    this.logError(errorInfo);

    if (this.config.autoReport) {
      this.reportError(errorInfo);
    }
  },

  /**
   * 处理资源加载错误
   */
  handleResourceError: function (event) {
    const errorInfo = {
      type: "resource",
      message: `Failed to load resource: ${event.target.src || event.target.href}`,
      tagName: event.target.tagName,
      src: event.target.src || event.target.href,
      timestamp: new Date().toISOString(),
      url: window.location.href,
    };

    this.logError(errorInfo);

    if (this.config.autoReport) {
      this.reportError(errorInfo);
    }
  },

  /**
   * 记录错误
   */
  logError: function (errorInfo) {
    // 添加到缓存
    this.errorCache.push(errorInfo);

    // 限制缓存数量
    if (this.errorCache.length > this.config.maxErrors) {
      this.errorCache.shift();
    }

    // 控制台输出
    console.error("[ErrorHandler]", errorInfo);

    // 发送事件通知
    if (typeof EventBus !== "undefined") {
      EventBus.emit("error:occurred", errorInfo);
    }
  },

  /**
   * 上报错误到后端
   */
  reportError: async function (errorInfo) {
    try {
      const payload = {
        level: this.getErrorLevel(errorInfo.type),
        source: "frontend",
        message: errorInfo.message,
        details: JSON.stringify({
          stack: errorInfo.stack,
          url: errorInfo.url,
          userAgent: errorInfo.userAgent,
          extra: errorInfo,
        }),
        timestamp: errorInfo.timestamp,
        userId: this.config.userInfo?.id || null,
      };

      await fetch(this.config.reportEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...SafeUtils?.getCsrfHeaders?.(),
        },
        body: JSON.stringify(payload),
      });
    } catch (e) {
      console.warn("[ErrorHandler] 错误上报失败:", e);
    }
  },

  /**
   * 获取错误级别
   */
  getErrorLevel: function (type) {
    const levelMap = {
      javascript: "error",
      promise: "warning",
      resource: "warning",
      network: "error",
    };
    return levelMap[type] || "error";
  },

  /**
   * 检查是否应该忽略该错误
   */
  shouldIgnore: function (error) {
    const message = error?.message || "";

    return this.config.ignorePatterns.some((pattern) => {
      if (typeof pattern === "string") {
        return message.includes(pattern);
      }
      return pattern.test(message);
    });
  },

  /**
   * 创建错误对象
   */
  create: function (message, options = {}) {
    const error = new Error(message);
    error.name = options.name || "CustomError";
    error.code = options.code;
    error.details = options.details;

    if (options.stack) {
      error.stack = options.stack;
    }

    return error;
  },

  /**
   * 抛出错误
   */
  throw: function (message, options = {}) {
    throw this.create(message, options);
  },

  /**
   * 包装异步函数以捕获错误
   */
  wrap: function (fn, context) {
    return (...args) => {
      try {
        const result = fn.apply(context, args);
        if (result && typeof result.then === "function") {
          return result.catch((error) => {
            this.handleError({ error });
            return Promise.reject(error);
          });
        }
        return result;
      } catch (error) {
        this.handleError({ error });
        throw error;
      }
    };
  },

  /**
   * 获取错误缓存
   */
  getCachedErrors: function () {
    return [...this.errorCache];
  },

  /**
   * 恢复缓存的错误（在页面刷新后）
   */
  recoverCachedErrors: function () {
    try {
      const cached = sessionStorage.getItem("errorCache");
      if (cached) {
        const errors = JSON.parse(cached);
        errors.forEach((error) => {
          this.errorCache.push(error);
        });
        // 清除缓存
        sessionStorage.removeItem("errorCache");
      }
    } catch (e) {
      // 忽略恢复错误
    }
  },

  /**
   * 持久化错误缓存
   */
  persistCache: function () {
    try {
      const errors = this.errorCache.slice(-this.config.maxErrors);
      sessionStorage.setItem("errorCache", JSON.stringify(errors));
    } catch (e) {
      // 忽略持久化错误
    }
  },

  /**
   * 清除错误缓存
   */
  clearCache: function () {
    this.errorCache = [];
    sessionStorage.removeItem("errorCache");
  },

  /**
   * 手动报告错误
   */
  manualReport: function (message, details = {}) {
    const errorInfo = {
      type: "manual",
      message: message,
      stack: new Error().stack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      details: details,
    };

    this.logError(errorInfo);
    this.reportError(errorInfo);
  },

  /**
   * 显示错误通知
   */
  showNotification: function (errorInfo, options = {}) {
    if (typeof Toast !== "undefined") {
      Toast.error(
        options.title || "发生错误",
        errorInfo.message.substring(0, 200),
        { duration: options.duration || 8000 },
      );
    }
  },
};

// 页面卸载前持久化错误
window.addEventListener("beforeunload", () => {
  ErrorHandler.persistCache();
});

// 导出到全局
window.ErrorHandler = ErrorHandler;
