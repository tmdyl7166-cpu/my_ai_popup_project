/**
 * Spinner Component - 加载动画组件
 * 提供多种加载动画效果
 */

const Spinner = {
  // 默认配置
  defaultConfig: {
    size: "md", // sm, md, lg, xl
    color: "primary", // primary, secondary, success, danger, warning, info, light, dark
    type: "border", // border, grow
    display: "inline-block",
  },

  /**
   * 创建旋转加载器
   * @param {string} containerId - 容器元素ID
   * @param {Object} config - 配置
   */
  createBorder: function (containerId, config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const mergedConfig = { ...this.defaultConfig, ...config };

    const sizeClass =
      mergedConfig.size === "sm"
        ? "spinner-border-sm"
        : mergedConfig.size === "lg"
          ? "spinner-border-lg"
          : mergedConfig.size === "xl"
            ? "spinner-border-xl"
            : "";

    const colorClass = mergedConfig.color ? `text-${mergedConfig.color}` : "";

    const style =
      mergedConfig.size === "xl"
        ? `style="width: 5rem; height: 5rem;"`
        : mergedConfig.size === "lg"
          ? `style="width: 3rem; height: 3rem;"`
          : "";

    const html = `
            <div class="spinner-border ${sizeClass} ${colorClass}" role="status"
                 style="${mergedConfig.display === "block" ? "display: block; margin: auto;" : ""}">
                <span class="visually-hidden">加载中...</span>
            </div>
        `;

    // 如果需要自定义尺寸
    if (mergedConfig.size === "xl" || mergedConfig.size === "lg") {
      container.innerHTML = `<div class="spinner-border ${colorClass}" ${style} role="status">
                <span class="visually-hidden">加载中...</span>
            </div>`;
    } else {
      container.innerHTML = html;
    }

    return {
      element: container.querySelector(".spinner-border"),
      show: () =>
        (container.style.display =
          mergedConfig.display === "block" ? "block" : "inline-block"),
      hide: () => (container.style.display = "none"),
      setColor: (color) => {
        const el = container.querySelector(".spinner-border");
        if (el) {
          el.classList.remove(
            "text-primary",
            "text-secondary",
            "text-success",
            "text-danger",
            "text-warning",
            "text-info",
            "text-light",
            "text-dark",
          );
          el.classList.add(`text-${color}`);
        }
      },
      destroy: () => (container.innerHTML = ""),
    };
  },

  /**
   * 创建脉冲加载器
   * @param {string} containerId - 容器元素ID
   * @param {Object} config - 配置
   */
  createGrow: function (containerId, config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const mergedConfig = { ...this.defaultConfig, ...config };

    const sizeClass =
      mergedConfig.size === "sm"
        ? "spinner-grow-sm"
        : mergedConfig.size === "lg"
          ? "spinner-grow-lg"
          : "";

    const colorClass = mergedConfig.color ? `text-${mergedConfig.color}` : "";

    const html = `
            <div class="spinner-grow ${sizeClass} ${colorClass}" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
        `;

    container.innerHTML = html;

    return {
      element: container.querySelector(".spinner-grow"),
      show: () => (container.style.display = "inline-block"),
      hide: () => (container.style.display = "none"),
      setColor: (color) => {
        const el = container.querySelector(".spinner-grow");
        if (el) {
          el.classList.remove(
            "text-primary",
            "text-secondary",
            "text-success",
            "text-danger",
            "text-warning",
            "text-info",
            "text-light",
            "text-dark",
          );
          el.classList.add(`text-${color}`);
        }
      },
      destroy: () => (container.innerHTML = ""),
    };
  },

  /**
   * 创建圆点加载器
   * @param {string} containerId - 容器元素ID
   * @param {Object} config - 配置
   */
  createDots: function (containerId, config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const count = config.count || 3;
    const color = config.color || "#3498db";
    const size = config.size || 12;

    let html = '<div class="dots-spinner" style="display: flex; gap: 4px;">';
    for (let i = 0; i < count; i++) {
      const delay = i * 0.15;
      html += `<span style="
                width: ${size}px;
                height: ${size}px;
                background-color: ${color};
                border-radius: 50%;
                animation: dotsBounce 0.6s infinite ease-in-out both;
                animation-delay: ${delay}s;
            "></span>`;
    }
    html += "</div>";

    // 添加关键帧样式
    if (!document.getElementById("dots-spinner-styles")) {
      const style = document.createElement("style");
      style.id = "dots-spinner-styles";
      style.textContent = `
                @keyframes dotsBounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
            `;
      document.head.appendChild(style);
    }

    container.innerHTML = html;

    return {
      show: () => (container.style.display = "flex"),
      hide: () => (container.style.display = "none"),
      destroy: () => (container.innerHTML = ""),
    };
  },

  /**
   * 创建条形加载器
   * @param {string} containerId - 容器元素ID
   * @param {Object} config - 配置
   */
  createBars: function (containerId, config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const count = config.count || 5;
    const color = config.color || "#3498db";
    const height = config.height || 4;

    let html =
      '<div class="bars-spinner" style="display: flex; align-items: center; gap: 3px;">';
    for (let i = 0; i < count; i++) {
      const delay = i * 0.1;
      html += `<span style="
                width: 6px;
                height: ${height}px;
                background-color: ${color};
                border-radius: 3px;
                animation: barsWave 1s ease-in-out infinite;
                animation-delay: ${delay}s;
            "></span>`;
    }
    html += "</div>";

    // 添加关键帧样式
    if (!document.getElementById("bars-spinner-styles")) {
      const style = document.createElement("style");
      style.id = "bars-spinner-styles";
      style.textContent = `
                @keyframes barsWave {
                    0%, 40%, 100% { height: ${height}px; }
                    20% { height: ${height * 2}px; }
                }
            `;
      document.head.appendChild(style);
    }

    container.innerHTML = html;

    return {
      show: () => (container.style.display = "flex"),
      hide: () => (container.style.display = "none"),
      destroy: () => (container.innerHTML = ""),
    };
  },

  /**
   * 创建文字加载提示
   * @param {string} containerId - 容器元素ID
   * @param {Object} config - 配置
   */
  createWithText: function (containerId, config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const text = config.text || "加载中...";
    const showIcon = config.showIcon !== false;

    const html = `
            <div class="text-center py-3">
                ${
                  showIcon
                    ? `
                <div class="spinner-border text-primary mb-2" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                `
                    : ""
                }
                <div class="text-muted">${text}</div>
                ${config.showPercent ? '<div class="mt-2 fw-bold" id="' + containerId + 'Percent">0%</div>' : ""}
            </div>
        `;

    container.innerHTML = html;

    return {
      show: () => (container.style.display = "block"),
      hide: () => (container.style.display = "none"),
      setText: (text) => {
        const textEl = container.querySelector(".text-muted");
        if (textEl) textEl.textContent = text;
      },
      setPercent: (percent) => {
        const percentEl = container.querySelector(
          "#" + containerId + "Percent",
        );
        if (percentEl) percentEl.textContent = `${percent}%`;
      },
      destroy: () => (container.innerHTML = ""),
    };
  },

  /**
   * 创建全屏加载遮罩
   * @param {Object} config - 配置
   */
  createOverlay: function (config = {}) {
    const text = config.text || "加载中...";
    const showSpinner = config.showSpinner !== false;

    const overlay = document.createElement("div");
    overlay.id = "spinnerOverlay";
    overlay.className = "spinner-overlay";
    overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;

    const content = document.createElement("div");
    content.className = "text-center";
    content.innerHTML = `
            ${
              showSpinner
                ? `
            <div class="spinner-border text-primary" style="width: 4rem; height: 4rem;" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            `
                : ""
            }
            <div class="text-white mt-3" style="font-size: 1.2rem;">${text}</div>
            ${config.showPercent ? `<div class="text-white mt-2" id="overlayPercent">0%</div>` : ""}
        `;

    overlay.appendChild(content);
    document.body.appendChild(overlay);

    return {
      show: () => (overlay.style.display = "flex"),
      hide: () => (overlay.style.display = "none"),
      setText: (text) => {
        const textEl = content.querySelector(
          ".text-white:not(#overlayPercent)",
        );
        if (textEl) textEl.textContent = text;
      },
      setPercent: (percent) => {
        const percentEl = content.querySelector("#overlayPercent");
        if (percentEl) percentEl.textContent = `${percent}%`;
      },
      destroy: () => overlay.remove(),
    };
  },

  /**
   * 显示全局加载
   * @param {string} message - 消息
   */
  showGlobal: function (message = "加载中...") {
    // 移除已存在的
    this.hideGlobal();

    const overlay = this.createOverlay({ text: message, showPercent: true });
    overlay.show();
    window._globalSpinner = overlay;

    return overlay;
  },

  /**
   * 隐藏全局加载
   */
  hideGlobal: function () {
    if (window._globalSpinner) {
      window._globalSpinner.destroy();
      window._globalSpinner = null;
    }
  },
};

// 导出到全局
window.Spinner = Spinner;
