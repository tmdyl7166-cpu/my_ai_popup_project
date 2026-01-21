/**
 * 冒泡事件监控器
 * 监听并上报所有用户交互事件，支持数据驱动UI的联动分析
 */

class BubbleMonitor {
  constructor() {
    this.events = [];
    this.listeners = new Map();
    this.enabled = true;
    this.batchSize = 100;
    this.batchInterval = 5000;
    this.batchTimer = null;
    this.selectorConfig = {
      bubble: "[data-bubble]",
      module: "[data-module]",
      action: "[data-action]",
      card: ".function-card",
    };
  }

  /**
   * 初始化监控器
   */
  init() {
    if (!this.enabled) {
      console.log("BubbleMonitor is disabled");
      return;
    }

    // 绑定全局事件监听
    this.bindGlobalEvents();

    // 启动批量上报
    this.startBatchReporting();

    console.log("BubbleMonitor initialized");
  }

  /**
   * 绑定全局事件
   */
  bindGlobalEvents() {
    // 点击事件
    document.addEventListener(
      "click",
      (event) => {
        this.handleEvent("click", event);
      },
      true,
    );

    // 表单提交事件
    document.addEventListener(
      "submit",
      (event) => {
        this.handleEvent("submit", event);
      },
      true,
    );

    // 输入事件
    document.addEventListener(
      "input",
      (event) => {
        this.handleEvent("input", event);
      },
      true,
    );

    // 变化事件
    document.addEventListener(
      "change",
      (event) => {
        this.handleEvent("change", event);
      },
      true,
    );

    // 焦点事件
    document.addEventListener(
      "focus",
      (event) => {
        this.handleEvent("focus", event);
      },
      true,
    );

    document.addEventListener(
      "blur",
      (event) => {
        this.handleEvent("blur", event);
      },
      true,
    );
  }

  /**
   * 处理事件
   */
  handleEvent(type, event) {
    const target = event.target;

    // 检查是否是需要监控的元素
    if (!this.shouldMonitor(target)) {
      return;
    }

    // 获取事件上下文
    const context = this.getEventContext(target, type);

    // 创建事件记录
    const record = {
      id: this.generateId(),
      type,
      timestamp: Date.now(),
      element: {
        id: target.id || null,
        tagName: target.tagName,
        className: this.getShortClassName(target.className),
        text: this.getShortText(target.textContent),
        attributes: this.extractRelevantAttributes(target),
      },
      context,
      page: {
        url: window.location.pathname,
        title: document.title,
      },
      session: this.getSessionInfo(),
    };

    // 存储事件
    this.events.push(record);

    // 触发本地监听器
    this.notifyListeners(type, record);

    // 如果是卡片相关事件，发送到后端
    if (context.module) {
      this.reportToBackend(record);
    }
  }

  /**
   * 检查是否需要监控
   */
  shouldMonitor(target) {
    return (
      target.matches(this.selectorConfig.bubble) ||
      target.matches(this.selectorConfig.module) ||
      target.matches(this.selectorConfig.action) ||
      target.closest(this.selectorConfig.card)
    );
  }

  /**
   * 获取事件上下文
   */
  getEventContext(target, eventType) {
    const card = target.closest(this.selectorConfig.card);
    const actionBtn = target.closest("[data-action]");
    const module = target.closest("[data-module]");

    return {
      card: card
        ? {
            module: card.dataset.module,
            endpoint: card.dataset.endpoint,
          }
        : null,
      action: actionBtn
        ? {
            name: actionBtn.dataset.action,
            endpoint: actionBtn.dataset.endpoint,
          }
        : null,
      module: module ? module.dataset.module : null,
      eventType,
    };
  }

  /**
   * 提取相关属性
   */
  extractRelevantAttributes(element) {
    const attrs = {};
    const relevantAttrs = [
      "data-action",
      "data-module",
      "data-endpoint",
      "data-method",
      "data-status",
      "data-bubble",
    ];

    relevantAttrs.forEach((attr) => {
      if (element.dataset[attr]) {
        attrs[attr] = element.dataset[attr];
      }
    });

    return attrs;
  }

