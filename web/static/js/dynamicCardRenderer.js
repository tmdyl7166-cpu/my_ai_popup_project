/**
 * 动态卡片渲染器
 * 根据 api/mapping/api_mapping.json 中的 cardSpec 动态生成功能卡片
 * 实现数据驱动UI的核心逻辑
 */

class DynamicCardRenderer {
  constructor() {
    this.apiMapping = null;
    this.cards = new Map();
    this.container = null;
    this.eventBus = new EventTarget();
  }

  /**
   * 初始化渲染器
   * @param {string} containerSelector - 卡片容器选择器
   */
  async init(containerSelector) {
    this.container = document.querySelector(containerSelector);
    if (!this.container) {
      console.error("Card container not found:", containerSelector);
      return false;
    }

    // 加载API映射配置
    await this.loadApiMapping();

    // 初始化事件监听
    this.initEventListeners();

    console.log("DynamicCardRenderer initialized");
    return true;
  }

  /**
   * 加载API映射配置
   */
  async loadApiMapping() {
    try {
      const response = await fetch("/api/mapping/api_mapping.json");
      this.apiMapping = await response.json();
      console.log("API mapping loaded:", this.apiMapping.meta.version);
    } catch (error) {
      console.error("Failed to load API mapping:", error);
      // 使用备用配置
      this.apiMapping = this.getDefaultMapping();
    }
  }

  /**
   * 获取默认映射配置
   */
  getDefaultMapping() {
    return {
      meta: { version: "2.0.0" },
      mappings: {},
      functionCardSpecification: {
        requiredFields: {},
      },
    };
  }

  /**
   * 初始化事件监听
   */
  initEventListeners() {
    // 监听WebSocket消息
    window.addEventListener("ws_message", (event) => {
      this.handleWSMessage(event.detail);
    });
  }

  /**
   * 处理WebSocket消息
   */
  handleWSMessage(data) {
    const { type, payload } = data;

    switch (type) {
      case "status_update":
        this.updateCardStates(payload);
        break;
      case "script_result":
        this.updateScriptCard(payload);
        break;
      case "health_update":
        this.updateHealthCards(payload);
        break;
    }
  }

  /**
   * 渲染所有功能卡片
   */
  async renderAllCards() {
    if (!this.apiMapping || !this.apiMapping.mappings) {
      console.warn("API mapping not loaded");
      return;
    }

    this.container.innerHTML = "";
    this.cards.clear();

    // 按模块分组渲染
    for (const [moduleName, moduleData] of Object.entries(
      this.apiMapping.mappings,
    )) {
      for (const [endpointKey, endpointData] of Object.entries(moduleData)) {
        if (endpointData.cardSpec) {
          const card = this.createCard(moduleName, endpointKey, endpointData);
          this.container.appendChild(card.element);
          this.cards.set(`${moduleName}.${endpointKey}`, card);
        }
      }
    }

    // 发送卡片渲染完成事件
    this.eventBus.dispatchEvent(
      new CustomEvent("cardsRendered", {
        detail: { count: this.cards.size },
      }),
    );
  }

