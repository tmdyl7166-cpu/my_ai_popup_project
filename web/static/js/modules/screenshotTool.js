/**
 * 截图工具模块
 * Screenshot Tool Module
 * 
 * 功能：
 * - 截取视频流截图
 * - 保存截图到文件
 * - 管理截图历史
 * 
 * 依赖：
 * - apiInterface.js - API调用封装
 * - cameraManager.js - 摄像头管理
 */

class ScreenshotTool {
    constructor() {
        // 截图配置
        this.config = {
            format: 'png',           // 'png' | 'jpeg' | 'webp'
            quality: 0.92,           // 0.0 - 1.0 (仅JPEG/WebP)
            filename: 'screenshot',  // 文件名模板
            savePath: null,          // 保存路径
            autoIncrement: true      // 自动编号
        };
        
        // 截图历史
        this.screenshotHistory = [];
        
        // 计数器
        this.counter = 1;
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[ScreenshotTool] 初始化截图工具');
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        document.addEventListener('screenshot:capture', (e) => this.capture(e.detail));
        document.addEventListener('screenshot:config', (e) => this.configure(e.detail));
        document.addEventListener('screenshot:open-save-dialog', () => this.openSaveDialog());
    }
    
    /**
     * 截取截图
     * @param {Object} options - 截图选项
     */
    async capture(options = {}) {
        const {
            sourceElement = 'camera-preview',
            format = this.config.format,
            quality = this.config.quality,
            filename = this.generateFilename(),
            saveToFile = true
        } = options;
        
        try {
            // 获取视频元素
            const video = document.getElementById(sourceElement);
            if (!video) {
                throw new Error('未找到视频元素');
            }
            
            // 创建画布
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            // 转换为Blob
            const mimeType = `image/${format}`;
            const dataUrl = canvas.toDataURL(mimeType, quality);
            const blob = await this.dataUrlToBlob(dataUrl);
            
            const result = {
                timestamp: Date.now(),
                width: canvas.width,
                height: canvas.height,
                format: format,
                dataUrl: dataUrl,
                size: blob.size
            };
            
            // 保存到历史记录
            this.screenshotHistory.push(result);
            
            // 如果需要保存到文件
            if (saveToFile) {
                const savedFilename = await this.saveToFile(blob, filename);
                result.filename = savedFilename;
                
                // 通知后端
                await apiInterface.post('/api/screenshot', {
                    filename: savedFilename,
                    format: format,
                    width: canvas.width,
                    height: canvas.height,
                    size: blob.size
                });
            }
            
            // 发送截图完成事件
            document.dispatchEvent(new CustomEvent('screenshot:captured', {
                detail: { result: result }
            }));
            
            notifications.showSuccess(`截图已保存: ${result.filename || '已复制到剪贴板'}`);
            
            // 如果配置了自动复制到剪贴板
            if (this.config.copyToClipboard) {
                await this.copyToClipboard(dataUrl);
            }
            
            return { success: true, result: result };
        } catch (error) {
            console.error('[ScreenshotTool] 截取截图失败:', error);
            notifications.showError(`截图失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 生成文件名
     */
    generateFilename() {
        const timestamp = new Date();
        const dateStr = timestamp.toISOString().split('T')[0];
        const timeStr = timestamp.toTimeString().split(' ')[0].replace(/:/g, '-');
        
        if (this.config.autoIncrement) {
            const filename = `${this.config.filename}_${dateStr}_${timeStr}_${this.counter}`;
            this.counter++;
            return filename;
        }
        
        return `${this.config.filename}_${dateStr}_${timeStr}`;
    }
    
    /**
     * 保存到文件
     * @param {Blob} blob - 图片数据
     * @param {string} filename - 文件名
     */
    async saveToFile(blob, filename) {
        // 创建下载链接
        const link = document.createElement('a');
        link.download = `${filename}.${this.config.format}`;
        link.href = URL.createObjectURL(blob);
        link.click();
        
        // 释放URL
        setTimeout(() => {
            URL.revokeObjectURL(link.href);
        }, 1000);
        
        return link.download;
    }
    
    /**
     * 复制到剪贴板
     * @param {string} dataUrl - 图片数据URL
     */
    async copyToClipboard(dataUrl) {
        try {
            // 获取Blob
            const blob = await this.dataUrlToBlob(dataUrl);
            
            // 复制到剪贴板
            await navigator.clipboard.write([
                new ClipboardItem({
                    [blob.type]: blob
                })
            ]);
            
            notifications.showInfo('截图已复制到剪贴板');
            return true;
        } catch (error) {
            console.error('[ScreenshotTool] 复制到剪贴板失败:', error);
            return false;
        }
    }
    
    /**
     * DataURL转Blob
     * @param {string} dataUrl - DataURL
     */
    async dataUrlToBlob(dataUrl) {
        const response = await fetch(dataUrl);
        return await response.blob();
    }
    
    /**
     * 配置截图参数
     * @param {Object} config - 配置对象
     */
    async configure(config) {
        const validKeys = ['format', 'quality', 'filename', 'savePath', 'autoIncrement', 'copyToClipboard'];
        
        validKeys.forEach(key => {
            if (config[key] !== undefined) {
                this.config[key] = config[key];
            }
        });
        
        await this.saveConfig();
        
        document.dispatchEvent(new CustomEvent('screenshot:configured', {
            detail: { config: this.config }
        }));
        
        console.log('[ScreenshotTool] 截图配置已更新:', this.config);
        return { success: true, config: this.config };
    }
    
    /**
     * 保存配置
     */
    async saveConfig() {
        try {
            await apiInterface.post('/api/screenshot/config', this.config);
        } catch (error) {
            console.error('[ScreenshotTool] 保存配置失败:', error);
        }
    }
    
    /**
     * 打开保存路径对话框
     */
    async openSaveDialog() {
        // 使用File System Access API（如果支持）
        if (window.showDirectoryPicker) {
            try {
                const dirHandle = await window.showDirectoryPicker();
                this.config.savePath = dirHandle;
                
                document.dispatchEvent(new CustomEvent('screenshot:save-path-selected', {
                    detail: { path: dirHandle }
                }));
                
                return { success: true, path: dirHandle };
            } catch (error) {
                console.error('[ScreenshotTool] 选择保存路径失败:', error);
                return { success: false, error: error };
            }
        }
        
        // 降级处理：显示提示
        notifications.showInfo('请在下载时选择保存位置');
        return { success: false, error: 'API不支持' };
    }
    
    /**
     * 获取截图历史
     */
    getHistory() {
        return [...this.screenshotHistory];
    }
    
    /**
     * 清除历史记录
     */
    clearHistory() {
        this.screenshotHistory = [];
        this.counter = 1;
    }
    
    /**
     * 获取当前配置
     */
    getConfig() {
        return { ...this.config };
    }
    
    /**
     * 创建截图UI
     * @param {string} containerId - 容器ID
     */
    createConfigUI(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[ScreenshotTool] 未找到容器元素: ${containerId}`);
            return;
        }
        
        container.innerHTML = `
            <div class="screenshot-tool-config">
                <h4>截图设置</h4>
                
                <div class="form-group">
                    <label>图片格式</label>
                    <select id="screenshot-format" class="form-control">
                        <option value="png" ${this.config.format === 'png' ? 'selected' : ''}>PNG (无损)</option>
                        <option value="jpeg" ${this.config.format === 'jpeg' ? 'selected' : ''}>JPEG (有损)</option>
                        <option value="webp" ${this.config.format === 'webp' ? 'selected' : ''}>WebP (现代格式)</option>
                    </select>
                </div>
                
                <div class="form-group" id="quality-group" style="display: ${this.config.format !== 'png' ? 'block' : 'none'};">
                    <label>图片质量: <span id="quality-value">${Math.round(this.config.quality * 100)}%</span></label>
                    <input type="range" id="screenshot-quality" 
                           min="0.1" max="1.0" step="0.1" 
                           value="${this.config.quality}" class="form-control">
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="screenshot-auto-increment" 
                               ${this.config.autoIncrement ? 'checked' : ''}>
                        自动编号
                    </label>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="screenshot-copy-clipboard" 
                               ${this.config.copyToClipboard ? 'checked' : ''}>
                        自动复制到剪贴板
                    </label>
                </div>
                
                <div class="form-actions">
                    <button id="screenshot-apply" class="btn btn-primary">应用设置</button>
                    <button id="screenshot-clear-history" class="btn btn-secondary">清除历史</button>
                </div>
            </div>
        `;
        
        // 绑定事件
        this.bindConfigUIEvents(container);
    }
    
