# API目录结构

> **全局统一API调用映射目录** - 包含对整个项目所有子项目的调用

## 目录结构

```
api/
├── README.md              # 本说明文档 ⭐
├── config/
│   └── api_config.json    # API配置参数
├── frontend/
│   └── api.js             # 前端统一API封装
├── backend/               # API后端服务 ⭐
│   ├── app.py             # FastAPI应用主程序
│   ├── routes.py          # 路由定义
│   ├── routes.md          # 路由文档
│   ├── config_manager.py  # 配置管理
│   ├── deployment_monitor.py
│   ├── entry.py
│   ├── script_manager.py
│   ├── security.py
│   ├── socket_events.py
│   ├── system_monitor.py
│   ├── web_monitor.py
│   └── README.md          # 后端服务说明
└── mapping/
    ├── api_mapping.json   # API端点映射JSON配置 ⭐
    └── api_mapping.md     # API接口说明文档
```

## 功能概述

### 1. 后端服务 (backend/)

**职责**: FastAPI后端服务，提供所有API接口实现

**入口**: `app.py`

**依赖**: src、scripts、assets

**组件**:

- `app.py` - FastAPI应用主程序
- `routes.py` - 路由定义
- `config_manager.py` - 配置管理
- `deployment_monitor.py` - 部署监控
- `script_manager.py` - 脚本管理
- `security.py` - 安全模块
- `socket_events.py` - WebSocket事件
- `system_monitor.py` - 系统监控
- `web_monitor.py` - Web监控

### 2. 前端API封装 (frontend/)

**职责**: 前端JavaScript API封装，提供统一调用接口

**入口**: `api.js`

**使用方式**:

```javascript
// 统一API调用
API.get("/api/health").then((data) => {
  console.log("系统健康:", data);
});

// 启动引擎
API.post("/api/engines/deep_live_cam/start", {
  params: { device: "cuda" },
});

// WebSocket订阅
const ws = new WebSocket("ws://localhost:8080/ws");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("收到消息:", data);
};
```

### 3. API映射配置 (mapping/)

**职责**: 定义和维护API接口规范

**文件**:

- `api_mapping.json` - API端点映射JSON配置
- `api_mapping.md` - API接口说明文档

### 4. API配置 (config/)

**职责**: 管理API配置

**文件**: `api_config.json`

## 完整API端点清单

### 系统管理

| 端点                  | 方法 | 说明         |
| --------------------- | ---- | ------------ |
| `/api/health`         | GET  | 系统健康检查 |
| `/api/project/status` | GET  | 项目整体状态 |
| `/api/ports`          | GET  | 端口状态列表 |

### 脚本管理

| 端点                              | 方法 | 说明               |
| --------------------------------- | ---- | ------------------ |
| `/api/scripts/list`               | GET  | 获取脚本列表       |
| `/api/scripts/status`             | GET  | 获取脚本运行状态   |
| `/api/scripts/run/{script_name}`  | POST | 执行指定脚本       |
| `/api/scripts/stop/{script_name}` | POST | 停止正在运行的脚本 |

### 日志管理

| 端点                      | 方法 | 说明                   |
| ------------------------- | ---- | ---------------------- |
| `/api/logs/{script_name}` | GET  | 获取指定脚本的执行日志 |
| `/api/audit/logs`         | GET  | 审计日志查询           |
| `/api/audit/export`       | GET  | 审计日志导出           |

### 配置管理

| 端点                      | 方法 | 说明         |
| ------------------------- | ---- | ------------ |
| `/api/config/{component}` | GET  | 获取组件配置 |
| `/api/config/{component}` | POST | 更新组件配置 |

### 系统资源

| 端点                    | 方法 | 说明             |
| ----------------------- | ---- | ---------------- |
| `/api/system/resources` | GET  | 系统资源使用情况 |
| `/api/system/gpu`       | GET  | GPU资源使用情况  |

### 子项目

| 端点                       | 方法 | 说明         |
| -------------------------- | ---- | ------------ |
| `/api/subprojects`         | GET  | 子项目状态   |
| `/api/deployment/progress` | GET  | 项目部署进度 |

### 数据监控

| 端点                   | 方法 | 说明             |
| ---------------------- | ---- | ---------------- |
| `/api/bubbles`         | GET  | 实时冒泡数据     |
| `/api/bubbles/history` | GET  | 获取历史冒泡记录 |

### 性能监控

| 端点                        | 方法 | 说明         |
| --------------------------- | ---- | ------------ |
| `/api/performance`          | GET  | 性能监控概览 |
| `/api/performance/metrics`  | GET  | 性能指标数据 |
| `/api/performance/optimize` | POST | 性能优化执行 |

### 视频处理

| 端点                 | 方法 | 说明       |
| -------------------- | ---- | ---------- |
| `/api/video`         | GET  | 视频流概览 |
| `/api/video/cameras` | GET  | 摄像头设备 |
| `/api/video/streams` | GET  | 视频流数据 |
| `/api/video/engines` | GET  | 引擎状态   |

### 引擎管理

| 端点                         | 方法 | 说明     |
| ---------------------------- | ---- | -------- |
| `/api/engines`               | GET  | 引擎列表 |
| `/api/engines/{name}/status` | GET  | 引擎状态 |
| `/api/engines/{name}/start`  | POST | 启动引擎 |
| `/api/engines/{name}/stop`   | POST | 停止引擎 |

### 备份管理

| 端点                              | 方法 | 说明         |
| --------------------------------- | ---- | ------------ |
| `/api/backup`                     | GET  | 获取备份列表 |
| `/api/backup/create`              | POST | 创建新备份   |
| `/api/backup/restore/{backup_id}` | POST | 从备份恢复   |

## WebSocket API

### 连接地址

```
ws://localhost:8080/ws
```

### 订阅频道

| 频道            | 说明     |
| --------------- | -------- |
| `progress`      | 进度更新 |
| `log`           | 日志消息 |
| `data`          | 数据更新 |
| `heartbeat`     | 心跳检测 |
| `status_update` | 状态更新 |

## 与其他模块的关系

```
api/
 ├── frontend/  → web/  (前端静态资源)
 ├── backend/   → src/backend/  (后端服务)
 ├── mapping/   → docs/  (接口文档)
 └── config/    → project_config.json  (配置)
```

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

## 相关文档

- API详细文档: `api/mapping/api_mapping.md`
- API映射配置: `api/mapping/api_mapping.json`
- 项目配置: `project_config.json`
- Web监控中心: `web/`
- [项目架构设计](../../docs/project_docs/01-project-architecture.md)
- [API接口文档](../../docs/project_docs/04-frontend-backend-api.md)

---

_创建时间: 2026-01-19_
_最后更新: 2026-01-21_
_版本: 2.0.0_
