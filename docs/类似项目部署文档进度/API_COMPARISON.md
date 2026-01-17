# API文件对比分析

> **分析日期**: 2025-01-21  
> **对比文件**: `api.py` vs `unified_api.py`

## 端点对比

### 共同端点 (存在于两个文件)

| 端点 | 方法 | 说明 | 状态 |
|------|------|------|------|
| `/health` | GET | 健康检查 | ✅ |
| `/api/auth/login` | POST | 用户登录 | ✅ |
| `/api/auth/logout` | POST | 用户登出 | ✅ |
| `/api/auth/me` | GET | 当前用户 | ✅ |
| `/api/auth/status` | GET | 认证状态 | ✅ |
| `/api/auth/refresh` | POST | 刷新会话 | ✅ |
| `/api/tasks` | GET | 列出任务 | ✅ |
| `/api/tasks` | POST | 创建任务 | ✅ |
| `/api/tasks/{id}` | GET | 任务详情 | ✅ |
| `/api/tasks/{id}/execute` | POST | 执行任务 | ✅ |
| `/api/tasks/stats` | GET | 任务统计 | ✅ |
| `/api/frame/process` | POST | 处理帧 | ✅ |
| `/api/strategy/generate` | POST | AI策略生成 | ✅ |
| `/api/status` | GET | 系统状态 | ✅ |
| `/api/status/performance` | GET | 性能统计 | ✅ |
| `/api/faces/detect` | POST | 检测人脸 | ✅ |
| `/api/faces/known` | GET | 列出已知人脸 | ✅ |
| `/api/faces/known` | POST | 添加已知人脸 | ✅ |
| `/api/db/performance` | GET | 数据库日志 | ✅ |

### 仅在 api.py 中

| 端点 | 方法 | 说明 | 处理建议 |
|------|------|------|----------|
| `/api/config` | GET | 获取配置 | ✅ 需要迁移 |
| `/api/config` | POST | 更新配置 | ✅ 需要迁移 |

### 仅在 unified_api.py 中

| 端点 | 方法 | 说明 | 处理建议 |
|------|------|------|----------|
| `/web/api/status` | GET | 监控状态 | ✅ 保留在统一API |
| `/web/api/realtime-status` | GET | 实时状态 | ✅ 保留 |
| `/web/api/history` | GET | 历史数据 | ✅ 保留 |
| `/web/api/full-status` | GET | 完整状态 | ✅ 保留 |
| `/web/api/run_check` | POST | 运行检查 | ✅ 保留 |
| `/web/api/dependencies` | GET | 依赖状态 | ✅ 保留 |
| `/web/api/system` | GET | 系统资源 | ✅ 保留 |
| `/web/api/processes` | GET | 进程状态 | ✅ 保留 |
| `/web/api/business` | GET | 业务模块 | ✅ 保留 |
| `/web/api/output` | GET | 输出模块 | ✅ 保留 |
| `/web/api/engines` | GET | 引擎详情 | ✅ 保留 |
| `/web/api/summary` | GET | 摘要 | ✅ 保留 |
| `/web/api/layers` | GET | 项目层级 | ✅ 保留 |
| `/web/api/structure` | GET | 项目结构 | ✅ 保留 |
| `/api/camera/status` | GET | 摄像头状态 | ✅ 保留 |
| `/api/camera/start` | POST | 启动摄像头 | ✅ 保留 |
| `/api/camera/stop` | POST | 停止摄像头 | ✅ 保留 |
| `/api/camera/list` | GET | 摄像头列表 | ✅ 保留 |
| `/api/recognition/status` | GET | 识别状态 | ✅ 保留 |
| `/api/recognition/detect` | POST | 检测人脸 | ✅ 保留 |
| `/api/recognition/compose` | POST | 图片合成 | ✅ 保留 |
| `/api/video/status` | GET | 视频状态 | ✅ 保留 |
| `/api/video/compose` | POST | 视频合成 | ✅ 保留 |
| `/api/video/extract_frame` | POST | 提取帧 | ✅ 保留 |
| `/api/ar/engines` | GET | AR引擎列表 | ✅ 保留 |
| `/api/ar/start` | POST | 启动AR引擎 | ✅ 保留 |
| `/api/ar/stop` | POST | 停止AR引擎 | ✅ 保留 |
| `/api/live/status` | GET | 直播状态 | ✅ 保留 |
| `/api/live/config` | GET | 直播配置 | ✅ 保留 |
| `/api/live/config` | POST | 设置直播配置 | ✅ 保留 |
| `/api/live/start` | POST | 开始直播 | ✅ 保留 |
| `/api/live/stop` | POST | 停止直播 | ✅ 保留 |

