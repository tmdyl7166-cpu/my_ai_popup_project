# Backend 模块功能说明

> AISP 后端服务层功能详解
> 
> 文档版本: 1.0.0
> 最后更新: 2025-01-21

---

## 模块结构

```
backend/
├── api.py                         # FastAPI入口（旧版）
├── unified_api.py                 # 统一API入口（新版）⭐
├── models.py                      # Pydantic数据模型
│
├── services/                      # 核心服务层 ⭐
│   ├── face_detection.py          # 人脸检测
│   ├── face_recognition.py        # 人脸识别
│   ├── face_swap.py               # 人脸换脸
│   ├── camera_service.py          # 摄像头管理
│   ├── recognition_service.py     # 图片识别
│   ├── video_compositor.py        # 视频合成
│   ├── video_pipeline.py          # 视频流水线
│   ├── task_scheduler.py          # 异步任务调度
│   ├── performance_monitor.py     # 性能监控
│   └── local_ai_interface.py      # 本地AI接口
│
├── ai_control/                    # AI控制层 ⭐
│   ├── auto_strategy.py           # AI策略自动生成
│   ├── ollama_client.py           # Ollama客户端
│   └── memory_db.py               # SQLite存储
│
├── ar_engine/                     # AR引擎层 ⭐
│   ├── frame_pipeline.py          # 帧处理流水线
│   ├── tracker/                   # 人脸追踪
│   │   └── face_tracker.py
│   └── adapters/                  # 引擎适配器
│       ├── deep_live_cam.py
│       ├── facefusion.py
│       ├── iroop.py
│       └── expression.py
│
├── control_core/                  # 控制核心 ⭐
│   ├── server.py                  # FastAPI服务器（启动入口）
│   ├── state_manager.py           # 状态管理
│   ├── pipeline_manager.py        # 流水线管理
│   ├── resource_guard.py          # 资源守护
│   ├── validator.py               # 配置验证器
│   ├── instruction_parser.py      # 指令解析
│   ├── module_router.py           # 模块路由
│   ├── auth.py                    # 认证管理
│   └── user_session.py            # 用户会话
│
├── database/                      # 数据库层
│   └── db.py                      # SQLite操作
│
└── utils/                         # 工具函数
    └── image_utils.py             # 图像处理
```

---

## 服务层详情

### face_detection.py - 人脸检测

**功能**: 检测图像中的人脸位置

**方法**:
- `detect(frame)` - 检测人脸
- `get_status()` - 获取检测器状态

**依赖**: opencv-python, mediapipe, ONNX Runtime

### face_recognition.py - 人脸识别

**功能**: 识别人脸特征并进行匹配

**方法**:
- `recognize(frame, faces)` - 人脸识别
- `get_features(face)` - 提取特征

**依赖**: face_detection.py, ArcFace/简单特征

### face_swap.py - 人脸换脸

**功能**: 人脸合成/换脸，支持多种方法

**方法**:
- `swap(source_face, target_face)` - 换脸
- `compose(images)` - 图片合成

**支持方法**: seamless, morph, blend, opencv_wrap

### camera_service.py - 摄像头管理 ⭐

**功能**: 摄像头连接、配置、状态管理

**方法**:
- `get_status()` - 获取摄像头状态
- `start()` - 启动摄像头
- `stop()` - 停止摄像头
- `capture_frame()` - 捕获帧

### recognition_service.py - 图片识别 ⭐

**功能**: 人脸检测与图片合成

**方法**:
- `detect_faces(image)` - 检测人脸
- `compose(source, target)` - 图片合成

### video_compositor.py - 视频合成 ⭐

**功能**: 视频插入和特效叠加

**方法**:
- `compose_video(input_path, output_path)` - 合成视频
- `add_effect(frame, effect)` - 添加特效

### video_pipeline.py - 视频流水线

**功能**: 视频帧处理流水线，多线程+缓冲区管理

**特性**:
- ThreadPoolExecutor多线程处理
- 输入/输出帧缓冲区(deque)
- 缓冲区使用率和丢帧统计
- 非阻塞获取最新帧

### task_scheduler.py - 任务调度

**功能**: 异步任务队列管理，支持优先级调度

**优先级**: URGENT > HIGH > MEDIUM > LOW

### performance_monitor.py - 性能监控

**功能**: FPS/CPU/GPU监控，支持自动降级策略

**指标**:
- FPS实时监控
- CPU使用率
- GPU使用率（如果可用）
- 内存使用率

### local_ai_interface.py - 本地AI接口

**功能**: Ollama/LLaMA统一调用入口

**方法**:
- `infer(prompt)` - AI推理
- `generate_strategy(context)` - 生成策略

---

## AI控制层详情

### auto_strategy.py - AI策略生成

**功能**: 根据上下文生成AI优化策略

**方法**:
- `generate_strategy(context)` - 生成策略
- `optimize_for_module(module, task)` - 优化模块

### ollama_client.py - Ollama客户端

**功能**: 与本地Ollama服务通信

**方法**:
- `is_available()` - 检查可用性
- `generate(prompt)` - 生成文本
- `chat(messages)` - 对话模式

### memory_db.py - 数据存储

**功能**: SQLite数据库存储用户行为学习数据

**方法**:
- `save_strategy(strategy)` - 保存策略
- `get_history(module)` - 获取历史

---

## AR引擎层详情

### frame_pipeline.py - 帧处理流水线

**功能**: 统一处理视频帧，支持多引擎切换

**方法**:
- `process_frame(frame)` - 处理单帧
- `process_video(input, output)` - 处理视频

### adapters/ - 引擎适配器

所有适配器继承自 `engines/engine_base.py`，实现统一接口

### tracker/face_tracker.py - 人脸追踪

**功能**: 实时追踪人脸位置

---

## 控制核心详情

### server.py - FastAPI服务器

**启动入口**: `python -m backend.unified_api`

**端口**: 8000

---

## 相关文档

- [项目结构说明](../guide/项目结构说明.md) - 整体结构
- [模块依赖关系](../guide/模块依赖关系.md) - 依赖图
- [统一接口](../guide/统一接口.md) - API详情

---

*文档版本: 1.0.0*
*最后更新: 2025-01-21*

