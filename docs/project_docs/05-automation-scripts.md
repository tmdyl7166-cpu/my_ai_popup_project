# 自动化脚本说明

> 本文档描述夜灵AR多功能合成软件的自动化脚本系统和使用说明。

## 📁 脚本目录结构

```
scripts/
├── config/                      # 配置脚本
│   ├── config_loader.py         # 配置加载器
│   └── scripts_config.json      # 脚本配置定义
│
├── core/                        # 核心脚本
│   ├── script_registry.py       # 脚本注册表
│   ├── entry.py                 # 入口脚本
│   └── main_controller.py       # 主控制器
│
├── deploy/                      # 部署脚本
│   ├── deploy_entry.py          # 部署入口
│   ├── shell_wrapper.py         # Shell包装器
│   ├── deploy_core/             # 部署核心模块
│   ├── deploy_modules/          # 部署模块
│   └── deploy_utils/            # 部署工具
│
├── health/                      # 健康检查脚本
│   ├── health_check.py          # 健康检查
│   ├── emergency_recovery.sh    # 紧急恢复
│   ├── config_consistency_checker.py  # 配置一致性检查
│   ├── cross_domain_api_monitor.py    # 跨域API监控
│   ├── dependency_checker.py    # 依赖检查
│   ├── docs_sync_checker.py     # 文档同步检查
│   ├── file_cleanup_util.py     # 文件清理工具
│   ├── global_context_monitor.py # 全局上下文监控
│   ├── health_monitor_orchestrator.py # 健康监控编排器
│   ├── menu_interactivity_monitor.py  # 菜单交互监控
│   ├── rules_validator.py       # 规则验证器
│   ├── structure_checker.py     # 结构检查器
│   ├── task_docs_unifier.py     # 任务文档统一器
│   └── ui_popup_monitor.py      # UI弹窗监控
│
├── health_monitor/              # 健康监控脚本
│   ├── health_monitor.py        # 主健康监控
│   ├── config_monitor.py        # 配置监控
│   ├── config_validator.py      # 配置验证
│   ├── docs_sync_monitor.py     # 文档同步监控
│   ├── ui_interaction_monitor.py # UI交互监控
│   └── start_health_monitor.py  # 启动脚本
│
├── start/                       # 启动脚本
│   ├── main_launcher.py         # 主启动器
│   ├── start_backend_simple.py  # 启动后端
│   ├── start_gui_py.py          # 启动GUI
│   ├── start_hot_window.sh      # 启动热窗口
│   └── unified_launcher.py      # 统一启动器
│
├── test/                        # 测试脚本
│   ├── test_runner.py           # 测试运行器
│   ├── test_launch_config.py    # 启动配置测试
│   ├── test_frontend_backend.py # 前后端测试
│   ├── test_error_handling.py   # 错误处理测试
│   └── test_dependencies.py     # 依赖测试
│
├── utils/                       # 工具脚本
│   ├── file_utils.py            # 文件工具
│   ├── logging_utils.py         # 日志工具
│   ├── check_pylance_version.py # Pylance版本检查
│   ├── fix_opencv_deps.sh       # OpenCV依赖修复
│   ├── system_diagnostic        # 系统诊断
│   ├── validate_configs.py      # 配置验证
│   ├── verify_paths.py          # 路径验证
│   └── verify_venv.py           # 虚拟环境验证
│
├── verify/                      # 验证脚本
│   ├── verify_venv.py           # 虚拟环境验证
│   └── verify_paths.py          # 路径验证
│
├── web/                         # Web相关脚本
│   ├── api_manager.py           # API管理器
│   ├── entry.py                 # Web入口
│   ├── menu_manager.py          # 菜单管理器
│   ├── security_validator.py    # 安全验证器
│   └── web_orchestrator.py      # Web编排器
│
├── SCRIPTS_INDEX.md             # 目录索引
├── scripts_README.md            # 说明文档
├── scripts_config.json          # 脚本配置
├── __init__.py                  # 包标识
└── entry.py                     # 总入口
```

## 🚀 启动脚本

### 统一启动器

**脚本**: `scripts/start/unified_launcher.py`

**功能**: 统一启动所有服务

**使用方式**:

```bash
# 启动所有服务
python scripts/start/unified_launcher.py --mode all

# 仅启动后端
python scripts/start/unified_launcher.py --mode backend

# 仅启动GUI
python scripts/start/unified_launcher.py --mode gui

# 启动Web监控中心
python scripts/start/unified_launcher.py --mode web

# 带详细输出
python scripts/start/unified_launcher.py --mode all --verbose
```

