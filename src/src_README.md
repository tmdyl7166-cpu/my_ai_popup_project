# 核心源码模块 (src/)

## 概述

`src/` 文件夹包含了AI弹窗项目的核心源码，按照分层架构组织为多个功能模块。

## 模块结构

### frontend/ - 前端用户UI模块
```
frontend/
├── __init__.py                    # 模块初始化文件
├── frontend_config.json          # 前端界面配置定义文件
├── frontend_README.md            # 前端模块说明文档
├── main_window.py                # 主窗口类（计划中）
├── popup_window.py               # 弹窗窗口类（计划中）
├── components/                   # UI组件目录
│   └── progress_bar.py           # 进度条组件
├── styles/                       # 样式定义目录
│   └── __init__.py               # 样式模块初始化
```
- **职责**: PyQt5图形界面，用户交互和界面展示
- **主要文件**: `main_window.py`, `popup_window.py`, `components/progress_bar.py`
- **依赖**: backend, config

### backend/ - 后端服务模块
```
backend/
├── __init__.py                    # 模块初始化文件
├── backend_config.json           # 后端服务配置定义文件
├── backend_README.md             # 后端模块说明文档
├── api_server.py                # API服务器（FastAPI）
├── task_manager.py               # 任务管理器
├── scheduler.py                  # 任务调度器
├── entry.py                      # 后端服务入口
├── control_core/                 # 控制核心目录
│   ├── __init__.py
│   ├── pipeline_manager.py       # 管道管理器
│   ├── server.py                 # 服务器核心
│   └── state_manager.py          # 状态管理器
├── middleware/                   # 中间件目录
│   ├── logging_middleware.py     # 日志中间件
│   └── ...                       # 其他中间件
└── services/                     # 服务目录
    ├── __init__.py
    ├── async_pipeline.py         # 异步管道服务
    └── ...                       # 其他服务
```
- **职责**: FastAPI后端服务，任务管理、调度、API接口
- **主要文件**: `api_server.py`, `task_manager.py`, `scheduler.py`
- **依赖**: ai, processing, utils

### ai/ - AI模块
```
ai/
├── __init__.py                    # 模块初始化文件
├── ai_config.json                # AI模块配置定义文件
├── ai_README.md                  # AI模块说明文档
├── ollama_client.py              # Ollama客户端
├── analyzers/                    # 分析器子模块
├── face_recognition/             # 人脸识别子模块
└── processors/                   # 处理器子模块
```
- **职责**: AI推理和处理，Ollama客户端、人脸识别
- **主要文件**: `ollama_client.py`, `face_recognition/`, `processors/`
- **依赖**: config, integrations, utils

### processing/ - 处理模块
```
processing/
├── __init__.py                    # 模块初始化文件
├── processing_config.json        # 处理引擎配置定义文件
├── processing_README.md          # 处理模块说明文档
├── batch_processor.py            # 批量处理核心类
├── engines/                      # 引擎集成目录
├── pipelines/                    # 处理管道目录
└── utils/                        # 工具函数目录
```
- **职责**: 媒体处理引擎，图片/视频处理、批量处理
- **主要文件**: `batch_processor.py`, `engines/`, `pipelines/`
- **依赖**: ai, utils, integrations

### integrations/ - 集成模块
```
integrations/
├── __init__.py                    # 模块初始化文件
├── integrations_config.json      # 第三方集成配置定义文件
├── integrations_README.md        # 集成模块说明文档
├── engine_manager.py             # 引擎管理器
├── resource_allocator.py         # 资源分配器
├── engines/                      # 引擎封装目录
├── adapters/                     # 适配器目录
├── monitors/                     # 监控目录
└── utils/                        # 工具目录
```
- **职责**: 第三方引擎集成，Deep-Live-Cam、FaceFusion等
- **主要文件**: `engine_manager.py`, `engines/`, `adapters/`
- **依赖**: utils

### utils/ - 工具模块
```
utils/
├── __init__.py                    # 模块初始化文件
├── utils_config.json             # 工具模块配置定义文件
├── utils_README.md               # 工具模块说明文档
├── logger.py                     # 日志记录工具类
├── file_utils.py                 # 文件操作工具类
├── image_utils.py                # 图片处理工具类
├── video_utils.py                # 视频处理工具类
├── thread_utils.py               # 线程管理工具类
└── path_resolver.py              # 路径解析工具类
```
- **职责**: 通用工具函数，文件操作、日志、线程管理
- **主要文件**: `file_utils.py`, `video_utils.py`, `logger.py`, `path_resolver.py`
- **依赖**: 无

### config/ - 配置模块
```
config/
├── __init__.py                    # 模块初始化文件
├── config_config.json            # 配置模块配置定义文件
├── config_README.md              # 配置模块说明文档
└── app_config.py                 # 应用配置管理类
```
- **职责**: 应用配置管理，环境变量、设置加载
- **主要文件**: `app_config.py`
- **依赖**: 无

## 依赖关系

```
frontend → backend → ai → processing → integrations
    ↓         ↓       ↓         ↓
  config    utils   config    utils
                      ↓
                    utils
```

## 入口点

- `main.py` - 主入口文件
- `frontend/main_window.py` - GUI启动入口
- `backend/api_server.py` - API服务启动入口
- `cli.py` - 命令行接口入口

## 开发指南

### 环境要求
- Python >= 3.10
- 依赖包见 `../requirements.txt`

### 运行方式
```bash
# GUI模式
python src/frontend/main_window.py

# API模式
python src/backend/api_server.py

# CLI模式
python src/cli.py
```

### 代码规范
- 遵循PEP 8编码规范
- 使用类型提示
- 所有模块必须有 `__all__` 导出列表
- 文档字符串使用Google风格

### 测试
```bash
# 运行所有测试
pytest ../tests/

# 运行特定模块测试
pytest ../tests/test_backend/
```

## 注意事项

1. **单向依赖**: 严格遵循分层架构，禁止反向依赖
2. **接口契约**: 模块间通过明确定义的接口通信
3. **错误处理**: 统一的异常处理和日志记录
4. **性能监控**: 关键路径需要性能监控和优化

## 扩展开发

新增功能时请：
1. 确定所属模块层级
2. 遵循依赖关系原则
3. 更新相应的配置文件
4. 添加单元测试
5. 更新文档
