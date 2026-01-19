/**
 * 摄像头管理模块
 * Camera Manager Module
 * 
 * 功能：
 * - 启动/停止摄像头
 * - 设置摄像头权限
 * - 检测摄像头设备
 * - 管理视频流捕获
 * 
 * 依赖：
 * - apiInterface.js - API调用封装
 * - modalManager.js - 弹窗管理
 * - notifications.js - 通知系统
 */

class CameraManager {
    constructor() {
        // 摄像头状态
        this.cameraStatus = {
            isRunning: false,
            currentDevice: null,
            devices: [],
            stream: null,
            previewElement: null
        };
        
        // 权限状态
        this.permissionStatus = {
            camera: 'prompt', // 'granted', 'denied', 'prompt'
            microphone: 'prompt'
        };
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[CameraManager] 初始化摄像头管理器');
        this.loadDevices();
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 摄像头相关事件监听
        document.addEventListener('camera:start', (e) => this.startCamera(e.detail));
        document.addEventListener('camera:stop', () => this.stopCamera());
        document.addEventListener('camera:check-permissions', () => this.checkPermissions());
        document.addEventListener('camera:switch-device', (e) => this.switchDevice(e.detail.deviceId));
    }
    
    /**
     * 加载可用摄像头设备
     */
    async loadDevices() {
        try {
            const response = await apiInterface.get('/api/video/cameras');
            if (response.status === 'success') {
                this.cameraStatus.devices = response.cameras || [];
                console.log(`[CameraManager] 加载到 ${this.cameraStatus.devices.length} 个摄像头设备`);
                
                // 发送设备列表更新事件
                document.dispatchEvent(new CustomEvent('cameras:updated', {
                    detail: { devices: this.cameraStatus.devices }
                }));
            }
        } catch (error) {
            console.error('[CameraManager] 加载摄像头设备失败:', error);
            this.cameraStatus.devices = [];
        }
    }
    
    /**
     * 检查摄像头权限
     */
    async checkPermissions() {
        try {
            // 使用浏览器API检查权限
            if (navigator.permissions && navigator.permissions.query) {
                const result = await navigator.permissions.query({ name: 'camera' });
                this.permissionStatus.camera = result.state;
                
                // 监听权限变化
                result.onchange = () => {
                    this.permissionStatus.camera = result.state;
                    document.dispatchEvent(new CustomEvent('camera:permission-changed', {
                        detail: { permission: 'camera', status: result.state }
                    }));
                };
            }
            
            // 发送权限状态事件
            document.dispatchEvent(new CustomEvent('camera:permissions-checked', {
                detail: { permissions: this.permissionStatus }
            }));
            
            return this.permissionStatus;
        } catch (error) {
            console.error('[CameraManager] 检查权限失败:', error);
            return this.permissionStatus;
        }
    }
    
    /**
     * 请求摄像头权限
     */
    async requestPermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            // 停止流，因为只是请求权限
            stream.getTracks().forEach(track => track.stop());
            
            this.permissionStatus.camera = 'granted';
            notifications.showSuccess('摄像头权限已授予');
            