  /**
   * 获取简化的类名
   */
  getShortClassName(className) {
    if (!className) return "";
    return className.split(" ").slice(0, 3).join(" ");
  }

  /**
   * 获取简化的文本内容
   */
  getShortText(text) {
    if (!text) return "";
    return text.trim().substring(0, 50);
  }

  /**
   * 获取会话信息
   */
  getSessionInfo() {
    return {
      sessionId: this.getCookie("session_id") || this.generateId(),
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
      },
    };
  }

  /**
   * 生成唯一ID
   */
  generateId() {
    return (
      "evt_" + Date.now().toString(36) + Math.random().toString(36).substr(2, 9)
    );
  }

  /**
   * 获取Cookie
   */
  getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  /**
   * 启动批量上报
   */
  startBatchReporting() {
    this.batchTimer = setInterval(() => {
      this.flushEvents();
    }, this.batchInterval);
  }

  /**
   * 停止批量上报
   */
  stopBatchReporting() {
    if (this.batchTimer) {
      clearInterval(this.batchTimer);
      this.batchTimer = null;
    }
  }

  /**
   * 刷新事件到后端
   */
  async flushEvents() {
    if (this.events.length === 0) return;

    const eventsToSend = this.events.splice(0, this.batchSize);

    try {
      await fetch("/api/bubbles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          events: eventsToSend,
          batch: true,
        }),
      });
    } catch (error) {
      // 如果失败，重新加入队列
      this.events.unshift(...eventsToSend);
      console.error("Failed to report bubbles:", error);
    }
  }

  /**
   * 上报单个事件到后端
   */
  async reportToBackend(record) {
    try {
      await fetch("/api/bubbles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(record),
      });
    } catch (error) {
      console.error("Failed to report bubble event:", error);
    }
  }

  /**
   * 添加事件监听器
   */
  addListener(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  /**
   * 移除事件监听器
   */
  removeListener(eventType, callback) {
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * 通知监听器
   */
  notifyListeners(eventType, record) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach((callback) => {
        try {
          callback(record);
        } catch (error) {
          console.error("Listener error:", error);
        }
      });
    }
  }

  /**
   * 获取事件历史
   */
  getEventHistory(filter = {}) {
    let filtered = [...this.events];

    if (filter.type) {
      filtered = filtered.filter((e) => e.type === filter.type);
    }

    if (filter.module) {
      filtered = filtered.filter((e) => e.context.module === filter.module);
    }

    if (filter.startTime) {
      filtered = filtered.filter((e) => e.timestamp >= filter.startTime);
    }

    if (filter.endTime) {
      filtered = filtered.filter((e) => e.timestamp <= filter.endTime);
    }

    return filtered;
  }

  /**
   * 获取统计信息
   */
  getStatistics() {
    const stats = {
      total: this.events.length,
      byType: {},
      byModule: {},
      recent: [],
    };

    // 按类型统计
    this.events.forEach((event) => {
      stats.byType[event.type] = (stats.byType[event.type] || 0) + 1;

      if (event.context.module) {
        stats.byModule[event.context.module] =
          (stats.byModule[event.context.module] || 0) + 1;
      }
    });

    // 最近10个事件
    stats.recent = this.events.slice(-10).map((e) => ({
      type: e.type,
      module: e.context.module,
      timestamp: e.timestamp,
    }));

    return stats;
  }

  /**
   * 清除所有事件
   */
  clearEvents() {
    this.events = [];
  }

  /**
   * 启用/禁用监控
   */
  setEnabled(enabled) {
    this.enabled = enabled;
    if (enabled) {
      this.init();
    } else {
      this.stopBatchReporting();
    }
  }

  /**
   * 销毁监控器
   */
  destroy() {
    this.stopBatchReporting();
    this.flushEvents();
    this.listeners.clear();
    this.events = [];
  }
}

// 导出实例
window.bubbleMonitor = new BubbleMonitor();
