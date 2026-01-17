# 自动化脚本系统

本目录包含项目的所有自动化脚本，用于环境验证、依赖安装、健康检查、部署等任务。

**重要说明**: 所有路径以 `/workspaces/my_ai_popup_project` 为项目根目录

## 目录结构

```
scripts/
├── entry.py                    # 统一入口脚本
├── main_controller.py          # 主控制器
├── path_config.py              # 路径配置模块
├── health_check.py             # 健康检查脚本
├── start_health_monitor.py     # 健康监控启动脚本
├── start_backend_simple.py     # 后端启动脚本
├── start_gui_py.py             # GUI 启动脚本
├── validate_configs.py         # 配置验证脚本
├── verify_paths.py             # 路径验证脚本
├── check_pylance_version.py    # Pylance 版本检查
├── scripts_config.json         # 脚本配置定义
├── scripts_config_refactor.json # 脚本配置重构版
├── scripts_README.md           # 本说明文档
│
├── core/                       # 核心脚本模块
│   └── script_registry.py      # 脚本注册管理器
│
├── health/                     # 健康检查模块
│   ├── structure_checker.py        # 项目结构检查器
│   ├── config_consistency_checker.py # 配置一致性检查器
│   ├── rules_validator.py          # 规则验证器
│   ├── docs_sync_checker.py        # 文档同步检查器
│   ├── dependency_checker.py       # 依赖检查器
│   ├── task_docs_unifier.py        # 任务文档统一器
│   ├── file_cleanup_util.py        # 文件清理工具
│   ├── health_monitor_orchestrator.py # 健康监控编排器
│   └── menu_interactivity_monitor.py # 菜单交互监控器
│
├── health_monitor/             # 健康监控脚本
│   ├── health_monitor.py       # 主健康监控脚本
│   ├── config_monitor.py       # 配置监控脚本
│   ├── config_validator.py     # 配置验证脚本
│   ├── docs_sync_monitor.py    # 文档同步监控
│   └── ui_interaction_monitor.py # UI交互监控
│
├── config/                     # 配置模块
│   └── config_loader.py        # 配置加载器
│
├── utils/                      # 工具模块
│   ├── logging_utils.py        # 日志工具
│   └── file_utils.py           # 文件工具
│
├── web/                        # Web相关脚本
│   ├── api_manager.py          # API 管理器
│   ├── entry.py                # Web 入口
│   ├── menu_manager.py         # 菜单管理器
│   ├── security_validator.py   # 安全验证器
│   ├── web_orchestrator.py     # Web 编排器
│   └── web_config.json         # Web 配置
│
├── deploy/                     # 部署模块
│   ├── deploy_entry.py         # 部署入口
│   ├── shell_wrapper.py        # Shell 包装器
│   ├── deploy_core/            # 部署核心模块
│   │   ├── base.py             # 基础部署类
│   │   └── platform.py         # 平台适配
│   ├── deploy_modules/         # 部署功能模块
│   │   ├── build_app.py        # 应用构建
│   │   ├── deploy_app.py       # 应用部署
│   │   ├── health_check.py     # 健康检查
│   │   ├── install_deps.py     # 依赖安装
│   │   └── setup_env.py        # 环境设置
│   └── deploy_utils/           # 部署工具
│       ├── config.py           # 配置工具
│       └── logger.py           # 日志工具
│
├── test/                       # 测试模块
│   ├── __init__.py
│   ├── test_runner.py          # 测试运行器
│   ├── test_launch_config.py   # 启动配置测试
│   ├── test_frontend_backend.py # 前后端测试
│   ├── test_error_handling.py  # 错误处理测试
│   └── test_dependencies.py    # 依赖测试
│
├── ui/                         # UI 相关脚本
│
├── logs/                       # 日志目录
│   └── deploy/                 # 部署日志
│
├── reports/                    # 报告目录
│
└── *.sh                        # Shell 脚本
    ├── deploy.sh               # 部署脚本
    ├── emergency_recovery.sh   # 紧急恢复脚本
    ├── fix_opencv_deps.sh      # OpenCV 依赖修复
    ├── start_hot_window.sh     # 热窗口启动
    └── sync_web_config.sh      # Web 配置同步
```

## 快速使用

### 方式1：使用统一入口 (entry.py)

```bash
cd /workspaces/my_ai_popup_project

# 显示帮助
python3 scripts/entry.py --help

# 运行健康检查
python3 scripts/entry.py --task health-check

# 运行配置管理
python3 scripts/entry.py --task config-management

# 运行文档管理
python3 scripts/entry.py --task docs-management

# 运行UI监控
python3 scripts/entry.py --task ui-monitoring

# 列出所有可用模块
python3 scripts/entry.py --list-modules

# 查看模块信息
python3 scripts/entry.py --module-info health
```

### 方式2：直接运行特定脚本

```bash
cd /workspaces/my_ai_popup_project

# 健康检查
python3 scripts/health_check.py

# 路径验证
python3 scripts/verify_paths.py

# 配置验证
python3 scripts/validate_configs.py

# 启动健康监控
python3 scripts/start_health_monitor.py --verbose

# 启动后端服务
python3 scripts/start_backend_simple.py

# 启动 GUI
python3 scripts/start_gui_py.py

# 系统诊断
./scripts/system_diagnostic
```

