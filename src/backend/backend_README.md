# 后端服务模块 (backend/)

## 概述

`backend/` 模块是整个系统的"心脏"，负责任务调度、API服务、状态管理和系统协调。

## 核心职责

1. **API网关**: 提供RESTful API接口
2. **任务管理**: 创建、调度、监控任务执行
3. **状态协调**: 维护系统状态和数据流转
4. **安全控制**: 请求验证、速率限制、权限控制

## 模块组成

### api_server.py - API服务器
- **框架**: FastAPI
- **功能**: REST API服务，WebSocket实时通信
- **路由**: `/api/v1/*`
- **中间件**: 日志、认证、CORS、速率限制

### task_manager.py - 任务管理器
- **功能**: 任务生命周期管理
- **特性**:
  - 任务创建、状态跟踪
  - 优先级队列管理
  - 超时和重试机制
  - 统计信息收集

### scheduler.py - 任务调度器
- **功能**: 任务调度和并发执行
- **特性**:
  - 异步任务执行
  - 资源池管理
  - 负载均衡
  - 性能监控

### middleware/ - 中间件目录
- **logging_middleware.py**: 请求响应日志记录
- **auth_middleware.py**: 用户认证和授权
- **rate_limit_middleware.py**: API速率限制

## API接口

### 任务管理API
```http
POST   /api/v1/tasks          # 创建任务
GET    /api/v1/tasks/{id}     # 获取任务状态
DELETE /api/v1/tasks/{id}     # 取消任务
PUT    /api/v1/tasks/{id}/pause   # 暂停任务
PUT    /api/v1/tasks/{id}/resume  # 恢复任务
```

### 处理API
```http
POST   /api/v1/process/image  # 图片处理
POST   /api/v1/process/video  # 视频处理
POST   /api/v1/process/batch  # 批量处理
```

### 系统API
```http
GET    /api/v1/health         # 健康检查
GET    /api/v1/stats          # 系统统计
GET    /api/v1/metrics        # 性能指标
```

## 任务状态机

```
IDLE → SELECTING_SOURCE → SOURCE_SELECTED → READY → PROCESSING ↗
  ↑                                                            ↓
  └──────────────────── CANCELLED ← PAUSED ←───────────────────┘
                              ↓
                            FAILED
```

## 依赖关系

```
frontend (HTTP/WebSocket)
    ↓
backend (API/Middleware)
    ↓
ai + processing (业务逻辑)
```

## 配置说明

### 环境变量
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
MAX_WORKERS=4
TASK_TIMEOUT=300000
```

### 性能调优
- **并发任务数**: 根据CPU核心数调整
- **队列大小**: 根据内存情况设置
- **超时时间**: 根据任务复杂度设置

## 开发指南

### 启动服务
```bash
# 开发模式
uvicorn src.backend.api_server:app --reload --host 0.0.0.0 --port 8000

# 生产模式
python src/backend/api_server.py
```

### 添加新API
1. 在 `api_server.py` 中定义路由
2. 添加请求/响应模型
3. 实现业务逻辑
4. 添加单元测试
5. 更新API文档

### 任务管理扩展
1. 在 `task_manager.py` 中添加任务类型
2. 实现任务执行逻辑
3. 添加状态转换
4. 更新统计收集

## 监控和调试

### 日志级别
- **DEBUG**: 详细调试信息
- **INFO**: 正常运行信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息

### 性能指标
- 请求响应时间
- 任务执行时间
- 队列长度
- 错误率

### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

## 故障排除

### 常见问题
1. **端口占用**: 检查8000端口是否被占用
2. **依赖缺失**: 确认所有Python包已安装
3. **权限问题**: 检查文件读写权限
4. **内存不足**: 监控系统资源使用

### 调试技巧
1. 使用 `--reload` 选项热重载代码
2. 查看 `/api/v1/metrics` 端点获取性能数据
3. 检查日志文件了解详细错误信息

## 扩展开发

新增功能时请：
1. 遵循RESTful API设计原则
2. 添加适当的中间件
3. 实现错误处理和日志记录
4. 添加单元测试和集成测试
5. 更新API文档和README
