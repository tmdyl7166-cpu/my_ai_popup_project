/**
 * Toast Component - 通知提示组件
 * 提供多种类型的通知提示功能
 */

const Toast = {
  // 默认配置
  defaultConfig: {
    position: "top-right", // top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
    duration: 5000, // 显示时长(ms)
    closable: true, // 是否可关闭
    showIcon: true, // 是否显示图标
    animation: true, // 是否显示动画
    maxToasts: 5, // 最大显示数量
    container: null, // 自定义容器
  },

  // 容器元素
  container: null,

  /**
   * 初始化
   */
  init: function (config = {}) {
    this.config = { ...this.defaultConfig, ...config };
    this.createContainer();
  },

  /**
   * 创建容器
   */
  createContainer: function () {
    if (this.container) return;

    const position = this.config.position;
    const positionClass =
      position === "top-right"
        ? "toast-tr"
        : position === "top-left"
          ? "toast-tl"
          : position === "bottom-right"
            ? "toast-br"
            : position === "bottom-left"
              ? "toast-bl"
              : position === "top-center"
                ? "toast-tc"
                : "toast-bc";

    const container = document.createElement("div");
    container.id = "toastContainer";
    container.className = `toast-container ${positionClass}`;

    // 添加样式
    container.style.cssText = `
            position: fixed;
            ${position.includes("top") ? "top: 20px;" : "bottom: 20px;"}
            ${position.includes("right") ? "right: 20px;" : position.includes("left") ? "left: 20px;" : ""}
            ${position.includes("center") ? "left: 50%; transform: translateX(-50%);" : ""}
            z-index: 1090;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;

    document.body.appendChild(container);
    this.container = container;
  },

  /**
   * 显示成功提示
   * @param {string} title - 标题
   * @param {string} message - 消息内容
   * @param {Object} options - 选项
   */
  success: function (title, message, options = {}) {
    return this.show({
      type: "success",
      title: title,
      message: message,
      icon: "check-circle",
      ...options,
    });
  },

  /**
   * 显示错误提示
   * @param {string} title - 标题
   * @param {string} message - 消息内容
   * @param {Object} options - 选项
   */
  error: function (title, message, options = {}) {
    return this.show({
      type: "error",
      title: title,
      message: message,
      icon: "times-circle",
      ...options,
    });
  },

  /**
   * 显示警告提示
   * @param {string} title - 标题
   * @param {string} message - 消息内容
   * @param {Object} options - 选项
   */
  warning: function (title, message, options = {}) {
    return this.show({
      type: "warning",
      title: title,
      message: message,
      icon: "exclamation-triangle",
      ...options,
    });
  },

  /**
   * 显示信息提示
   * @param {string} title - 标题
   * @param {string} message - 消息内容
   * @param {Object} options - 选项
   */
  info: function (title, message, options = {}) {
    return this.show({
      type: "info",
      title: title,
      message: message,
      icon: "info-circle",
      ...options,
    });
  },

  /**
   * 显示自定义提示
   * @param {Object} options - 选项
   */
  show: function (options = {}) {
    const config = { ...this.config, ...options };
    const {
      type,
      title,
      message,
      icon,
      duration,
      closable,
      onClose,
      elementId,
    } = config;

    // 检查最大数量
    const existingToasts = this.container.querySelectorAll(".toast");
    if (existingToasts.length >= this.config.maxToasts) {
      existingToasts[0].remove();
    }

    // 创建Toast元素
    const toastId =
      elementId ||
      `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const toast = document.createElement("div");
    toast.id = toastId;
    toast.className = `toast toast-${type}`;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "polite");

    // 样式
    const bgColor =
      type === "success"
        ? "#d4edda"
        : type === "error"
          ? "#f8d7da"
          : type === "warning"
            ? "#fff3cd"
            : "#d1ecf1";
    const textColor =
      type === "success"
        ? "#155724"
        : type === "error"
          ? "#721c24"
          : type === "warning"
            ? "#856404"
            : "#0c5460";
    const borderColor =
      type === "success"
        ? "#c3e6cb"
        : type === "error"
          ? "#f5c6cb"
          : type === "warning"
            ? "#ffeeba"
            : "#bee5eb";
    const iconColor =
      type === "success"
        ? "#28a745"
        : type === "error"
          ? "#dc3545"
          : type === "warning"
            ? "#ffc107"
            : "#17a2b8";

    toast.style.cssText = `
            background-color: ${bgColor};
            color: ${textColor};
            border: 1px solid ${borderColor};
            border-radius: 8px;
            padding: 12px 16px;
            min-width: 300px;
            max-width: 450px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: flex-start;
            gap: 12px;
            pointer-events: auto;
            opacity: 0;
            transform: translateX(100%);
            transition: opacity 0.3s, transform 0.3s;
        `;

    // 图标
    const iconHtml =
      config.showIcon !== false
        ? `<i class="fas fa-${icon}" style="color: ${iconColor}; font-size: 1.25rem; flex-shrink: 0; margin-top: 2px;"></i>`
        : "";

    // 关闭按钮
    const closeBtn = closable
      ? `<button type="button" class="toast-close" style="
                background: none;
                border: none;
                color: ${textColor};
                font-size: 1.25rem;
                cursor: pointer;
                padding: 0;
                margin-left: auto;
                opacity: 0.6;
            ">&times;</button>`
      : "";

    toast.innerHTML = `
            ${iconHtml}
            <div class="toast-content" style="flex: 1;">
                ${title ? `<div class="toast-title" style="font-weight: 600; margin-bottom: 4px;">${title}</div>` : ""}
                ${message ? `<div class="toast-message" style="font-size: 0.9rem; opacity: 0.9;">${message}</div>` : ""}
            </div>
            ${closeBtn}
        `;

    this.container.appendChild(toast);

    // 显示动画
    requestAnimationFrame(() => {
      toast.style.opacity = "1";
      toast.style.transform = "translateX(0)";
    });

    // 自动关闭
    if (duration > 0) {
      const timer = setTimeout(() => {
        this.hide(toastId);
      }, duration);
      toast._timer = timer;
    }

    // 绑定关闭事件
    const closeBtnEl = toast.querySelector(".toast-close");
    if (closeBtnEl) {
      closeBtnEl.addEventListener("click", () => {
        this.hide(toastId);
      });
    }

    // 鼠标悬停暂停
    toast.addEventListener("mouseenter", () => {
      if (toast._timer) {
        clearTimeout(toast._timer);
        toast._timer = null;
      }
    });

    toast.addEventListener("mouseleave", () => {
      if (duration > 0 && !toast._timer) {
        toast._timer = setTimeout(() => {
          this.hide(toastId);
        }, 2000);
      }
    });

    return toastId;
  },

  /**
   * 隐藏Toast
   * @param {string} toastId - Toast元素ID
   */
  hide: function (toastId) {
    const toast =
      typeof toastId === "string" ? document.getElementById(toastId) : toastId;
    if (!toast) return;

    // 清除定时器
    if (toast._timer) {
      clearTimeout(toast._timer);
    }

    // 隐藏动画
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";

    // 移除元素
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
      if (this.config.onHide) {
        this.config.onHide(toastId);
      }
    }, 300);
  },

  /**
   * 隐藏所有Toast
   */
  hideAll: function () {
    const toasts = this.container.querySelectorAll(".toast");
    toasts.forEach((toast) => {
      this.hide(toast);
    });
  },

  /**
   * 创建固定位置通知（右上角）
   * @param {string} message - 消息内容
   * @param {string} type - 类型
   */
  showFixed: function (message, type = "info") {
    const iconMap = {
      success: "check",
      error: "times",
      warning: "exclamation",
      info: "info",
    };

    const colorMap = {
      success: "#28a745",
      error: "#dc3545",
      warning: "#ffc107",
      info: "#17a2b8",
    };

    const notification = document.createElement("div");
    notification.className = `fixed-notification fixed-notification-${type}`;
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === "warning" ? "#fff" : colorMap[type]};
            color: ${type === "warning" ? "#856404" : "#fff"};
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 9999;
            animation: slideInRight 0.3s ease-out;
        `;

    notification.innerHTML = `
            <i class="fas fa-${iconMap[type]}" style="font-size: 1.2rem;"></i>
            <span>${message}</span>
        `;

    document.body.appendChild(notification);

    // 5秒后移除
    setTimeout(() => {
      notification.style.animation = "slideOutRight 0.3s ease-in forwards";
      setTimeout(() => notification.remove(), 300);
    }, 5000);

    return notification;
  },

  /**
   * 显示确认对话框
   * @param {Object} options - 选项
   */
  confirm: function (options = {}) {
    const {
      title = "确认",
      message = "确定要执行此操作吗？",
      onConfirm,
      onCancel,
      confirmText = "确定",
      cancelText = "取消",
      type = "warning",
    } = options;

    return new Promise((resolve) => {
      const modalId = `confirmModal_${Date.now()}`;
      const backdrop = document.createElement("div");
      backdrop.className = "modal-backdrop fade show";
      backdrop.id = `${modalId}_backdrop`;

      const modal = document.createElement("div");
      modal.className = "modal fade show";
      modal.id = modalId;
      modal.style.display = "block";
      modal.style.backgroundColor = "rgba(0, 0, 0, 0.5)";

      const icon =
        type === "danger"
          ? "exclamation-triangle text-danger"
          : type === "warning"
            ? "exclamation-triangle text-warning"
            : "question-circle text-info";

      modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-${icon} me-2"></i>${title}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" id="${modalId}_cancel">
                                ${cancelText}
                            </button>
                            <button type="button" class="btn btn-primary" id="${modalId}_confirm">
                                ${confirmText}
                            </button>
                        </div>
                    </div>
                </div>
            `;

      document.body.appendChild(backdrop);
      document.body.appendChild(modal);

      // 绑定事件
      document
        .getElementById(`${modalId}_confirm`)
        .addEventListener("click", () => {
          this.removeConfirm(modalId);
          if (onConfirm) onConfirm();
          resolve(true);
        });

      document
        .getElementById(`${modalId}_cancel`)
        .addEventListener("click", () => {
          this.removeConfirm(modalId);
          if (onCancel) onCancel();
          resolve(false);
        });

      document
        .querySelector(`#${modalId} .btn-close`)
        .addEventListener("click", () => {
          this.removeConfirm(modalId);
          resolve(false);
        });
    });
  },

  /**
   * 移除确认框
   */
  removeConfirm: function (modalId) {
    const backdrop = document.getElementById(`${modalId}_backdrop`);
    const modal = document.getElementById(modalId);
    if (backdrop) backdrop.remove();
    if (modal) modal.remove();
  },
};

// 导出到全局
window.Toast = Toast;
