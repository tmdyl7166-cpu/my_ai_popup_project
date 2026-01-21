/**
 * 图片识别配置模块
 * Image Recognition Configuration Module
 * 
 * 功能：
 * - 选择识别模型（人脸识别、物体识别）
 * - 配置识别参数
 * - 管理识别模型
 * 
 * 依赖：
 * - apiInterface.js - API调用封装
 * - modalManager.js - 弹窗管理
 */

class ImageRecognitionConfig {
    constructor() {
        // 配置状态
        this.config = {
            model: 'face',           // 'face' | 'object'
            modelType: 'mediapipe',  // 'mediapipe' | 'opencv' | 'dlib' | 'tensorflow'
            sensitivity: 0.8,        // 0.1 - 1.0
            detectionArea: 'auto',   // 'auto' | 'manual'
            manualRegion: null,      // {x, y, width, height}
            enableTracking: true,
            enableLandmarks: false
        };
        
        // 可用模型
        this.availableModels = [
            { id: 'face', name: '人脸识别', types: ['mediapipe', 'opencv', 'dlib'] },
            { id: 'object', name: '物体识别', types: ['tensorflow', 'opencv'] }
        ];
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[ImageRecognitionConfig] 初始化图片识别配置');
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        document.addEventListener('recognition:config', (e) => this.configure(e.detail));
        document.addEventListener('recognition:select-model', (e) => this.selectModel(e.detail.model));
        document.addEventListener('recognition:select-type', (e) => this.selectType(e.detail.type));
        document.addEventListener('recognition:update-params', (e) => this.updateParams(e.detail.params));
    }
    
    /**
     * 加载配置
     */
    async loadConfig() {
        try {
            const response = await apiInterface.get('/api/recognition/config');
            if (response.status === 'success' && response.config) {
                this.config = { ...this.config, ...response.config };
                console.log('[ImageRecognitionConfig] 配置已加载:', this.config);
            }
        } catch (error) {
            console.error('[ImageRecognitionConfig] 加载配置失败:', error);
        }
    }
    
    /**
     * 保存配置
     */
    async saveConfig() {
        try {
            const response = await apiInterface.post('/api/recognition/config', this.config);
            if (response.status === 'success') {
                console.log('[ImageRecognitionConfig] 配置已保存');
                notifications.showSuccess('配置已保存');
            }
        } catch (error) {
            console.error('[ImageRecognitionConfig] 保存配置失败:', error);
        }
    }
    
    /**
     * 选择识别模型
     * @param {string} model - 模型ID ('face' | 'object')
     */
    async selectModel(model) {
        const modelInfo = this.availableModels.find(m => m.id === model);
        if (!modelInfo) {
            throw new Error('未知的模型类型');
        }
        
        this.config.model = model;
        
        // 如果当前类型不在新模型的可用类型中，重置为第一个
        if (!modelInfo.types.includes(this.config.modelType)) {
            this.config.modelType = modelInfo.types[0];
        }
        
        // 发送模型变更事件
        document.dispatchEvent(new CustomEvent('recognition:model-selected', {
            detail: { model: model, modelInfo: modelInfo }
        }));
        
        // 加载模型后重新保存配置
        await this.saveConfig();
        
        console.log(`[ImageRecognitionConfig] 已选择模型: ${modelInfo.name}`);
        return { success: true, model: model, modelInfo: modelInfo };
    }
    
    /**
     * 选择模型类型
     * @param {string} type - 类型 ('mediapipe' | 'opencv' | etc.)
     */
    async selectType(type) {
        const availableTypes = this.availableModels
            .find(m => m.id === this.config.model)?.types || [];
        
        if (!availableTypes.includes(type)) {
            throw new Error(`模型类型 ${type} 不可用`);
        }
        
        this.config.modelType = type;
        
        // 发送类型变更事件
        document.dispatchEvent(new CustomEvent('recognition:type-selected', {
            detail: { type: type }
        }));
        
        await this.saveConfig();
        
        console.log(`[ImageRecognitionConfig] 已选择类型: ${type}`);
        return { success: true, type: type };
    }
    
    /**
     * 更新识别参数
     * @param {Object} params - 参数对象
     */
    async updateParams(params) {
        const validParams = ['sensitivity', 'detectionArea', 'enableTracking', 'enableLandmarks'];
        
        validParams.forEach(key => {
            if (params[key] !== undefined) {
                this.config[key] = params[key];
            }
        });
        
        // 如果是手动区域，验证格式
        if (params.manualRegion) {
            const { x, y, width, height } = params.manualRegion;
            if (typeof x !== 'number' || typeof y !== 'number' ||
                typeof width !== 'number' || typeof height !== 'number') {
                throw new Error('手动区域参数格式错误');
            }
            this.config.manualRegion = params.manualRegion;
        }
        
        // 发送参数更新事件
        document.dispatchEvent(new CustomEvent('recognition:params-updated', {
            detail: { params: this.config }
        }));
        
        await this.saveConfig();
        
        console.log('[ImageRecognitionConfig] 参数已更新:', this.config);
        return { success: true, config: this.config };
    }
    
