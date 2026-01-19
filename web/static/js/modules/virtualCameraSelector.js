/**
 * 虚拟摄像头选择模块
 * Virtual Camera Selector Module
 * 
 * 功能：
 * - 检测可用虚拟摄像头
 * - 选择虚拟摄像头设备
 * - 配置虚拟摄像头输出
 * 
 * 依赖：
 * - apiInterface.js - API调用封装
 * - cameraManager.js - 摄像头管理
 */

class VirtualCameraSelector {
    constructor() {
        // 虚拟摄像头状态
        this.virtualCameraStatus = {
            devices: [],
            selectedDevice: null,
            isOutputting: false,
            outputConfig: {
                width: 1280,
                height: 720,
                fps: 30
            }
        };
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[VirtualCameraSelector] 初始化虚拟摄像头选择器');
        this.loadDevices();
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        document.addEventListener('virtual-cam:load-devices', () => this.loadDevices());
        document.addEventListener('virtual-cam:select', (e) => this.selectDevice(e.detail.deviceId));
        document.addEventListener('virtual-cam:configure', (e) => this.configureOutput(e.detail.config));
        document.addEventListener('virtual-cam:start-output', () => this.startOutput());
        document.addEventListener('virtual-cam:stop-output', () => this.stopOutput());
    }
    
    /**
     * 加载可用虚拟摄像头设备
     */
    async loadDevices() {
        try {
            const response = await apiInterface.get('/api/virtual-camera/devices');
            if (response.status === 'success') {
                this.virtualCameraStatus.devices = response.devices || [];
                console.log(`[VirtualCameraSelector] 加载到 ${this.virtualCameraStatus.devices.length} 个虚拟摄像头设备`);
                
                // 发送设备列表更新事件
                document.dispatchEvent(new CustomEvent('virtual-cam:devices-loaded', {
                    detail: { devices: this.virtualCameraStatus.devices }
                }));
            }
        } catch (error) {
            console.error('[VirtualCameraSelector] 加载虚拟摄像头设备失败:', error);
            this.virtualCameraStatus.devices = [];
        }
    }
    
    /**
     * 获取可用虚拟摄像头列表（包含真实摄像头）
     */
    async getAllVideoDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');
            
            // 区分真实摄像头和虚拟摄像头
            const realCameras = [];
            const virtualCameras = [];
            
            videoDevices.forEach(device => {
                const deviceInfo = {
                    deviceId: device.deviceId,
                    label: device.label || `摄像头 ${videoDevices.indexOf(device) + 1}`,
                    groupId: device.groupId
                };
                
                // 根据标签判断是否为虚拟摄像头
                if (device.label.toLowerCase().includes('virtual') || 
                    device.label.toLowerCase().includes('obs') ||
                    device.label.toLowerCase().includes('cam') ||
                    device.label.includes('HD')) {
                    virtualCameras.push({ ...deviceInfo, type: 'virtual' });
                } else {
                    realCameras.push({ ...deviceInfo, type: 'real' });
                }
            });
            
