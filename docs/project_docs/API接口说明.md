# 🔗 前端功能模块与后端执行脚本配置API统一接口表

## 📋 接口总览

### 接口设计原则
- **RESTful设计**: 遵循RESTful API设计规范
- **统一响应格式**: 所有接口返回统一的JSON格式
- **版本控制**: API版本通过URL路径控制 (v1)
- **认证机制**: 使用Token-based认证
- **错误处理**: 统一的错误响应格式

### 响应格式规范
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z",
  "requestId": "req-123456"
}
```

## 🎨 前端功能模块表

### 主窗口模块 (Main Window)
| 模块名 | 功能描述 | 相关API | 数据格式 |
|--------|----------|---------|----------|
| main_window | 主应用窗口管理 | GET /api/v1/status | StatusResponse |
| popup_window | AI弹窗入口 | POST /api/v1/popup/open | PopupRequest |
| video_panel | 实时视频显示 | GET /api/v1/video/stream | VideoStream |
| image_panel | 静态图片预览 | GET /api/v1/image/preview | ImageData |
| progress_bar | 任务进度显示 | GET /api/v1/task/progress | ProgressData |
| control_buttons | 用户控制按钮 | POST /api/v1/control/action | ControlRequest |

### 组件模块 (Components)
| 组件名 | 功能描述 | 相关API | 数据格式 |
|--------|----------|---------|----------|
| task_list | 任务列表显示 | GET /api/v1/tasks | TaskList |
| settings_panel | 设置面板 | GET/PUT /api/v1/settings | SettingsData |
| log_viewer | 日志查看器 | GET /api/v1/logs | LogData |
| notification_center | 通知中心 | GET /api/v1/notifications | NotificationList |

## 🔧 后端执行脚本配置表

### 任务管理模块 (Task Manager)
| 脚本名 | 功能描述 | 配置参数 | 执行条件 |
|--------|----------|----------|----------|
| task_manager.py | 任务生命周期管理 | task_config.json | 应用启动时 |
| scheduler.py | 任务调度执行 | scheduler_config.json | 任务创建时 |
| api_server.py | REST API服务 | api_config.json | 应用启动时 |

### AI处理模块 (AI Processing)
| 脚本名 | 功能描述 | 配置参数 | 执行条件 |
|--------|----------|----------|----------|
| ollama_client.py | AI推理客户端 | ai_config.json | 用户输入时 |
| face_analyzer.py | 人脸分析器 | face_config.json | 媒体处理时 |
| expression_editor.py | 表情编辑器 | expression_config.json | 表情修改时 |

### 媒体处理模块 (Media Processing)
| 脚本名 | 功能描述 | 配置参数 | 执行条件 |
|--------|----------|----------|----------|
| video_processor.py | 视频处理引擎 | video_config.json | 视频任务时 |
| image_processor.py | 图片处理引擎 | image_config.json | 图片任务时 |
| realtime_processor.py | 实时处理引擎 | realtime_config.json | 实时模式时 |
| batch_processor.py | 批量处理引擎 | batch_config.json | 批量任务时 |

## 🌐 API接口详细定义

### 状态管理接口
```
GET /api/v1/status
- 功能: 获取应用运行状态
- 参数: 无
- 返回: StatusResponse
- 频率: 实时轮询

POST /api/v1/status/update
- 功能: 更新应用状态
- 参数: StatusUpdate
- 返回: SuccessResponse
- 频率: 状态变更时
```

### 任务管理接口
```
GET /api/v1/tasks
- 功能: 获取任务列表
- 参数: TaskQuery
- 返回: TaskList
- 频率: 页面加载时

POST /api/v1/tasks
- 功能: 创建新任务
- 参数: TaskCreate
- 返回: TaskResponse
- 频率: 用户操作时

PUT /api/v1/tasks/{taskId}
- 功能: 更新任务状态
- 参数: TaskUpdate
- 返回: TaskResponse
- 频率: 任务状态变更时