    /**
     * 配置识别
     * @param {Object} options - 配置选项
     */
    async configure(options = {}) {
        try {
            if (options.model) {
                await this.selectModel(options.model);
            }
            if (options.modelType) {
                await this.selectType(options.modelType);
            }
            if (options.params) {
                await this.updateParams(options.params);
            }
            
            // 发送配置完成事件
            document.dispatchEvent(new CustomEvent('recognition:configured', {
                detail: { config: this.config }
            }));
            
            return { success: true, config: this.config };
        } catch (error) {
            console.error('[ImageRecognitionConfig] 配置失败:', error);
            notifications.showError(`配置失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 获取当前配置
     */
    getConfig() {
        return { ...this.config };
    }
    
    /**
     * 获取可用模型列表
     */
    getAvailableModels() {
        return this.availableModels;
    }
    
    /**
     * 创建配置UI
     * @param {string} containerId - 容器ID
     */
    createConfigUI(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[ImageRecognitionConfig] 未找到容器元素: ${containerId}`);
            return;
        }
        
        container.innerHTML = `
            <div class="recognition-config">
                <h4>图片识别配置</h4>
                
                <div class="form-group">
                    <label>识别模型</label>
                    <select id="recognition-model" class="form-control">
                        ${this.availableModels.map(m => 
                            `<option value="${m.id}" ${this.config.model === m.id ? 'selected' : ''}>${m.name}</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>模型类型</label>
                    <select id="recognition-type" class="form-control">
                        ${this.getCurrentTypes().map(t => 
                            `<option value="${t}" ${this.config.modelType === t ? 'selected' : ''}>${t}</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>识别灵敏度: <span id="sensitivity-value">${this.config.sensitivity}</span></label>
                    <input type="range" id="recognition-sensitivity" 
                           min="0.1" max="1.0" step="0.1" 
                           value="${this.config.sensitivity}" class="form-control">
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="recognition-tracking" 
                               ${this.config.enableTracking ? 'checked' : ''}>
                        启用实时追踪
                    </label>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="recognition-landmarks" 
                               ${this.config.enableLandmarks ? 'checked' : ''}>
                        显示关键点
                    </label>
                </div>
                
                <div class="form-actions">
                    <button id="recognition-apply" class="btn btn-primary">应用配置</button>
                    <button id="recognition-reset" class="btn btn-secondary">重置</button>
                </div>
            </div>
        `;
        
        // 绑定事件
        this.bindConfigUIEvents(container);
    }
    
    /**
     * 获取当前模型的可用类型
     */
    getCurrentTypes() {
        const model = this.availableModels.find(m => m.id === this.config.model);
        return model ? model.types : [];
    }
    
    /**
     * 绑定配置UI事件
     */
    bindConfigUIEvents(container) {
        // 模型变更
        container.querySelector('#recognition-model').addEventListener('change', async (e) => {
            await this.selectModel(e.target.value);
            
            // 更新类型下拉框
            const typeSelect = container.querySelector('#recognition-type');
            typeSelect.innerHTML = this.getCurrentTypes().map(t => 
                `<option value="${t}">${t}</option>`
            ).join('');
        });
        
        // 灵敏度滑块
        container.querySelector('#recognition-sensitivity').addEventListener('input', (e) => {
            container.querySelector('#sensitivity-value').textContent = e.target.value;
        });
        
        // 应用按钮
        container.querySelector('#recognition-apply').addEventListener('click', async () => {
            const params = {
                sensitivity: parseFloat(container.querySelector('#recognition-sensitivity').value),
                enableTracking: container.querySelector('#recognition-tracking').checked,
                enableLandmarks: container.querySelector('#recognition-landmarks').checked
            };
            
            await this.updateParams(params);
            notifications.showSuccess('配置已应用');
        });
        
        // 重置按钮
        container.querySelector('#recognition-reset').addEventListener('click', async () => {
            this.config = {
                model: 'face',
                modelType: 'mediapipe',
                sensitivity: 0.8,
                detectionArea: 'auto',
                enableTracking: true,
                enableLandmarks: false
            };
            
            // 重新渲染UI
            this.createConfigUI(container.id);
            
            // 同步到后端
            await this.saveConfig();
        });
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        document.removeEventListener('recognition:config');
        document.removeEventListener('recognition:select-model');
        document.removeEventListener('recognition:select-type');
        document.removeEventListener('recognition:update-params');
    }
}

// 创建全局实例
window.imageRecognitionConfig = new ImageRecognitionConfig();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageRecognitionConfig;
}

