# 配置文档目录

本目录包含项目的配置相关文档。

## 目录结构

| 文件 | 说明 |
|------|------|
| [AI3_RULES.md](./AI3_RULES.md) | AI3规则配置 |
| [CONFIG_LOCAL.md](./CONFIG_LOCAL.md) | 本地配置说明 |
| [config.json](./config.json) | 文档配置 |

## 配置类型

### 核心配置

- [AI_TASK_AUTOMATION_CONFIG.md](../plan/AI_TASK_AUTOMATION_CONFIG.md) - AI任务自动化配置
- [AI3_RULES.md](./AI3_RULES.md) - AI3规则

### 配置方案

- [CONFIG_REARCHITECTURE_PLAN.md](../plan/CONFIG_REARCHITECTURE_PLAN.md) - 配置重构方案
- [CONFIG_OPTIMIZATION_REPAIR_PLAN.md](../plan/CONFIG_OPTIMIZATION_REPAIR_PLAN.md) - 配置优化方案

## 配置层级

### L1 根规则层
- AI_RULES.json
- AI_PATH_CONTEXT.json
- AI_CLEANUP_POLICY.json

### L2 项目主配置层
- project_config.json
- engines_config.json
- output_config.json
- ai_config.json

### L3 运行配置层
- run_config.json
- health_check_config.json
- AI3.json

### L4 功能子配置层
- ai/model_config.json
- ai/capability_map.json
- tasks/task_queue.json
- tasks/task_schema.json

## 相关目录

- [../guide/配置说明.md](../guide/配置说明.md) - 配置使用说明
- [data/rules/](../data/rules/) - 规则配置目录

