/**
 * ModalStack - 统一弹窗堆栈管理
 * 管理所有layer.open，解决嵌套与内存泄漏问题
 */

const ModalStack = {
  // 弹窗堆栈
  stack: [],
  // Z-index基准值
  baseZIndex: 1040,
  // 增量Z-index
  zIndexIncrement: 20,
  // 当前Z-index
  currentZIndex: 1040,

  /**
   * 初始化
   */
  init: function () {
    console.log("[ModalStack] 初始化弹窗堆栈管理器");
    this.createModalContainer();
    this.bindGlobalEvents();
  },

  /**
   * 创建模态框容器
   */
  createModalContainer: function () {
    if (document.getElementById("modalStackContainer")) return;

    const container = document.createElement("div");
    container.id = "modalStackContainer";
    container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: ${this.baseZIndex - 1};
        `;
    document.body.appendChild(container);
  },

  /**
   * 绑定全局事件
   */
  bindGlobalEvents: function () {
    // ESC键关闭顶部弹窗
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.closeTop();
      }
    });

    // 点击遮罩层不关闭（由各弹窗自行处理）
  },

  /**
   * 打开弹窗
   * @param {Object} options - layui layer.open选项
   * @returns {string} 弹窗ID
   */
  open: function (options = {}) {
    const id =
      options.id ||
      `modal_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const zIndex = this.currentZIndex;

    // 更新Z-index
    this.currentZIndex += this.zIndexIncrement;

    // 合并选项
    const mergedOptions = {
      ...options,
      id: id,
      zIndex: zIndex,
      success: (layero, index) => {
        // 记录弹窗
        this.stack.push({
          id: id,
          index: index,
          layer: layero,
          options: options,
          timestamp: Date.now(),
        });

        // 标记为顶层
        document.querySelectorAll(".layui-layer").forEach((layer) => {
          layer.classList.remove("modal-stack-top");
        });
        layero.addClass("modal-stack-top");

        // 绑定关闭事件
        this.bindCloseEvents(layero, id);

        // 调用原始success
        if (options.success) {
          options.success(layero, index);
        }

        // 发送事件
        if (typeof EventBus !== "undefined") {
          EventBus.emit("modal:opened", { id, options });
        }
      },
      end: () => {
        // 移除弹窗记录
        this.remove(id);

        // 调用原始end
        if (options.end) {
          options.end();
        }

        // 发送事件
        if (typeof EventBus !== "undefined") {
          EventBus.emit("modal:closed", { id, options });
        }
      },
    };

    // 调用layer.open
    if (typeof layer !== "undefined") {
      layer.open(mergedOptions);
    } else {
      // 降级为原生模态框
      this.openNativeModal(mergedOptions);
    }

    return id;
  },

  /**
   * 打开原生模态框（降级方案）
   */
  openNativeModal: function (options) {
    const {
      type = 1,
      title = "提示",
      content = "",
      area = ["500px", "300px"],
      id,
      btn = ["确定", "取消"],
      yes,
      no,
      cancel,
    } = options;

    // 创建模态框
    const modal = document.createElement("div");
    modal.id = id;
    modal.className = "modal-stack-native";
    modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: ${options.zIndex};
        `;

    const dialog = document.createElement("div");
    dialog.className = "modal-dialog";
    dialog.style.cssText = `
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            max-width: ${area[0]};
            max-height: ${area[1]};
            overflow: auto;
        `;

    // 构建内容
    let html = `
            <div class="modal-header" style="padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                <h5 class="modal-title" style="margin: 0; font-size: 1.1rem;">${title}</h5>
                <button type="button" class="modal-close" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
            </div>
            <div class="modal-body" style="padding: 20px;">${content}</div>
        `;

    if (btn && btn.length > 0) {
      html += `
                <div class="modal-footer" style="padding: 15px 20px; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 10px;">
                    ${btn.map((b, i) => `<button class="btn btn-${i === 0 ? "primary" : "secondary"} modal-btn" data-index="${i}">${b}</button>`).join("")}
                </div>
            `;
    }

    dialog.innerHTML = html;
    modal.appendChild(dialog);
    document.body.appendChild(modal);

    // 记录弹窗
    this.stack.push({
      id: id,
      element: modal,
      options: options,
      timestamp: Date.now(),
    });

    // 绑定事件
    dialog.querySelector(".modal-close").addEventListener("click", () => {
      this.close(id);
      if (cancel) cancel();
    });

    dialog.querySelectorAll(".modal-btn").forEach((btnEl, index) => {
      btnEl.addEventListener("click", () => {
        const callback = index === 0 ? yes : no;
        if (callback) {
          const result = callback(index);
          if (result !== false) {
            this.close(id);
          }
        } else {
          this.close(id);
        }
      });
    });

    // 显示动画
    modal.style.opacity = "0";
    requestAnimationFrame(() => {
      modal.style.transition = "opacity 0.2s";
      modal.style.opacity = "1";
      dialog.style.transform = "scale(0.9)";
      requestAnimationFrame(() => {
        dialog.style.transition = "transform 0.2s";
        dialog.style.transform = "scale(1)";
      });
    });

    return id;
  },

  /**
   * 关闭弹窗
   * @param {string} id - 弹窗ID
   */
  close: function (id) {
    const modal = this.get(id);
    if (!modal) return;

    if (modal.index !== undefined && typeof layer !== "undefined") {
      layer.close(modal.index);
    } else if (modal.element) {
      // 原生模态框
      modal.element.style.opacity = "0";
      setTimeout(() => {
        if (modal.element.parentNode) {
          modal.element.parentNode.removeChild(modal.element);
        }
      }, 200);
    }

    this.remove(id);
  },

  /**
   * 关闭顶部弹窗
   */
  closeTop: function () {
    if (this.stack.length > 0) {
      const top = this.stack[this.stack.length - 1];
      this.close(top.id);
    }
  },

  /**
   * 关闭所有弹窗
   */
  closeAll: function () {
    [...this.stack].forEach((modal) => {
      this.close(modal.id);
    });
  },

  /**
   * 移除弹窗记录
   */
  remove: function (id) {
    const index = this.stack.findIndex((m) => m.id === id);
    if (index !== -1) {
      this.stack.splice(index, 1);
    }

    // 更新顶层标记
    if (this.stack.length > 0) {
      const top = this.stack[this.stack.length - 1];
      if (top.layer) {
        top.layer.classList.add("modal-stack-top");
      }
    }
  },

  /**
   * 获取弹窗
   */
  get: function (id) {
    return this.stack.find((m) => m.id === id);
  },

  /**
   * 获取顶部弹窗
   */
  getTop: function () {
    return this.stack.length > 0 ? this.stack[this.stack.length - 1] : null;
  },

  /**
   * 获取弹窗数量
   */
  getCount: function () {
    return this.stack.length;
  },

  /**
   * 检查弹窗是否打开
   */
  has: function (id) {
    return this.stack.some((m) => m.id === id);
  },

  /**
   * 绑定关闭事件
   */
  bindCloseEvents: function (layero, id) {
    // 阻止事件冒泡
    layero[0].addEventListener("click", (e) => {
      e.stopPropagation();
    });
  },

  /**
   * 警告框
   */
  alert: function (message, options = {}) {
    return this.open({
      type: 1,
      title: options.title || "警告",
      content: message,
      btn: ["确定"],
      yes: (index) => {
        if (options.yes) options.yes();
        layer.close(index);
      },
    });
  },

  /**
   * 确认框
   */
  confirm: function (message, options = {}) {
    return new Promise((resolve) => {
      const id = this.open({
        type: 1,
        title: options.title || "确认",
        content: message,
        btn: ["确定", "取消"],
        yes: (index) => {
          if (options.yes) options.yes();
          layer.close(index);
          resolve(true);
        },
        no: (index) => {
          if (options.no) options.no();
          layer.close(index);
          resolve(false);
        },
        cancel: () => {
          if (options.cancel) options.cancel();
          resolve(false);
        },
      });
    });
  },

  /**
   * 提示框
   */
  msg: function (message, options = {}) {
    const id = `msg_${Date.now()}`;
    return layer.msg(message, {
      ...options,
      id: id,
      zIndex: this.currentZIndex,
    });
  },

  /**
   * 加载层
   */
  loading: function (message = "加载中...") {
    return layer.load(2, {
      content: message,
      shade: [0.3, "#fff"],
      zIndex: this.currentZIndex,
    });
  },

  /**
   * 关闭加载层
   */
  closeLoading: function (index) {
    if (index !== undefined) {
      layer.close(index);
    } else {
      // 关闭所有加载层
      this.stack.forEach((modal) => {
        if (modal.options.type === 3 || modal.options.type === 4) {
          this.close(modal.id);
        }
      });
    }
  },
};

// 导出到全局
window.ModalStack = ModalStack;
