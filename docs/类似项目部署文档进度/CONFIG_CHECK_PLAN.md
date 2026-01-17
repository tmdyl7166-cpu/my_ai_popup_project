# AISP配置识别与同步检查计划

## 1. 项目概述

### 1.1 任务目标
检查AISP项目中所有子项目的配置内容是否能被主配置识别，并且所有配置内容是否会根据修改进行同步。

### 1.2 项目结构分析

根据 `directory_structure.json`，AISP项目包含以下子项目：
- **gui** - 用户界面层
- **backend** - 后端服务层
- **engines** - 引擎基类
- **virtual_cam** - 虚拟摄像头
- **obs_integration** - OBS集成
- **web** - Web监控层
- **containers** - Docker容器配置
- **scripts** - 自动化脚本
- **ollama-models** - Ollama模型目录

---

## 2. 配置层级分析

### 2.1 主配置层 (data/rules/)

| 层级 | 文件 | 描述 | 优先级 |
|------|------|------|--------|
| L0 | root_rules.json | 根规则配置 - 命名、结构、安全约束 | 0 |
| L1 | project_config.json | 项目配置 - 模块定义、路径、数据流 | 1 |
| L2 | runtime_config.json | 运行配置 - 服务器、资源、性能 | 2 |
| L3 | feature_config.json | 功能配置 - GUI、AR、AI、管道等 | 3 |
| L4 | execution_config.json | 执行配置 - 执行流程、冲突解决 | 4 |
| L5 | feature_index.json | 功能索引 - 配置关系和引用 | 5 |

### 2.2 AI辅助配置 (config/)

| 文件 | 描述 | 来源 |
|------|------|------|
| AI_RULES.json | AI行为规则配置 | .vscode/config/AI_RULES.json |
| AI_PATH_CONTEXT.json | AI路径上下文和目录映射 | .vscode/config/AI_PATH_CONTEXT.json |
| AI_CLEANUP_POLICY.json | AI清理策略配置 | .vscode/config/AI_CLEANUP_POLICY.json |

### 2.3 核心配置

| 文件 | 描述 |
|------|------|
| directory_structure.json | 目录结构配置 |
| logic_layers_deployment.json | 五层逻辑部署配置 |
| ai_task_config.json | AI任务自动化配置 |

---

## 3. 配置识别检查清单

### 3.1 主配置识别子项目配置

| 子项目 | config.json位置 | 是否被主配置引用 | 引用文件 |
|--------|-----------------|------------------|----------|
| gui | gui/config.json | ✓ | directory_structure.json#directory_mapping.gui |
| backend | backend/config.json | ✓ | directory_structure.json#directory_mapping.backend |
| engines | engines/config.json | ✓ | directory_structure.json#directory_mapping.engines |
| virtual_cam | virtual_cam/config.json | ✓ | directory_structure.json#directory_mapping.virtual_cam |
| obs_integration | obs_integration/config.json | ✓ | directory_structure.json#directory_mapping.obs_integration |
| web | web/config.json | ✓ | directory_structure.json#directory_mapping.web |
| containers | containers/config.json | ✓ | directory_structure.json#directory_mapping.containers |
| scripts | scripts/config.json | ✓ | directory_structure.json#directory_mapping.scripts |
| ollama-models | ollama-models/config.json | ✓ | directory_structure.json#directory_mapping.ollama-models |

### 3.2 配置同步机制检查

根据 `ai_task_config.json#sync_configuration`:

```json
{
  "sync_configuration": {
    "enabled": true,
    "sync_on_change": true,
    "sync_targets": {
      "documentation": {
        "paths": ["docs/"],
        "auto_update": true,
        "backup_before_sync": true
      },
      "scripts": {
        "paths": ["scripts/"],
        "auto_update": true,
        "backup_before_sync": true
      },
      "configuration": {
        "paths": ["data/rules/", "*.json"],
        "auto_update": true,
        "backup_before_sync": true
      }
    }
  }
}
```

---

## 4. 检查步骤

### 步骤1: 配置引用验证

1. 验证 `directory_structure.json` 中引用的所有 `config_ref` 是否存在
2. 验证 `feature_index.json` 中的 `feature_modules` 配置是否完整
3. 验证 `logic_layers_deployment.json` 中的 `rules_alignment` 映射是否正确

### 步骤2: 配置层级关系验证

1. 验证 `config_hierarchy` 的父子关系是否正确
2. 验证 `config_load_order` 是否符合层级要求
3. 验证 `cross_config_references` 的引用是否有效

### 步骤3: 同步机制验证

1. 验证 `sync_configuration` 是否启用
2. 验证同步目标路径是否正确
3. 验证同步触发条件是否配置

### 步骤4: 子项目配置一致性验证

1. 检查子项目 `config.json` 是否符合主配置命名规范
2. 检查子项目配置是否与 `feature_config.json` 对齐
3. 检查子项目依赖关系是否符合 `project_config.json`

---

## 5. 检查项详细清单

### 5.1 识别检查项

- [ ] 1.1 `gui/config.json` 被 `directory_structure.json` 识别
- [ ] 1.2 `backend/config.json` 被 `directory_structure.json` 识别
- [ ] 1.3 `engines/config.json` 被 `directory_structure.json` 识别
- [ ] 1.4 `virtual_cam/config.json` 被 `directory_structure.json` 识别
- [ ] 1.5 `obs_integration/config.json` 被 `directory_structure.json` 识别
- [ ] 1.6 `web/config.json` 被 `directory_structure.json` 识别
- [ ] 1.7 `containers/config.json` 被 `directory_structure.json` 识别
- [ ] 1.8 `scripts/config.json` 被 `directory_structure.json` 识别
- [ ] 1.9 `ollama-models/config.json` 被 `directory_structure.json` 识别

### 5.2 同步检查项

- [ ] 2.1 `ai_task_config.json` 中的 `sync_configuration` 已启用
- [ ] 2.2 同步目标 `docs/` 配置正确
- [ ] 2.3 同步目标 `scripts/` 配置正确
- [ ] 2.4 同步目标 `data/rules/` 配置正确
- [ ] 2.5 同步验证 `sync_validation` 已启用
- [ ] 2.6 回滚机制 `rollback_on_failure` 已启用

### 5.3 一致性检查项

- [ ] 3.1 `logic_layers_deployment.json` 与 `root_rules.json` 一致
- [ ] 3.2 `logic_layers_deployment.json` 与 `project_config.json` 一致
- [ ] 3.3 `logic_layers_deployment.json` 与 `feature_config.json` 一致
- [ ] 3.4 `directory_structure.json` 与 `feature_index.json` 一致
- [ ] 3.5 `ai_task_config.json` 与 `logic_layers_deployment.json` 一致

---

## 6. 预期输出

执行检查后，将生成以下输出：

1. **配置识别报告** - 列出所有被识别和未被识别的配置
2. **同步机制报告** - 列出同步机制的启用状态和配置
3. **一致性报告** - 列出配置间的一致性问题
4. **修复建议** - 针对发现的问题提供修复方案

---

## 7. 后续步骤

1. 执行检查脚本验证所有配置项
2. 生成详细检查报告
3. 修复识别或同步问题
4. 验证修复后的配置一致性
5. 更新相关文档

