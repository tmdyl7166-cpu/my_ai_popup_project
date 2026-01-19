# API目录结构

## 目录说明

### frontend/

前端 API 调用模块

- `api.js` - 前端统一 API 封装

### backend/

后端 API 路由和逻辑

- `routes.py` - Flask/FastAPI 路由定义

### mapping/

API 映射文档和配置

- `api_mapping.json` - API 映射 JSON 配置
- `api_mapping.md` - API 映射说明文档

### config/

API 相关配置

- `api_config.json` - API 配置参数

## API 端点清单

### 后端API (web/app.py)

| 端点                      | 方法 | 说明             |
| ------------------------- | ---- | ---------------- |
| /api/health               | GET  | 系统健康检查     |
| /api/project/status       | GET  | 项目整体状态     |
| /api/scripts/list         | GET  | 获取脚本列表     |
| /api/scripts/status       | GET  | 获取脚本运行状态 |
| /api/system/resources     | GET  | 系统资源使用情况 |
| /api/system/gpu           | GET  | GPU资源使用情况  |
| /api/ports                | GET  | 端口状态列表     |
| /api/subprojects          | GET  | 子项目状态       |
| /api/bubbles              | GET  | 实时冒泡数据     |
| /api/audit/logs           | GET  | 审计日志查询     |
| /api/audit/export         | GET  | 审计日志导出     |
| /api/performance          | GET  | 性能监控概览     |
| /api/performance/metrics  | GET  | 性能指标数据     |
| /api/performance/optimize | POST | 性能优化执行     |
| /api/video                | GET  | 视频流概览       |
| /api/video/cameras        | GET  | 摄像头设备       |
| /api/video/streams        | GET  | 视频流数据       |
| /api/video/engines        | GET  | 引擎状态         |
| /api/engines              | GET  | 引擎列表         |
| /api/engines/:name/status | GET  | 引擎状态         |
| /api/engines/:name/start  | POST | 启动引擎         |
| /api/engines/:name/stop   | POST | 停止引擎         |

## 使用方式

### 前端调用示例

```javascript
// 统一API调用
API.get("/api/health").then((data) => {
  console.log("系统健康:", data);
});

API.post("/api/engines/deep_live_cam/start", {
  params: { device: "cuda" },
});
```

### 后端路由注册

```python
from api.backend.routes import register_routes

register_routes(app)
```

---

_创建时间: 2026-01-19_
