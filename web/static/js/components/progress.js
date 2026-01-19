/**
 * Progress Component - 进度条组件
 * 提供多种进度条样式和动画效果
 */

const Progress = {
  // 默认配置
  defaultConfig: {
    type: "default", // default, success, warning, danger, info
    striped: false,
    animated: false,
    showLabel: true,
    size: "md", // sm, md, lg
    height: 20,
  },

  /**
   * 创建简单进度条
   * @param {string} containerId - 容器元素ID
   * @param {Object} config - 配置
   */
  createSimple: function (containerId, config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const mergedConfig = { ...this.defaultConfig, ...config };

    const sizeClass =
      mergedConfig.size === "sm"
        ? "progress-sm"
        : mergedConfig.size === "lg"
          ? "progress-lg"
          : "";

    const stripedClass = mergedConfig.striped ? "progress-bar-striped" : "";
    const animatedClass = mergedConfig.animated ? "progress-bar-animated" : "";

    const colorClass =
      mergedConfig.type === "success"
        ? "bg-success"
        : mergedConfig.type === "warning"
          ? "bg-warning"
          : mergedConfig.type === "danger"
            ? "bg-danger"
            : mergedConfig.type === "info"
              ? "bg-info"
              : "bg-primary";

    const html = `
            <div class="progress ${sizeClass}" style="height: ${mergedConfig.height}px;">
                <div class="progress-bar ${colorClass} ${stripedClass} ${animatedClass}"
                     role="progressbar"
                     style="width: 0%"
                     aria-valuenow="0"
                     aria-valuemin="0"
                     aria-valuemax="100"
                     id="${containerId}Bar">
                    ${mergedConfig.showLabel ? '<span class="progress-label">0%</span>' : ""}
                </div>
            </div>
        `;

    container.innerHTML = html;

    return {
      element: container.querySelector(".progress-bar"),
      setValue: (percent) => this.setValue(containerId, percent),
      increment: (delta) => this.increment(containerId, delta),
      setType: (type) => this.setType(containerId, type),
      show: () => this.show(containerId),
      hide: () => this.hide(containerId),
    };
  },

  /**
   * 设置进度值
   * @param {string} barId - 进度条元素ID
   * @param {number} percent - 百分比
   */
  setValue: function (barId, percent) {
    const bar =
      document.getElementById(barId) || document.querySelector(`#${barId}Bar`);
    if (!bar) return;

    percent = Math.max(0, Math.min(100, percent));
    bar.style.width = `${percent}%`;
    bar.setAttribute("aria-valuenow", percent);

    const label = bar.querySelector(".progress-label");
    if (label) {
      label.textContent = `${Math.round(percent)}%`;
    }
  },

  /**
   * 增加进度值
   * @param {string} barId - 进度条元素ID
   * @param {number} delta - 增加量
   * @returns {number} 新值
   */
  increment: function (barId, delta) {
    const bar =
      document.getElementById(barId) || document.querySelector(`#${barId}Bar`);
    if (!bar) return 0;

    const currentValue = parseFloat(bar.getAttribute("aria-valuenow")) || 0;
    const newValue = Math.max(0, Math.min(100, currentValue + delta));
    this.setValue(barId, newValue);
    return newValue;
  },

  /**
   * 设置进度条类型
   * @param {string} barId - 进度条元素ID
   * @param {string} type - 类型
   */
  setType: function (barId, type) {
    const bar =
      document.getElementById(barId) || document.querySelector(`#${barId}Bar`);
    if (!bar) return;

    // 移除所有颜色类
    bar.classList.remove(
      "bg-success",
      "bg-warning",
      "bg-danger",
      "bg-info",
      "bg-primary",
    );

    // 添加新颜色类
    const colorClass =
      type === "success"
        ? "bg-success"
        : type === "warning"
          ? "bg-warning"
          : type === "danger"
            ? "bg-danger"
            : type === "info"
              ? "bg-info"
              : "bg-primary";
    bar.classList.add(colorClass);
  },

  /**
   * 显示进度条
   * @param {string} barId - 进度条元素ID
   */
  show: function (barId) {
    const bar =
      document.getElementById(barId) || document.querySelector(`#${barId}Bar`);
    if (bar) bar.style.display = "block";
  },

  /**
   * 隐藏进度条
   * @param {string} barId - 进度条元素ID
   */
  hide: function (barId) {
    const bar =
      document.getElementById(barId) || document.querySelector(`#${barId}Bar`);
    if (bar) bar.style.display = "none";
  },

  /**
   * 创建多阶段进度条
   * @param {string} containerId - 容器元素ID
   * @param {Array} stages - 阶段数组
   * @param {Object} config - 配置
   */
  createMultiStage: function (containerId, stages = [], config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const total = stages.reduce((sum, s) => sum + (s.weight || 1), 0);
    let currentOffset = 0;

    let html = '<div class="multi-stage-progress">';

    stages.forEach((stage, index) => {
      const widthPercent = ((stage.weight || 1) / total) * 100;
      const colorClass =
        stage.type === "success"
          ? "bg-success"
          : stage.type === "warning"
            ? "bg-warning"
            : stage.type === "danger"
              ? "bg-danger"
              : stage.type === "info"
                ? "bg-info"
                : "bg-primary";

      const completedClass = stage.completed ? "" : "bg-secondary";
      const activeClass = stage.active ? "progress-bar-animated" : "";

      html += `
                <div class="progress mb-1" style="height: ${config.height || 24}px;">
                    <div class="progress-bar ${completedClass} ${activeClass}"
                         role="progressbar"
                         style="width: ${widthPercent}%; margin-left: ${currentOffset}%"
                         data-stage="${index}"
                         title="${stage.name || ""}">
                        ${config.showLabels !== false ? `<span class="small">${stage.name || ""}</span>` : ""}
                    </div>
                </div>
            `;
      currentOffset += widthPercent;
    });

    html += "</div>";
    container.innerHTML = html;

    return {
      setStage: (index, value) => this.setStageValue(containerId, index, value),
      completeStage: (index) => this.completeStage(containerId, index),
      activateStage: (index) => this.activateStage(containerId, index),
    };
  },

  /**
   * 设置阶段值
   */
  setStageValue: function (containerId, stageIndex, value) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const bar = container.querySelector(`[data-stage="${stageIndex}"]`);
    if (bar) {
      bar.style.width = `${value}%`;
    }
  },

  /**
   * 完成阶段
   */
  completeStage: function (containerId, stageIndex) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const bar = container.querySelector(`[data-stage="${stageIndex}"]`);
    if (bar) {
      bar.classList.remove("bg-secondary");
      bar.classList.add("bg-success");
    }
  },

  /**
   * 激活阶段
   */
  activateStage: function (containerId, stageIndex) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // 重置所有阶段
    container.querySelectorAll(".progress-bar").forEach((bar, idx) => {
      if (idx < stageIndex) {
        bar.classList.remove("bg-secondary", "bg-success");
        bar.classList.add("bg-success");
      } else if (idx === stageIndex) {
        bar.classList.remove("bg-secondary");
        bar.classList.add("bg-primary", "progress-bar-animated");
      } else {
        bar.classList.remove(
          "bg-success",
          "bg-primary",
          "progress-bar-animated",
        );
        bar.classList.add("bg-secondary");
      }
    });
  },

  /**
   * 创建环形进度条
   * @param {string} containerId - 容器元素ID
   * @param {Object} config - 配置
   */
  createCircular: function (containerId, config = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`容器元素不存在: ${containerId}`);
      return null;
    }

    const size = config.size || 120;
    const strokeWidth = config.strokeWidth || 10;
    const color = config.color || "#3498db";

    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (0 / 100) * circumference;

    const html = `
            <div class="circular-progress-container" style="width: ${size}px; height: ${size}px;">
                <svg class="circular-progress" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
                    <circle class="circular-bg" cx="${size / 2}" cy="${size / 2}" r="${radius}"
                            fill="none" stroke="#eee" stroke-width="${strokeWidth}"/>
                    <circle class="circular-bar" cx="${size / 2}" cy="${size / 2}" r="${radius}"
                            fill="none" stroke="${color}" stroke-width="${strokeWidth}"
                            stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
                            stroke-linecap="round" transform="rotate(-90 ${size / 2} ${size / 2})"/>
                </svg>
                <div class="circular-label" style="font-size: ${size / 4}px;">
                    <span class="percent">0</span>%
                </div>
            </div>
        `;

    container.innerHTML = html;

    return {
      setValue: (percent) => this.setCircularValue(containerId, percent),
      setColor: (color) => this.setCircularColor(containerId, color),
    };
  },

  /**
   * 设置环形进度值
   */
  setCircularValue: function (containerId, percent) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const bar = container.querySelector(".circular-bar");
    const label = container.querySelector(".percent");
    if (!bar || !label) return;

    const size = container.querySelector("svg").getAttribute("width");
    const strokeWidth = parseFloat(bar.getAttribute("stroke-width"));
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (percent / 100) * circumference;

    bar.style.strokeDashoffset = offset;
    label.textContent = Math.round(percent);
  },

  /**
   * 设置环形进度颜色
   */
  setCircularColor: function (containerId, color) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const bar = container.querySelector(".circular-bar");
    if (bar) {
      bar.style.stroke = color;
    }
  },
};

// 导出到全局
window.Progress = Progress;