  /**
   * 创建功能卡片
   */
  createCard(moduleName, endpointKey, endpointData) {
    const spec = endpointData.cardSpec;

    // 创建卡片元素
    const card = document.createElement("div");
    card.className = "function-card";
    card.dataset.module = moduleName;
    card.dataset.endpoint = endpointKey;
    card.dataset.bubble = spec.bubbleDetection;

    // 状态图标
    const statusIcon = this.getStatusIcon(spec.status);

    // 标签渲染
    const tagsHtml = spec.tags
      .map(
        (tag) => `<span class="tag tag-${this.getTagClass(tag)}">${tag}</span>`,
      )
      .join("");

    // 动态参数区域
    const paramsHtml = this.renderInputParameters(spec.inputParameters);

    // 优化建议
    const optimizationHtml = spec.optimization
      ? `<div class="optimization-tip"><i class="fas fa-lightbulb"></i> ${spec.optimization}</div>`
      : "";

    card.innerHTML = `
            <div class="card-header">
                <div class="card-title">
                    <span class="status-indicator ${spec.status}">${statusIcon}</span>
                    <span class="name">${spec.frontendName}</span>
                </div>
                <div class="card-tags">${tagsHtml}</div>
            </div>
            <div class="card-body">
                <p class="description">${spec.description}</p>
                <div class="backend-endpoint">
                    <code>${endpointData.method} ${endpointData.endpoint}</code>
                </div>
                ${paramsHtml}
                ${optimizationHtml}
            </div>
            <div class="card-footer">
                <div class="card-actions" data-endpoint="${endpointData.endpoint}" data-method="${endpointData.method}">
                    ${this.renderActions(endpointData)}
                </div>
            </div>
        `;

    // 绑定事件
    this.bindCardEvents(card, moduleName, endpointKey, endpointData);

    return {
      element: card,
      moduleName,
      endpointKey,
      data: endpointData,
    };
  }

  /**
   * 获取状态图标
   */
  getStatusIcon(status) {
    const icons = {
      available: "🟢",
      partial: "🟡",
      unavailable: "🔴",
    };
    return icons[status] || "⚪";
  }

  /**
   * 获取标签样式类
   */
  getTagClass(tag) {
    const classes = {
      功能具体说明: "info",
      API接口: "primary",
      脚本运行逻辑: "success",
      DAG: "warning",
    };
    return classes[tag] || "secondary";
  }

  /**
   * 渲染输入参数区域
   */
  renderInputParameters(inputParameters) {
    if (!inputParameters) return "";

    let html = '<div class="input-parameters">';

    for (const [paramName, paramConfig] of Object.entries(inputParameters)) {
      html += this.renderParameterInput(paramName, paramConfig);
    }

    html += "</div>";
    return html;
  }

  /**
   * 渲染单个参数输入
   */
  renderParameterInput(paramName, config) {
    const id = `param_${paramName}`;
    let inputHtml = "";

    switch (config.type) {
      case "string":
        inputHtml = `<input type="text" id="${id}" class="form-control" placeholder="${config.description || paramName}">`;
        break;
      case "number":
        inputHtml = `<input type="number" id="${id}" class="form-control" placeholder="${config.description || paramName}">`;
        break;
      case "boolean":
        inputHtml = `
                    <div class="form-check">
                        <input type="checkbox" id="${id}" class="form-check-input">
                        <label class="form-check-label" for="${id}">${config.description || paramName}</label>
                    </div>
                `;
        break;
      case "select":
        const options = config.options
          .map((opt) => `<option value="${opt}">${opt}</option>`)
          .join("");
        inputHtml = `
                    <select id="${id}" class="form-select">
                        ${options}
                    </select>
                `;
        break;
      default:
        inputHtml = `<input type="text" id="${id}" class="form-control" placeholder="${config.description || paramName}">`;
    }

    return `
            <div class="parameter-item">
                <label for="${id}">${config.description || paramName}</label>
                ${inputHtml}
            </div>
        `;
  }

  /**
   * 渲染操作按钮
   */
  renderActions(endpointData) {
    const actions = [];

    if (endpointData.actions) {
      for (const [actionName, actionConfig] of Object.entries(
        endpointData.actions,
      )) {
        const btnClass = this.getActionButtonClass(actionName);
        const icon = this.getActionIcon(actionName);
        actions.push(`
                    <button class="btn ${btnClass}" data-action="${actionName}" data-endpoint="${actionConfig.endpoint}" data-method="${actionConfig.method}">
                        <i class="fas ${icon}"></i> ${this.getActionLabel(actionName)}
                    </button>
                `);
      }
    } else {
      // 默认查看详情按钮
      actions.push(`
                <button class="btn btn-outline-primary" data-action="view" data-endpoint="${endpointData.endpoint}" data-method="${endpointData.method}">
                    <i class="fas fa-eye"></i> 查看
                </button>
            `);
    }

    return actions.join("");
  }

