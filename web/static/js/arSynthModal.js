/**
 * AR合成弹窗模块
 * AR Synthesis Modal Module
 * 
 * 功能：
 * - 显示AR合成应用的完整弹窗界面
 * - 集成所有功能模块（摄像头、合成、AI配置等）
 * - 提供统一的用户交互界面
 * 
 * 依赖：
 * - modalManager.js - 弹窗管理
 * - cameraManager.js - 摄像头管理
 * - virtualCameraSelector.js - 虚拟摄像头选择
 * - imageRecognitionConfig.js - 图片识别配置
 * - imageCompositor.js - 图片合成
 * - videoInserter.js - 视频插入
 * - aiConfigPanel.js - AI配置
 * - screenshotTool.js - 截图工具
 */

class ARSynthModal {
    constructor() {
        // 弹窗状态
        this.state = {
            isOpen: false,
            currentTab: 'camera',
            previewElement: 'ar-preview-video'
        };
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[ARSynthModal] 初始化AR合成弹窗');
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 打开弹窗
        document.addEventListener('ar-modal:open', () => this.open());
        
        // 关闭弹窗
        document.addEventListener('ar-modal:close', () => this.close());
        
        // 切换标签
        document.addEventListener('ar-modal:switch-tab', (e) => this.switchTab(e.detail.tab));
        
        // 摄像头事件
        document.addEventListener('camera:started', () => this.onCameraStarted());
        document.addEventListener('camera:stopped', () => this.onCameraStopped());
    }
    
    /**
     * 打开AR合成弹窗
     */
    open() {
        if (this.state.isOpen) {
            return;
        }
        
        // 检查摄像头权限
        cameraManager.checkPermissions();
        
        // 创建弹窗
        const modalId = 'ar-synth-modal';
        modalManager.createModal({
            id: modalId,
            title: 'AR 合成应用功能配置',
            content: this.generateModalContent(),
            size: 'large',
            onShow: () => {
                this.state.isOpen = true;
                this.initializeModules();
                this.bindModalEvents(modalId);
            },
            onClose: () => {
                this.state.isOpen = false;
                this.cleanup();
            }
        });
        
        document.dispatchEvent(new CustomEvent('ar-modal:opened', {}));
    }
    
    /**
     * 关闭弹窗
     */
    close() {
        // 停止摄像头
        cameraManager.stopCamera();
        
        // 关闭弹窗
        modalManager.closeModal('ar-synth-modal');
        
        document.dispatchEvent(new CustomEvent('ar-modal:closed', {}));
    }
    
