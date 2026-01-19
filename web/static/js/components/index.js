/**
 * Components Index - 组件索引
 * 统一导出所有组件模块
 */

// 图表组件
window.Charting = require("./charting.js");

// 进度条组件
window.Progress = require("./progress.js");

// 加载动画组件
window.Spinner = require("./spinner.js");

// 通知提示组件
window.Toast = require("./toast.js");

// WebSocket管道组件
window.WS = require("./ws.js");

console.log("[Components] 所有组件模块已加载");