  /**
   * 获取操作按钮样式类
   */
  getActionButtonClass(actionName) {
    const classes = {
      run: "btn-success",
      start: "btn-success",
      stop: "btn-danger",
      view: "btn-outline-primary",
      test: "btn-info",
    };
    return classes[actionName] || "btn-secondary";
  }

  /**
   * 获取操作图标
   */
  getActionIcon(actionName) {
    const icons = {
      run: "fa-play",
      start: "fa-play",
      stop: "fa-stop",
      view: "fa-eye",
      test: "fa-vial",
    };
    return icons[actionName] || "fa-cog";
  }

  /**
   * 获取操作标签
   */
  getActionLabel(actionName) {
    const labels = {
      run: "运行",
      start: "启动",
      stop: "停止",
      view: "查看",
      test: "测试",
    };
    return labels[actionName] || actionName;
  }

  /**
   * 绑定卡片事件
   */
  bindCardEvents(card, moduleName, endpointKey, endpointData) {
    // 冒泡检测
    card.addEventListener("click", (event) => {
      const target = event.target.closest("[data-action]");
      if (target) {
        this.handleAction(target, endpointData);
        this.dispatchBubbleEvent("click", {
          moduleName,
          endpointKey,
          action: target.dataset.action,
        });
      }
    });

    card.addEventListener("submit", (event) => {
      if (event.target.classList.contains("card-form")) {
        this.handleFormSubmit(event, endpointData);
        this.dispatchBubbleEvent("submit", { moduleName, endpointKey });
      }
    });
  }

  /**
   * 处理操作按钮点击
   */
  handleAction(button, endpointData) {
    const action = button.dataset.action;
    const endpoint = button.dataset.endpoint;
    const method = button.dataset.method;

    switch (action) {
      case "run":
      case "start":
        this.runEndpoint(endpoint, method);
        break;
      case "stop":
        this.stopExecution(endpoint);
        break;
      case "view":
        this.viewDetails(endpointData);
        break;
      case "test":
        this.testEndpoint(endpoint, method);
        break;
    }
  }

