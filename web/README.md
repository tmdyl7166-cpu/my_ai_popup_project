# AI弹窗项目Web监控中心

> **注意**: 本目录已精简，仅保留前端静态资源和入口脚本。后端 Python 脚本已移动到 `api/backend/` 目录。

统一的Web管理员界面，用于监控和管理AI弹窗项目的各个组件、脚本执行状态、部署进度和系统资源。

## 功能特性

### 📊 实时监控

- **脚本状态监控**: 实时显示所有自动化脚本的运行状态
- **系统资源监控**: CPU、内存、磁盘使用情况实时更新
- **部署进度跟踪**: 各组件部署状态和配置进度

### 🔧 管理功能

- **脚本控制**: 启动、停止、重启自动化脚本
- **配置管理**: 在线查看和编辑项目配置
- **日志查看**: 实时查看脚本执行日志和系统日志

### 🌐 Web界面

- **响应式设计**: 支持桌面和移动设备
- **实时更新**: WebSocket实时推送状态变化
- **直观界面**: 现代化的Bootstrap UI设计

## 快速开始

### 1. 安装依赖

```bash
# 方式1: 自动安装并启动
python web/start_monitor.py --auto-install

# 方式2: 手动安装
pip install -r web/requirements.txt
python web/start_monitor.py
```

### 2. 访问界面

启动成功后，在浏览器中访问：

```
http://localhost:8080
```

## 目录结构

```
web/
├── README.md              # 本说明文档
├── requirements.txt       # Python依赖
├── __init__.py            # 包标识
├── start_monitor.py       # 唯一入口脚本 ⭐
├── static/                # 静态资源 ⭐
│   ├── css/               # 样式文件
│   │   ├── modules/       # 模块化CSS
│   │   │   ├── theme.css  # 主题样式
│   │   │   └── ...
│   │   └── ...
│   ├── js/                # JavaScript文件
│   │   ├── app.js         # 应用主程序
│   │   ├── components/    # 组件模块
│   │   │   ├── charting.js
│   │   │   ├── progress.js
│   │   │   ├── spinner.js
│   │   │   ├── toast.js
│   │   │   ├── ws.js
│   │   │   └── index.js
│   │   ├── modules/       # 功能模块
│   │   │   ├── globalMonitor.js
│   │   │   ├── deploymentProgress.js
│   │   │   ├── gpuMonitor.js
│   │   │   └── ...
│   │   └── utils/         # 工具模块
│   │       ├── eventBus.js
│   │       ├── api.js
│   │       ├── safeUtils.js
│   │       └── ...
│   └── images/            # 图片资源
└── templates/             # HTML模板 ⭐
    ├── dashboard.html     # 主仪表板
    ├── base.html          # 基础模板
    └── components/        # 组件模板
```

## 后端脚本位置

> **重要**: 所有后端 Python 脚本已移动到 `api/backend/` 目录

| 原位置                    | 新位置                            |
| ------------------------- | --------------------------------- |
| web/app.py                | api/backend/app.py                |
| web/config_manager.py     | api/backend/config_manager.py     |
| web/deployment_monitor.py | api/backend/deployment_monitor.py |
| web/entry.py              | api/backend/entry.py              |
| web/script_manager.py     | api/backend/script_manager.py     |
| web/security.py           | api/backend/security.py           |
| web/socket_events.py      | api/backend/socket_events.py      |
| web/system_monitor.py     | api/backend/system_monitor.py     |
| web/web_monitor.py        | api/backend/web_monitor.py        |

## 启动方式

### 方式1: 使用 start_monitor.py (推荐)

```bash
python web/start_monitor.py --auto-install
```

### 方式2: 使用统一启动器

```bash
python scripts/start/unified_launcher.py --mode all
```

### 方式3: 直接运行后端

```bash
python -m api.backend.app --host 0.0.0.0 --port 8080
```

## API接口

所有API端点定义在 `api/backend/routes.py` 和 `api/mapping/` 目录中。

### REST API

| 端点                  | 方法 | 说明             |
| --------------------- | ---- | ---------------- |
| /api/health           | GET  | 系统健康检查     |
| /api/project/status   | GET  | 项目整体状态     |
| /api/scripts/list     | GET  | 获取脚本列表     |
| /api/scripts/status   | GET  | 获取脚本状态     |
| /api/system/resources | GET  | 系统资源使用情况 |
| /api/system/gpu       | GET  | GPU资源使用情况  |
| /api/ports            | GET  | 端口状态列表     |
| /api/subprojects      | GET  | 子项目状态       |
| /api/bubbles          | GET  | 实时冒泡数据     |
| /api/audit/logs       | GET  | 审计日志查询     |
| /api/performance      | GET  | 性能监控概览     |
| /api/video            | GET  | 视频流概览       |
| /api/engines          | GET  | 引擎列表         |

详细API文档请参考: `api/mapping/api_mapping.md`

## 脚本架构

### 独立脚本设计

每个监控功能都是独立的Python脚本：

```
scripts/
├── health/                # 健康检查脚本
│   ├── health_check.py
│   └── emergency_recovery.sh
├── health_monitor/        # 健康监控脚本
│   ├── health_monitor.py
│   └── config_monitor.py
├── start/                 # 启动脚本 ⭐
│   ├── main_launcher.py
│   ├── start_backend_simple.py
│   └── unified_launcher.py
├── verify/                # 验证脚本 ⭐
│   ├── verify_venv.py
│   └── verify_paths.py
└── ...
```

## 扩展开发

### 添加新的前端组件

1. 在 `web/static/js/components/` 创建新的组件
2. 在 `web/static/js/components/index.js` 中注册
3. 在 `web/templates/dashboard.html` 中添加引用

### 添加新的功能模块

1. 在 `web/static/js/modules/` 创建新的模块
2. 在 `web/static/js/app.js` 中初始化

### 添加新的API接口

1. 在 `api/backend/routes.py` 中添加路由
2. 在 `api/mapping/api_mapping.json` 中注册
3. 更新 `api/frontend/api.js` 中的前端调用

## 相关文档

- 项目结构: `PROJECT_STRUCTURE.md`
- API文档: `api/mapping/api_mapping.md`
- 脚本索引: `scripts/SCRIPTS_INDEX.md`
- 部署进度: `docs/deployment_progress/任务部署跟踪文档.md`

## 许可证

本项目采用MIT许可证。

---

_最后更新: 2026-01-21_