            return true;
        } catch (error) {
            console.error('[CameraManager] 请求摄像头权限失败:', error);
            this.permissionStatus.camera = 'denied';
            notifications.showError('无法获取摄像头权限，请检查系统设置');
            return false;
        }
    }
    
    /**
     * 启动摄像头
     * @param {Object} options - 启动选项
     * @param {string} options.deviceId - 设备ID（可选）
     * @param {string} options.previewElement - 预览元素ID（可选）
     * @param {number} options.width - 视频宽度（可选）
     * @param {number} options.height - 视频高度（可选）
     */
    async startCamera(options = {}) {
        const {
            deviceId = null,
            previewElement = 'camera-preview',
            width = 1280,
            height = 720
        } = options;
        
        try {
            // 检查权限
            if (this.permissionStatus.camera !== 'granted') {
                const granted = await this.requestPermission();
                if (!granted) {
                    throw new Error('摄像头权限被拒绝');
                }
            }
            
            // 构建媒体约束
            const constraints = {
                video: {
                    width: { ideal: width },
                    height: { ideal: height },
                    facingMode: 'user'
                }
            };
            
            // 如果指定了设备ID
            if (deviceId) {
                constraints.video.deviceId = { exact: deviceId };
            }
            
            // 停止现有流
            if (this.cameraStatus.stream) {
                this.stopCamera();
            }
            
            // 启动摄像头
            console.log('[CameraManager] 启动摄像头...');
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            this.cameraStatus.stream = stream;
            this.cameraStatus.isRunning = true;
            
            // 设置预览
            const preview = document.getElementById(previewElement);
            if (preview) {
                preview.srcObject = stream;
                this.cameraStatus.previewElement = previewElement;
            }
            
            // 更新状态
            this.cameraStatus.currentDevice = deviceId;
            
            // 发送启动成功事件
            document.dispatchEvent(new CustomEvent('camera:started', {
                detail: {
                    deviceId: deviceId,
                    stream: stream,
                    previewElement: previewElement
                }
            }));
            
            notifications.showSuccess('摄像头已启动');
            
            // 调用后端API记录状态
            await apiInterface.post('/api/camera/start', {
                deviceId: deviceId,
                width: width,
                height: height
            });
            
            return { success: true, stream: stream };
        } catch (error) {
            console.error('[CameraManager] 启动摄像头失败:', error);
            
            let errorMessage = '无法启动摄像头';
            if (error.name === 'NotAllowedError') {
                errorMessage = '摄像头权限被拒绝，请前往系统设置开启权限';
            } else if (error.name === 'NotFoundError') {
                errorMessage = '未找到摄像头设备';
            } else if (error.name === 'NotReadableError') {
                errorMessage = '摄像头被其他应用占用';
            }
            
            notifications.showError(errorMessage);
            
            document.dispatchEvent(new CustomEvent('camera:error', {
                detail: { error: error, message: errorMessage }
            }));
            
            return { success: false, error: error, message: errorMessage };
        }
    }
    
    /**
     * 停止摄像头
     */
    stopCamera() {
        try {
            if (this.cameraStatus.stream) {
                this.cameraStatus.stream.getTracks().forEach(track => {
                    track.stop();
                });
                this.cameraStatus.stream = null;
            }
            
            // 清除预览
            if (this.cameraStatus.previewElement) {
                const preview = document.getElementById(this.cameraStatus.previewElement);
                if (preview) {
                    preview.srcObject = null;
                }
                this.cameraStatus.previewElement = null;
            }
            
            this.cameraStatus.isRunning = false;
            this.cameraStatus.currentDevice = null;
            
            // 发送停止事件
            document.dispatchEvent(new CustomEvent('camera:stopped', {
                detail: {}
            }));
            
            notifications.showInfo('摄像头已关闭');
            
            // 调用后端API
            apiInterface.post('/api/camera/stop', {});
            
            return true;
        } catch (error) {
            console.error('[CameraManager] 停止摄像头失败:', error);
            return false;
        }
    }
    
    /**
     * 切换摄像头设备
     * @param {string} deviceId - 新设备ID
     */
    async switchDevice(deviceId) {
        if (this.cameraStatus.isRunning) {
            const currentDevice = this.cameraStatus.currentDevice;
            
            // 如果是同一个设备，不做处理
            if (currentDevice === deviceId) {
                return { success: true, message: '已是当前设备' };
            }
            
            // 重新启动摄像头
            const result = await this.startCamera({
                deviceId: deviceId,
                previewElement: this.cameraStatus.previewElement
            });
            
            return result;
        } else {
            // 只设置设备ID，不启动
            this.cameraStatus.currentDevice = deviceId;
            return { success: true, message: '设备已切换，下次启动时生效' };
        }
    }
    
    /**
     * 截图
     * @param {string} elementId - 视频元素ID
     * @param {Object} options - 截图选项
     */
    async takeScreenshot(elementId = 'camera-preview', options = {}) {
        const {
            format = 'png',
            quality = 0.92,
            filename = null
        } = options;
        
        try {
            const video = document.getElementById(elementId);
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
            
            // 如果需要保存文件
            if (filename) {
                const link = document.createElement('a');
                link.download = filename;
                link.href = dataUrl;
                link.click();
                
                // 调用后端API
                await apiInterface.post('/api/screenshot', {
                    format: format,
                    quality: quality,
                    filename: filename
                });
            }
            
            return {
                success: true,
                dataUrl: dataUrl,
                width: canvas.width,
                height: canvas.height
            };
        } catch (error) {
            console.error('[CameraManager] 截图失败:', error);
            notifications.showError('截图失败');
            return { success: false, error: error };
        }
    }
    
    /**
     * 获取摄像头状态
     */
    getStatus() {
        return {
            isRunning: this.cameraStatus.isRunning,
            currentDevice: this.cameraStatus.currentDevice,
            devices: this.cameraStatus.devices,
            permission: this.permissionStatus.camera
        };
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        this.stopCamera();
        this.cameraStatus.devices = [];
        document.removeEventListener('camera:start');
        document.removeEventListener('camera:stop');
        document.removeEventListener('camera:check-permissions');
    }
}

// 创建全局实例
window.cameraManager = new CameraManager();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CameraManager;
}

