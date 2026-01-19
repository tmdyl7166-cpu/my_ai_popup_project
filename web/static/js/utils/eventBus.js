/**
 * EventBus - 全局事件总线
 * 提供模块间松耦合通信机制
 */

const EventBus = {
  // 事件缓存
  events: {},

  // 调试模式
  debug: false,

  /**
   * 订阅事件
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   * @param {Object} options - 选项
   * @returns {string} 订阅ID
   */
  on: function (event, callback, options = {}) {
    if (!this.events[event]) {
      this.events[event] = [];
    }

    const subscription = {
      id: `${event}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      callback: callback,
      once: options.once || false,
      context: options.context || null,
      priority: options.priority || 0,
    };

    // 按优先级排序
    this.events[event].push(subscription);
    this.events[event].sort((a, b) => b.priority - a.priority);

    if (this.debug) {
      console.log(`[EventBus] 订阅事件: ${event}`, subscription.id);
    }

    return subscription.id;
  },

  /**
   * 取消订阅
   * @param {string} event - 事件名称
   * @param {string} subscriptionId - 订阅ID
   */
  off: function (event, subscriptionId) {
    if (!this.events[event]) return;

    const index = this.events[event].findIndex(
      (sub) => sub.id === subscriptionId,
    );
    if (index !== -1) {
      this.events[event].splice(index, 1);
      if (this.debug) {
        console.log(`[EventBus] 取消订阅: ${event}`, subscriptionId);
      }
    }
  },

  /**
   * 取消事件的所有订阅
   * @param {string} event - 事件名称
   */
  offAll: function (event) {
    if (event) {
      delete this.events[event];
      if (this.debug) {
        console.log(`[EventBus] 取消所有订阅: ${event}`);
      }
    } else {
      this.events = {};
      if (this.debug) {
        console.log("[EventBus] 取消所有事件订阅");
      }
    }
  },

  /**
   * 触发事件
   * @param {string} event - 事件名称
   * @param {*} data - 传递的数据
   */
  emit: function (event, data) {
    if (!this.events[event]) return;

    const subscriptions = [...this.events[event]];

    if (this.debug) {
      console.log(`[EventBus] 触发事件: ${event}`, data);
    }

    // 遍历所有订阅者
    subscriptions.forEach((subscription) => {
      try {
        if (subscription.context) {
          subscription.callback.call(subscription.context, data);
        } else {
          subscription.callback(data);
        }

        // 如果是一次性订阅，触发后移除
        if (subscription.once) {
          this.off(event, subscription.id);
        }
      } catch (error) {
        console.error(`[EventBus] 事件处理错误: ${event}`, error);
      }
    });
  },

  /**
   * 触发一次事件（一次性订阅）
   * @param {string} event - 事件名称
   * @param {*} data - 传递的数据
   */
  once: function (event, callback) {
    return this.on(event, callback, { once: true });
  },

  /**
   * 条件触发事件（满足条件才触发）
   * @param {string} event - 事件名称
   * @param {*} data - 传递的数据
   * @param {Function} condition - 条件函数
   */
  emitIf: function (event, data, condition) {
    if (condition(data)) {
      this.emit(event, data);
    }
  },

  /**
   * 延迟触发事件
   * @param {string} event - 事件名称
   * @param {*} data - 传递的数据
   * @param {number} delay - 延迟时间(ms)
   */
  emitAfter: function (event, data, delay = 0) {
    setTimeout(() => {
      this.emit(event, data);
    }, delay);
  },

  /**
   * 获取事件订阅者数量
   * @param {string} event - 事件名称
   * @returns {number}
   */
  listenerCount: function (event) {
    return this.events[event] ? this.events[event].length : 0;
  },

  /**
   * 检查事件是否存在订阅者
   * @param {string} event - 事件名称
   * @returns {boolean}
   */
  hasListeners: function (event) {
    return this.listenerCount(event) > 0;
  },

  /**
   * 获取所有事件名称
   * @returns {Array}
   */
  getEvents: function () {
    return Object.keys(this.events);
  },

  /**
   * 启用调试模式
   */
  enableDebug: function () {
    this.debug = true;
  },

  /**
   * 禁用调试模式
   */
  disableDebug: function () {
    this.debug = false;
  },
};

// 常用事件常量
EventBus.EVENTS = {
  // 应用事件
  APP_INIT: "app:init",
  APP_READY: "app:ready",
  APP_ERROR: "app:error",
  APP_DESTROY: "app:destroy",

  // 模块事件
  MODULE_LOADED: "module:loaded",
  MODULE_UNLOADED: "module:unloaded",
  MODULE_ERROR: "module:error",

  // 数据事件
  DATA_UPDATED: "data:updated",
  DATA_FETCHED: "data:fetched",
  DATA_ERROR: "data:error",

  // UI事件
  UI_REFRESH: "ui:refresh",
  UI_RESIZE: "ui:resize",
  UI_THEME_CHANGE: "ui:theme:change",

  // 网络事件
  NETWORK_ONLINE: "network:online",
  NETWORK_OFFLINE: "network:offline",
  API_SUCCESS: "api:success",
  API_ERROR: "api:error",

  // WebSocket事件
  WS_CONNECTED: "ws:connected",
  WS_DISCONNECTED: "ws:disconnected",
  WS_MESSAGE: "ws:message",

  // 弹窗事件
  MODAL_OPENED: "modal:opened",
  MODAL_CLOSED: "modal:closed",

  // 通知事件
  NOTIFICATION_SHOW: "notification:show",
  NOTIFICATION_HIDE: "notification:hide",
};

// 导出到全局
window.EventBus = EventBus;