### 方式3：使用 Shell 脚本

```bash
cd /workspaces/my_ai_popup_project

# 部署脚本
./scripts/deploy.sh

# 紧急恢复
./scripts/emergency_recovery.sh

# 同步 Web 配置
./scripts/sync_web_config.sh

# 修复 OpenCV 依赖
./scripts/fix_opencv_deps.sh
```

## 路径配置

```python
from scripts.path_config import ProjectPaths

paths = ProjectPaths()

# 获取目录绝对路径
paths.get('src')           # /workspaces/my_ai_popup_project/src
paths.get('scripts')       # /workspaces/my_ai_popup_project/scripts
paths.get('assets')        # /workspaces/my_ai_popup_project/assets
paths.get('models')        # /workspaces/my_ai_popup_project/assets/models
paths.get('images')        # /workspaces/my_ai_popup_project/assets/images
paths.get('videos')        # /workspaces/my_ai_popup_project/assets/videos
paths.get('logs')          # /workspaces/my_ai_popup_project/logs
paths.get('temp')          # /workspaces/my_ai_popup_project/temp
paths.get('output')        # /workspaces/my_ai_popup_project/output
paths.get('web')           # /workspaces/my_ai_popup_project/web
paths.get('ai_popup_env')  # /workspaces/my_ai_popup_project/ai_popup_env

# 获取启动入口
entry_points = ProjectPaths.get_entry_points()

# 获取配置文件
config_files = ProjectPaths.get_config_files()
```

## 环境策略

### 部署阶段 vs 运行阶段

| 阶段 | 环境 | 说明 |
|------|------|------|
| 验证 | 本地 | 检查 Python、pip、目录结构 |
| 安装 | 本地 | 使用本地 pip 安装依赖 |
| 设置 | 本地 | 创建目录、配置文件 |
| 启动 | 虚拟环境 | 使用 ai_popup_env 中的 Python |

### 虚拟环境位置

- **路径**: `/workspaces/my_ai_popup_project/ai_popup_env/`
- **Python**: `/workspaces/my_ai_popup_project/ai_popup_env/bin/python`

## 脚本说明

### 入口脚本
| 脚本 | 说明 |
|------|------|
| `entry.py` | 统一入口脚本，负责调度和执行所有自动化脚本 |
| `main_controller.py` | 主控制器，协调各模块执行 |

### 健康检查脚本
| 脚本 | 说明 |
|------|------|
| `health_check.py` | 健康检查脚本，验证项目各组件状态 |
| `start_health_monitor.py` | 健康监控启动脚本，支持 `--verbose` 参数 |
| `health/` | 健康检查模块目录，包含各类检查器 |
| `health_monitor/` | 健康监控脚本目录，包含监控脚本 |

### 启动脚本
| 脚本 | 说明 |
|------|------|
| `start_backend_simple.py` | 启动后端服务 |
| `start_gui_py.py` | 启动 GUI 界面 |

### 验证脚本
| 脚本 | 说明 |
|------|------|
| `verify_paths.py` | 验证项目路径配置 |
| `validate_configs.py` | 验证配置文件 |
| `check_pylance_version.py` | 检查 Pylance 版本 |

### 部署脚本
| 脚本 | 说明 |
|------|------|
| `deploy.sh` | Shell 部署脚本 |
| `emergency_recovery.sh` | 紧急恢复脚本 |
| `deploy/` | 部署模块目录 |

### Web 相关脚本
| 脚本 | 说明 |
|------|------|
| `web/` | Web 相关脚本目录 |
| `sync_web_config.sh` | 同步 Web 配置 |

### 测试脚本
| 脚本 | 说明 |
|------|------|
| `test/` | 测试模块目录 |
| `test_runner.py` | 测试运行器 |

## 输出路径

- **日志**: `/workspaces/my_ai_popup_project/logs/`
- **报告**: `/workspaces/my_ai_popup_project/scripts/reports/`
- **测试报告**: `/workspaces/my_ai_popup_project/scripts/test/reports/`
- **临时文件**: `/workspaces/my_ai_popup_project/temp/`

## 最佳实践

```bash
# 首次使用 - 运行健康检查
cd /workspaces/my_ai_popup_project
python3 scripts/entry.py --task health-check

# 启动健康监控
python3 scripts/start_health_monitor.py --verbose

# 验证项目配置
python3 scripts/validate_configs.py

# 使用虚拟环境运行
/workspace/my_ai_popup_project/ai_popup_env/bin/python3 scripts/entry.py --task health-check
```

## 常见问题

### Q: 如何添加新脚本？
1. 在相应目录创建 Python 脚本
2. 在 `scripts_config.json` 中注册脚本信息
3. 更新 `scripts_README.md` 文档

### Q: 如何运行特定模块的健康检查？
```bash
python3 scripts/entry.py --module health --method run
```

### Q: 如何查看所有可用模块？
```bash
python3 scripts/entry.py --list-modules
```

---

最后更新: 2026-01-17