## 差异分析

### 导入差异

**api.py 导入:**
```python
from backend.database.db import get_db
from backend.control_core.auth import (...)
from backend.control_core.user_session import (...)
from backend.control_core.state_manager import StateManager
from backend.services.performance_monitor import create_performance_monitor
from backend.services.face_detection import create_face_detector
from backend.services.task_scheduler import create_task_scheduler
from backend.services.local_ai_interface import create_local_ai_interface
from backend.services.video_pipeline import create_video_pipeline
from backend.models import (...)
```

**unified_api.py 导入:**
```python
from backend.database.db import get_db
from backend.control_core.auth import (...)
from backend.control_core.user_session import (...)
from backend.control_core.state_manager import StateManager
from backend.services.video_compositor import create_video_compositor  # 新增
from backend.services.recognition_service import create_recognition_service  # 新增
from backend.services.camera_service import create_camera_manager  # 新增
from backend.services.performance_monitor import create_performance_monitor
from backend.services.face_detection import create_face_detector
from backend.services.task_scheduler import create_task_scheduler
from backend.services.local_ai_interface import create_local_ai_interface
from backend.services.video_pipeline import create_video_pipeline
from backend.models import (...)
from backend.path_utils import get_project_root  # 新增
import psutil, GPUtil  # 新增
```

### 架构差异

**api.py:**
- 单一FastAPI应用
- 所有端点直接注册到app

**unified_api.py:**
- 多个APIRouter分组
- 支持子路由:
  - `api_router` - 业务API
  - `monitor_router` - 监控API (前缀 /web)
  - `info_router` - 项目信息API (前缀 /web)
  - `camera_router` - 摄像头API
  - `recognition_router` - 识别API
  - `video_router` - 视频API
  - `ar_router` - AR引擎API
  - `live_router` - 直播API

### 监控数据差异

**api.py:**
- 简单状态获取

**unified_api.py:**
- 完整的 `monitor_data` 字典
- 包含依赖检查、系统检查、进程检查、业务检查、输出检查
- 支持实时数据收集

## 合并策略

### 最终统一API结构

```
unified_api.py
├── app = FastAPI()
├── api_router (业务API)
│   ├── /health
│   ├── /api/auth/*
│   ├── /api/status
│   ├── /api/tasks
│   ├── /api/frame/process
│   ├── /api/strategy/generate
│   ├── /api/config  ← 从 api.py 迁移
│   ├── /api/faces/*
│   └── /api/db/*
├── monitor_router (/web前缀)
│   ├── /api/status
│   ├── /api/realtime-status
│   ├── /api/history
│   ├── /api/full-status
│   └── ... (所有监控端点)
├── info_router (/web前缀)
│   ├── /api/layers
│   └── /api/structure
├── camera_router (/api前缀)
│   ├── /camera/status
│   ├── /camera/start
│   ├── /camera/stop
│   └── /camera/list
├── recognition_router (/api前缀)
│   ├── /recognition/status
│   ├── /recognition/detect
│   └── /recognition/compose
├── video_router (/api前缀)
│   ├── /video/status
│   ├── /video/compose
│   └── /video/extract_frame
├── ar_router (/api前缀)
│   ├── /ar/engines
│   ├── /ar/start
│   └── /ar/stop
└── live_router (/api前缀)
    ├── /live/status
    ├── /live/config
    ├── /live/start
    └── /live/stop
```

---

*最后更新: 2025-01-21*

