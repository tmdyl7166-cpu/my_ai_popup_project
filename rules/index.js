/**
 * AI弹窗项目 - 规则配置系统入口
 * 
 * 本系统采用五层逻辑规则配置：
 * L1: 元目标层 - 项目最高目标和约束
 * L2: 全局理解层 - 架构和模块关系
 * L3: 约束层 - 技术约束和依赖
 * L4: 决策层 - 关键设计决策
 * L5: 执行层 - 具体执行规则
 */

const fs = require('fs');
const path = require('path');

class RulesEngine {
    constructor() {
        this.configPath = path.join(__dirname, 'rules.config.js');
        this.layers = {};
        this.loadAllLayers();
    }

    /**
     * 加载所有规则层配置
     */
    loadAllLayers() {
        const layerFiles = [
            'L1-meta-goal.json',
            'L2-understanding.json',
            'L3-constraints.json',
            'L4-decisions.json',
            'L5-execution.json'
        ];

        layerFiles.forEach(file => {
            const filePath = path.join(__dirname, file);
            if (fs.existsSync(filePath)) {
                const layerName = file.replace('.json', '').toLowerCase();
                this.layers[layerName] = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            }
        });
    }

    /**
     * 获取指定层的配置
     * @param {string} layerName - 层名称 (如 'L1', 'meta-goal')
     */
    getLayer(layerName) {
        const normalizedName = layerName.toLowerCase().replace('l', '');
        return this.layers[`l${normalizedName}`] || null;
    }

    /**
     * 获取所有配置
     */
    getAllLayers() {
        return this.layers;
    }

    /**
     * 验证配置一致性
     * @returns {Object} 验证结果
     */
    validate() {
        const results = {
            valid: true,
            errors: [],
            warnings: []
        };

        // 检查L1必需字段
        const l1 = this.layers['l1'];
        if (!l1?.project?.name) {
            results.errors.push("L1层缺少项目名称");
            results.valid = false;
        }
        if (!l1?.goals?.primary) {
            results.errors.push("L1层缺少主要目标");
            results.valid = false;
        }

        // 检查L2模块定义
        const l2 = this.layers['l2'];
        if (!l2?.modules) {
            results.warnings.push("L2层未定义模块");
        }

        // 检查L3依赖
        const l3 = this.layers['l3'];
        if (!l3?.python?.version) {
            results.warnings.push("L3层未指定Python版本");
        }

        return results;
    }

    /**
     * 根据任务类型获取执行参数
     * @param {string} taskType - 任务类型
     */
    getExecutionParams(taskType) {
        const l5 = this.layers['l5'];
        if (!l5?.task_workflows) {
            return null;
        }
        return l5.task_workflows[taskType] || null;
    }

    /**
     * 获取性能指标
     */
    getPerformanceMetrics() {
        const l1 = this.layers['l1'];
        return l1?.constraints?.performance || null;
    }

    /**
     * 获取技术约束
     */
    getTechnicalConstraints() {
        const l3 = this.layers['l3'];
        return l3 || null;
    }

    /**
     * 获取模块关系
     */
    getModuleRelationships() {
        const l2 = this.layers['l2'];
        return l2?.relationships || null;
    }
}

// 导出规则引擎实例
const rulesEngine = new RulesEngine();

// 验证配置
const validation = rulesEngine.validate();
if (!validation.valid) {
    console.error('规则配置验证失败:', validation.errors);
    process.exit(1);
}

module.exports = {
    RulesEngine,
    rulesEngine,
    // 便捷方法
    getLayer: (name) => rulesEngine.getLayer(name),
    getAllLayers: () => rulesEngine.getAllLayers(),
    validate: () => rulesEngine.validate(),
    getExecutionParams: (type) => rulesEngine.getExecutionParams(type),
    getPerformanceMetrics: () => rulesEngine.getPerformanceMetrics(),
    getTechnicalConstraints: () => rulesEngine.getTechnicalConstraints(),
    getModuleRelationships: () => rulesEngine.getModuleRelationships()
};

