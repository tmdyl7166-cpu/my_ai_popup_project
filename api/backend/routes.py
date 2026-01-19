# API Backend Routes - 后端路由定义

## 路由清单

### 系统健康
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/health | GET | 系统健康检查 | `health()` |
| /api/project/status | GET | 项目整体状态 | `project_status()` |

### 脚本管理
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/scripts/list | GET | 获取脚本列表 | `scripts_list()` |
| /api/scripts/status | GET | 获取脚本状态 | `scripts_status()` |
| /api/scripts/run/{name} | POST | 运行脚本 | `scripts_run()` |
| /api/scripts/stop/{name} | POST | 停止脚本 | `scripts_stop()` |

### 系统资源
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/system/resources | GET | 系统资源 | `system_resources()` |
| /api/system/gpu | GET | GPU资源 | `system_gpu()` |

### 端口管理
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/ports | GET | 端口状态 | `ports()` |

### 子项目
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/subprojects | GET | 子项目状态 | `subprojects()` |

### 冒泡数据
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/bubbles | GET | 实时冒泡 | `bubbles()` |

### 审计日志
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/audit/logs | GET | 审计日志 | `audit_logs()` |
| /api/audit/export | GET | 审计导出 | `audit_export()` |

### 性能监控
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/performance | GET | 性能概览 | `performance()` |
| /api/performance/metrics | GET | 性能指标 | `performance_metrics()` |
| /api/performance/optimize | POST | 性能优化 | `performance_optimize()` |

### 视频流
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/video | GET | 视频概览 | `video()` |
| /api/video/cameras | GET | 摄像头设备 | `video_cameras()` |
| /api/video/streams | GET | 视频流 | `video_streams()` |
| /api/video/engines | GET | 引擎状态 | `video_engines()` |

### 引擎管理
| 端点 | 方法 | 说明 | 处理函数 |
|------|------|------|----------|
| /api/engines | GET | 引擎列表 | `engines()` |
| /api/engines/{name}/status | GET | 引擎状态 | `engine_status()` |
| /api/engines/{name}/start | POST | 启动引擎 | `engine_start()` |
| /api/engines/{name}/stop | POST | 停止引擎 | `engine_stop()` |

---

*创建时间: 2026-01-19*

