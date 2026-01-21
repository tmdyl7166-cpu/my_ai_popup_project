/**
 * 视频插入器模块
 * Video Inserter Module
 * 
 * 功能：
 * - 向视频流中插入视频片段
 * - 配置视频插入参数
 * - 插入到虚拟摄像头
 * 
 * 依赖：
 * - apiInterface.js - API调用封装
 * - cameraManager.js - 摄像头管理
 */

class VideoInserter {
    constructor() {
        // 插入配置
        this.config = {
            sourceVideo: null,      // 源视频路径
            insertPosition: 'overlay', // 插入位置 ('overlay' | 'background' | 'picture-in-picture')
            position: { x: 0, y: 0 },
            size: { width: 320, height: 240 },
            opacity: 1.0,
            volume: 0.5,
            loop: true,
            startTime: 0,
            endTime: null
        };
        
        // 插入历史
        this.insertHistory = [];
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[VideoInserter] 初始化视频插入器');
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        document.addEventListener('video-insert:config', (e) => this.configure(e.detail));
        document.addEventListener('video-insert:start', (e) => this.startInsert(e.detail));
        document.addEventListener('video-insert:stop', () => this.stopInsert());
        document.addEventListener('video-insert:load-video', (e) => this.loadVideo(e.detail.videoPath));
    }
    
