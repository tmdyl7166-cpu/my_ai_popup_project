# Scripts目录结构统计

## 目录概览

```
scripts/
├── config/              # 配置相关脚本
├── core/                # 核心脚本
├── deploy/              # 部署脚本
├── health/              # 健康检查脚本
├── health_monitor/      # 健康监控脚本
├── start/               # 启动脚本 (新增)
├── test/                # 测试脚本
├── utils/               # 工具脚本
├── web/                 # Web相关脚本
└── __init__.py          # 包标识
```

## 脚本统计

### 根目录脚本 (需要归类)

| 脚本名                       | 类型     | 建议归类        |
| ---------------------------- | -------- | --------------- |
| check_pylance_version.py     | Python   | utils/          |
| deploy.sh                    | Shell    | deploy/         |
| emergency_recovery.sh        | Shell    | health/         |
| entry.py                     | Python   | core/           |
| fix_opencv_deps.sh           | Shell    | utils/          |
| health_check.py              | Python   | health/         |
| main_controller.py           | Python   | core/           |
| main_launcher.py             | Python   | start/          |
| path_config.py               | Python   | config/         |
| scripts_config_refactor.json | JSON     | config/         |
| scripts_config.json          | JSON     | config/         |
| scripts_README.md            | Markdown | -               |
| start_backend_simple.py      | Python   | start/          |
| start_gui_py.py              | Python   | start/          |
| start_health_monitor.py      | Python   | health_monitor/ |
| start_hot_window.sh          | Shell    | start/          |
| sync_web_config.sh           | Shell    | deploy/         |
| system_diagnostic            | Binary   | utils/          |
| unified_launcher.py          | Python   | start/          |
| validate_configs.py          | Python   | utils/          |
| verify_paths.py              | Python   | verify/         |
| verify_venv.py               | Python   | verify/         |

### 子目录脚本

#### config/ (配置脚本)

| 文件                         | 说明           |
| ---------------------------- | -------------- |
| config_loader.py             | 配置加载器     |
| scripts_config.json          | 脚本配置       |
| scripts_config_refactor.json | 脚本配置(重构) |

#### core/ (核心脚本)

| 文件               | 说明       |
| ------------------ | ---------- |
| script_registry.py | 脚本注册表 |
| entry.py           | 入口脚本   |
| main_controller.py | 主控制器   |

#### deploy/ (部署脚本)

| 文件             | 说明         |
| ---------------- | ------------ |
| deploy_entry.py  | 部署入口     |
| shell_wrapper.sh | Shell包装器  |
| deploy_core/     | 部署核心模块 |
| deploy_modules/  | 部署模块     |
| deploy_utils/    | 部署工具     |

#### health/ (健康检查)

| 文件                           | 说明           |
| ------------------------------ | -------------- |
| config_consistency_checker.py  | 配置一致性检查 |
| cross_domain_api_monitor.py    | 跨域API监控    |
| dependency_checker.py          | 依赖检查       |
| docs_sync_checker.py           | 文档同步检查   |
| file_cleanup_util.py           | 文件清理工具   |
| global_context_monitor.py      | 全局上下文监控 |
| health_monitor_orchestrator.py | 健康监控编排器 |
| menu_interactivity_monitor.py  | 菜单交互监控   |
| rules_validator.py             | 规则验证器     |
| structure_checker.py           | 结构检查器     |
| task_docs_unifier.py           | 任务文档统一器 |
| ui_popup_monitor.py            | UI弹窗监控     |
| emergency_recovery.sh          | 紧急恢复       |
| health_check.py                | 健康检查       |

#### health_monitor/ (健康监控)

| 文件                      | 说明         |
| ------------------------- | ------------ |
| config_monitor.py         | 配置监控     |
| config_validator.py       | 配置验证     |
| docs_sync_monitor.py      | 文档同步监控 |
| health_monitor.py         | 健康监控     |
| ui_interaction_monitor.py | UI交互监控   |
| start_health_monitor.py   | 启动脚本     |

#### start/ (启动脚本) - 新增

| 文件                    | 说明       |
| ----------------------- | ---------- |
| main_launcher.py        | 主启动器   |
| start_backend_simple.py | 启动后端   |
| start_gui_py.py         | 启动GUI    |
| start_hot_window.sh     | 启动热窗口 |
| unified_launcher.py     | 统一启动器 |

#### test/ (测试脚本)

| 文件                     | 说明         |
| ------------------------ | ------------ |
| **init**.py              | 包标识       |
| test_dependencies.py     | 依赖测试     |
| test_error_handling.py   | 错误处理测试 |
| test_frontend_backend.py | 前后端测试   |
| test_launch_config.py    | 启动配置测试 |
| test_runner.py           | 测试运行器   |
| reports/                 | 测试报告目录 |

#### utils/ (工具脚本)

| 文件                     | 说明            |
| ------------------------ | --------------- |
| file_utils.py            | 文件工具        |
| logging_utils.py         | 日志工具        |
| check_pylance_version.py | Pylance版本检查 |
| fix_opencv_deps.sh       | OpenCV依赖修复  |
| system_diagnostic        | 系统诊断        |
| validate_configs.py      | 配置验证        |
| verify_paths.py          | 路径验证        |
| verify_venv.py           | 虚拟环境验证    |

#### web/ (Web相关)

| 文件                  | 说明       |
| --------------------- | ---------- |
| api_manager.py        | API管理器  |
| entry.py              | 入口       |
| menu_manager.py       | 菜单管理器 |
| security_validator.py | 安全验证器 |
| web_config.json       | Web配置    |
| web_orchestrator.py   | Web编排器  |

## 统计汇总

| 类别         | 数量    |
| ------------ | ------- |
| Python脚本   | 35+     |
| Shell脚本    | 8       |
| JSON配置     | 4       |
| Markdown文档 | 1       |
| 目录         | 9       |
| **总计**     | **50+** |

## 使用说明

### 健康检查

```bash
# 完整健康检查
python scripts/health/health_check.py

# 使用编排器
python scripts/health/health_monitor_orchestrator.py

# 启动监控
python scripts/health_monitor/start_health_monitor.py
```

### 启动脚本

```bash
# 统一启动器
python scripts/start/unified_launcher.py

# 启动后端
python scripts/start/start_backend_simple.py

# 启动GUI
python scripts/start/start_gui_py.py
```

### 部署脚本

```bash
# 部署入口
python scripts/deploy/deploy_entry.py

# 同步Web配置
bash scripts/deploy/sync_web_config.sh
```

### 验证脚本

```bash
# 验证虚拟环境
python scripts/verify/verify_venv.py

# 验证路径
python scripts/verify/verify_paths.py
```

---

_创建时间: 2026-01-19_
_版本: 1.0.0_