  /**
   * 执行API调用
   */
  async runEndpoint(endpoint, method = "POST") {
    // 从卡片中收集参数
    const params = this.collectCardParameters(endpoint);

    try {
      const response = await fetch(endpoint, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });

      const result = await response.json();

      if (response.ok) {
        this.showNotification("操作执行成功", "success");
        this.eventBus.dispatchEvent(
          new CustomEvent("actionComplete", {
            detail: { endpoint, result },
          }),
        );
      } else {
        this.showNotification(result.message || "操作执行失败", "error");
      }
    } catch (error) {
      console.error("Action failed:", error);
      this.showNotification("网络错误，请稍后重试", "error");
    }
  }

  /**
   * 收集卡片参数
   */
  collectCardParameters(endpoint) {
    const params = {};
    const container = document.querySelector(`[data-endpoint="${endpoint}"]`);

    if (container) {
      const inputs = container.querySelectorAll(
        ".input-parameters input, .input-parameters select",
      );
      inputs.forEach((input) => {
        const paramName = input.id.replace("param_", "");
        if (input.type === "checkbox") {
          params[paramName] = input.checked;
        } else {
          params[paramName] = input.value;
        }
      });
    }

    return params;
  }

  /**
   * 停止执行
   */
  async stopExecution(endpoint) {
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ force: false }),
      });

      if (response.ok) {
        this.showNotification("已停止执行", "info");
      }
    } catch (error) {
      console.error("Stop failed:", error);
    }
  }

  /**
   * 查看详情
   */
  viewDetails(endpointData) {
    this.eventBus.dispatchEvent(
      new CustomEvent("viewDetails", {
        detail: { data: endpointData },
      }),
    );

    // 打开详情模态框
    this.showDetailModal(endpointData);
  }

  /**
   * 测试端点
   */
  async testEndpoint(endpoint, method) {
    this.showNotification("正在测试...", "info");

    try {
      const response = await fetch(endpoint, { method });
      const result = await response.json();

      this.showResultModal("测试结果", JSON.stringify(result, null, 2));
    } catch (error) {
      this.showNotification("测试失败: " + error.message, "error");
    }
  }

  /**
   * 显示详情模态框
   */
  showDetailModal(data) {
    const modal = document.getElementById("cardDetailModal");
    if (!modal) {
      console.warn("Detail modal not found");
      return;
    }

    const content = document.getElementById("cardDetailContent");
    content.innerHTML = `
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;

    new bootstrap.Modal(modal).show();
  }

  /**
   * 显示结果模态框
   */
  showResultModal(title, content) {
    const modal = document.getElementById("resultModal");
    if (!modal) return;

    document.getElementById("result-title").textContent = title;
    document.getElementById("result-content").textContent = content;
    new bootstrap.Modal(modal).show();
  }

  /**
   * 显示通知
   */
  showNotification(message, type = "info") {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText =
      "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

    document.body.appendChild(alertDiv);

    setTimeout(() => {
      if (alertDiv.parentNode) alertDiv.remove();
    }, 3000);
  }

  /**
   * 派发冒泡事件
   */
  dispatchBubbleEvent(eventType, detail) {
    window.dispatchEvent(
      new CustomEvent("bubbleEvent", {
        detail: { eventType, timestamp: Date.now(), ...detail },
      }),
    );
  }

  /**
   * 更新卡片状态
   */
  updateCardStates(states) {
    for (const [key, state] of Object.entries(states)) {
      const card = this.cards.get(key);
      if (card) {
        this.updateCardState(card.element, state);
      }
    }
  }

  /**
   * 更新单个卡片状态
   */
  updateCardState(card, state) {
    if (state.status) {
      const indicator = card.querySelector(".status-indicator");
      if (indicator) {
        indicator.className = `status-indicator ${state.status}`;
      }
    }
  }

  /**
   * 更新脚本卡片
   */
  updateScriptCard(payload) {
    const key = `scripts.${payload.script}`;
    const card = this.cards.get(key);
    if (card) {
      const progress = card.element.querySelector(".progress-bar");
      if (progress && payload.progress !== undefined) {
        progress.style.width = `${payload.progress}%`;
      }
    }
  }

  /**
   * 更新健康状态卡片
   */
  updateHealthCards(payload) {
    for (const [key, health] of Object.entries(payload)) {
      const card = this.cards.get(key);
      if (card) {
        const status = health.healthy ? "available" : "unavailable";
        this.updateCardState(card.element, { status });
      }
    }
  }

  /**
   * 获取所有卡片
   */
  getAllCards() {
    return this.cards;
  }

  /**
   * 获取单个卡片
   */
  getCard(moduleName, endpointKey) {
    return this.cards.get(`${moduleName}.${endpointKey}`);
  }

  /**
   * 刷新所有卡片数据
   */
  async refreshAllCards() {
    const promises = [];

    for (const [key, card] of this.cards) {
      if (card.data.cardSpec.status === "available") {
        promises.push(this.refreshCard(card));
      }
    }

    await Promise.all(promises);
  }

  /**
   * 刷新单个卡片
   */
  async refreshCard(card) {
    try {
      const response = await fetch(card.data.endpoint);
      const data = await response.json();
      this.updateCardState(card.element, data);
    } catch (error) {
      console.error("Failed to refresh card:", card.endpointKey, error);
    }
  }
}

// 导出实例
window.dynamicCardRenderer = new DynamicCardRenderer();
