# API接口文档

> 本文档描述夜灵AR多功能合成软件的前后端API接口规范。

## 📡 API 概述

### 基础信息

| 项目 | 值 |
|------|-----|
| API 版本 | v1 |
| 基础路径 | `/api/v1` |
| WebSocket | `ws://host:port/ws` |
| 响应格式 | JSON |
| 认证方式 | 无 (本地应用) |

### 响应格式

#### 成功响应

```json
{
    "success": true,
    "status": "success",
    "data": { ... },
    "message": "操作成功",
    "timestamp": "2026-01-19T12:00:00Z"
}
```

#### 错误响应

```json
{
    "success": false,
    "status": "error",
    "error": "ERROR_CODE",
    "message": "用户友好的错误描述",
    "details": "详细错误信息",
    "timestamp": "2026-01-19T12:00:00Z"
}
```

## 🏥 系统管理

### 健康检查

**GET** `/api/health`

返回系统健康状态。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "timestamp": "2026-01-19T12:00:00Z",
        "version": "1.0.0",
        "services": {
            "api": "running",
            "database": "connected",
            "gpu": "available"
        }
    }
}
```

### 项目状态

**GET** `/api/project/status`

返回项目整体状态。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "project_name": "夜灵AR多功能合成软件",
        "version": "1.0.0",
        "status": "running",
        "components": {
            "frontend": "ready",
            "backend": "running",
            "ai": "ready",
            "processing": "idle"
        },
        "health_score": 95,
        "last_updated": "2026-01-19T12:00:00Z"
    }
}
```

### 系统资源

**GET** `/api/system/resources`

返回系统资源使用情况。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "cpu_percent": 45.5,
        "memory": {
            "total": 16777216000,
            "available": 8593982464,
            "percent": 48.7,
            "used": 8183234560
        },
        "disk": {
            "total": 512105157888,
            "free": 256052578816,
            "percent": 50.0,
            "used": 256052579072
        },
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### GPU 资源

**GET** `/api/system/gpu`

返回GPU资源使用情况。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "success",
        "has_gpu": true,
        "gpus": [
            {
                "name": "NVIDIA GeForce RTX 3080",
                "memory_total": 10737418240,
                "memory_used": 3221225472,
                "memory_percent": 30.0,
                "utilization": 45,
                "temperature": 65
            }
        ],
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

## 📜 脚本管理

### 脚本列表

**GET** `/api/scripts/list`

返回所有可用脚本列表。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "scripts": [
            {
                "name": "health_monitor.py",
                "description": "系统健康监控脚本",
                "category": "health_monitor",
                "enabled": true
            },
            {
                "name": "deploy.sh",
                "description": "部署脚本",
                "category": "deploy",
                "enabled": true
            }
        ],
        "total": 15,
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 脚本状态

**GET** `/api/scripts/status`

返回所有脚本的运行状态。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "scripts": {
            "health_monitor.py": {
                "status": "running",
                "pid": 1234,
                "start_time": "2026-01-19T10:00:00Z",
                "memory_usage": "150MB"
            },
            "config_validator.py": {
                "status": "idle"
            }
        },
        "monitoring_active": true,
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 执行脚本

**POST** `/api/scripts/run/{script_name}`

执行指定脚本。

**参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| script_name | string | 是 | 脚本名称 |
| args | array | 否 | 脚本参数 |
| timeout | number | 否 | 超时时间(秒) |

**请求示例**:

```json
{
    "args": ["--verbose", "--check"],
    "timeout": 300
}
```

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "started",
        "message": "脚本已启动",
        "script": "health_monitor.py",
        "pid": 1234,
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 停止脚本

**POST** `/api/scripts/stop/{script_name}`

停止正在运行的脚本。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "stopped",
        "message": "脚本已停止",
        "script": "health_monitor.py",
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

## ⚙️ 配置管理

### 获取配置

**GET** `/api/config/{component}`

获取指定组件的配置。

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| component | string | 组件名称 (project/scripts/web/api) |

**响应示例**:

```json
{
    "success": true,
    "data": {
        "component": "project",
        "config": {
            "paths": { ... },
            "entryPoints": { ... }
        },
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 更新配置

**POST** `/api/config/{component}`

更新指定组件的配置。

**请求体**:

```json
{
    "config": {
        "paths": {
            "projectRoot": "./new_path"
        }
    }
}
```

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "updated",
        "message": "配置已更新",
        "component": "project",
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

## 📊 部署进度

### 获取部署进度

**GET** `/api/deployment/progress`

返回项目部署进度。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "overall_progress": 75,
        "components": {
            "dependencies": { "progress": 100, "status": "completed" },
            "configuration": { "progress": 80, "status": "in_progress" },
            "testing": { "progress": 60, "status": "in_progress" }
        },
        "last_updated": "2026-01-19T12:00:00Z"
    }
}
```

