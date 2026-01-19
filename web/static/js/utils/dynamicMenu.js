/**
 * DynamicMenu - 动态菜单模块
 * 主/子菜单动态加载和渲染
 */

const DynamicMenu = {
  // 配置
  config: {
    containerId: "mainMenu",
    dataEndpoint: "/api/menu",
    defaultMenu: [],
    lazyLoad: true,
    maxDepth: 3,
    showIcons: true,
    showBadges: true,
  },

  // 菜单数据
  menuData: [],
  // 渲染缓存
  renderCache: {},

  /**
   * 初始化
   */
  init: function (options = {}) {
    this.config = { ...this.config, ...options };
    console.log("[DynamicMenu] 初始化动态菜单模块");

    // 加载菜单数据
    this.loadMenu();
  },

  /**
   * 加载菜单数据
   */
  loadMenu: async function () {
    try {
      // 尝试从API获取
      if (typeof API !== "undefined") {
        const response = await API.get(this.config.dataEndpoint);
        if (response && response.data) {
          this.menuData = response.data;
          this.render();
          return;
        }
      }

      // 使用默认菜单
      this.menuData = this.getDefaultMenu();
      this.render();
    } catch (error) {
      console.warn("[DynamicMenu] 加载菜单失败，使用默认菜单:", error);
      this.menuData = this.getDefaultMenu();
      this.render();
    }
  },

  /**
   * 获取默认菜单
   */
  getDefaultMenu: function () {
    return [
      {
        id: "dashboard",
        name: "仪表盘",
        icon: "tachometer-alt",
        url: "#dashboard",
        badge: null,
        children: [],
      },
      {
        id: "monitor",
        name: "系统监控",
        icon: "chart-line",
        url: null,
        badge: null,
        children: [
          {
            id: "global-monitor",
            name: "全局监控",
            icon: "globe",
            url: "#global-monitor",
          },
          {
            id: "performance",
            name: "性能监控",
            icon: "tachometer-alt",
            url: "#performance",
          },
          {
            id: "gpu-monitor",
            name: "GPU监控",
            icon: "microchip",
            url: "#gpu-monitor",
          },
        ],
      },
      {
        id: "deployment",
        name: "部署管理",
        icon: "rocket",
        url: null,
        badge: null,
        children: [
          {
            id: "deployment-progress",
            name: "部署进度",
            icon: "tasks",
            url: "#deployment-progress",
          },
          {
            id: "module-status",
            name: "模块状态",
            icon: "cubes",
            url: "#module-status",
          },
          {
            id: "scripts",
            name: "脚本控制",
            icon: "terminal",
            url: "#scripts",
          },
        ],
      },
      {
        id: "config",
        name: "配置管理",
        icon: "cogs",
        url: null,
        badge: null,
        children: [
          {
            id: "config-management",
            name: "配置编辑",
            icon: "edit",
            url: "#config-management",
          },
          {
            id: "port-mapping",
            name: "端口映射",
            icon: "sitemap",
            url: "#port-mapping",
          },
          {
            id: "logs",
            name: "日志查看",
            icon: "file-alt",
            url: "#logs-viewer",
          },
        ],
      },
      {
        id: "tools",
        name: "工具",
        icon: "tools",
        url: null,
        badge: null,
        children: [
          {
            id: "camera-manager",
            name: "摄像头管理",
            icon: "camera",
            url: "#camera-manager",
          },
          { id: "ai-config", name: "AI配置", icon: "brain", url: "#ai-config" },
          {
            id: "test-runner",
            name: "测试运行",
            icon: "vial",
            url: "#test-runner",
          },
        ],
      },
      {
        id: "engines",
        name: "引擎管理",
        icon: "engine",
        url: null,
        badge: null,
        children: [
          {
            id: "deep-live-cam",
            name: "Deep-Live-Cam",
            icon: "video",
            url: "#engine-deep-live-cam",
          },
          {
            id: "facefusion",
            name: "FaceFusion",
            icon: "user",
            url: "#engine-facefusion",
          },
          { id: "iroop", name: "iRoop", icon: "magic", url: "#engine-iroop" },
        ],
      },
    ];
  },

  /**
   * 渲染菜单
   */
  render: function (containerId = this.config.containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`[DynamicMenu] 容器不存在: ${containerId}`);
      return;
    }

    // 检查缓存
    const cacheKey = `${containerId}_${JSON.stringify(this.menuData)}`;
    if (this.renderCache[cacheKey]) {
      container.innerHTML = this.renderCache[cacheKey];
      this.bindEvents();
      return;
    }

    // 构建菜单HTML
    let html = this.buildMenuHtml(this.menuData, 0);

    // 缓存并渲染
    this.renderCache[cacheKey] = html;
    container.innerHTML = html;

    // 绑定事件
    this.bindEvents();

    console.log("[DynamicMenu] 菜单渲染完成");
  },

  /**
   * 构建菜单HTML
   */
  buildMenuHtml: function (items, depth) {
    if (depth >= this.config.maxDepth) return "";

    let html = "";

    items.forEach((item, index) => {
      const hasChildren = item.children && item.children.length > 0;
      const isActive = this.isActive(item);
      const badgeHtml =
        item.badge && this.config.showBadges
          ? `<span class="badge bg-${item.badge.type || "info"} ms-2">${item.badge.text}</span>`
          : "";

      if (hasChildren) {
        // 父菜单
        html += `
                    <div class="menu-item menu-group" data-menu-id="${item.id}">
                        <div class="menu-group-header ${isActive ? "active" : ""}" data-bs-toggle="collapse"
                             data-bs-target="#menuCollapse_${item.id}" aria-expanded="${isActive ? "true" : "false"}">
                            ${
                              this.config.showIcons
                                ? `<i class="fas fa-${item.icon} menu-icon"></i>`
                                : ""
                            }
                            <span class="menu-title">${item.name}</span>
                            ${badgeHtml}
                            <i class="fas fa-chevron-down menu-arrow ms-auto"></i>
                        </div>
                        <div class="collapse ${isActive ? "show" : ""}" id="menuCollapse_${item.id}">
                            <div class="menu-group-body">
                                ${this.buildMenuHtml(item.children, depth + 1)}
                            </div>
                        </div>
                    </div>
                `;
      } else {
        // 子菜单
        html += `
                    <a href="${item.url || "#"}" class="menu-item menu-link ${isActive ? "active" : ""}"
                       data-menu-id="${item.id}" data-url="${item.url || ""}">
                        ${
                          this.config.showIcons
                            ? `<i class="fas fa-${item.icon} menu-icon"></i>`
                            : ""
                        }
                        <span class="menu-title">${item.name}</span>
                        ${badgeHtml}
                    </a>
                `;
      }
    });

    return html;
  },

  /**
   * 绑定事件
   */
  bindEvents: function () {
    const container = document.getElementById(this.config.containerId);
    if (!container) return;

    // 菜单项点击事件
    container.querySelectorAll(".menu-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const menuId = link.dataset.menuId;
        const url = link.dataset.url;

        // 更新激活状态
        this.setActive(menuId);

        // 导航
        if (url && url !== "#") {
          this.navigateTo(url);
        }

        // 发送事件
        if (typeof EventBus !== "undefined") {
          EventBus.emit("menu:clicked", { menuId, url });
        }
      });
    });
  },

  /**
   * 设置激活状态
   */
  setActive: function (menuId) {
    const container = document.getElementById(this.config.containerId);
    if (!container) return;

    // 移除所有激活状态
    container.querySelectorAll(".menu-item, .menu-link").forEach((item) => {
      item.classList.remove("active");
    });

    // 添加激活状态
    const activeItem = container.querySelector(`[data-menu-id="${menuId}"]`);
    if (activeItem) {
      activeItem.classList.add("active");

      // 展开父级
      const parentCollapse = activeItem.closest(".collapse");
      if (parentCollapse) {
        parentCollapse.classList.add("show");
      }
    }
  },

  /**
   * 检查是否激活
   */
  isActive: function (item) {
    const currentHash = window.location.hash.slice(1) || "dashboard";
    return (
      item.url === `#${currentHash}` ||
      item.id === currentHash ||
      (item.children &&
        item.children.some(
          (child) =>
            child.url === `#${currentHash}` || child.id === currentHash,
        ))
    );
  },

  /**
   * 导航到指定位置
   */
  navigateTo: function (url) {
    // 滚动到目标元素
    const targetId = url.replace("#", "");
    const targetElement = document.getElementById(targetId);

    if (targetElement) {
      targetElement.scrollIntoView({ behavior: "smooth", block: "start" });

      // 高亮目标元素
      targetElement.classList.add("highlighted");
      setTimeout(() => {
        targetElement.classList.remove("highlighted");
      }, 2000);
    }

    // 更新URL哈希
    window.location.hash = url;
  },

  /**
   * 添加菜单项
   */
  addItem: function (parentId, item) {
    const parent = this.findMenuItem(this.menuData, parentId);
    if (parent) {
      if (!parent.children) {
        parent.children = [];
      }
      parent.children.push(item);
      this.render();
      return true;
    }
    return false;
  },

  /**
   * 移除菜单项
   */
  removeItem: function (itemId) {
    const removeFromArray = (items) => {
      const index = items.findIndex((item) => item.id === itemId);
      if (index !== -1) {
        items.splice(index, 1);
        return true;
      }
      for (const item of items) {
        if (item.children && removeFromArray(item.children)) {
          return true;
        }
      }
      return false;
    };

    if (removeFromArray(this.menuData)) {
      this.render();
      return true;
    }
    return false;
  },

  /**
   * 更新菜单项
   */
  updateItem: function (itemId, updates) {
    const updateInArray = (items) => {
      const item = items.find((i) => i.id === itemId);
      if (item) {
        Object.assign(item, updates);
        return true;
      }
      for (const item of items) {
        if (item.children && updateInArray(item.children)) {
          return true;
        }
      }
      return false;
    };

    if (updateInArray(this.menuData)) {
      this.render();
      return true;
    }
    return false;
  },

  /**
   * 查找菜单项
   */
  findMenuItem: function (items, id) {
    for (const item of items) {
      if (item.id === id) {
        return item;
      }
      if (item.children) {
        const found = this.findMenuItem(item.children, id);
        if (found) return found;
      }
    }
    return null;
  },

  /**
   * 更新徽章
   */
  updateBadge: function (itemId, badge) {
    const item = this.findMenuItem(this.menuData, itemId);
    if (item) {
      item.badge = badge;
      this.render();
      return true;
    }
    return false;
  },

  /**
   * 获取菜单数据
   */
  getMenuData: function () {
    return this.menuData;
  },

  /**
   * 导出菜单为JSON
   */
  exportAsJson: function () {
    return JSON.stringify(this.menuData, null, 2);
  },

  /**
   * 刷新菜单
   */
  refresh: function () {
    this.menuData = [];
    this.renderCache = {};
    this.loadMenu();
  },

  /**
   * 创建快捷菜单
   */
  createQuickMenu: function (containerId, maxItems = 5) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const recentItems = this.getRecentItems(maxItems);

    let html = '<div class="quick-menu">';
    recentItems.forEach((item) => {
      html += `
                <a href="${item.url || "#"}" class="quick-menu-item" data-url="${item.url || ""}">
                    <i class="fas fa-${item.icon}"></i>
                    <span>${item.name}</span>
                </a>
            `;
    });
    html += "</div>";

    container.innerHTML = html;
  },

  /**
   * 获取最近使用的菜单项
   */
  getRecentItems: function (maxItems = 5) {
    // 从localStorage获取使用历史
    try {
      const history = JSON.parse(localStorage.getItem("menuHistory") || "[]");
      return history.slice(0, maxItems);
    } catch {
      return [];
    }
  },

  /**
   * 记录菜单使用历史
   */
  recordUsage: function (itemId) {
    const item = this.findMenuItem(this.menuData, itemId);
    if (!item) return;

    try {
      let history = JSON.parse(localStorage.getItem("menuHistory") || "[]");

      // 移除已存在的记录
      history = history.filter((h) => h.id !== itemId);

      // 添加到开头
      history.unshift({
        id: item.id,
        name: item.name,
        icon: item.icon,
        url: item.url,
        timestamp: Date.now(),
      });

      // 限制数量
      history = history.slice(0, 10);

      localStorage.setItem("menuHistory", JSON.stringify(history));
    } catch (e) {
      console.warn("[DynamicMenu] 记录菜单使用历史失败:", e);
    }
  },
};

// 导出到全局
window.DynamicMenu = DynamicMenu;
