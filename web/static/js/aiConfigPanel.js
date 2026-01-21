/**
 * AI配置面板模块
 * AI Config Panel Module
 * 
 * 功能：
 * - 开启/关闭AI模型
 * - 配置AI训练选项
 * - 管理模型下载和安装
 * 
 * 依赖：
 * - apiInterface.js - API调用封装
 * - notifications.js - 通知系统
 */

class AIConfigPanel {
    constructor() {
        // AI配置状态
        this.config = {
            modelEnabled: false,
            modelType: 'ollama',        // 'ollama' | 'local' | 'api'
            modelName: 'llama3.2:3b',
            trainingEnabled: false,
            trainingConfig: {
                epochs: 10,
                batchSize: 32,
                learningRate: 0.001,
                datasetPath: null
            },
            installedModels: [],
            availableModels: [
                { id: 'llama3.2:3b', name: 'Llama 3.2 3B', size: '~2GB', type: 'text' },
                { id: 'llama3.2:1b', name: 'Llama 3.2 1B', size: '~1GB', type: 'text' },
                { id: 'qwen2.5:3b', name: 'Qwen 2.5 3B', size: '~2GB', type: 'text' },
                { id: 'mistral:7b', name: 'Mistral 7B', size: '~4GB', type: 'text' }
            ]
        };
        
        // 初始化
        this.init();
    }
    
    init() {
        console.log('[AIConfigPanel] 初始化AI配置面板');
        this.loadConfig();
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        document.addEventListener('ai:toggle-model', (e) => this.toggleModel(e.detail.enabled));
        document.addEventListener('ai:toggle-training', (e) => this.toggleTraining(e.detail.enabled));
        document.addEventListener('ai:select-model', (e) => this.selectModel(e.detail.modelId));
        document.addEventListener('ai:install-model', (e) => this.installModel(e.detail.modelId));
        document.addEventListener('ai:configure-training', (e) => this.configureTraining(e.detail.config));
    }
    
    /**
     * 加载配置
     */
    async loadConfig() {
        try {
            const response = await apiInterface.get('/api/ai/config');
            if (response.status === 'success' && response.config) {
                this.config = { ...this.config, ...response.config };
                console.log('[AIConfigPanel] AI配置已加载:', this.config);
            }
        } catch (error) {
            console.error('[AIConfigPanel] 加载配置失败:', error);
        }
    }
    
    /**
     * 保存配置
     */
    async saveConfig() {
        try {
            await apiInterface.post('/api/ai/config', this.config);
            console.log('[AIConfigPanel] AI配置已保存');
        } catch (error) {
            console.error('[AIConfigPanel] 保存配置失败:', error);
        }
    }
    