## 🎥 视频处理

### 视频流概览

**GET** `/api/video`

返回视频流概览。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "overview": {
            "cameraCount": 1,
            "activeStreams": 1,
            "engineCount": 3,
            "avgFps": 25.0
        },
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 摄像头列表

**GET** `/api/video/cameras`

返回可用的摄像头设备列表。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "cameras": [
            {
                "id": 0,
                "name": "USB Camera",
                "resolution": "1920x1080",
                "fps": 30,
                "status": "available"
            }
        ],
        "total": 1,
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 引擎状态

**GET** `/api/video/engines`

返回视频处理引擎状态。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "engines": [
            {
                "name": "deep-live-cam",
                "status": "ready",
                "version": "1.0.0",
                "priority": 1
            },
            {
                "name": "facefusion",
                "status": "ready",
                "version": "2.0.0",
                "priority": 2
            }
        ],
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 启动引擎

**POST** `/api/engines/{name}/start`

启动指定引擎。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "started",
        "message": "引擎已启动",
        "engine": "deep-live-cam",
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 停止引擎

**POST** `/api/engines/{name}/stop`

停止指定引擎。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "stopped",
        "message": "引擎已停止",
        "engine": "deep-live-cam",
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

## 📝 日志管理

### 获取脚本日志

**GET** `/api/logs/{script_name}`

获取指定脚本的执行日志。

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| script_name | string | 脚本名称 |
| lines | number | 返回行数 (默认100) |

**响应示例**:

```json
{
    "success": true,
    "data": {
        "status": "success",
        "logs": [
            {
                "timestamp": "2026-01-19T12:00:00Z",
                "level": "INFO",
                "message": "脚本启动"
            }
        ],
        "total_lines": 150,
        "returned_lines": 100,
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 审计日志

**GET** `/api/audit/logs`

获取审计日志。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "logs": [
            {
                "id": 1,
                "action": "script_run",
                "user": "system",
                "details": "执行脚本: health_monitor.py",
                "timestamp": "2026-01-19T12:00:00Z"
            }
        ],
        "total": 50,
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

## 📈 性能监控

### 性能概览

**GET** `/api/performance`

返回性能监控概览。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "overview": {
            "total_requests": 1500,
            "avg_response_time": 45.2,
            "error_rate": 0.5,
            "throughput": 25.0,
            "active_connections": 3
        },
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

### 性能指标

**GET** `/api/performance/metrics`

返回详细的性能指标数据。

**响应示例**:

```json
{
    "success": true,
    "data": {
        "metrics": {
            "response_time": {
                "avg": 45.2,
                "p95": 120.0,
                "p99": 200.0
            },
            "memory_usage": {
                "current": "2.5GB",
                "peak": "3.2GB"
            },
            "cpu_usage": {
                "current": 45.0,
                "peak": 78.0
            },
            "active_connections": 3
        },
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

## 🔌 WebSocket API

### 连接

```
ws://localhost:8080/ws
```

### 订阅频道

| 频道 | 描述 | 数据类型 |
|------|------|----------|
| progress | 任务进度更新 | JSON |
| log | 日志消息 | JSON |
| data | 数据更新 | JSON |
| heartbeat | 心跳检测 | JSON |
| status_update | 状态更新 | JSON |

### 消息格式

**进度更新**:

```json
{
    "channel": "progress",
    "data": {
        "task_id": "task_001",
        "progress": 45,
        "message": "处理中...",
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

**日志消息**:

```json
{
    "channel": "log",
    "data": {
        "script": "health_monitor.py",
        "level": "INFO",
        "message": "健康检查完成",
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

**心跳**:

```json
{
    "channel": "heartbeat",
    "data": {
        "status": "alive",
        "timestamp": "2026-01-19T12:00:00Z"
    }
}
```

## 📝 文档版本

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| 1.0 | 2026-01-19 | 初始版本 |

## 🔗 相关文档

- [项目整体架构设计](01-project-architecture.md)
- [系统运行时逻辑流程](02-runtime-logic.md)
- [依赖和配置说明](03-dependencies-config.md)
- [自动化脚本说明](05-automation-scripts.md)