    /**
     * 加载视频文件
     * @param {string} videoPath - 视频路径
     */
    async loadVideo(videoPath) {
        try {
            const response = await apiInterface.post('/api/video/insert/load', {
                videoPath: videoPath
            });
            
            if (response.status === 'success') {
                this.config.sourceVideo = response.videoData;
                
                // 发送视频加载事件
                document.dispatchEvent(new CustomEvent('video-insert:video-loaded', {
                    detail: { videoData: response.videoData, duration: response.duration }
                }));
                
                return { success: true, videoData: response.videoData, duration: response.duration };
            } else {
                throw new Error(response.message || '加载失败');
            }
        } catch (error) {
            console.error('[VideoInserter] 加载视频失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 配置插入参数
     * @param {Object} config - 配置对象
     */
    async configure(config) {
        const validKeys = ['insertPosition', 'position', 'size', 'opacity', 'volume', 'loop', 'startTime', 'endTime'];
        
        validKeys.forEach(key => {
            if (config[key] !== undefined) {
                this.config[key] = config[key];
            }
        });
        
        await this.saveConfig();
        
        document.dispatchEvent(new CustomEvent('video-insert:configured', {
            detail: { config: this.config }
        }));
        
        console.log('[VideoInserter] 插入配置已更新:', this.config);
        return { success: true, config: this.config };
    }
    
    /**
     * 保存配置
     */
    async saveConfig() {
        try {
            await apiInterface.post('/api/video/insert/config', this.config);
        } catch (error) {
            console.error('[VideoInserter] 保存配置失败:', error);
        }
    }
    
    /**
     * 开始插入视频
     * @param {Object} options - 插入选项
     */
    async startInsert(options = {}) {
        const {
            videoData = this.config.sourceVideo,
            position = this.config.position,
            size = this.config.size,
            opacity = this.config.opacity,
            insertPosition = this.config.insertPosition,
            loop = this.config.loop
        } = options;
        
        if (!videoData) {
            notifications.showError('请先加载要插入的视频');
            return { success: false, error: '未加载视频' };
        }
        
        try {
            const response = await apiInterface.post('/api/video/insert/start', {
                videoData: videoData,
                position: position,
                size: size,
                opacity: opacity,
                insertPosition: insertPosition,
                loop: loop
            });
            
            if (response.status === 'success') {
                this.insertHistory.push({
                    timestamp: Date.now(),
                    videoData: videoData,
                    position: position,
                    insertPosition: insertPosition
                });
                
                document.dispatchEvent(new CustomEvent('video-insert:started', {
                    detail: { result: response }
                }));
                
                notifications.showSuccess('视频插入已开始');
                return { success: true, result: response };
            } else {
                throw new Error(response.message || '插入失败');
            }
        } catch (error) {
            console.error('[VideoInserter] 插入视频失败:', error);
            notifications.showError(`插入失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 停止插入视频
     */
    async stopInsert() {
        try {
            const response = await apiInterface.post('/api/video/insert/stop', {});
            
            document.dispatchEvent(new CustomEvent('video-insert:stopped', {
                detail: {}
            }));
            
            notifications.showInfo('视频插入已停止');
            return { success: true };
        } catch (error) {
            console.error('[VideoInserter] 停止插入失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 暂停插入
     */
    async pauseInsert() {
        try {
            await apiInterface.post('/api/video/insert/pause', {});
            notifications.showInfo('视频插入已暂停');
            return { success: true };
        } catch (error) {
            console.error('[VideoInserter] 暂停插入失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 继续插入
     */
    async resumeInsert() {
        try {
            await apiInterface.post('/api/video/insert/resume', {});
            notifications.showSuccess('视频插入已继续');
            return { success: true };
        } catch (error) {
            console.error('[VideoInserter] 继续插入失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 获取插入历史
     */
    getHistory() {
        return [...this.insertHistory];
    }
    
    /**
     * 获取当前配置
     */
    getConfig() {
        return { ...this.config };
    }
    
    /**
     * 创建配置UI
     * @param {string} containerId - 容器ID
     */
    createConfigUI(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[VideoInserter] 未找到容器元素: ${containerId}`);
            return;
        }
        
        container.innerHTML = `
            <div class="video-inserter-config">
                <h4>视频插入配置</h4>
                
                <div class="form-group">
                    <label>插入位置</label>
                    <select id="insert-position" class="form-control">
                        <option value="overlay" ${this.config.insertPosition === 'overlay' ? 'selected' : ''}>叠加层</option>
                        <option value="background" ${this.config.insertPosition === 'background' ? 'selected' : ''}>背景</option>
                        <option value="pip" ${this.config.insertPosition === 'pip' ? 'selected' : ''}>画中画</option>
                    </select>
                </div>
                
                <div class="form-group" id="pip-position-group">
                    <label>画中画位置</label>
                    <select id="pip-position" class="form-control">
                        <option value="top-left">左上</option>
                        <option value="top-right">右上</option>
                        <option value="bottom-left">左下</option>
                        <option value="bottom-right">右下</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>尺寸 (宽 x 高)</label>
                    <div class="input-group">
                        <input type="number" id="insert-width" value="${this.config.size.width}" class="form-control">
                        <span class="input-group-text">x</span>
                        <input type="number" id="insert-height" value="${this.config.size.height}" class="form-control">
                    </div>
                </div>
                
                <div class="form-group">
                    <label>透明度: <span id="insert-opacity-value">${this.config.opacity}</span></label>
                    <input type="range" id="insert-opacity" 
                           min="0" max="1" step="0.1" 
                           value="${this.config.opacity}" class="form-control">
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="insert-loop" 
                               ${this.config.loop ? 'checked' : ''}>
                        循环播放
                    </label>
                </div>
                
                <div class="form-actions">
                    <button id="insert-start" class="btn btn-primary">开始插入</button>
                    <button id="insert-pause" class="btn btn-secondary">暂停</button>
                    <button id="insert-stop" class="btn btn-danger">停止</button>
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
        // 透明度滑块
        container.querySelector('#insert-opacity').addEventListener('input', (e) => {
            container.querySelector('#insert-opacity-value').textContent = e.target.value;
        });
        
        // 开始按钮
        container.querySelector('#insert-start').addEventListener('click', async () => {
            const config = {
                insertPosition: container.querySelector('#insert-position').value,
                size: {
                    width: parseInt(container.querySelector('#insert-width').value),
                    height: parseInt(container.querySelector('#insert-height').value)
                },
                opacity: parseFloat(container.querySelector('#insert-opacity').value),
                loop: container.querySelector('#insert-loop').checked
            };
            
            await this.configure(config);
            await this.startInsert();
        });
        
        // 暂停按钮
        container.querySelector('#insert-pause').addEventListener('click', async () => {
            await this.pauseInsert();
        });
        
        // 停止按钮
        container.querySelector('#insert-stop').addEventListener('click', async () => {
            await this.stopInsert();
        });
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        this.stopInsert();
        this.insertHistory = [];
        document.removeEventListener('video-insert:config');
        document.removeEventListener('video-insert:start');
        document.removeEventListener('video-insert:stop');
        document.removeEventListener('video-insert:load-video');
    }
}

// 创建全局实例
window.videoInserter = new VideoInserter();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VideoInserter;
}

