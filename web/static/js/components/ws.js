/**
 * WS (WebSocket Pipeline) - WebSocket管道连接
 * 提供任务进度、日志流订阅功能
 */

const WS = {
  // 连接配置
  config: {
    baseUrl: "",
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    heartbeatInterval: 30000,
    heartbeatTimeout: 5000,
  },

  // Socket实例
  socket: null,
  // 连接状态
  connected: false,
  // 重新连接计数
  reconnectAttempts: 0,
  // 心跳定时器
  heartbeatTimer: null,
  // 回调函数缓存
  callbacks: {},
  // 订阅缓存
  subscriptions: {},

  /**
   * 初始化
   */
  init: function (options = {}) {
    this.config = { ...this.config, ...options };
    console.log("[WS] 初始化WebSocket模块");

    // 获取基础URL
    this.config.baseUrl = this.getBaseUrl();
  },

  /**
   * 获取基础URL
   */
  getBaseUrl: function () {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}`;
  },

  /**
   * 建立连接
   */
  connect: function () {
    if (this.socket && this.connected) {
      console.log("[WS] 连接已存在");
      return Promise.resolve(this.socket);
    }

    return new Promise((resolve, reject) => {
      try {
        const url = `${this.config.baseUrl}/ws`;
        console.log("[WS] 尝试连接:", url);

        this.socket = new WebSocket(url);

        // 连接打开
        this.socket.onopen = (event) => {
          console.log("[WS] 连接成功");
          this.connected = true;
          this.reconnectAttempts = 0;

          // 启动心跳
          this.startHeartbeat();

          // 恢复订阅
          this.resubscribeAll();

          // 发送事件
          if (typeof EventBus !== "undefined") {
            EventBus.emit("ws:connected", event);
          }

          resolve(this.socket);
        };

        // 接收消息
        this.socket.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        // 连接错误
        this.socket.onerror = (error) => {
          console.error("[WS] 连接错误:", error);
          reject(error);

          if (typeof EventBus !== "undefined") {
            EventBus.emit("ws:error", error);
          }
        };

        // 连接关闭
        this.socket.onclose = (event) => {
          console.log("[WS] 连接关闭:", event.code, event.reason);
          this.connected = false;

          // 停止心跳
          this.stopHeartbeat();

          // 尝试重连
          if (event.code !== 1000) {
            this.attemptReconnect();
          }

          // 发送事件
          if (typeof EventBus !== "undefined") {
            EventBus.emit("ws:disconnected", event);
          }
        };
      } catch (error) {
        console.error("[WS] 连接失败:", error);
        reject(error);
      }
    });
  },

  /**
   * 尝试重连
   */
  attemptReconnect: function () {
    if (this.reconnectAttempts >= this.config.reconnectionAttempts) {
      console.error("[WS] 重连次数已达上限");
      return;
    }

    this.reconnectAttempts++;
    const delay =
      this.config.reconnectionDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`[WS] ${this.reconnectAttempts}次重连尝试，${delay}ms后执行`);

    setTimeout(() => {
      this.connect().catch(() => {});
    }, delay);
  },

  /**
   * 关闭连接
   */
  disconnect: function () {
    if (this.socket) {
      this.socket.close(1000, "Client disconnect");
      this.socket = null;
      this.connected = false;
    }
  },

  /**
   * 发送消息
   */
  send: function (data) {
    if (!this.socket || !this.connected) {
      console.warn("[WS] 未连接，无法发送消息");
      return false;
    }

    const message = typeof data === "string" ? data : JSON.stringify(data);
    this.socket.send(message);
    return true;
  },

  /**
   * 处理消息
   */
  handleMessage: function (data) {
    try {
      const message = typeof data === "string" ? JSON.parse(data) : data;

      // 处理不同类型的消息
      switch (message.type) {
        case "heartbeat":
          this.handleHeartbeat(message);
          break;

        case "progress":
          this.handleProgress(message);
          break;

        case "log":
          this.handleLog(message);
          break;

        case "data":
          this.handleData(message);
          break;

        case "error":
          this.handleError(message);
          break;

        default:
          this.handleCustomMessage(message);
      }
    } catch (error) {
      console.error("[WS] 消息处理错误:", error);
    }
  },

  /**
   * 处理心跳
   */
  handleHeartbeat: function (message) {
    // 响应心跳
    this.send({ type: "heartbeat", timestamp: Date.now() });
  },

  /**
   * 处理进度更新
   */
  handleProgress: function (message) {
    const { taskId, progress, status, detail } = message;

    // 触发进度事件
    if (typeof EventBus !== "undefined") {
      EventBus.emit("progress:update", { taskId, progress, status, detail });
    }

    // 调用注册的回掉
    if (this.callbacks[`progress:${taskId}`]) {
      this.callbacks[`progress:${taskId}`]({ progress, status, detail });
    }
  },

  /**
   * 处理日志
   */
  handleLog: function (message) {
    const { taskId, level, content, timestamp } = message;

    // 触发日志事件
    if (typeof EventBus !== "undefined") {
      EventBus.emit("log:received", { taskId, level, content, timestamp });
    }

    // 调用注册的回调
    if (this.callbacks[`log:${taskId}`]) {
      this.callbacks[`log:${taskId}`]({ level, content, timestamp });
    }
  },

  /**
   * 处理数据更新
   */
  handleData: function (message) {
    const { channel, data } = message;

    // 触发数据事件
    if (typeof EventBus !== "undefined") {
      EventBus.emit("data:received", { channel, data });
    }

    // 调用注册的回调
    if (this.callbacks[`data:${channel}`]) {
      this.callbacks[`data:${channel}`](data);
    }
  },

  /**
   * 处理错误
   */
  handleError: function (message) {
    const { taskId, error, code } = message;

    // 触发错误事件
    if (typeof EventBus !== "undefined") {
      EventBus.emit("ws:error", message);
    }

    // 调用注册的回调
    if (this.callbacks[`error:${taskId}`]) {
      this.callbacks[`error:${taskId}`]({ error, code });
    }
  },

  /**
   * 处理自定义消息
   */
  handleCustomMessage: function (message) {
    // 触发自定义消息事件
    if (typeof EventBus !== "undefined") {
      EventBus.emit("ws:message", message);
    }

    // 调用注册的回调
    if (this.callbacks[`message:${message.type}`]) {
      this.callbacks[`message:${message.type}`](message);
    }
  },

  /**
   * 启动心跳
   */
  startHeartbeat: function () {
    this.stopHeartbeat();

    this.heartbeatTimer = setInterval(() => {
      if (this.connected) {
        this.send({ type: "heartbeat", timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  },

  /**
   * 停止心跳
   */
  stopHeartbeat: function () {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  },

  // === 订阅API ===

  /**
   * 订阅任务进度
   * @param {string} taskId - 任务ID
   * @param {Function} callback - 回调函数
   */
  subscribeProgress: function (taskId, callback) {
    this.callbacks[`progress:${taskId}`] = callback;
    this.subscriptions[`progress:${taskId}`] = { taskId, type: "progress" };

    // 发送订阅消息
    this.send({
      type: "subscribe",
      channel: "progress",
      taskId: taskId,
    });

    return () => this.unsubscribeProgress(taskId);
  },

  /**
   * 取消订阅进度
   */
  unsubscribeProgress: function (taskId) {
    delete this.callbacks[`progress:${taskId}`];
    delete this.subscriptions[`progress:${taskId}`];

    this.send({
      type: "unsubscribe",
      channel: "progress",
      taskId: taskId,
    });
  },

  /**
   * 订阅任务日志
   * @param {string} taskId - 任务ID
   * @param {Function} callback - 回调函数
   */
  subscribeLogs: function (taskId, callback) {
    this.callbacks[`log:${taskId}`] = callback;
    this.subscriptions[`log:${taskId}`] = { taskId, type: "log" };

    this.send({
      type: "subscribe",
      channel: "log",
      taskId: taskId,
    });

    return () => this.unsubscribeLogs(taskId);
  },

  /**
   * 取消订阅日志
   */
  unsubscribeLogs: function (taskId) {
    delete this.callbacks[`log:${taskId}`];
    delete this.subscriptions[`log:${taskId}`];

    this.send({
      type: "unsubscribe",
      channel: "log",
      taskId: taskId,
    });
  },

  /**
   * 订阅数据通道
   * @param {string} channel - 通道名
   * @param {Function} callback - 回调函数
   */
  subscribeData: function (channel, callback) {
    this.callbacks[`data:${channel}`] = callback;
    this.subscriptions[`data:${channel}`] = { channel, type: "data" };

    this.send({
      type: "subscribe",
      channel: "data",
      target: channel,
    });

    return () => this.unsubscribeData(channel);
  },

  /**
   * 取消订阅数据
   */
  unsubscribeData: function (channel) {
    delete this.callbacks[`data:${channel}`];
    delete this.subscriptions[`data:${channel}`];

    this.send({
      type: "unsubscribe",
      channel: "data",
      target: channel,
    });
  },

  /**
   * 订阅任务（进度+日志）
   * @param {string} taskId - 任务ID
   * @param {Object} callbacks - 回调函数对象
   */
  subscribeTask: function (taskId, callbacks = {}) {
    const unsubProgress = callbacks.onProgress
      ? this.subscribeProgress(taskId, callbacks.onProgress)
      : null;
    const unsubLogs = callbacks.onLog
      ? this.subscribeLogs(taskId, callbacks.onLog)
      : null;
    const unsubError = callbacks.onError
      ? this.subscribe(`error:${taskId}`, callbacks.onError)
      : null;

    return () => {
      if (unsubProgress) unsubProgress();
      if (unsubLogs) unsubLogs();
      if (unsubError) this.unsubscribe(`error:${taskId}`);
    };
  },

  /**
   * 恢复所有订阅
   */
  resubscribeAll: function () {
    Object.values(this.subscriptions).forEach((sub) => {
      if (sub.type === "progress") {
        this.send({
          type: "subscribe",
          channel: "progress",
          taskId: sub.taskId,
        });
      } else if (sub.type === "log") {
        this.send({
          type: "subscribe",
          channel: "log",
          taskId: sub.taskId,
        });
      } else if (sub.type === "data") {
        this.send({
          type: "subscribe",
          channel: "data",
          target: sub.channel,
        });
      }
    });
  },

  /**
   * 取消所有订阅
   */
  unsubscribeAll: function () {
    this.send({ type: "unsubscribe", all: true });
    this.callbacks = {};
    this.subscriptions = {};
  },

  /**
   * 注册自定义消息回调
   */
  subscribe: function (key, callback) {
    this.callbacks[key] = callback;
    return () => delete this.callbacks[key];
  },

  /**
   * 获取连接状态
   */
  isConnected: function () {
    return this.connected;
  },

  /**
   * 获取订阅列表
   */
  getSubscriptions: function () {
    return Object.values(this.subscriptions);
  },

  /**
   * 快捷方法：连接Pipeline WS
   */
  connectPipelineWS: function (taskId) {
    return {
      onProgress: (callback) => this.subscribeProgress(taskId, callback),
      onLog: (callback) => this.subscribeLogs(taskId, callback),
      onError: (callback) => this.subscribe(`error:${taskId}`, callback),
      unsubscribe: () => {
        this.unsubscribeProgress(taskId);
        this.unsubscribeLogs(taskId);
        this.unsubscribe(`error:${taskId}`);
      },
    };
  },
};

// 导出到全局
window.WS = WS;
