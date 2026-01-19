/**
 * ThemeManager - 主题管理模块
 * 提供明亮/暗黑主题切换功能
 */

const ThemeManager = {
  // 当前主题
  currentTheme: "light",
  // 主题配置
  themes: {
    light: {
      name: "明亮",
      icon: "sun",
      colors: {
        primary: "#3498db",
        secondary: "#6c757d",
        success: "#28a745",
        warning: "#ffc107",
        danger: "#dc3545",
        info: "#17a2b8",
        background: "#f8f9fa",
        surface: "#ffffff",
        text: "#212529",
        border: "#dee2e6",
      },
    },
    dark: {
      name: "暗黑",
      icon: "moon",
      colors: {
        primary: "#5c8dbe",
        secondary: "#8a9aa9",
        success: "#4caf7a",
        warning: "#ffc107",
        danger: "#e06c75",
        info: "#4dc0e3",
        background: "#1a1a2e",
        surface: "#16213e",
        text: "#e4e4e4",
        border: "#2d3748",
      },
    },
  },
  // 存储键名
  storageKey: "app_theme",

  /**
   * 初始化
   */
  init: function () {
    console.log("[ThemeManager] 初始化主题管理器");

    // 加载保存的主题
    this.loadTheme();

    // 绑定事件
    this.bindEvents();

    // 应用主题
    this.applyTheme();
  },

  /**
   * 加载主题
   */
  loadTheme: function () {
    const savedTheme = localStorage.getItem(this.storageKey);
    if (savedTheme && this.themes[savedTheme]) {
      this.currentTheme = savedTheme;
    } else {
      // 检测系统主题偏好
      if (
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches
      ) {
        this.currentTheme = "dark";
      }
    }
  },

  /**
   * 绑定事件
   */
  bindEvents: function () {
    // 系统主题变化监听
    if (window.matchMedia) {
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", (e) => {
          if (!localStorage.getItem(this.storageKey)) {
            this.setTheme(e.matches ? "dark" : "light");
          }
        });
    }
  },

  /**
   * 设置主题
   */
  setTheme: function (theme) {
    if (!this.themes[theme]) {
      console.warn(`[ThemeManager] 未知主题: ${theme}`);
      return false;
    }

    this.currentTheme = theme;
    localStorage.setItem(this.storageKey, theme);
    this.applyTheme();

    // 发送事件
    if (typeof EventBus !== "undefined") {
      EventBus.emit("theme:changed", {
        theme,
        colors: this.themes[theme].colors,
      });
    }

    console.log(`[ThemeManager] 主题已切换为: ${theme}`);
    return true;
  },

  /**
   * 切换主题
   */
  toggleTheme: function () {
    const newTheme = this.currentTheme === "light" ? "dark" : "light";
    return this.setTheme(newTheme);
  },

  /**
   * 应用主题
   */
  applyTheme: function () {
    const theme = this.themes[this.currentTheme];
    if (!theme) return;

    const root = document.documentElement;

    // 应用CSS变量
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // 添加主题类
    document.body.classList.remove("theme-light", "theme-dark");
    document.body.classList.add(`theme-${this.currentTheme}`);

    // 更新图标
    this.updateThemeIcon();
  },

  /**
   * 更新主题图标
   */
  updateThemeIcon: function () {
    const icons = document.querySelectorAll(".theme-toggle-icon");
    icons.forEach((icon) => {
      const theme = this.themes[this.currentTheme];
      icon.className = `fas fa-${theme.icon} theme-toggle-icon`;
    });
  },

  /**
   * 获取当前主题
   */
  getTheme: function () {
    return this.currentTheme;
  },

  /**
   * 获取主题配置
   */
  getThemeConfig: function (theme) {
    return this.themes[theme] || null;
  },

  /**
   * 获取当前主题配置
   */
  getCurrentConfig: function () {
    return this.themes[this.currentTheme];
  },

  /**
   * 获取所有主题
   */
  getAllThemes: function () {
    return Object.entries(this.themes).map(([key, value]) => ({
      id: key,
      name: value.name,
      icon: value.icon,
    }));
  },

  /**
   * 创建主题切换按钮
   */
  createToggleButton: function (containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const theme = this.themes[this.currentTheme];

    container.innerHTML = `
            <button class="btn btn-outline-secondary theme-toggle-btn" onclick="ThemeManager.toggleTheme()">
                <i class="fas fa-${theme.icon} theme-toggle-icon"></i>
                <span class="ms-1 theme-label">${theme.name}模式</span>
            </button>
        `;
  },

  /**
   * 添加主题样式
   */
  addThemeStyles: function () {
    const styleId = "theme-manager-styles";
    if (document.getElementById(styleId)) return;

    const style = document.createElement("style");
    style.id = styleId;
    style.textContent = `
            /* 主题切换按钮 */
            .theme-toggle-btn {
                display: inline-flex;
                align-items: center;
                padding: 0.4rem 0.8rem;
                font-size: 0.875rem;
            }

            .theme-toggle-btn:hover {
                background-color: var(--color-secondary);
                border-color: var(--color-secondary);
                color: white;
            }

            /* 主题样式 */
            .theme-light {
                transition: background-color 0.3s, color 0.3s;
            }

            .theme-dark {
                transition: background-color 0.3s, color 0.3s;
            }

            /* 暗黑主题特定样式 */
            .theme-dark body {
                background-color: #0d1117;
                color: #e4e4e4;
            }

            .theme-dark .card {
                background-color: #161b22;
                border-color: #30363d;
            }

            .theme-dark .card-header {
                background-color: #21262d;
                border-color: #30363d;
            }

            .theme-dark .list-group-item {
                background-color: #161b22;
                border-color: #30363d;
                color: #e4e4e4;
            }

            .theme-dark .navbar {
                background-color: #161b22 !important;
            }

            .theme-dark .table {
                color: #e4e4e4;
            }

            .theme-dark .table th,
            .theme-dark .table td {
                border-color: #30363d;
            }

            .theme-dark .dropdown-menu {
                background-color: #161b22;
                border-color: #30363d;
            }

            .theme-dark .dropdown-item {
                color: #e4e4e4;
            }

            .theme-dark .dropdown-item:hover {
                background-color: #30363d;
            }

            .theme-dark .modal-content {
                background-color: #161b22;
                border-color: #30363d;
            }

            .theme-dark .modal-header {
                border-color: #30363d;
            }

            .theme-dark .modal-footer {
                border-color: #30363d;
            }

            .theme-dark .form-control {
                background-color: #0d1117;
                border-color: #30363d;
                color: #e4e4e4;
            }

            .theme-dark .form-control:focus {
                background-color: #161b22;
                border-color: #58a6ff;
                color: #e4e4e4;
            }

            .theme-dark .form-select {
                background-color: #0d1117;
                border-color: #30363d;
                color: #e4e4e4;
            }

            .theme-dark .input-group-text {
                background-color: #21262d;
                border-color: #30363d;
                color: #e4e4e4;
            }

            .theme-dark .btn-outline-light {
                border-color: #30363d;
                color: #e4e4e4;
            }

            .theme-dark .btn-outline-light:hover {
                background-color: #30363d;
                border-color: #30363d;
                color: white;
            }
        `;

    document.head.appendChild(style);
  },
};

// 导出到全局
window.ThemeManager = ThemeManager;
