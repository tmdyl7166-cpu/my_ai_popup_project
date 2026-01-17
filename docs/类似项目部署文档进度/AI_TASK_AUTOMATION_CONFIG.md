# AI任务自动化配置说明

## 📋 概述

`ai_task_config.json` 是AISP项目中专门用于配置AI自动化任务执行规则的配置文件。该配置文件定义了AI如何自动化完成各种开发和维护任务的规则、流程和安全机制。

## 📁 文件位置

```
AISP/
└── ai_task_config.json  # AI任务自动化配置文件
```

## 🔧 配置结构

### 1. 任务执行引擎 (task_execution_engine)

```json
{
  "enabled": true,
  "execution_mode": "automated",
  "max_concurrent_tasks": 3,
  "task_timeout": 3600,
  "retry_policy": {
    "max_retries": 3,
    "retry_delay": 30,
    "backoff_multiplier": 2.0
  }
}
```

**配置说明：**
- `enabled`: 是否启用AI自动化任务执行
- `execution_mode`: 执行模式 (automated/manual)
- `max_concurrent_tasks`: 最大并发任务数
- `task_timeout`: 单个任务超时时间(秒)
- `retry_policy`: 重试策略

### 2. 任务分类 (task_categories)

定义不同类型任务的执行规则：

```json
{
  "code_generation": {
    "description": "代码生成和修改任务",
    "priority": "high",
    "auto_approval": true,
    "validation_required": true,
    "rollback_supported": true
  }
}
```

### 3. 执行阶段 (execution_phases)

定义任务执行的五个阶段：

- **phase_1_analysis**: 需求分析阶段
- **phase_2_planning**: 执行规划阶段
- **phase_3_execution**: 任务执行阶段
- **phase_4_validation**: 结果验证阶段
- **phase_5_completion**: 任务完成阶段

### 4. 自动化规则 (automation_rules)

#### 文件操作规则
```json
{
  "file_operations": {
    "create_file": {
      "auto_execute": true,
      "validation_required": true,
      "backup_required": false
    },
    "edit_file": {
      "auto_execute": true,
      "validation_required": true,
      "backup_required": true,
      "diff_analysis_required": true
    }
  }
}
```

#### 命令执行规则
```json
{
  "command_execution": {
    "safe_commands": {
      "auto_execute": true,
      "whitelist": ["python3", "pip", "npm", "git status"]
    },
    "risky_commands": {
      "auto_execute": false,
      "whitelist": ["rm", "sudo", "chmod"],
      "manual_approval_required": true
    }
  }
}
```

### 5. 验证框架 (validation_framework)

#### 语法验证
- 支持多种语言：Python, JSON, YAML, JavaScript, Bash
- 严格模式检查

#### 逻辑验证
- 检查导入关系
- 验证依赖完整性
- 函数签名验证
- 命名规范检查

#### 安全验证
- 硬编码密钥检测
- 输入清理验证
- 文件权限检查
- 网络安全验证

#### 性能验证
- 执行时间监控
- 内存使用监控
- CPU使用率监控

### 6. 错误处理 (error_handling)

#### 错误分类
- `syntax_error`: 语法错误 - 可自动重试
- `logic_error`: 逻辑错误 - 需要回滚
- `dependency_error`: 依赖错误 - 可重试
- `permission_error`: 权限错误 - 人工处理
- `network_error`: 网络错误 - 可重试

#### 恢复策略
- **回滚**: 支持自动回滚，保留7天备份
- **替代执行**: 提供备选执行方案
- **部分完成**: 支持断点续传

### 7. 监控和日志 (monitoring_and_logging)

#### 任务监控
- 进度跟踪
- 性能指标
- 错误统计
- 完成率监控

#### 日志配置
- INFO级别日志
- 控制台和文件双重输出
- 日志轮转 (100MB, 5个备份)

#### 审计跟踪
- 变更记录
- 用户操作记录
- 系统事件记录
- 90天保留期

### 8. 集成规则 (integration_rules)

#### 外部工具集成
- **Git**: 自动提交，特性分支策略
- **测试框架**: Pytest自动运行，覆盖率要求70%
- **代码质量**: Black自动格式化，Flake8代码检查

#### API集成
- **Ollama**: 本地AI模型集成
- **GitHub**: PR自动创建 (可选)

### 9. 用户交互规则 (user_interaction_rules)

#### 反馈收集
- 内联注释
- 完成总结
- 错误报告

#### 澄清请求
- 需求模糊时触发
- 信息缺失时触发
- 24小时超时

#### 审批工作流
- 高风险任务需要人工审批
- 标准任务24小时后自动审批

### 10. 性能优化 (performance_optimization)

#### 缓存机制
- 文件分析缓存
- 依赖解析缓存
- 验证结果缓存
- 1小时TTL

#### 并行处理
- 最多4个工作线程
- 支持验证、测试、代码分析并行

#### 资源限制
- 最大内存1024MB
- 最大CPU使用率80%
- 最大磁盘使用5120MB

## 🚀 使用方法

### 1. 基本加载

```python
from data.rules.config_loader import load_config

# 加载AI任务配置
ai_config = load_config("ai_task_config")
execution_engine = ai_config["task_execution_engine"]
```

### 2. 获取任务规则

```python
# 获取代码生成任务规则
code_gen_rules = ai_config["task_categories"]["code_generation"]

# 检查是否需要自动审批
if code_gen_rules["auto_approval"]:
    execute_task_automatically()
```

### 3. 验证任务执行

```python
# 获取验证框架配置
validation_config = ai_config["validation_framework"]

# 执行语法验证
if validation_config["syntax_validation"]["enabled"]:
    validate_syntax(file_path)
```

### 4. 错误处理

```python
# 获取错误处理配置
error_config = ai_config["error_handling"]

# 根据错误类型选择处理策略
error_type = classify_error(exception)
strategy = error_config["error_categories"][error_type]

if strategy["auto_retry"]:
    retry_task(max_retries=strategy["max_retries"])
```

## 📊 配置验证

### 验证脚本

```bash
# 验证配置文件格式
python3 -c "import json; json.load(open('ai_task_config.json')); print('✓ 格式正确')"

# 运行配置验证
python3 scripts/validate_configs.py --config ai_task_config.json
```

### 验证清单

- [ ] JSON格式正确性
- [ ] 必需字段完整性
- [ ] 引用关系有效性
- [ ] 约束规则一致性
- [ ] 依赖关系正确性

## 🔒 安全考虑

1. **命令执行限制**: 危险命令需要人工审批
2. **文件操作审计**: 所有文件操作都有审计跟踪
3. **资源使用监控**: 防止资源耗尽攻击
4. **网络访问控制**: 限制外部网络访问
5. **敏感信息保护**: 自动检测和警告敏感信息

## 📈 性能监控

- 任务执行时间统计
- 资源使用率监控
- 错误率和成功率跟踪
- 自动化效率评估

## 🔄 更新机制

配置文件支持热更新，无需重启服务。更新时会自动验证配置一致性。

## 📝 版本信息

- **版本**: 1.0.0
- **创建日期**: 2025-01-21
- **作者**: AISP Team
- **兼容性**: AISP 2.0.0+

---

*该配置文件遵循AISP项目的五层逻辑架构，确保AI自动化任务执行的安全性、可靠性和可控性。*
