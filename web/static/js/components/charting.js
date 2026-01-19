/**
 * Charting Component - 图表组件
 * 提供图表绘制功能，集成 Chart.js
 */

const Charting = {
  // 图表实例缓存
  charts: {},

  /**
   * 初始化
   */
  init: function () {
    console.log("Charting组件初始化");
  },

  /**
   * 创建折线图
   * @param {string} canvasId - Canvas元素ID
   * @param {Object} config - 图表配置
   * @returns {Object} Chart实例
   */
  createLineChart: function (canvasId, config = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas元素不存在: ${canvasId}`);
      return null;
    }

    const defaultConfig = {
      type: "line",
      data: {
        labels: config.labels || [],
        datasets: config.datasets || [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
            labels: {
              usePointStyle: true,
              padding: 20,
            },
          },
          tooltip: {
            mode: "index",
            intersect: false,
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            titleFont: { size: 14 },
            bodyFont: { size: 13 },
            padding: 12,
            cornerRadius: 8,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
        },
        interaction: {
          mode: "nearest",
          axis: "x",
          intersect: false,
        },
      },
    };

    const chartConfig = { ...defaultConfig, ...config };
    const chart = new Chart(canvas, chartConfig);

    this.charts[canvasId] = chart;
    return chart;
  },

  /**
   * 创建柱状图
   * @param {string} canvasId - Canvas元素ID
   * @param {Object} config - 图表配置
   * @returns {Object} Chart实例
   */
  createBarChart: function (canvasId, config = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas元素不存在: ${canvasId}`);
      return null;
    }

    const defaultConfig = {
      type: "bar",
      data: {
        labels: config.labels || [],
        datasets: config.datasets || [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
            labels: {
              usePointStyle: true,
              padding: 20,
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
        },
      },
    };

    const chartConfig = { ...defaultConfig, ...config };
    const chart = new Chart(canvas, chartConfig);

    this.charts[canvasId] = chart;
    return chart;
  },

  /**
   * 创建饼图
   * @param {string} canvasId - Canvas元素ID
   * @param {Object} config - 图表配置
   * @returns {Object} Chart实例
   */
  createPieChart: function (canvasId, config = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas元素不存在: ${canvasId}`);
      return null;
    }

    const defaultConfig = {
      type: "doughnut",
      data: {
        labels: config.labels || [],
        datasets: config.datasets || [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
            labels: {
              usePointStyle: true,
              padding: 20,
            },
          },
        },
        cutout: "60%",
      },
    };

    const chartConfig = { ...defaultConfig, ...config };
    const chart = new Chart(canvas, chartConfig);

    this.charts[canvasId] = chart;
    return chart;
  },

  /**
   * 更新图表数据
   * @param {string} canvasId - Canvas元素ID
   * @param {Object} newData - 新数据
   */
  updateChart: function (canvasId, newData) {
    const chart = this.charts[canvasId];
    if (!chart) {
      console.error(`图表不存在: ${canvasId}`);
      return;
    }

    if (newData.labels) {
      chart.data.labels = newData.labels;
    }
    if (newData.datasets) {
      chart.data.datasets = newData.datasets;
    }
    chart.update();
  },

  /**
   * 添加数据点到图表
   * @param {string} canvasId - Canvas元素ID
   * @param {string} label - 数据标签
   * @param {number} value - 数据值
   * @param {number} maxPoints - 最大数据点数
   */
  addDataPoint: function (canvasId, label, value, maxPoints = 20) {
    const chart = this.charts[canvasId];
    if (!chart) {
      console.error(`图表不存在: ${canvasId}`);
      return;
    }

    // 添加新数据
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
      dataset.data.push(value);
    });

    // 移除旧数据
    while (chart.data.labels.length > maxPoints) {
      chart.data.labels.shift();
      chart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
      });
    }

    chart.update();
  },

  /**
   * 销毁图表
   * @param {string} canvasId - Canvas元素ID
   */
  destroyChart: function (canvasId) {
    const chart = this.charts[canvasId];
    if (chart) {
      chart.destroy();
      delete this.charts[canvasId];
    }
  },

  /**
   * 获取图表实例
   * @param {string} canvasId - Canvas元素ID
   * @returns {Object|null} Chart实例
   */
  getChart: function (canvasId) {
    return this.charts[canvasId] || null;
  },

  /**
   * 导出图表为图片
   * @param {string} canvasId - Canvas元素ID
   * @param {string} filename - 文件名
   */
  exportChart: function (canvasId, filename = "chart.png") {
    const chart = this.charts[canvasId];
    if (!chart) {
      console.error(`图表不存在: ${canvasId}`);
      return;
    }

    const link = document.createElement("a");
    link.download = filename;
    link.href = chart.toBase64Image();
    link.click();
  },
};

// 导出到全局
window.Charting = Charting;