    /**
     * 切换标签
     * @param {string} tab - 标签ID
     */
    switchTab(tab) {
        this.state.currentTab = tab;
        
        // 更新标签页激活状态
        document.querySelectorAll('.ar-tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`.ar-tab-btn[data-tab="${tab}"]`)?.classList.add('active');
        
        // 更新内容区域
        document.querySelectorAll('.ar-tab-content').forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById(`ar-tab-${tab}`).style.display = 'block';
    }
    
    /**
     * 生成弹窗内容
     */
    generateModalContent() {
        return `
            <div class="ar-synth-container">
                <!-- 标签页导航 -->
                <div class="ar-tabs">
                    <button class="ar-tab-btn active" data-tab="camera">📷 摄像头</button>
                    <button class="ar-tab-btn" data-tab="virtual">🔄 虚拟摄像头</button>
                    <button class="ar-tab-btn" data-tab="recognition">🔍 图片识别</button>
                    <button class="ar-tab-btn" data-tab="composite">🎨 图片合成</button>
                    <button class="ar-tab-btn" data-tab="video-insert">🎬 视频插入</button>
                    <button class="ar-tab-btn" data-tab="ai">🤖 AI配置</button>
                    <button class="ar-tab-btn" data-tab="screenshot">📸 截图</button>
                </div>
                
                <!-- 视频预览区域 -->
                <div class="ar-preview-area">
                    <video id="${this.state.previewElement}" autoplay playsinline muted>
                        您的浏览器不支持视频播放
                    </video>
                    <div class="ar-preview-overlay">
                        <span id="camera-status">摄像头未启动</span>
                    </div>
                </div>
                
                <!-- 标签页内容 -->
                <div class="ar-tab-content active" id="ar-tab-camera">
                    ${this.generateCameraTab()}
                </div>
                
                <div class="ar-tab-content" id="ar-tab-virtual">
                    ${this.generateVirtualCameraTab()}
                </div>
                
                <div class="ar-tab-content" id="ar-tab-recognition">
                    ${this.generateRecognitionTab()}
                </div>
                
                <div class="ar-tab-content" id="ar-tab-composite">
                    ${this.generateCompositeTab()}
                </div>
                
                <div class="ar-tab-content" id="ar-tab-video-insert">
                    ${this.generateVideoInsertTab()}
                </div>
                
                <div class="ar-tab-content" id="ar-tab-ai">
                    ${this.generateAITab()}
                </div>
                
                <div class="ar-tab-content" id="ar-tab-screenshot">
                    ${this.generateScreenshotTab()}
                </div>
                
                <!-- 底部按钮 -->
                <div class="ar-modal-footer">
                    <button id="ar-apply" class="btn btn-primary">应用</button>
                    <button id="ar-close" class="btn btn-secondary">关闭</button>
                </div>
            </div>
        `;
    }
    
    /**
     * 生成摄像头标签内容
     */
    generateCameraTab() {
        return `
            <div class="ar-config-section">
                <h4>摄像头管理</h4>
                <div class="button-group">
                    <button id="btn-start-camera" class="btn btn-success">▶ 启动摄像头</button>
                    <button id="btn-stop-camera" class="btn btn-danger" disabled>⏹ 停止摄像头</button>
                    <button id="btn-check-perms" class="btn btn-secondary">🔐 检查权限</button>
                </div>
                <div class="form-group">
                    <label>摄像头状态: <span id="camera-state-text">未启动</span></label>
                </div>
            </div>
        `;
    }
    
    /**
     * 生成虚拟摄像头标签内容
     */
    generateVirtualCameraTab() {
        return `
            <div class="ar-config-section">
                <h4>虚拟摄像头选择</h4>
                <div class="form-group">
                    <label>选择摄像头设备</label>
                    <select id="virtual-cam-select" class="form-control">
                        <option value="">-- 选择摄像头 --</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>输出配置</label>
                    <div class="input-row">
                        <input type="number" id="vc-width" value="1280" placeholder="宽度" class="form-control">
                        <span>x</span>
                        <input type="number" id="vc-height" value="720" placeholder="高度" class="form-control">
                    </div>
                </div>
                <div class="button-group">
                    <button id="btn-select-vc" class="btn btn-primary">选择设备</button>
                    <button id="btn-start-vc" class="btn btn-success">▶ 开始输出</button>
                    <button id="btn-stop-vc" class="btn btn-danger" disabled>⏹ 停止输出</button>
                </div>
            </div>
        `;
    }
    
    /**
     * 生成图片识别标签内容
     */
    generateRecognitionTab() {
        return `
            <div class="ar-config-section">
                <h4>图片识别配置</h4>
                <div id="recognition-config-container">
                    <!-- 由 imageRecognitionConfig 模块渲染 -->
                    <p class="text-muted">加载配置中...</p>
                </div>
            </div>
        `;
    }
    
    /**
     * 生成图片合成标签内容
     */
    generateCompositeTab() {
        return `
            <div class="ar-config-section">
                <h4>图片合成配置</h4>
                <div class="form-group">
                    <label>选择要合成的图片</label>
                    <input type="file" id="composite-image-input" accept="image/*" class="form-control">
                </div>
                <div id="composite-config-container">
                    <!-- 由 imageCompositor 模块渲染 -->
                    <p class="text-muted">加载配置中...</p>
                </div>
                <div class="button-group">
                    <button id="btn-composite-video" class="btn btn-primary">合成到视频</button>
                    <button id="btn-composite-vc" class="btn btn-primary">合成到虚拟摄像头</button>
                    <button id="btn-clear-composite" class="btn btn-secondary">清除效果</button>
                </div>
            </div>
        `;
    }
    
    /**
     * 生成视频插入标签内容
     */
    generateVideoInsertTab() {
        return `
            <div class="ar-config-section">
                <h4>视频插入配置</h4>
                <div class="form-group">
                    <label>选择要插入的视频</label>
                    <input type="file" id="insert-video-input" accept="video/*" class="form-control">
                </div>
                <div id="video-insert-config-container">
                    <!-- 由 videoInserter 模块渲染 -->
                    <p class="text-muted">加载配置中...</p>
                </div>
                <div class="button-group">
                    <button id="btn-start-insert" class="btn btn-success">▶ 开始插入</button>
                    <button id="btn-stop-insert" class="btn btn-danger" disabled>⏹ 停止插入</button>
                </div>
            </div>
        `;
    }
    
    /**
     * 生成AI配置标签内容
     */
    generateAITab() {
        return `
            <div class="ar-config-section">
                <h4>AI 配置与训练</h4>
                <div id="ai-config-container">
                    <!-- 由 aiConfigPanel 模块渲染 -->
                    <p class="text-muted">加载配置中...</p>
                </div>
            </div>
        `;
    }
    
    /**
     * 生成截图标签内容
     */
    generateScreenshotTab() {
        return `
            <div class="ar-config-section">
                <h4>截图设置</h4>
                <div id="screenshot-config-container">
                    <!-- 由 screenshotTool 模块渲染 -->
                    <p class="text-muted">加载配置中...</p>
                </div>
                <div class="button-group">
                    <button id="btn-take-screenshot" class="btn btn-primary">📸 截图</button>
                </div>
            </div>
        `;
    }
    
    /**
     * 初始化各模块
     */
    initializeModules() {
        // 初始化配置UI
        if (typeof imageRecognitionConfig !== 'undefined') {
            imageRecognitionConfig.createConfigUI('recognition-config-container');
        }
        if (typeof imageCompositor !== 'undefined') {
            imageCompositor.createConfigUI('composite-config-container');
        }
        if (typeof videoInserter !== 'undefined') {
            videoInserter.createConfigUI('video-insert-config-container');
        }
        if (typeof aiConfigPanel !== 'undefined') {
            aiConfigPanel.createConfigUI('ai-config-container');
        }
        if (typeof screenshotTool !== 'undefined') {
            screenshotTool.createConfigUI('screenshot-config-container');
        }
        
        // 加载虚拟摄像头设备列表
        if (typeof virtualCameraSelector !== 'undefined') {
            virtualCameraSelector.createSelectorUI('virtual-cam-select', {
                onChange: (deviceId) => {
                    virtualCameraSelector.selectDevice(deviceId);
                }
            });
        }
    }
    
    /**
     * 绑定弹窗内的事件
     */
    bindModalEvents(modalId) {
        // 标签切换
        document.querySelectorAll('.ar-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.dataset.tab);
            });
        });
        
        // 摄像头控制
        document.getElementById('btn-start-camera')?.addEventListener('click', () => {
            cameraManager.startCamera({
                previewElement: this.state.previewElement
            });
        });
        
        document.getElementById('btn-stop-camera')?.addEventListener('click', () => {
            cameraManager.stopCamera();
        });
        
        document.getElementById('btn-check-perms')?.addEventListener('click', () => {
            cameraManager.checkPermissions();
        });
        
        // 虚拟摄像头控制
        document.getElementById('btn-select-vc')?.addEventListener('click', () => {
            const deviceId = document.getElementById('virtual-cam-select').value;
            virtualCameraSelector.selectDevice(deviceId);
        });
        
        document.getElementById('btn-start-vc')?.addEventListener('click', () => {
            const width = document.getElementById('vc-width').value;
            const height = document.getElementById('vc-height').value;
            virtualCameraSelector.configureOutput({ width: parseInt(width), height: parseInt(height) });
            virtualCameraSelector.startOutput();
        });
        
        document.getElementById('btn-stop-vc')?.addEventListener('click', () => {
            virtualCameraSelector.stopOutput();
        });
        
        // 图片合成
        document.getElementById('composite-image-input')?.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                const result = await imageCompositor.loadImage({ imagePath: file.name });
                if (result.success) {
                    notifications.showSuccess('图片已加载');
                }
            }
        });
        
        document.getElementById('btn-composite-video')?.addEventListener('click', () => {
            imageCompositor.compositeToVideo();
        });
        
        document.getElementById('btn-composite-vc')?.addEventListener('click', () => {
            imageCompositor.compositeToVirtualCamera();
        });
        
        document.getElementById('btn-clear-composite')?.addEventListener('click', () => {
            imageCompositor.clearComposite();
        });
        
        // 视频插入
        document.getElementById('insert-video-input')?.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                const result = await videoInserter.loadVideo({ videoPath: file.name });
                if (result.success) {
                    notifications.showSuccess('视频已加载');
                }
            }
        });
        
        document.getElementById('btn-start-insert')?.addEventListener('click', () => {
            videoInserter.startInsert();
        });
        
        document.getElementById('btn-stop-insert')?.addEventListener('click', () => {
            videoInserter.stopInsert();
        });
        
        // 截图
        document.getElementById('btn-take-screenshot')?.addEventListener('click', () => {
            screenshotTool.capture({
                sourceElement: this.state.previewElement
            });
        });
        
        // 底部按钮
        document.getElementById('ar-apply')?.addEventListener('click', () => {
            notifications.showSuccess('配置已应用');
        });
        
        document.getElementById('ar-close')?.addEventListener('click', () => {
            this.close();
        });
    }
    
    /**
     * 摄像头启动回调
     */
    onCameraStarted() {
        document.getElementById('btn-start-camera').disabled = true;
        document.getElementById('btn-stop-camera').disabled = false;
        document.getElementById('camera-state-text').textContent = '运行中';
        document.getElementById('camera-status').textContent = '● 摄像头运行中';
        
        // 启用虚拟摄像头输出按钮
        document.getElementById('btn-start-vc').disabled = false;
    }
    
    /**
     * 摄像头停止回调
     */
    onCameraStopped() {
        document.getElementById('btn-start-camera').disabled = false;
        document.getElementById('btn-stop-camera').disabled = true;
        document.getElementById('camera-state-text').textContent = '已停止';
        document.getElementById('camera-status').textContent = '摄像头未启动';
        
        // 禁用虚拟摄像头输出按钮
        document.getElementById('btn-start-vc').disabled = true;
        document.getElementById('btn-stop-vc').disabled = true;
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        // 停止摄像头
        cameraManager.stopCamera();
        
        // 停止虚拟摄像头输出
        virtualCameraSelector.stopOutput();
        
        // 停止视频插入
        videoInserter.stopInsert();
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        this.cleanup();
        document.removeEventListener('ar-modal:open');
        document.removeEventListener('ar-modal:close');
        document.removeEventListener('ar-modal:switch-tab');
        document.removeEventListener('camera:started');
        document.removeEventListener('camera:stopped');
    }
}

// 创建全局实例
window.arSynthModal = new ARSynthModal();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ARSynthModal;
}

