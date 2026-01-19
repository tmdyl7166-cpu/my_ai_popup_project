# API 映射说明

## 概述

本文档描述项目中所有 API 端点的映射关系，包括请求格式、响应格式和调用示例。

## 基础信息

- **Base URL**: `http://localhost:8080`
- **协议**: HTTP / WebSocket
- **认证**: Bearer Token (可选)

## REST API

### 健康检查

**端点**: `GET /api/health`

**响应**:

```json
{
  "status": "ok",
  "timestamp": "2026-01-19T12:00:00Z",
  "version": "1.0.0"
}
```

### 项目状态

**端点**: `GET /api/project/status`

**响应**:

```json
{
  "status": "ok",
  "modules": {
    "total": 22,
    "running": 20,
    "stopped": 2
  },
  "scripts": {
    "total": 15,
    "running": 5,
    "idle": 10
  }
}
```

### 脚本管理

**获取脚本列表**:

```
GET /api/scripts/list
```

**获取脚本状态**:

```
GET /api/scripts/status
```

**运行脚本**:

```
POST /api/scripts/run/{name}
```

**停止脚本**:

```
POST /api/scripts/stop/{name}
```

### 系统资源

**获取系统资源**:

```
GET /api/system/resources
```

**响应示例**:

```json
{
  "cpu": {
    "usage": 45.2,
    "cores": 8
  },
  "memory": {
    "total": 16384,
    "used": 8192,
    "usage": 50.0
  },
  "disk": {
    "total": 512000,
    "used": 256000,
    "usage": 50.0
  }
}
```

### GPU资源

**端点**: `GET /api/system/gpu`

**响应示例**:

```json
{
  "gpu": {
    "name": "NVIDIA GeForce RTX 3080",
    "memory": {
      "total": 10737418240,
      "used": 2147483648,
      "usage": 20.0
    },
    "utilization": 35,
    "temperature": 65
  }
}
```

### 性能监控

**获取性能指标**:

```
GET /api/performance/metrics
```

**执行性能优化**:

```
POST /api/performance/optimize
```

### 视频流

**端点**: `GET /api/video`

**响应示例**:

```json
{
  "cameras": [
    {
      "id": "camera_0",
      "name": "Integrated Camera",
      "status": "active"
    }
  ],
  "streams": [
    {
      "id": "stream_0",
      "camera": "camera_0",
      "fps": 30,
      "resolution": "1920x1080"
    }
  ]
}
```

### 引擎管理

**获取引擎列表**:

```
GET /api/engines
```

**响应示例**:

```json
{
  "engines": [
    {
      "name": "deep_live_cam",
      "status": "running",
      "version": "1.0.0"
    },
    {
      "name": "facefusion",
      "status": "idle",
      "version": "2.0.0"
    }
  ]
}
```

**启动引擎**:

```
POST /api/engines/{name}/start
```

**停止引擎**:

```
POST /api/engines/{name}/stop
```

## WebSocket API

### 连接

```
ws://localhost:8080/ws
```

### 消息类型

| 类型      | 说明     |
| --------- | -------- |
| heartbeat | 心跳消息 |
| progress  | 进度更新 |
| log       | 日志消息 |
| data      | 数据更新 |

### 订阅

```javascript
// 订阅进度更新
ws.send(
  JSON.stringify({
    type: "subscribe",
    channel: "progress",
    taskId: "task_123",
  }),
);

// 订阅日志
ws.send(
  JSON.stringify({
    type: "subscribe",
    channel: "log",
    taskId: "task_123",
  }),
);
```

---

_创建时间: 2026-01-19_
