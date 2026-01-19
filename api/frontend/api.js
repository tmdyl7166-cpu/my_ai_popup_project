/**
 * API - 前端统一API调用封装
 * 提供RESTful API调用、自动鉴权、错误处理
 */

const API = {
  // 基础配置
  config: {
    baseUrl: "",
    timeout: 30000,
    retries: 0,
    authHeader: "Authorization",
    authPrefix: "Bearer",
    defaultHeaders: {
      "Content-Type": "application/json",
    },
    withCredentials: true,
  },

  // 请求ID生成器
  requestIdCounter: 0,

  /**
   * 初始化
   */
  init: function (options = {}) {
    this.config = { ...this.config, ...options };
    console.log("[API] 初始化API模块");

    // 从localStorage获取token
    this.loadToken();
  },

  /**
   * 加载存储的token
   */
  loadToken: function () {
    const token = localStorage.getItem("auth_token");
    if (token) {
      this.token = token;
    }
  },

  /**
   * 设置认证token
   */
  setToken: function (token) {
    this.token = token;
    localStorage.setItem("auth_token", token);
  },

  /**
   * 清除认证token
   */
  clearToken: function () {
    delete this.token;
    localStorage.removeItem("auth_token");
  },

  /**
   * 获取请求头
   */
  getHeaders: function (additionalHeaders = {}) {
    const headers = {
      ...this.config.defaultHeaders,
      ...additionalHeaders,
    };

    // 添加认证头
    if (this.token) {
      headers[this.config.authHeader] =
        `${this.config.authPrefix} ${this.token}`;
    }

    // 添加CSRF头
    if (typeof SafeUtils !== "undefined") {
      const csrfHeaders = SafeUtils.getCsrfHeaders();
      Object.assign(headers, csrfHeaders);
    }

    return headers;
  },

  /**
   * 发起请求
   */
  request: async function (options) {
    const {
      method = "GET",
      url,
      data,
      headers = {},
      timeout = this.config.timeout,
      retries = this.config.retries,
    } = options;

    const requestId = ++this.requestIdCounter;

    // 构建完整URL
    const fullUrl = this.config.baseUrl + url;

    // 记录请求
    console.log(`[API] 请求 #${requestId}: ${method} ${fullUrl}`);

    // 构建请求配置
    const fetchOptions = {
      method,
      headers: this.getHeaders(headers),
      credentials: this.config.withCredentials ? "include" : "same-origin",
    };

    // 添加请求体
    if (data && method !== "GET" && method !== "HEAD") {
      fetchOptions.body = JSON.stringify(data);
    }

    // 超时处理
    const controller = new AbortController();
    fetchOptions.signal = controller.signal;

    const timeoutId = setTimeout(() => {
      controller.abort();
    }, timeout);

    try {
      const response = await fetch(fullUrl, fetchOptions);
      clearTimeout(timeoutId);

      // 处理响应
      const result = await this.handleResponse(response, requestId);

      return result;
    } catch (error) {
      clearTimeout(timeoutId);

      // 处理重试
      if (retries > 0 && this.isRetryableError(error)) {
        console.log(`[API] 请求 #${requestId} 重试中 (剩余 ${retries} 次)`);
        return this.request({ ...options, retries: retries - 1 });
      }

      throw this.handleError(error, requestId);
    }
  },

  /**
   * 处理响应
   */
  handleResponse: async function (response, requestId) {
    const contentType = response.headers.get("content-type");

    // 解析响应数据
    let data;
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // 检查HTTP状态
    if (!response.ok) {
      // 处理401未授权
      if (response.status === 401) {
        this.clearToken();
        if (typeof EventBus !== "undefined") {
          EventBus.emit("auth:unauthorized");
        }
      }

      // 抛出错误
      throw {
        status: response.status,
        statusText: response.statusText,
        data: data,
        message: data?.message || `HTTP ${response.status} Error`,
      };
    }

    // 记录成功响应
    console.log(`[API] 响应 #${requestId}: 成功`);

    return data;
  },

  /**
   * 处理错误
   */
  handleError: function (error, requestId) {
    console.error(`[API] 请求 #${requestId} 错误:`, error);

    // 处理AbortError（超时）
    if (error.name === "AbortError") {
      return {
        status: 0,
        statusText: "Request Timeout",
        message: "请求超时，请稍后重试",
      };
    }

    // 返回标准化错误
    return {
      status: error.status || 0,
      statusText: error.statusText || "Network Error",
      message: error.message || "网络请求失败",
      data: error.data || null,
    };
  },

  /**
   * 检查是否可重试
   */
  isRetryableError: function (error) {
    // 超时可重试
    if (error.name === "AbortError") return true;

    // 5xx服务器错误可重试
    if (error.status && error.status >= 500) return true;

    // 网络错误可重试
    if (error.status === 0) return true;

    return false;
  },

  // === 快捷方法 ===

  /**
   * GET请求
   */
  get: function (url, params = {}, options = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request({ ...options, method: "GET", url: fullUrl });
  },

  /**
   * POST请求
   */
  post: function (url, data = {}, options = {}) {
    return this.request({ ...options, method: "POST", url, data });
  },

  /**
   * PUT请求
   */
  put: function (url, data = {}, options = {}) {
    return this.request({ ...options, method: "PUT", url, data });
  },

  /**
   * PATCH请求
   */
  patch: function (url, data = {}, options = {}) {
    return this.request({ ...options, method: "PATCH", url, data });
  },

  /**
   * DELETE请求
   */
  delete: function (url, options = {}) {
    return this.request({ ...options, method: "DELETE", url });
  },

  /**
   * 文件上传
   */
  upload: async function (url, file, onProgress, options = {}) {
    const formData = new FormData();
    formData.append("file", file);

    const requestId = ++this.requestIdCounter;
    console.log(`[API] 上传 #${requestId}: ${file.name}`);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // 进度处理
      if (onProgress && xhr.upload) {
        xhr.upload.addEventListener("progress", (event) => {
          if (event.lengthComputable) {
            const percent = Math.round((event.loaded / event.total) * 100);
            onProgress(percent);
          }
        });
      }

      // 完成处理
      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log(`[API] 上传 #${requestId} 完成`);
            resolve(data);
          } catch (e) {
            resolve(xhr.responseText);
          }
        } else {
          reject(
            this.handleError(
              {
                status: xhr.status,
                statusText: xhr.statusText,
                data: xhr.responseText,
              },
              requestId,
            ),
          );
        }
      });

      // 错误处理
      xhr.addEventListener("error", () => {
        reject(
          this.handleError(
            {
              status: 0,
              statusText: "Network Error",
            },
            requestId,
          ),
        );
      });

      // 超时处理
      xhr.timeout = options.timeout || this.config.timeout;
      xhr.ontimeout = () => {
        reject(
          this.handleError(
            {
              status: 0,
              statusText: "Upload Timeout",
            },
            requestId,
          ),
        );
      };

      // 发起请求
      xhr.open("POST", this.config.baseUrl + url);

      // 添加认证头
      if (this.token) {
        xhr.setRequestHeader(
          this.config.authHeader,
          `${this.config.authPrefix} ${this.token}`,
        );
      }

      xhr.send(formData);
    });
  },

  /**
   * 批量请求
   */
  all: async function (requests) {
    const promises = requests.map((req) => {
      if (typeof req === "string") {
        return this.get(req);
      }
      const { url, method = "GET", data } = req;
      return this.request({ url, method, data });
    });

    return Promise.all(promises);
  },

  /**
   * 竞速请求（返回最快的）
   */
  race: async function (requests) {
    const promises = requests.map((req) => {
      if (typeof req === "string") {
        return this.get(req);
      }
      const { url, method = "GET", data } = req;
      return this.request({ url, method, data });
    });

    return Promise.race(promises);
  },

  /**
   * 健康检查
   */
  healthCheck: async function () {
    return this.get("/api/health");
  },

  /**
   * 获取项目状态
   */
  getProjectStatus: function () {
    return this.get("/api/project/status");
  },

  /**
   * 获取系统资源
   */
  getSystemResources: function () {
    return this.get("/api/system/resources");
  },
};

// 导出到全局
window.API = API;