    /**
     * 开启/关闭AI模型
     * @param {boolean} enabled - 是否开启
     */
    async toggleModel(enabled) {
        try {
            const response = await apiInterface.post('/api/ai/toggle', {
                enabled: enabled,
                modelType: this.config.modelType,
                modelName: this.config.modelName
            });
            
            if (response.status === 'success') {
                this.config.modelEnabled = enabled;
                
                document.dispatchEvent(new CustomEvent('ai:model-toggled', {
                    detail: { enabled: enabled }
                }));
                
                notifications.showSuccess(enabled ? 'AI模型已启动' : 'AI模型已关闭');
                return { success: true };
            } else {
                throw new Error(response.message || '操作失败');
            }
        } catch (error) {
            console.error('[AIConfigPanel] 切换模型状态失败:', error);
            notifications.showError(`操作失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 选择AI模型
     * @param {string} modelId - 模型ID
     */
    async selectModel(modelId) {
        const model = this.config.availableModels.find(m => m.id === modelId);
        if (!model) {
            throw new Error('未找到指定模型');
        }
        
        this.config.modelName = modelId;
        
        document.dispatchEvent(new CustomEvent('ai:model-selected', {
            detail: { modelId: modelId, model: model }
        }));
        
        await this.saveConfig();
        
        console.log(`[AIConfigPanel] 已选择模型: ${model.name}`);
        return { success: true, model: model };
    }
    
    /**
     * 安装模型
     * @param {string} modelId - 模型ID
     */
    async installModel(modelId) {
        const model = this.config.availableModels.find(m => m.id === modelId);
        if (!model) {
            throw new Error('未找到指定模型');
        }
        
        try {
            notifications.showInfo(`正在下载模型 ${model.name}...`);
            
            const response = await apiInterface.post('/api/ai/install-model', {
                modelId: modelId,
                modelName: model.name
            });
            
            if (response.status === 'success') {
                this.config.installedModels.push(modelId);
                
                document.dispatchEvent(new CustomEvent('ai:model-installed', {
                    detail: { modelId: modelId, model: model }
                }));
                
                notifications.showSuccess(`模型 ${model.name} 安装完成`);
                return { success: true };
            } else {
                throw new Error(response.message || '安装失败');
            }
        } catch (error) {
            console.error('[AIConfigPanel] 安装模型失败:', error);
            notifications.showError(`安装失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 开启/关闭AI训练
     * @param {boolean} enabled - 是否开启
     */
    async toggleTraining(enabled) {
        if (enabled && !this.config.modelEnabled) {
            notifications.showWarning('请先开启AI模型');
            return { success: false, error: '模型未开启' };
        }
        
        this.config.trainingEnabled = enabled;
        
        document.dispatchEvent(new CustomEvent('ai:training-toggled', {
            detail: { enabled: enabled }
        }));
        
        await this.saveConfig();
        
        notifications.showSuccess(enabled ? 'AI训练已开启' : 'AI训练已关闭');
        return { success: true };
    }
    
    /**
     * 配置训练参数
     * @param {Object} config - 训练配置
     */
    async configureTraining(config) {
        const validKeys = ['epochs', 'batchSize', 'learningRate', 'datasetPath'];
        
        validKeys.forEach(key => {
            if (config[key] !== undefined) {
                this.config.trainingConfig[key] = config[key];
            }
        });
        
        document.dispatchEvent(new CustomEvent('ai:training-configured', {
            detail: { config: this.config.trainingConfig }
        }));
        
        await this.saveConfig();
        
        console.log('[AIConfigPanel] 训练配置已更新:', this.config.trainingConfig);
        return { success: true, config: this.config.trainingConfig };
    }
    
    /**
     * 开始训练
     * @param {Object} options - 训练选项
     */
    async startTraining(options = {}) {
        const {
            modelId = this.config.modelName,
            config = this.config.trainingConfig
        } = options;
        
        if (!this.config.modelEnabled) {
            notifications.showError('请先开启AI模型');
            return { success: false, error: '模型未开启' };
        }
        
        try {
            const response = await apiInterface.post('/api/ai/training/start', {
                modelId: modelId,
                config: config
            });
            
            if (response.status === 'success') {
                this.config.trainingEnabled = true;
                
                document.dispatchEvent(new CustomEvent('ai:training-started', {
                    detail: { taskId: response.taskId }
                }));
                
                notifications.showSuccess('AI训练已开始');
                return { success: true, taskId: response.taskId };
            } else {
                throw new Error(response.message || '启动训练失败');
            }
        } catch (error) {
            console.error('[AIConfigPanel] 启动训练失败:', error);
            notifications.showError(`启动训练失败: ${error.message}`);
            return { success: false, error: error };
        }
    }
    
    /**
     * 获取训练进度
     * @param {string} taskId - 任务ID
     */
    async getTrainingProgress(taskId) {
        try {
            const response = await apiInterface.get(`/api/ai/training/progress?taskId=${taskId}`);
            return response;
        } catch (error) {
            console.error('[AIConfigPanel] 获取训练进度失败:', error);
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
        return this.config.availableModels;
    }
    
    /**
     * 创建配置UI
     * @param {string} containerId - 容器ID
     */
    createConfigUI(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[AIConfigPanel] 未找到容器元素: ${containerId}`);
            return;
        }
        
        container.innerHTML = `
            <div class="ai-config-panel">
                <h4>AI 配置与训练</h4>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="ai-model-toggle" 
                               ${this.config.modelEnabled ? 'checked' : ''}>
                        启用 AI 模型
                    </label>
                </div>
                
                <div class="form-group">
                    <label>选择模型</label>
                    <select id="ai-model-select" class="form-control" ${!this.config.modelEnabled ? 'disabled' : ''}>
                        ${this.config.availableModels.map(m => `
                            <option value="${m.id}" ${this.config.modelName === m.id ? 'selected' : ''}>
                                ${m.name} (${m.size})
                            </option>
                        `).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <button id="ai-install-model" class="btn btn-secondary" ${!this.config.modelEnabled ? 'disabled' : ''}>
                        安装模型
                    </button>
                </div>
                
                <hr>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="ai-training-toggle" 
                               ${this.config.trainingEnabled ? 'checked' : ''}>
                        启用 AI 训练
                    </label>
                </div>
                
                <div class="training-config" style="display: ${this.config.trainingEnabled ? 'block' : 'none'};">
                    <div class="form-group">
                        <label>训练轮数 (Epochs)</label>
                        <input type="number" id="ai-epochs" 
                               value="${this.config.trainingConfig.epochs}" 
                               min="1" max="100" class="form-control">
                    </div>
                    
                    <div class="form-group">
                        <label>批次大小 (Batch Size)</label>
                        <input type="number" id="ai-batch-size" 
                               value="${this.config.trainingConfig.batchSize}" 
                               min="1" max="256" class="form-control">
                    </div>
                    
                    <div class="form-group">
                        <label>学习率</label>
                        <input type="number" id="ai-learning-rate" 
                               value="${this.config.trainingConfig.learningRate}" 
                               min="0.0001" max="0.1" step="0.0001" class="form-control">
                    </div>
                </div>
                
                <div class="form-actions">
                    <button id="ai-start-training" class="btn btn-primary" ${!this.config.trainingEnabled ? 'disabled' : ''}>
                        开始训练
                    </button>
                    <button id="ai-save-config" class="btn btn-secondary">
                        保存配置
                    </button>
                </div>
                
                <div class="training-progress" style="display: none;">
                    <label>训练进度</label>
                    <div class="progress">
                        <div id="training-progress-bar" class="progress-bar" role="progressbar" style="width: 0%">0%</div>
                    </div>
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
        // 模型开关
        container.querySelector('#ai-model-toggle').addEventListener('change', async (e) => {
            await this.toggleModel(e.target.checked);
            
            // 更新相关控件状态
            const modelSelect = container.querySelector('#ai-model-select');
            const installBtn = container.querySelector('#ai-install-model');
            modelSelect.disabled = !e.target.checked;
            installBtn.disabled = !e.target.checked;
        });
        
        // 选择模型
        container.querySelector('#ai-model-select').addEventListener('change', async (e) => {
            await this.selectModel(e.target.value);
        });
        
        // 安装模型
        container.querySelector('#ai-install-model').addEventListener('click', async () => {
            const modelId = container.querySelector('#ai-model-select').value;
            await this.installModel(modelId);
        });
        
        // 训练开关
        container.querySelector('#ai-training-toggle').addEventListener('change', async (e) => {
            await this.toggleTraining(e.target.checked);
            
            const trainingConfig = container.querySelector('.training-config');
            const startBtn = container.querySelector('#ai-start-training');
            trainingConfig.style.display = e.target.checked ? 'block' : 'none';
            startBtn.disabled = !e.target.checked;
        });
        
        // 开始训练
        container.querySelector('#ai-start-training').addEventListener('click', async () => {
            const config = {
                epochs: parseInt(container.querySelector('#ai-epochs').value),
                batchSize: parseInt(container.querySelector('#ai-batch-size').value),
                learningRate: parseFloat(container.querySelector('#ai-learning-rate').value)
            };
            
            await this.configureTraining(config);
            await this.startTraining({ config: config });
        });
        
        // 保存配置
        container.querySelector('#ai-save-config').addEventListener('click', async () => {
            await this.saveConfig();
            notifications.showSuccess('配置已保存');
        });
    }
    
    /**
     * 销毁实例
     */
    destroy() {
        document.removeEventListener('ai:toggle-model');
        document.removeEventListener('ai:toggle-training');
        document.removeEventListener('ai:select-model');
        document.removeEventListener('ai:install-model');
        document.removeEventListener('ai:configure-training');
    }
}

// 创建全局实例
window.aiConfigPanel = new AIConfigPanel();

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIConfigPanel;
}

