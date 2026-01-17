# AISP 项目全面修复计划

## 修复概述

基于对AISP项目的全面分析，制定本修复计划，解决项目中的结构问题、配置冲突和功能重复等问题。

---

## 一、问题诊断

### 1.1 配置层级分析 ✅

| 层级 | 文件 | 状态 |
|------|------|------|
| L1 (最高) | AI_RULES.json | ✅ 正确 |
| L1 (最高) | AI_PATH_CONTEXT.json | ✅ 正确 |
| L1 (最高) | AI_CLEANUP_POLICY.json | ✅ 正确 |
| L2 | project_config.json | ⚠️ 需要验证 |
| L2 | ai_config.json | ⚠️ 需要验证 |
| L2 | engines_config.json | ⚠️ 需要验证 |
| L2 | output_config.json | ⚠️ 需要验证 |
| L3 | run_config.json | ⚠️ 需要验证 |
| L3 | health_check_config.json | ⚠️ 需要验证 |
| L4 | config/ai/*.json | ✅ 正确 |
| L4 | config/tasks/*.json | ✅ 正确 |

### 1.2 发现的问题

#### 问题1: 废弃文件未清理
- **文件**: `backend/api.py`
- **问题**: 已标记为DEPRECATED但仍存在
- **影响**: 可能导致导入混乱

#### 问题2: 任务队列重复
- **位置1**: `AISP/task_queue.json`
- **位置2**: `AISP/config/tasks/task_queue.json`
- **影响**: 任务状态可能不同步

#### 问题3: 项目名称混用
- 混用: "AISP" 和 "夜灵AR多功能合成软件"
- 需要统一使用 "AISP" 作为主要标识

#### 问题4: 状态枚举不一致
- **代码中**: INIT, CHECK_ENV, IDLE, RUNNING, DEGRADED, SHUTDOWN
- **文档中**: INIT, WAITING, STARTING, IDLE, PROCESSING, PAUSED, COMPLETED, ERROR, RETRY
- **影响**: 文档与代码不同步

#### 问题5: 路径引用需要统一
- 部分脚本使用硬编码路径
- 需要全部改为动态获取

---

## 二、修复计划

### 阶段1: 配置验证与修复

#### 任务 2.1: 验证L2配置层级
**优先级**: HIGH | **状态**: PENDING

检查以下文件是否存在且有效:
- [ ] config/project_config.json
- [ ] config/ai_config.json
- config/engines_config.json
- [ ] config/output_config.json

#### 任务 2.2: 验证L3配置层级
**优先级**: HIGH | **状态**: PENDING

检查以下文件是否存在且有效:
- [ ] config/run_config.json
- [ ] config/health_check_config.json

#### 任务 2.3: 验证L4配置层级
**优先级**: MEDIUM | **状态**: PENDING

检查以下文件是否存在且有效:
- [ ] config/ai/model_config.json
- [ ] config/ai/capability_map.json
- [ ] config/tasks/task_queue.json
- [ ] config/tasks/task_schema.json
- [ ] config/tasks/completed_tasks.json

### 阶段2: 文件清理

#### 任务 2.4: 清理废弃API文件
**优先级**: HIGH | **状态**: PENDING

- [ ] 验证 backend/api.py 是否可以删除
- [ ] 更新启动脚本使用 unified_api.py
- [ ] 更新文档说明

#### 任务 2.5: 统一任务队列位置
**优先级**: HIGH | **状态**: PENDING

- [ ] 确定任务队列的规范位置 (config/tasks/)
- [ ] 迁移或删除根目录的 task_queue.json
- [ ] 更新所有引用

### 阶段3: 文档同步

#### 任务 2.6: 更新状态枚举文档
**优先级**: MEDIUM | **状态**: PENDING

- [ ] 更新 docs/整体项目逻辑.md 中的状态图
- [ ] 确保与 state_manager.py 一致
- [ ] 添加状态转换说明

#### 任务 2.7: 统一项目名称
**优先级**: MEDIUM | **状态**: PENDING

- [ ] 确定主要项目名称 (AISP)
- [ ] 更新所有文档中的项目名称
- [ ] 清理中文环境变量引用

### 阶段4: 路径统一

#### 任务 2.8: 统一路径获取
**优先级**: MEDIUM | **状态**: PENDING

- [ ] 检查所有脚本使用统一路径配置
- [ ] 更新 scripts/path_config.py
- [ ] 移除硬编码路径

---

## 三、执行顺序

```
阶段1: 配置验证 (阻塞后续任务)
    │
    ▼
阶段2: 文件清理 (基于验证结果)
    │
    ▼
阶段3: 文档同步 (与文件清理并行)
    │
    ▼
阶段4: 路径统一 (最后执行)
```

---

## 四、验证检查清单

### 配置验证
- [ ] L1配置文件语法正确
- [ ] L2配置文件语法正确
- [ ] L3配置文件语法正确
- [ ] L4配置文件语法正确
- [ ] 配置优先级继承关系正确

### 模块验证
- [ ] backend/api.py 已废弃
- [ ] backend/unified_api.py 可用
- [ ] backend/control_core/*.py 语法正确
- [ ] backend/services/*.py 语法正确

### 任务验证
- [ ] 任务队列位置统一
- [ ] 任务状态流转正确
- [ ] 任务Schema定义完整

### 文档验证
- [ ] 状态枚举与代码一致
- [ ] 项目名称统一
- [ ] API文档与实现一致

---

## 五、回滚计划

如果修复过程中出现问题:
1. 使用Git版本控制回滚
2. 备份原始文件到 deprecated/ 目录
3. 记录所有修改操作

---

## 六、进度追踪

| 阶段 | 任务数 | 已完成 | 进行中 | 待开始 |
|------|--------|--------|--------|--------|
| 阶段1: 配置验证 | 3 | 0 | 0 | 3 |
| 阶段2: 文件清理 | 2 | 0 | 0 | 2 |
| 阶段3: 文档同步 | 2 | 0 | 0 | 2 |
| 阶段4: 路径统一 | 1 | 0 | 0 | 1 |
| **总计** | **8** | **0** | **0** | **8** |

---

## 七、风险评估

| 风险 | 级别 | 应对措施 |
|------|------|----------|
| 删除必要文件 | 高 | 先备份后删除 |
| 配置语法错误 | 中 | 验证后应用 |
| 文档不同步 | 低 | 同步更新 |

---

最后更新: 2025-01-21

