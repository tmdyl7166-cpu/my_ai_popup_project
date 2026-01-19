/**
 * Core Module - 核心模块
 * 提供通用工具函数和帮助方法
 * 单一职责：工具函数集合
 */

const Core = {
    // 版本信息
    version: '1.0.0',

    // 工具函数
    utils: {
        /**
         * 格式化时间
         */
        formatTime: function(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
            const date = new Date(timestamp);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');

            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes)
                .replace('ss', seconds);
        },

        /**
         * 格式化文件大小
         */
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        /**
         * 格式化百分比
         */
        formatPercentage: function(value, decimals = 1) {
            return (value * 100).toFixed(decimals) + '%';
        },

        /**
         * 生成UUID
         */
        generateUUID: function() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        },

        /**
         * 检查是否为空
         */
        isEmpty: function(value) {
            if (value == null) return true;
            if (typeof value === 'string' || Array.isArray(value)) return value.length === 0;
            if (typeof value === 'object') return Object.keys(value).length === 0;
            return false;
        },

        /**
         * 防抖函数
         */
        debounce: function(func, wait, immediate = false) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    timeout = null;
                    if (!immediate) func.apply(this, args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(this, args);
            };
        },

        /**
         * 节流函数
         */
        throttle: function(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        /**
         * 获取URL参数
         */
        getUrlParameter: function(name) {
            const url = new URL(window.location.href);
            return url.searchParams.get(name);
        },

        /**
         * 设置URL参数
         */
        setUrlParameter: function(name, value) {
            const url = new URL(window.location.href);
            url.searchParams.set(name, value);
            window.history.replaceState({}, '', url.toString());
        },

        /**
         * 复制到剪贴板
         */
        copyToClipboard: async function(text) {
            try {
                if (navigator.clipboard && window.isSecureContext) {
                    await navigator.clipboard.writeText(text);
                    return true;
                } else {
                    // 降级方案
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    textArea.style.position = 'fixed';
                    textArea.style.left = '-999999px';
                    textArea.style.top = '-999999px';
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    const success = document.execCommand('copy');
                    textArea.remove();
                    return success;
                }
            } catch (error) {
                console.error('Failed to copy to clipboard:', error);
                return false;
            }
        },

        /**
         * 下载文件
         */
        downloadFile: function(data, filename, mimeType = 'text/plain') {
            const blob = new Blob([data], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        },

        /**
         * 触发自定义事件
         */
        triggerCustomEvent: function(eventName, detail = {}) {
            const event = new CustomEvent(eventName, { detail });
            document.dispatchEvent(event);
        },

        /**
         * 事件委托
         */
        delegate: function(element, eventType, selector, handler) {
            element.addEventListener(eventType, function(event) {
                const target = event.target.closest(selector);
                if (target) {
                    handler.call(target, event);
                }
            });
        },

        /**
         * 深度克隆对象
         */
        deepClone: function(obj) {
            if (obj === null || typeof obj !== 'object') return obj;
            if (obj instanceof Date) return new Date(obj.getTime());
            if (obj instanceof Array) return obj.map(item => this.deepClone(item));
            if (typeof obj === 'object') {
                const cloned = {};
                Object.keys(obj).forEach(key => {
                    cloned[key] = this.deepClone(obj[key]);
                });
                return cloned;
            }
        },

        /**
         * 合并对象
         */
        mergeObjects: function(target, source) {
            const result = this.deepClone(target);
            Object.keys(source).forEach(key => {
                if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                    result[key] = this.mergeObjects(result[key] || {}, source[key]);
                } else {
                    result[key] = source[key];
                }
            });
            return result;
        }
    },

    // DOM操作
    dom: {
        /**
         * 创建元素
         */
        createElement: function(tagName, attributes = {}, content = '') {
            const element = document.createElement(tagName);
            Object.keys(attributes).forEach(attr => {
                element.setAttribute(attr, attributes[attr]);
            });
            if (content) {
                element.innerHTML = content;
            }
            return element;
        },

        /**
         * 添加类名
         */
        addClass: function(element, className) {
            element.classList.add(className);
        },

        /**
         * 移除类名
         */
        removeClass: function(element, className) {
            element.classList.remove(className);
        },

        /**
         * 切换类名
         */
        toggleClass: function(element, className) {
            element.classList.toggle(className);
        },

        /**
         * 检查是否包含类名
         */
        hasClass: function(element, className) {
            return element.classList.contains(className);
        }
    },

    // 存储操作
    storage: {
        /**
         * 设置本地存储
         */
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Failed to set localStorage:', error);
                return false;
            }
        },

        /**
         * 获取本地存储
         */
        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Failed to get localStorage:', error);
                return defaultValue;
            }
        },

        /**
         * 移除本地存储
         */
        remove: function(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Failed to remove localStorage:', error);
                return false;
            }
        },

        /**
         * 清空本地存储
         */
        clear: function() {
            try {
                localStorage.clear();
                return true;
            } catch (error) {
                console.error('Failed to clear localStorage:', error);
                return false;
            }
        }
    },

    /**
     * 初始化核心模块
     */
    init: function() {
        console.log('Core module initialized, version:', this.version);
    },

    /**
     * 销毁核心模块
     */
    destroy: function() {
        console.log('Core module destroyed');
    }
};

// 导出到全局
window.Core = Core;
