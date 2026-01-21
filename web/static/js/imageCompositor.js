/**
 * 图片合成器模块
 * Image Compositor Module
 * 
 * 功能：
 * - 将图片合成到视频流
 * - 将图片合成到虚拟摄像头
 * - 配置合成参数（透明度、位置、大小）
 * 
 * 依赖：
 * - apiInterface.js - API调用封装
 * - cameraManager.js - 摄像头管理
 * - virtualCameraSelector.js - 虚拟摄像头选择
 */

class ImageCompositor {
    constructor() {
        // 合成配置
        this.config = {
            sourceImage: null,      // 源图片路径/URL
            targetRegion: 'face',   // 合成区域 ('face' | 'full' | 'manual')
            position: { x: 0, y: 0 },     // 手动位置
            size: { width: 200, height: 200 },  // 合成尺寸
            opacity: 1.0,           // 透明度 0.0 - 1.0
            blendMode: 'source-over', // 混合模式
            rotation: 0,            // 旋转角度
            scale: 1.0              // 缩放比例
        };
        
        // 合成历史
        this.compositeHistory = [];
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[ImageCompositor] 初始化图片合成器');
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        document.addEventListener('composite:config', (e) => this.configure(e.detail));
        document.addEventListener('composite:to-video', (e) => this.compositeToVideo(e.detail));
        document.addEventListener('composite:to-virtual', (e) => this.compositeToVirtualCamera(e.detail));
        document.addEventListener('composite:load-image', (e) => this.loadImage(e.detail.imagePath));
    }
    