**参数**:

| 参数 | 描述 |
|------|------|
| --mode | 启动模式 (all/backend/gui/web) |
| --verbose | 详细输出 |
| --no-health-check | 跳过健康检查 |

### 主启动器

**脚本**: `scripts/start/main_launcher.py`

**功能**: 主入口启动器

**使用方式**:

```bash
python scripts/start/main_launcher.py
```

### 后端启动

**脚本**: `scripts/start/start_backend_simple.py`

**功能**: 启动后端API服务

**使用方式**:

```bash
python scripts/start/start_backend_simple.py --host 0.0.0.0 --port 8000
```

### GUI启动

**脚本**: `scripts/start/start_gui_py.py`

**功能**: 启动PyQt5 GUI应用

**使用方式**:

```bash
python scripts/start/start_gui_py.py
```

## 🔧 健康检查脚本

### 主健康监控

**脚本**: `scripts/health_monitor/health_monitor.py`

**功能**: 执行全面的项目健康检查

**使用方式**:

```bash
# 运行完整健康检查
python scripts/health_monitor/health_monitor.py

# 带详细输出
python scripts/health_monitor/health_monitor.py --verbose

# 生成报告
python scripts/health_monitor/health_monitor.py --report
```

**检查项目**:

- 项目结构完整性
- 配置文件有效性
- 规则文件一致性
- 文档同步状态
- 依赖包安装情况

### 配置验证

**脚本**: `scripts/health_monitor/config_validator.py`

**功能**: 验证项目配置的一致性和完整性

**使用方式**:

```bash
# 验证配置
python scripts/health_monitor/config_validator.py

# 验证规则一致性
python scripts/health_monitor/config_validator.py --rules

# 验证合规性
python scripts/health_monitor/config_validator.py --compliance

# 修复问题
python scripts/health_monitor/config_validator.py --fix
```

### UI交互监控

**脚本**: `scripts/health_monitor/ui_interaction_monitor.py`

**功能**: 检测前端交互、弹窗管理、数据传递等UI相关问题

**使用方式**:

```bash
python scripts/health_monitor/ui_interaction_monitor.py --verbose
```

### 文档同步监控

**脚本**: `scripts/health_monitor/docs_sync_monitor.py`

**功能**: 监控文档更新状态和同步情况

**使用方式**:

```bash
python scripts/health_monitor/docs_sync_monitor.py --report
```

## 🔍 验证脚本

### 虚拟环境验证

**脚本**: `scripts/verify/verify_venv.py`

**功能**: 验证虚拟环境是否正确配置

**使用方式**:

```bash
# 验证虚拟环境
python scripts/verify/verify_venv.py

# 详细输出
python scripts/verify/verify_venv.py --verbose

# 自动修复
python scripts/verify/verify_venv.py --fix
```

### 路径验证

**脚本**: `scripts/verify/verify_paths.py`

**功能**: 验证项目路径配置是否正确

**使用方式**:

```bash
python scripts/verify/verify_paths.py
```

## 🧪 测试脚本

### 测试运行器

**脚本**: `scripts/test/test_runner.py`

**功能**: 运行所有测试

**使用方式**:

```bash
# 运行所有测试
python scripts/test/test_runner.py

# 运行特定模块测试
python scripts/test/test_runner.py --module backend

# 生成覆盖率报告
python scripts/test/test_runner.py --coverage

# 仅运行单元测试
python scripts/test/test_runner.py --type unit
```

### 依赖测试

**脚本**: `scripts/test/test_dependencies.py`

**功能**: 测试依赖包是否正确安装

**使用方式**:

```bash
python scripts/test/test_dependencies.py
```

### 前后端测试

**脚本**: `scripts/test/test_frontend_backend.py`

**功能**: 测试前后端API通信

**使用方式**:

```bash
python scripts/test/test_frontend_backend.py --verbose
```

## 📦 部署脚本

### 部署入口

**脚本**: `scripts/deploy/deploy_entry.py`

**功能**: 项目部署入口

**使用方式**:

```bash
# 完整部署
python scripts/deploy/deploy_entry.py --full

# 仅部署依赖
python scripts/deploy/deploy_entry.py --deps

# 仅配置
python scripts/deploy/deploy_entry.py --config
```

