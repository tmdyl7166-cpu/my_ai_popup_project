# 核心源码模块 (src/)

## 概述

`src/` 文件夹包含了AI弹窗项目的核心源码，按照分层架构组织为多个功能模块。

## 模块结构

### frontend/ - 前端用户UI模块

**职责**: PyQt5图形界面，用户交互和界面展示

**入口**: `main_window.py`

**依赖**: backend, config

**组件**:

- `main_window.py` - 主窗口类
- `popup_window.py` - 弹窗窗口类
- `components/` - UI组件目录
- `styles/` - 样式定义目录

### backend/ - 后端服务模块

**职责**: FastAPI后端服务，任务管理、调度、API接口

**入口**: `api_server.py`

**依赖**: ai, processing, utils

**组件**:

- `api_server.py` - API服务器（FastAPI）
- `task_manager.py` - 任务管理器
- `scheduler.py` - 任务调度器
- `control_core/` - 控制核心目录
- `middleware/` - 中间件目录
- `services/` - 服务目录

### ai/ - AI模块

**职责**: AI推理和处理，Ollama客户端、人脸识别

**入口**: `ollama_client.py`

**依赖**: config, integrations, utils

**组件**:

- `ollama_client.py` - Ollama客户端
- `analyzers/` - 分析器子模块
- `face_recognition/` - 人脸识别子模块
- `processors/` - 处理器子模块

### processing/ - 处理模块

**职责**: 媒体处理引擎，图片/视频处理、批量处理

**入口**: `batch_processor.py`

**依赖**: ai, utils, integrations

**组件**:

- `batch_processor.py` - 批量处理核心类
- `engines/` - 引擎集成目录
- `pipelines/` - 处理管道目录
- `utils/` - 工具函数目录

### integrations/ - 集成模块

**职责**: 第三方引擎集成，Deep-Live-Cam、FaceFusion等

**入口**: `__init__.py`

**依赖**: utils

**组件**:

- `engine_manager.py` - 引擎管理器
- `engines/` - 引擎封装目录
- `adapters/` - 适配器目录
- `monitors/` - 监控目录

### utils/ - 工具模块

**职责**: 通用工具函数，文件操作、日志、线程管理

**依赖**: 无

**组件**:

- `logger.py` - 日志记录工具类
- `file_utils.py` - 文件操作工具类
- `image_utils.py` - 图片处理工具类
- `video_utils.py` - 视频处理工具类
- `thread_utils.py` - 线程管理工具类
- `path_resolver.py` - 路径解析工具类

### config/ - 配置模块

**职责**: 应用配置管理，环境变量、设置加载

**依赖**: 无

**组件**:

- `app_config.py` - 应用配置管理类

## 依赖关系图

```
frontend → backend → ai → processing → integrations
    ↓         ↓       ↓         ↓
  config    utils   config    utils
                      ↓
                    utils
```

## 入口点

| 入口 | 文件 | 说明 |
|------|------|------|
| 主入口 | `main.py` | 程序主入口 |
| GUI入口 | `frontend/main_window.py` | GUI启动入口 |
| API入口 | `backend/api_server.py` | API服务启动入口 |
| CLI入口 | `cli.py` | 命令行接口入口 |

## 运行方式

```bash
# GUI模式
python src/frontend/main_window.py

# API模式
python src/backend/api_server.py

# CLI模式
python src/cli.py

# 使用统一启动器
python scripts/start/unified_launcher.py --mode all
```

## 代码规范

- 遵循PEP 8编码规范
- 使用类型提示（Type Hints）
- 所有模块必须有 `__all__` 导出列表
- 文档字符串使用Google风格

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

## 相关文档

- [项目架构设计](../../docs/project_docs/01-project-architecture.md)
- [运行时逻辑流程](../../docs/project_docs/02-runtime-logic.md)
- [依赖和配置说明](../../docs/project_docs/03-dependencies-config.md)

---

_创建时间: 2026-01-16_
_最后更新: 2026-01-19_
_版本: 2.0.0_