    /**
     * 加载图片
     * @param {string} imagePath - 图片路径或URL
     */
    async loadImage(imagePath) {
        try {
            const response = await apiInterface.post('/api/composite/load-image', {
                imagePath: imagePath
            });
            
            if (response.status === 'success') {
                this.config.sourceImage = response.imageData;
                
                // 发送图片加载事件
                document.dispatchEvent(new CustomEvent('composite:image-loaded', {
                    detail: { imageData: response.imageData }
                }));
                
                return { success: true, imageData: response.imageData };
            } else {
                throw new Error(response.message || '加载失败');
            }
        } catch (error) {
            console.error('[ImageCompositor] 加载图片失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 配置合成参数
     * @param {Object} config - 配置对象
     */
    async configure(config) {
        const validKeys = ['targetRegion', 'position', 'size', 'opacity', 'blendMode', 'rotation', 'scale'];
        
        validKeys.forEach(key => {
            if (config[key] !== undefined) {
                this.config[key] = config[key];
            }
        });
        
        // 如果提供了位置或大小，切换到手动模式
        if (config.position || config.size) {
            this.config.targetRegion = 'manual';
        }
        
        // 保存配置
        await this.saveConfig();
        
        // 发送配置事件
        document.dispatchEvent(new CustomEvent('composite:configured', {
            detail: { config: this.config }
        }));
        
        console.log('[ImageCompositor] 合成配置已更新:', this.config);
        return { success: true, config: this.config };
    }
    
    /**
     * 保存配置到后端
     */
    async saveConfig() {
        try {
            await apiInterface.post('/api/composite/config', this.config);
        } catch (error) {
            console.error('[ImageCompositor] 保存配置失败:', error);
        }
    }
    
    /**
     * 合成到视频流
     * @param {Object} options - 合成选项
     */
    async compositeToVideo(options = {}) {
        const {
            imageData = this.config.sourceImage,
            region = this.config.targetRegion,
            position = this.config.position,
            size = this.config.size,
            opacity = this.config.opacity
        } = options;
        
        if (!imageData) {
            notifications.showError('请先加载要合成的图片');
            return { success: false, error: '未加载图片' };
        }
        
        try {
            const response = await apiInterface.post('/api/composite/image-to-video', {
                imageData: imageData,
                region: region,
                position: position,
                size: size,
                opacity: opacity
            });
            
            if (response.status === 'success') {
                // 添加到历史记录
                this.compositeHistory.push({
                    timestamp: Date.now(),
                    type: 'video',
                    imageData: imageData,
                    region: region
                });
                
                // 发送合成完成事件
                document.dispatchEvent(new CustomEvent('composite:to-video-complete', {
                    detail: { result: response }
                }));
                
                notifications.showSuccess('图片已合成到视频流');
                return { success: true, result: response };
            } else {
                throw new Error(response.message || '合成失败');
            }
        } catch (error) {
            console.error('[ImageCompositor] 合成到视频失败:', error);
            notifications.showError(`合成失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 合成到虚拟摄像头
     * @param {Object} options - 合成选项
     */
    async compositeToVirtualCamera(options = {}) {
        const {
            imageData = this.config.sourceImage,
            position = this.config.position,
            size = this.config.size,
            opacity = this.config.opacity,
            blendMode = this.config.blendMode
        } = options;
        
        if (!imageData) {
            notifications.showError('请先加载要合成的图片');
            return { success: false, error: '未加载图片' };
        }
        
        try {
            const response = await apiInterface.post('/api/composite/image-to-virtual', {
                imageData: imageData,
                position: position,
                size: size,
                opacity: opacity,
                blendMode: blendMode
            });
            
            if (response.status === 'success') {
                // 添加到历史记录
                this.compositeHistory.push({
                    timestamp: Date.now(),
                    type: 'virtual',
                    imageData: imageData,
                    position: position
                });
                
                // 发送合成完成事件
                document.dispatchEvent(new CustomEvent('composite:to-virtual-complete', {
                    detail: { result: response }
                }));
                
                notifications.showSuccess('图片已合成到虚拟摄像头');
                return { success: true, result: response };
            } else {
                throw new Error(response.message || '合成失败');
            }
        } catch (error) {
            console.error('[ImageCompositor] 合成到虚拟摄像头失败:', error);
            notifications.showError(`合成失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 清除合成效果
     */
    async clearComposite() {
        try {
            const response = await apiInterface.post('/api/composite/clear', {});
            
            // 发送清除事件
            document.dispatchEvent(new CustomEvent('composite:cleared', {
                detail: {}
            }));
            
            notifications.showInfo('合成效果已清除');
            return { success: true };
        } catch (error) {
            console.error('[ImageCompositor] 清除合成失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 获取合成历史
     */
    getHistory() {
        return [...this.compositeHistory];
    }
    
    /**
     * 清除历史记录
     */
    clearHistory() {
        this.compositeHistory = [];
    }
    
    /**
     * 获取当前配置
     */
    getConfig() {
        return { ...this.config };
    }
    
    /**
     * 创建合成配置UI
     * @param {string} containerId - 容器ID
     */
    createConfigUI(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[ImageCompositor] 未找到容器元素: ${containerId}`);
            return;
        }
        
        container.innerHTML = `
            <div class="image-compositor-config">
                <h4>图片合成配置</h4>
                
                <div class="form-group">
                    <label>合成区域</label>
                    <select id="composite-region" class="form-control">
                        <option value="face" ${this.config.targetRegion === 'face' ? 'selected' : ''}>人脸区域</option>
                        <option value="full" ${this.config.targetRegion === 'full' ? 'selected' : ''}>全屏</option>
                        <option value="manual" ${this.config.targetRegion === 'manual' ? 'selected' : ''}>手动选择</option>
                    </select>
                </div>
                
                <div class="form-group" id="manual-position-group" style="display: none;">
                    <label>位置 (X, Y)</label>
                    <div class="input-group">
                        <input type="number" id="composite-pos-x" value="${this.config.position.x}" class="form-control">
                        <span class="input-group-text">,</span>
                        <input type="number" id="composite-pos-y" value="${this.config.position.y}" class="form-control">
                    </div>
                </div>
                
                <div class="form-group" id="size-group" style="display: none;">
                    <label>尺寸 (宽 x 高)</label>
                    <div class="input-group">
                        <input type="number" id="composite-width" value="${this.config.size.width}" class="form-control">
                        <span class="input-group-text">x</span>
                        <input type="number" id="composite-height" value="${this.config.size.height}" class="form-control">
                    </div>
                </div>
                
                <div class="form-group">
                    <label>透明度: <span id="opacity-value">${this.config.opacity}</span></label>
                    <input type="range" id="composite-opacity" 
                           min="0" max="1" step="0.1" 
                           value="${this.config.opacity}" class="form-control">
                </div>
                
                <div class="form-group">
                    <label>混合模式</label>
                    <select id="composite-blend-mode" class="form-control">
                        <option value="source-over" ${this.config.blendMode === 'source-over' ? 'selected' : ''}>正常</option>
                        <option value="multiply" ${this.config.blendMode === 'multiply' ? 'selected' : ''}>正片叠底</option>
                        <option value="screen" ${this.config.blendMode === 'screen' ? 'selected' : ''}>滤色</option>
                        <option value="overlay" ${this.config.blendMode === 'overlay' ? 'selected' : ''}>叠加</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button id="composite-apply" class="btn btn-primary">应用配置</button>
                    <button id="composite-clear" class="btn btn-danger">清除效果</button>
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
        // 区域变更
        container.querySelector('#composite-region').addEventListener('change', (e) => {
            const manualGroup = container.querySelector('#manual-position-group');
            const sizeGroup = container.querySelector('#size-group');
            
            if (e.target.value === 'manual') {
                manualGroup.style.display = 'block';
                sizeGroup.style.display = 'block';
            } else {
                manualGroup.style.display = 'none';
                sizeGroup.style.display = 'none';
            }
        });
        
        // 透明度滑块
        container.querySelector('#composite-opacity').addEventListener('input', (e) => {
            container.querySelector('#opacity-value').textContent = e.target.value;
        });
        
        // 应用按钮
        container.querySelector('#composite-apply').addEventListener('click', async () => {
            const region = container.querySelector('#composite-region').value;
            const position = {
                x: parseInt(container.querySelector('#composite-pos-x').value) || 0,
                y: parseInt(container.querySelector('#composite-pos-y').value) || 0
            };
            const size = {
                width: parseInt(container.querySelector('#composite-width').value) || 200,
                height: parseInt(container.querySelector('#composite-height').value) || 200
            };
            const opacity = parseFloat(container.querySelector('#composite-opacity').value);
            const blendMode = container.querySelector('#composite-blend-mode').value;
            
            await this.configure({
                targetRegion: region,
                position: position,
                size: size,
                opacity: opacity,
                blendMode: blendMode
            });
            
            notifications.showSuccess('配置已应用');
        });
        
        // 清除按钮
        container.querySelector('#composite-clear').addEventListener('click', async () => {
            await this.clearComposite();
        });
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        this.compositeHistory = [];
        document.removeEventListener('composite:config');
        document.removeEventListener('composite:to-video');
        document.removeEventListener('composite:to-virtual');
        document.removeEventListener('composite:load-image');
    }
}

// 创建全局实例
window.imageCompositor = new ImageCompositor();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageCompositor;
}

