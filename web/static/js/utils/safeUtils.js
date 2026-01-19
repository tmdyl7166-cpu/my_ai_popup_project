/**
 * SafeUtils - 安全工具模块
 * 提供XSS防护、HTML转义、CSRF工具等安全功能
 */

const SafeUtils = {
  // XSS过滤规则
  xssRules: {
    // 允许的标签
    allowedTags: [
      "b",
      "i",
      "em",
      "strong",
      "u",
      "s",
      "br",
      "p",
      "span",
      "div",
      "ul",
      "ol",
      "li",
      "a",
      "code",
      "pre",
    ],
    // 允许的属性
    allowedAttributes: {
      a: ["href", "title", "target"],
      span: ["class", "style", "title"],
      div: ["class", "style"],
      img: ["src", "alt", "title", "width", "height"],
    },
    // 允许的协议
    allowedProtocols: ["http:", "https:", "mailto:"],
    // 禁止的标签（完全移除）
    forbiddenTags: [
      "script",
      "style",
      "iframe",
      "object",
      "embed",
      "form",
      "input",
      "button",
      "textarea",
      "select",
    ],
    // 禁止的属性
    forbiddenAttrs: [
      "onerror",
      "onclick",
      "onload",
      "onmouseover",
      "oncontextmenu",
      "javascript:",
      "vbscript:",
    ],
  },

  /**
   * HTML转义
   * @param {string} str - 原始字符串
   * @returns {string} 转义后的字符串
   */
  escapeHtml: function (str) {
    if (str === null || str === undefined) return "";
    if (typeof str !== "string") str = String(str);

    const escapeMap = {
      "&": "&amp;",
      "<": "<",
      ">": ">",
      '"': '"',
      "'": "&#x27;",
      "/": "&#x2F;",
      "`": "&#x60;",
      "=": "&#x3D;",
    };

    return str.replace(/[&<>"'`=/]/g, (char) => escapeMap[char]);
  },

  /**
   * HTML反转义
   * @param {string} str - 转义后的字符串
   * @returns {string} 原始字符串
   */
  unescapeHtml: function (str) {
    if (str === null || str === undefined) return "";
    if (typeof str !== "string") str = String(str);

    const unescapeMap = {
      "&amp;": "&",
      "<": "<",
      ">": ">",
      '"': '"',
      "&#x27;": "'",
      "&#x2F;": "/",
      "&#x60;": "`",
      "&#x3D;": "=",
    };

    return str.replace(
      /&amp;|<|>|"|&#x27;|&#x2F;|&#x60;|&#x3D;/g,
      (char) => unescapeMap[char],
    );
  },

  /**
   * XSS过滤
   * @param {string} str - 原始字符串
   * @param {Object} options - 选项
   * @returns {string} 过滤后的字符串
   */
  xss: function (str, options = {}) {
    if (str === null || str === undefined) return "";
    if (typeof str !== "string") str = String(str);

    const rules = { ...this.xssRules, ...options };

    // 移除禁止的标签
    rules.forbiddenTags.forEach((tag) => {
      const regex = new RegExp(`<\\/?${tag}[^>]*>`, "gi");
      str = str.replace(regex, "");
    });

    // 移除禁止的属性
    rules.forbiddenAttrs.forEach((attr) => {
      const regex = new RegExp(`\\s*${attr}\\s*=\\s*["'][^"']*["']`, "gi");
      str = str.replace(regex, "");
      const regex2 = new RegExp(`\\s*${attr}\\s*=\\s*[^\\s>]+`, "gi");
      str = str.replace(regex2, "");
    });

    // 如果不是宽松模式，转义所有HTML
    if (!options.permissive) {
      str = this.escapeHtml(str);
    }

    return str;
  },

  /**
   * 清理富文本
   * @param {string} html - HTML字符串
   * @param {Object} options - 选项
   * @returns {string} 清理后的HTML
   */
  sanitizeHtml: function (html, options = {}) {
    if (html === null || html === undefined) return "";
    if (typeof html !== "string") return "";

    const rules = { ...this.xssRules, ...options };

    // 创建临时DOM
    const tempDiv = document.createElement("div");

    // 先转义所有内容
    let sanitized = this.escapeHtml(html);

    // 解析HTML
    tempDiv.innerHTML = sanitized;

    // 遍历所有元素
    const processNode = (node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        return;
      }

      if (node.nodeType === Node.ELEMENT_NODE) {
        const tagName = node.tagName.toLowerCase();

        // 检查是否允许的标签
        if (!rules.allowedTags.includes(tagName)) {
          // 不允许的标签，用文本内容替换
          const textContent = this.escapeHtml(node.textContent);
          node.parentNode.replaceChild(
            document.createTextNode(textContent),
            node,
          );
          return;
        }

        // 检查属性
        const attrs = node.attributes;
        for (let i = attrs.length - 1; i >= 0; i--) {
          const attrName = attrs[i].name.toLowerCase();

          // 移除禁止的属性
          if (
            rules.forbiddenAttrs.some((forbidden) =>
              attrName.startsWith(forbidden),
            )
          ) {
            node.removeAttribute(attrs[i].name);
            continue;
          }

          // 检查允许的属性
          const allowedAttrs = rules.allowedAttributes[tagName] || [];
          if (!allowedAttrs.includes(attrName)) {
            node.removeAttribute(attrs[i].name);
            continue;
          }

          // 检查href属性的协议
          if (attrName === "href") {
            const href = node.getAttribute("href");
            const isValidProtocol = rules.allowedProtocols.some((protocol) =>
              href.startsWith(protocol),
            );
            if (!isValidProtocol) {
              node.removeAttribute("href");
            }
          }
        }
      }
    };

    // 递归处理所有子节点
    const traverse = (node) => {
      processNode(node);
      node.childNodes.forEach((child) => traverse(child));
    };

    traverse(tempDiv);

    return tempDiv.innerHTML;
  },

  /**
   * JSON安全解析
   * @param {string} str - JSON字符串
   * @param {*} defaultValue - 默认值
   * @returns {*} 解析结果
   */
  safeJsonParse: function (str, defaultValue = null) {
    if (!str) return defaultValue;

    try {
      return JSON.parse(str);
    } catch (e) {
      // 尝试修复常见的JSON问题
      try {
        // 移除尾随逗号
        const fixed = str.replace(/,\s*([}\]])/g, "$1");
        return JSON.parse(fixed);
      } catch (e2) {
        console.warn("[SafeUtils] JSON解析失败:", e2);
        return defaultValue;
      }
    }
  },

  /**
   * 安全模板渲染
   * @param {string} template - 模板字符串
   * @param {Object} data - 数据对象
   * @returns {string} 渲染后的字符串
   */
  safeTemplate: function (template, data) {
    return template.replace(/\{\{\s*([^}]+)\s*\}\}/g, (match, key) => {
      const value = key
        .trim()
        .split(".")
        .reduce((obj, k) => obj && obj[k], data);
      return this.escapeHtml(value !== undefined ? value : "");
    });
  },

  /**
   * 生成随机令牌
   * @param {number} length - 令牌长度
   * @returns {string} 随机令牌
   */
  generateToken: function (length = 32) {
    const chars =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let token = "";
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    for (let i = 0; i < length; i++) {
      token += chars[array[i] % chars.length];
    }
    return token;
  },

  /**
   * 生成CSRF令牌
   * @returns {string} CSRF令牌
   */
  generateCsrfToken: function () {
    const token = this.generateToken(32);
    sessionStorage.setItem("csrf_token", token);
    return token;
  },

  /**
   * 获取CSRF令牌
   * @returns {string} CSRF令牌
   */
  getCsrfToken: function () {
    let token = sessionStorage.getItem("csrf_token");
    if (!token) {
      token = this.generateCsrfToken();
    }
    return token;
  },

  /**
   * 验证CSRF令牌
   * @param {string} token - 待验证的令牌
   * @returns {boolean} 是否有效
   */
  validateCsrfToken: function (token) {
    const storedToken = sessionStorage.getItem("csrf_token");
    return token && storedToken && token === storedToken;
  },

  /**
   * 获取带CSRF令牌的请求头
   * @returns {Object} 请求头对象
   */
  getCsrfHeaders: function () {
    return {
      "X-CSRF-Token": this.getCsrfToken(),
    };
  },

  /**
   * URL安全编码
   * @param {string} str - 原始字符串
   * @returns {string} 编码后的字符串
   */
  urlEncode: function (str) {
    return encodeURIComponent(str);
  },

  /**
   * URL安全解码
   * @param {string} str - 编码后的字符串
   * @returns {string} 原始字符串
   */
  urlDecode: function (str) {
    return decodeURIComponent(str);
  },

  /**
   * 验证URL安全性
   * @param {string} url - URL字符串
   * @returns {boolean} 是否安全
   */
  isSafeUrl: function (url) {
    if (!url) return false;

    try {
      const parsed = new URL(url, window.location.origin);
      return this.xssRules.allowedProtocols.includes(parsed.protocol);
    } catch (e) {
      return false;
    }
  },

  /**
   * 验证邮箱格式
   * @param {string} email - 邮箱地址
   * @returns {boolean} 是否有效
   */
  isValidEmail: function (email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  },

  /**
   * 验证URL格式
   * @param {string} url - URL地址
   * @returns {boolean} 是否有效
   */
  isValidUrl: function (url) {
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  },

  /**
   * 验证手机号格式
   * @param {string} phone - 手机号
   * @returns {boolean} 是否有效
   */
  isValidPhone: function (phone) {
    const regex = /^1[3-9]\d{9}$/;
    return regex.test(phone);
  },

  /**
   * 安全复制到剪贴板
   * @param {string} text - 要复制的文本
   * @returns {Promise<boolean>} 是否成功
   */
  copyToClipboard: async function (text) {
    try {
      await navigator.clipboard.writeText(this.escapeHtml(text));
      return true;
    } catch (e) {
      // 降级方案
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand("copy");
        return true;
      } catch (e2) {
        return false;
      } finally {
        document.body.removeChild(textarea);
      }
    }
  },
};

// 导出到全局
window.SafeUtils = SafeUtils;
