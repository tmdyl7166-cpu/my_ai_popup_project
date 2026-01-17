# AISP 项目配置重构计划

## 一、当前配置状态分析

### 1.1 配置文件清单

**L1 根规则层（3个文件）：**
```
.vscode/
├── AI_RULES.json          # AI行为约束规则
├── AI_PATH_CONTEXT.json   # 路径上下文与数据流定义
└── AI_CLEANUP_POLICY.json # 清理策略与重复检测规则
```

**L2 项目主配置层（4个文件）：**
```
.vscode/config/
├── project_config.json    # 项目主配置
├── engines_config.json    # 引擎集成配置
├── output_config.json     # 输出配置
└── ai_config.json         # AI能力配置
```

**L3 运行配置层（3个文件）：**
```
.vscode/config/
├── run_config.json        # 统一API与运行配置
├── health_check_config.json # 健康检查配置
└── daemon_guard_config.json # 进程守护配置
```

**L4 功能子配置层（5个文件）：**
```
.vscode/config/
├── AI3.json               # 前端交互与UI优化规则
├── resource_alert_config.json # 资源告警配置
├── DOCS_SYNC_CONFIG.json  # 文档同步配置
└── tasks/
    ├── task_queue.json    # 任务队列
    ├── task_schema.json   # 任务Schema定义
    └── completed_tasks.json # 已完成任务归档
```

**L5 执行配置层（2个文件）：**
```
.vscode/config/
├── resource_alert_config.json # 资源告警配置
└── data/docs_sync_state.json  # 文档同步状态
```

### 1.2 当前存在的问题

1. **配置重复**：L1根规则在 `.vscode/` 和 `config/` 目录各有一份
2. **backup目录冗余**：大量备份文件需要清理
3. **层级定义不一致**：部分配置文件的config_priority与实际内容不符
4. **关联关系缺失**：config_association字段不完整

---

## 二、重构目标

### 2.1 配置层级结构（最终状态）

```
AISP/.vscode/
├── L1_根规则层/
│   ├── AI_RULES.json
│   ├── AI_PATH_CONTEXT.json
│   └── AI_CLEANUP_POLICY.json
├── L2_项目主配置层/
│   ├── project_config.json
│   ├── engines_config.json
│   ├── output_config.json
│   └── ai_config.json
├── L3_运行配置层/
│   ├── run_config.json
│   ├── health_check_config.json
│   └── daemon_guard_config.json
├── L4_功能子配置层/
│   ├── AI3.json
│   ├── resource_alert_config.json
│   ├── DOCS_SYNC_CONFIG.json
│   └── tasks/
│       ├── task_queue.json
│       ├── task_schema.json
│       └── completed_tasks.json
├── L5_执行配置层/
│   └── resource_alert_config.json
├── extensions.json
├── launch.json
├── settings.json
└── tasks.json
```

### 2.2 配置加载顺序

```
1. .blackboxrules (项目根目录)
2. L1_根规则层/ (AI_RULES.json, AI_PATH_CONTEXT.json, AI_CLEANUP_POLICY.json)
3. L2_项目主配置层/ (project_config.json, engines_config.json, output_config.json, ai_config.json)
4. L3_运行配置层/ (run_config.json, health_check_config.json, daemon_guard_config.json)
5. L4_功能子配置层/ (AI3.json, resource_alert_config.json, DOCS_SYNC_CONFIG.json, tasks/*)
6. L5_执行配置层/ (resource_alert_config.json)
```

---

## 三、重构任务清单

### 3.1 第一阶段：清理冗余文件

- [ ] 删除 `config/` 目录下的重复L1根规则文件
- [ ] 清空或删除 `backup/` 目录
- [ ] 整合重复的配置文件

### 3.2 第二阶段：重构L1根规则层

- [ ] 重新定义 AI_RULES.json 的配置优先级
- [ ] 重新定义 AI_PATH_CONTEXT.json 的数据流
- [ ] 重新定义 AI_CLEANUP_POLICY.json 的清理规则

### 3.3 第三阶段：重构L2项目主配置层

- [ ] 重新定义 project_config.json
- [ ] 重新定义 engines_config.json
- [ ] 重新定义 output_config.json
- [ ] 重新定义 ai_config.json

### 3.4 第四阶段：重构L3运行配置层

- [ ] 重新定义 run_config.json
- [ ] 重新定义 health_check_config.json
- [ ] 重新定义 daemon_guard_config.json

### 3.5 第五阶段：重构L4功能子配置层

- [ ] 重新定义 AI3.json
- [ ] 重新定义 resource_alert_config.json
- [ ] 重新定义 DOCS_SYNC_CONFIG.json
- [ ] 重新定义 tasks/task_queue.json
- [ ] 重新定义 tasks/task_schema.json
- [ ] 重新定义 tasks/completed_tasks.json

### 3.6 第六阶段：创建统一索引

- [ ] 创建 CONFIG_INDEX.json
- [ ] 创建配置验证脚本

---

## 四、配置标准规范

### 4.1 元数据标准

每个配置文件必须包含以下meta字段：

```json
{
  "meta": {
    "name": "配置名称",
    "version": "1.0.0",
    "description": "配置描述",
    "author": "AISP Team",
    "created_at": "2025-01-21T00:00:00Z",
    "last_updated": "2025-01-21T00:00:00Z"
  }
}
```

### 4.2 配置优先级标准

每个配置文件必须包含以下config_priority字段：

```json
{
  "config_priority": {
    "level": 1,
    "layer_name": "层级名称",
    "role": "角色描述",
    "description": "配置说明",
    "depends_on_root_rules": true,
    "priority_override": {
      "allowed": false,
      "reason": "原因说明"
    }
  }
}
```

### 4.3 配置关联标准

每个配置文件必须包含以下config_association字段：

```json
{
  "config_association": {
    "root_rules": [],
    "depends_on": [],
    "related_configs": []
  }
}
```

---

## 五、执行顺序

1. 首先创建 L1_根规则层 目录
2. 将根规则文件移动到 L1_根规则层
3. 依次创建 L2-L5 目录结构
4. 重构每个配置文件
5. 删除旧的重复文件
6. 运行验证脚本确认配置正确

---

## 六、验证清单

- [ ] 所有配置文件符合标准规范
- [ ] 配置层级关系正确
- [ ] 配置关联关系完整
- [ ] 没有重复的配置定义
- [ ] 配置加载顺序正确
- [ ] 验证脚本运行通过

---

## 七、文档更新

- [ ] 更新 README.md
- [ ] 更新项目结构说明文档
- [ ] 更新配置说明文档