DELETE /api/v1/tasks/{taskId}
- 功能: 删除任务
- 参数: 无
- 返回: SuccessResponse
- 频率: 用户操作时
```

### AI处理接口
```
POST /api/v1/ai/analyze
- 功能: AI命令分析
- 参数: AnalyzeRequest
- 返回: AnalyzeResponse
- 频率: 用户输入时

POST /api/v1/ai/process
- 功能: AI处理执行
- 参数: ProcessRequest
- 返回: ProcessResponse
- 频率: 任务执行时
```

### 媒体处理接口
```
POST /api/v1/media/upload
- 功能: 上传媒体文件
- 参数: FileUpload
- 返回: UploadResponse
- 频率: 文件选择时

GET /api/v1/media/preview
- 功能: 获取媒体预览
- 参数: PreviewQuery
- 返回: PreviewData
- 频率: 预览请求时

POST /api/v1/media/process
- 功能: 执行媒体处理
- 参数: ProcessRequest
- 返回: ProcessResponse
- 频率: 处理开始时
```

### 配置管理接口
```
GET /api/v1/config
- 功能: 获取配置信息
- 参数: ConfigQuery
- 返回: ConfigData
- 频率: 设置页面加载时

PUT /api/v1/config
- 功能: 更新配置
- 参数: ConfigUpdate
- 返回: SuccessResponse
- 频率: 配置修改时
```

## 📊 数据契约定义

### 请求数据格式
```typescript
interface TaskCreate {
  type: 'video' | 'image' | 'realtime' | 'batch';
  sourcePath: string;
  targetPath?: string;
  parameters: Record<string, any>;
  priority: 'low' | 'normal' | 'high';
}

interface AnalyzeRequest {
  text: string;
  context?: Record<string, any>;
  options?: AnalyzeOptions;
}

interface ProcessRequest {
  taskId: string;
  processor: string;
  parameters: Record<string, any>;
}
```

### 响应数据格式
```typescript
interface TaskResponse {
  taskId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  result?: any;
  error?: string;
  createdAt: string;
  updatedAt: string;
}

interface AnalyzeResponse {
  intent: string;
  parameters: Record<string, any>;
  confidence: number;
  suggestions?: string[];
}

interface ProcessResponse {
  success: boolean;
  result: any;
  processingTime: number;
  metadata?: Record<string, any>;
}
```

## 🔄 前后端数据流

### 典型用户操作流程
1. **用户点击弹窗按钮**
   - 前端: popup_window → POST /api/v1/popup/open
   - 后端: api_server → task_manager.create_task()
   - 返回: PopupResponse

2. **用户输入AI命令**
   - 前端: input_field → POST /api/v1/ai/analyze
   - 后端: ollama_client.analyze() → rules_system.validate()
   - 返回: AnalyzeResponse

3. **开始媒体处理**
   - 前端: control_buttons → POST /api/v1/media/process
   - 后端: processing_engine.execute() → integrations.call()
   - 返回: ProcessResponse

## 🛡️ 安全与验证

### 输入验证
- **前端验证**: 表单验证、类型检查
- **后端验证**: 参数校验、业务规则验证
- **AI验证**: 内容安全检查、意图过滤

### 错误处理
- **统一错误码**: 使用标准HTTP状态码 + 自定义业务错误码
- **错误响应格式**: 包含错误详情、建议解决方案
- **日志记录**: 所有错误自动记录到日志系统

### 限流保护
- **API限流**: 基于用户/IP的请求频率限制
- **资源限流**: CPU/内存/GPU使用率监控
- **任务队列**: 防止任务积压的队列管理

## 📈 性能监控

### 接口性能指标
- **响应时间**: 平均响应时间 < 500ms
- **并发处理**: 支持同时处理 10+ 个任务
- **内存使用**: 峰值内存 < 2GB
- **CPU使用**: 平均CPU使用率 < 80%

### 前端性能指标
- **页面加载**: < 2秒
- **UI响应**: < 100ms
- **内存泄漏**: 无内存泄漏
- **渲染性能**: 60FPS稳定

---

*本文档由自动化系统维护，最后更新: 2024-01-01*