    /**
     * 绑定配置UI事件
     */
    bindConfigUIEvents(container) {
        // 格式变更
        container.querySelector('#screenshot-format').addEventListener('change', (e) => {
            const qualityGroup = container.querySelector('#quality-group');
            qualityGroup.style.display = e.target.value !== 'png' ? 'block' : 'none';
        });
        
        // 质量滑块
        container.querySelector('#screenshot-quality').addEventListener('input', (e) => {
            container.querySelector('#quality-value').textContent = `${Math.round(e.target.value * 100)}%`;
        });
        
        // 应用按钮
        container.querySelector('#screenshot-apply').addEventListener('click', async () => {
            const format = container.querySelector('#screenshot-format').value;
            const quality = parseFloat(container.querySelector('#screenshot-quality').value);
            const autoIncrement = container.querySelector('#screenshot-auto-increment').checked;
            const copyToClipboard = container.querySelector('#screenshot-copy-clipboard').checked;
            
            await this.configure({
                format: format,
                quality: quality,
                autoIncrement: autoIncrement,
                copyToClipboard: copyToClipboard
            });
            
            notifications.showSuccess('设置已应用');
        });
        
        // 清除历史按钮
        container.querySelector('#screenshot-clear-history').addEventListener('click', () => {
            this.clearHistory();
            notifications.showInfo('历史记录已清除');
        });
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        this.clearHistory();
        document.removeEventListener('screenshot:capture');
        document.removeEventListener('screenshot:config');
        document.removeEventListener('screenshot:open-save-dialog');
    }
}

// 创建全局实例
window.screenshotTool = new ScreenshotTool();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScreenshotTool;
}