### Web配置同步

**脚本**: `scripts/deploy/sync_web_config.sh`

**功能**: 同步Web配置

```bash
bash scripts/deploy/sync_web_config.sh
```

## 🔒 安全脚本

### 安全验证

**脚本**: `scripts/web/security_validator.py`

**功能**: 验证系统安全性

**使用方式**:

```bash
python scripts/web/security_validator.py
```

## 📊 配置脚本

### 配置加载

**脚本**: `scripts/config/config_loader.py`

**功能**: 加载和管理项目配置

**使用方式**:

```python
from scripts.config.config_loader import load_config

config = load_config("project")
```

### 配置验证

**脚本**: `scripts/utils/validate_configs.py`

**功能**: 验证所有配置文件

**使用方式**:

```bash
python scripts/utils/validate_configs.py --all
```

## 🛠️ 工具脚本

### 文件清理

**脚本**: `scripts/health/file_cleanup_util.py`

**功能**: 清理临时文件和缓存

**使用方式**:

```bash
# 预览清理内容
python scripts/health/file_cleanup_util.py --dry-run

# 执行清理
python scripts/health/file_cleanup_util.py

# 清理特定类型
python scripts/health/file_cleanup_util.py --type pycache
```

### 日志工具

**脚本**: `scripts/utils/logging_utils.py`

**功能**: 提供日志记录工具函数

### 文件工具

**脚本**: `scripts/utils/file_utils.py`

**功能**: 提供文件操作工具函数

## ⚙️ 脚本配置

### 脚本配置定义

配置文件: `scripts/scripts_config.json`

```json
{
  "executionRules": {
    "scheduling": {
      "daily": {
        "time": "02:00",
        "scripts": ["health_monitor.py"],
        "enabled": true
      },
      "weekly": {
        "day": "sunday",
        "time": "03:00",
        "scripts": ["config_monitor.py"],
        "enabled": true
      }
    },
    "errorHandling": {
      "retryPolicy": {
        "maxRetries": 3,
        "backoff": "exponential",
        "maxDelay": 300
      }
    }
  },
  "monitoring": {
    "metrics": {
      "executionTime": {
        "enabled": true,
        "threshold": 300
      },
      "successRate": {
        "enabled": true,
        "threshold": 95
      }
    }
  }
}
```

## 📋 使用示例

### 日常使用

```bash
# 1. 启动项目
python scripts/start/unified_launcher.py --mode all

# 2. 检查系统状态
python scripts/health_monitor/health_monitor.py --report

# 3. 验证配置
python scripts/health_monitor/config_validator.py --rules
```

### 开发调试

```bash
# 启动后端开发模式
python scripts/start/start_backend_simple.py --host 0.0.0.0 --port 8000 --reload

# 启动GUI调试模式
python scripts/start/start_gui_py.py --debug

# 验证路径配置
python scripts/verify/verify_paths.py --verbose
```

### 问题排查

```bash
# 运行健康检查
python scripts/health_monitor/health_monitor.py --verbose

# 验证依赖
python scripts/test/test_dependencies.py

# 清理并重新验证
python scripts/health/file_cleanup_util.py --fix
python scripts/verify/verify_venv.py --fix
```

### 定时任务设置

```bash
# 添加到 crontab
# 每天凌晨2点运行健康检查
0 2 * * * /usr/bin/python3 /path/to/scripts/health_monitor/health_monitor.py --report

# 每周日凌晨3点运行配置验证
0 3 * * 0 /usr/bin/python3 /path/to/scripts/health_monitor/config_validator.py --report
```

## 📝 脚本别名

项目提供了简化的脚本别名:

```bash
# 入口
python scripts/entry.py

# 健康检查
python scripts/entry.py --task health-check

# 配置检查
python scripts/validate_configs.py

# 验证路径
python scripts/verify_paths.py

# 启动健康监控
python scripts/start_health_monitor.py --verbose

# 启动后端
python scripts/start_backend_simple.py

# 启动GUI
python scripts/start_gui_py.py

# 运行测试
python -m scripts.test.test_runner
```

## 📝 文档版本

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| 1.0 | 2026-01-19 | 初始版本 |

## 🔗 相关文档

- [项目整体架构设计](01-project-architecture.md)
- [系统运行时逻辑流程](02-runtime-logic.md)
- [依赖和配置说明](03-dependencies-config.md)
- [API接口文档](04-frontend-backend-api.md)