            return {
                real: realCameras,
                virtual: virtualCameras,
                all: [...realCameras, ...virtualCameras]
            };
        } catch (error) {
            console.error('[VirtualCameraSelector] 获取视频设备列表失败:', error);
            return { real: [], virtual: [], all: [] };
        }
    }
    
    /**
     * 选择虚拟摄像头设备
     * @param {string} deviceId - 设备ID
     */
    async selectDevice(deviceId) {
        try {
            const device = this.virtualCameraStatus.devices.find(d => d.deviceId === deviceId);
            
            if (!device) {
                throw new Error('未找到指定设备');
            }
            
            this.virtualCameraStatus.selectedDevice = device;
            
            // 调用后端API
            await apiInterface.post('/api/virtual-camera/select', {
                deviceId: deviceId,
                deviceName: device.name
            });
            
            // 发送选择事件
            document.dispatchEvent(new CustomEvent('virtual-cam:selected', {
                detail: { device: device }
            }));
            
            console.log(`[VirtualCameraSelector] 已选择虚拟摄像头: ${device.name}`);
            return { success: true, device: device };
        } catch (error) {
            console.error('[VirtualCameraSelector] 选择设备失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 配置虚拟摄像头输出
     * @param {Object} config - 输出配置
     */
    async configureOutput(config) {
        const {
            width = 1280,
            height = 720,
            fps = 30,
            format = 'mjpeg'
        } = config;
        
        try {
            this.virtualCameraStatus.outputConfig = {
                width,
                height,
                fps,
                format
            };
            
            // 调用后端API
            await apiInterface.post('/api/virtual-camera/configure', {
                width,
                height,
                fps,
                format
            });
            
            // 发送配置事件
            document.dispatchEvent(new CustomEvent('virtual-cam:configured', {
                detail: { config: this.virtualCameraStatus.outputConfig }
            }));
            
            console.log('[VirtualCameraSelector] 虚拟摄像头输出已配置:', this.virtualCameraStatus.outputConfig);
            return { success: true, config: this.virtualCameraStatus.outputConfig };
        } catch (error) {
            console.error('[VirtualCameraSelector] 配置输出失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 开始虚拟摄像头输出
     */
    async startOutput() {
        if (!this.virtualCameraStatus.selectedDevice) {
            notifications.showWarning('请先选择虚拟摄像头设备');
            return { success: false, error: '未选择设备' };
        }
        
        try {
            // 调用后端API
            const response = await apiInterface.post('/api/virtual-camera/start', {
                deviceId: this.virtualCameraStatus.selectedDevice.deviceId,
                config: this.virtualCameraStatus.outputConfig
            });
            
            if (response.status === 'success') {
                this.virtualCameraStatus.isOutputting = true;
                
                // 发送输出开始事件
                document.dispatchEvent(new CustomEvent('virtual-cam:output-started', {
                    detail: { device: this.virtualCameraStatus.selectedDevice }
                }));
                
                notifications.showSuccess('虚拟摄像头输出已启动');
                return { success: true };
            } else {
                throw new Error(response.message || '启动失败');
            }
        } catch (error) {
            console.error('[VirtualCameraSelector] 启动输出失败:', error);
            notifications.showError('启动虚拟摄像头输出失败');
            return { success: false, error: error };
        }
    }
    
    /**
     * 停止虚拟摄像头输出
     */
    async stopOutput() {
        try {
            // 调用后端API
            await apiInterface.post('/api/virtual-camera/stop', {});
            
            this.virtualCameraStatus.isOutputting = false;
            
            // 发送输出停止事件
            document.dispatchEvent(new CustomEvent('virtual-cam:output-stopped', {
                detail: {}
            }));
            
            notifications.showInfo('虚拟摄像头输出已停止');
            return { success: true };
        } catch (error) {
            console.error('[VirtualCameraSelector] 停止输出失败:', error);
            return { success: false, error: error };
        }
    }
    
    /**
     * 创建虚拟摄像头下拉框UI
     * @param {string} containerId - 容器元素ID
     * @param {Object} options - 选项
     */
    createSelectorUI(containerId, options = {}) {
        const {
            includeRealCameras = true,
            onChange = null,
            defaultDevice = null
        } = options;
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[VirtualCameraSelector] 未找到容器元素: ${containerId}`);
            return;
        }
        
        // 清空容器
        container.innerHTML = '';
        
        // 创建选择器
        const select = document.createElement('select');
        select.id = `${containerId}-select`;
        select.className = 'virtual-camera-select form-control';
        
        // 添加默认选项
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- 选择摄像头 --';
        select.appendChild(defaultOption);
        
        // 渲染选项
        this.renderOptions(select, includeRealCameras);
        
        // 绑定变更事件
        select.addEventListener('change', async (e) => {
            const deviceId = e.target.value;
            if (deviceId) {
                await this.selectDevice(deviceId);
                if (onChange) {
                    onChange(deviceId);
                }
            }
        });
        
        container.appendChild(select);
        
        // 如果有默认设备
        if (defaultDevice) {
            select.value = defaultDevice;
        }
    }
    
    /**
     * 渲染设备选项
     * @param {HTMLSelectElement} select - 选择器元素
     * @param {boolean} includeRealCameras - 是否包含真实摄像头
     */
    async renderOptions(select, includeRealCameras) {
        const allDevices = await this.getAllVideoDevices();
        
        // 如果不包含真实摄像头，只显示虚拟摄像头
        const devices = includeRealCameras ? allDevices.all : allDevices.virtual;
        
        devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            
            // 添加类型前缀
            const typePrefix = device.type === 'virtual' ? '[虚拟] ' : '[真实] ';
            option.textContent = `${typePrefix}${device.label}`;
            
            select.appendChild(option);
        });
    }
    
    /**
     * 获取当前状态
     */
    getStatus() {
        return {
            devices: this.virtualCameraStatus.devices,
            selectedDevice: this.virtualCameraStatus.selectedDevice,
            isOutputting: this.virtualCameraStatus.isOutputting,
            outputConfig: this.virtualCameraStatus.outputConfig
        };
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        this.stopOutput();
        this.virtualCameraStatus.devices = [];
        this.virtualCameraStatus.selectedDevice = null;
        document.removeEventListener('virtual-cam:load-devices');
        document.removeEventListener('virtual-cam:select');
        document.removeEventListener('virtual-cam:configure');
        document.removeEventListener('virtual-cam:start-output');
        document.removeEventListener('virtual-cam:stop-output');
    }
}

// 创建全局实例
window.virtualCameraSelector = new VirtualCameraSelector();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VirtualCameraSelector;
}

