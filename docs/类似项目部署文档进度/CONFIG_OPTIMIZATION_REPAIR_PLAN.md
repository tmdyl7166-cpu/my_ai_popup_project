# AISP JSON配置优化修复计划

## 一、信息汇总

### 1.1 已分析的配置文件清单

| 序号 | 文件路径 | 优先级 | 状态 |
|------|----------|--------|------|
| 1 | `.vscode/AI_RULES.json` | L1 (最高) | 已分析 |
| 2 | `.vscode/AI_PATH_CONTEXT.json` | L1 (最高) | 已分析 |
| 3 | `.vscode/AI_CLEANUP_POLICY.json` | L1 (最高) | 已分析 |
| 4 | `.vscode/config/AI3.json` | L3 | 已分析 |
| 5 | `.vscode/config/project_config.json` | L2 | 已分析 |
| 6 | `.vscode/config/engines_config.json` | L2 | 已分析 |
| 7 | `.vscode/config/run_config.json` | L3 | 已分析 |
| 8 | `.vscode/config/health_check_config.json` | L3 | 已分析 |
| 9 | `.vscode/config/tasks/task_queue.json` | L4 | 已分析 |
| 10 | `.vscode/config/tasks/task_schema.json` | L4 | 已分析 |
| 11 | `.vscode/config/tasks/completed_tasks.json` | L4 | 已分析 |
| 12 | `.vscode/config/data/docs_sync_state.json` | 数据文件 | 已分析 |

### 1.2 配置层级结构

```
L1 (层级1 - 根规则):
├── AI_RULES.json          # AI行为约束与项目规则
├── AI_PATH_CONTEXT.json   # 路径上下文与模块职责
└── AI_CLEANUP_POLICY.json # 清理策略与去重规则

L2 (层级2 - 项目主配置):
├── project_config.json    # 项目主配置 (已存在)
├── ai_config.json         # AI配置 (引用中但不存在)
├── engines_config.json    # 引擎配置 (已存在)
└── output_config.json     # 输出配置 (引用中但不存在)

L3 (层级3 - 运行配置):
├── run_config.json        # 运行配置 (已存在)
└── health_check_config.json # 健康检查配置 (已存在)

L4 (层级4 - 功能子配置):
├── ai/model_config.json       # AI模型配置 (引用中但不存在)
├── ai/capability_map.json     # AI能力映射 (引用中但不存在)
├── tasks/task_queue.json      # 任务队列 (已存在)
└── tasks/task_schema.json     # 任务Schema (已存在)
```

---

## 二、问题诊断

### 2.1 路径不一致问题

| 文件 | 问题描述 | 正确路径 |
|------|----------|----------|
| `run_config.json` | `engines/deep_live_cam/` | `backend/ar_engine/Deep-Live-Cam/` |
| `run_config.json` | `engines/facefusion/` | `backend/ar_engine/facefusion/` |
| `run_config.json` | `engines/iroop/` | `backend/ar_engine/iRoopDeepFaceCam/` |
| `run_config.json` | `output.path` 格式错误 | `virtual_cam/, obs_integration/` |
| `health_check_config.json` | 引擎路径引用错误 | 同上 |
| `health_check_config.json` | `tracker/face_tracker.py` 不存在 | 应为 `tracker/` 目录 |

### 2.2 配置结构重复问题

1. **config_priority 重复定义**:
   - 每个文件都有完整的 `config_hierarchy` 定义，造成冗余
   - 建议：根引用，差异化存储

2. **data_flow_reference 重复**:
   - `run_config.json` 复制了 `AI_PATH_CONTEXT.json` 的数据流定义
   - 建议：统一引用，避免重复

3. **config_association 冗余**:
   - 多个文件定义了相似的关联配置
   - 建议：精简为基础引用

### 2.3 缺失/错误的文件引用

| 引用文件 | 问题 |
|----------|------|
| `ai_config.json` | 在多个配置中引用但不存在 |
| `output_config.json` | 在 `engines_config.json` 中引用但不存在 |
| `ai/model_config.json` | 在 `project_config.json` 中引用但不存在 |
| `ai/capability_map.json` | 在 `project_config.json` 中引用但不存在 |

### 2.4 数据同步状态不一致

`docs_sync_state.json` 中的 `progress` 字段与实际 `task_queue.json` 状态不匹配。

---

## 三、修复计划

### 3.1 第一阶段：修复根规则配置文件 (L1)

#### 任务1.1: 优化 AI_RULES.json
- [ ] 精简 `config_hierarchy` 为引用
- [ ] 确保所有配置关联正确

#### 任务1.2: 优化 AI_PATH_CONTEXT.json
- [ ] 精简 `config_hierarchy` 为引用
- [ ] 验证所有路径与实际目录结构一致

#### 任务1.3: 优化 AI_CLEANUP_POLICY.json
- [ ] 精简 `config_hierarchy` 为引用
- [ ] 验证清理规则与其他配置一致

### 3.2 第二阶段：修复项目主配置文件 (L2)

#### 任务2.1: 优化 project_config.json
- [ ] 修复引擎路径引用
- [ ] 移除对不存在配置的引用
- [ ] 精简 `config_association`

#### 任务2.2: 优化 engines_config.json
- [ ] 修复引擎路径为正确的相对路径
- [ ] 移除对 `output_config.json` 的引用（如果不存在）

### 3.3 第三阶段：修复运行配置文件 (L3)

#### 任务3.1: 优化 run_config.json
- [ ] 修复所有层级路径
- [ ] 移除重复的 `data_flow_reference`
- [ ] 精简 `config_association`

#### 任务3.2: 优化 health_check_config.json
- [ ] 修复引擎路径引用
- [ ] 修正不存在的模块引用
- [ ] 精简 `config_association`

### 3.4 第四阶段：修复功能子配置文件 (L4)

#### 任务4.1: 优化 task_queue.json
- [ ] 更新进度统计
- [ ] 确保与 `docs_sync_state.json` 同步

#### 任务4.2: 优化 task_schema.json
- [ ] 验证 Schema 定义完整性
- [ ] 精简 `config_association`

#### 任务4.3: 优化 completed_tasks.json
- [ ] 验证数据完整性

### 3.5 第五阶段：修复数据同步配置

#### 任务5.1: 优化 docs_sync_state.json
- [ ] 修正 `progress` 字段
- [ ] 清理不存在的文件引用
- [ ] 同步与 `task_queue.json` 的状态

---

## 四、依赖文件清单

### 4.1 需要创建的配置文件（如果需要）
- `config/ai_config.json` (如果确实需要)
- `config/output_config.json` (如果确实需要)
- `config/ai/model_config.json` (如果确实需要)
- `config/ai/capability_map.json` (如果确实需要)

### 4.2 需要删除的引用（如果配置不存在）
从所有配置文件中移除对上述不存在配置的引用

---

## 五、执行顺序

1. **备份现有配置** - 创建备份目录并备份所有JSON
2. **修复 L1 根规则** - 保持一致性
3. **修复 L2 项目配置** - 引用正确的L1规则
4. **修复 L3 运行配置** - 引用正确的L1/L2规则
5. **修复 L4 功能配置** - 引用正确的L1规则
6. **修复数据同步配置** - 确保状态一致
7. **验证修复结果** - 运行配置验证脚本

---

## 六、验证步骤

1. 检查所有JSON文件语法正确
2. 验证配置层级引用正确
3. 运行 `scripts/validate_configs.py` 验证配置
4. 检查路径引用与实际目录结构一致
5. 验证任务队列状态与同步状态一致

---

*创建时间: 2026-01-10*
*状态: 待执行*

