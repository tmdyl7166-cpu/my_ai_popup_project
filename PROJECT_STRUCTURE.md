# 项目结构总览

## 项目根目录: /home/vboxuser/桌面/BX/HC/my_ai_popup_project

```
my_ai_popup_project/
├── api/                        # API目录 (新增)
│   ├── README.md               # API说明文档
│   ├── frontend/               # 前端API调用
│   │   └── api.js              # 前端统一API封装
│   ├── backend/                # 后端路由 (从web移动)
│   │   ├── README.md           # 后端说明
│   │   ├── routes.py           # 路由定义
│   │   ├── routes.md           # 路由文档
│   │   ├── app.py              # Flask应用主程序
│   │   ├── config_manager.py   # 配置管理
│   │   ├── deployment_monitor.py
│   │   ├── entry.py
│   │   ├── script_manager.py
│   │   ├── security.py
│   │   ├── socket_events.py
│   │   ├── system_monitor.py
│   │   └── web_monitor.py
│   ├── mapping/                # API映射文档
│   │   ├── api_mapping.json    # API映射JSON配置
│   │   └── api_mapping.md      # API映射说明
│   └── config/                 # API配置
│       └── api_config.json     # API配置参数
│
├── web/                        # Web前端目录 (精简)
│   ├── README.md               # Web说明文档 (更新)
│   ├── requirements.txt        # Python依赖
│   ├── __init__.py             # 包标识
│   ├── start_monitor.py        # 唯一入口脚本 (保留)
│   ├── static/                 # 静态资源 (保留)
│   │   ├── css/                # 样式文件
│   │   ├── js/                 # JavaScript文件
│   │   └── templates/          # HTML模板
│   └── templates/              # 模板文件 (保留)
│       ├── dashboard.html
│       ├── base.html
│       └── components/
│
├── scripts/                    # 自动化脚本 (已整理)
│   ├── SCRIPTS_INDEX.md        # 目录索引文档
│   ├── config/                 # 配置脚本
│   ├── core/                   # 核心脚本
│   ├── deploy/                 # 部署脚本
│   ├── health/                 # 健康检查
│   ├── health_monitor/         # 健康监控
│   ├── start/                  # 启动脚本 (新增)
│   │   ├── README.md
│   │   ├── main_launcher.py
│   │   ├── start_backend_simple.py
│   │   ├── start_gui_py.py
│   │   ├── start_hot_window.sh
│   │   └── unified_launcher.py
│   ├── test/                   # 测试脚本
│   ├── utils/                  # 工具脚本
│   ├── verify/                 # 验证脚本 (新增)
│   │   ├── README.md
│   │   ├── verify_venv.py
│   │   └── verify_paths.py
│   └── __init__.py
│
├── src/                        # 核心源码
├── assets/                     # 资源文件
├── docs/                       # 项目文档
├── rules/                      # 规则配置
├── logs/                       # 日志文件
├── models/                     # AI模型
├── output/                     # 输出目录
├── tests/                      # 测试模块
│
├── project_config.json         # 项目配置
├── README.md                   # 项目说明
├── requirements.txt            # Python依赖
└── start.sh                    # 启动脚本
```

## 目录功能说明

### api/ - API目录 (新增)

**功能**: 集中管理所有前后端 API 调用逻辑

- **frontend/**: 前端 JavaScript API 封装
- **backend/**: 后端 Python 路由和业务逻辑
- **mapping/**: API 映射文档和 JSON 配置
- **config/**: API 相关配置参数

### web/ - Web前端目录 (精简)

**功能**: 仅保留前端静态资源和入口脚本

- **static/**: CSS、JavaScript、图片等静态资源
- **templates/**: HTML 模板文件
- **start_monitor.py**: 唯一的启动入口
- **requirements.txt**: Python 依赖声明

### scripts/ - 自动化脚本目录 (已整理)

**功能**: 系统级的自动化健康监测和运行脚本

| 子目录          | 功能            |
| --------------- | --------------- |
| config/         | 配置相关脚本    |
| core/           | 核心功能脚本    |
| deploy/         | 部署相关脚本    |
| health/         | 健康检查脚本    |
| health_monitor/ | 健康监控脚本    |
| start/          | 启动脚本 (新增) |
| test/           | 测试脚本        |
| utils/          | 工具脚本        |
| verify/         | 验证脚本 (新增) |

## 启动方式

### 方式1: 使用Web监控中心 (推荐)

```bash
cd /home/vboxuser/桌面/BX/HC/my_ai_popup_project
python web/start_monitor.py
# 访问 http://localhost:8080
```

### 方式2: 使用统一启动器

```bash
python scripts/start/unified_launcher.py --mode all
```

### 方式3: 直接启动后端

```bash
# 方式A: 从web目录
python web/start_monitor.py --host 0.0.0.0 --port 8080

# 方式B: 从api目录
python -m api.backend.app --host 0.0.0.0 --port 8080
```

## 文件移动说明

### 从 web/ 移动到 api/backend/

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

### 新增目录

- **api/**: API 调用逻辑和文档
- **scripts/start/**: 启动脚本集合
- **scripts/verify/**: 验证脚本集合

---

_更新时间: 2026-01-19_
_版本: 2.0.0_
