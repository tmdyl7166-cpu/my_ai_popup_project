/**
 * Utils Index - 工具模块索引
 * 统一导出所有工具模块
 */

// 全局事件总线
window.EventBus = require("./eventBus.js");

// 安全工具
window.SafeUtils = require("./safeUtils.js");

// 错误处理器
window.ErrorHandler = require("./errorHandler.js");

// 统一API封装
window.API = require("./api.js");

// 弹窗堆栈管理
window.ModalStack = require("./modalStack.js");

// 主题管理
window.ThemeManager = require("./themeManager.js");

// 动态菜单
window.DynamicMenu = require("./dynamicMenu.js");

console.log("[Utils] 所有工具模块已加载");
