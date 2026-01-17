# AI模块 (ai/)

## 概述

`ai/` 模块是系统的"智能大脑"，负责AI推理、人脸识别、命令理解等核心AI功能。

## 核心职责

1. **AI推理**: 本地LLM推理，命令理解和决策
2. **人脸识别**: 人脸检测、对齐、特征提取
3. **图像分析**: 质量评估、内容分析
4. **模型管理**: 模型加载、缓存、切换

## 模块组成

### ollama_client.py - Ollama客户端
- **功能**: 与Ollama服务通信
- **特性**:
  - 异步请求处理
  - 连接池管理
  - 错误重试机制
  - 模型切换支持

### face_recognition/ - 人脸识别子模块
#### detector.py - 人脸检测器
- 检测图片/视频中的人脸
- 支持多种检测算法
- 实时性能优化

#### aligner.py - 人脸对齐器
- 人脸关键点检测
- 姿态校正和对齐
- 统一坐标系统

#### recognizer.py - 人脸识别器
- 人脸特征提取
- 相似度计算
- 身份验证

### processors/ - 处理器子模块
#### face_swapper.py - 人脸交换器
- 执行人脸替换算法
- 支持多种融合模式
- 质量增强选项

#### face_enhancer.py - 人脸增强器
- 提升人脸图像质量
- 去除瑕疵和 artifacts
- 超分辨率重建

#### expression_editor.py - 表情编辑器
- 表情迁移和编辑
- 姿态调整
- 实时表情跟踪

### analyzers/ - 分析器子模块
#### image_analyzer.py - 图像分析器
- 图像质量评估
- 内容识别
- 元数据提取

#### video_analyzer.py - 视频分析器
- 视频内容分析
- 运动检测
- 人脸跟踪

## AI引擎集成

### Ollama集成
- **用途**: 自然语言命令理解
- **模型**: LLaMA 3.2, Mistral等
- **特性**:
  - 本地推理，保护隐私
  - 支持多种模型切换
  - 异步处理

### InsightFace集成
- **用途**: 高精度人脸分析
- **特性**:
  - ArcFace人脸识别
  - 实时检测
  - GPU加速

### 其他AI库
- **DeepFace**: 深度人脸分析
- **MediaPipe**: 面部网格检测
- **dlib**: 传统人脸特征点

## 配置说明

### 模型配置
```json
{
  "ollama": {
    "host": "http://localhost:11434",
    "defaultModel": "llama3.2:3b",
    "timeout": 300000
  },
  "faceRecognition": {
    "defaultEngine": "insightface",
    "fallbackEngine": "dlib"
  }
}
```

### 性能调优
- **GPU内存分配**: 根据显卡调整
- **批处理大小**: 根据任务复杂度
- **并发处理**: 异步vs同步选择

## 开发指南

### 使用AI推理
```python
from src.ai.ollama_client import OllamaClient

client = OllamaClient()
response = await client.generate("分析这张图片中的人脸", image_path)
```

### 人脸识别
```python
from src.ai.face_recognition import FaceRecognizer

recognizer = FaceRecognizer()
faces = await recognizer.detect_faces(image)
features = await recognizer.extract_features(faces[0])
```

### 添加新AI功能
1. 在相应子模块中实现功能
2. 添加配置选项
3. 实现错误处理
4. 添加单元测试
5. 更新文档

## 性能优化

### 缓存策略
- **模型缓存**: 预加载常用模型
- **特征缓存**: 避免重复计算
- **结果缓存**: 短期结果缓存

### 资源管理
- **GPU内存**: 动态分配和释放
- **CPU线程**: 线程池管理
- **内存监控**: 防止内存泄漏

### 并发处理
- **异步推理**: 非阻塞AI调用
- **批处理**: 合并相似任务
- **队列管理**: 任务优先级调度

## 监控和调试

### 性能指标
- 推理时间
- 准确率
- 资源使用率
- 错误率

### 日志记录
- AI操作日志
- 性能指标日志
- 错误和异常日志

### 健康检查
```python
# 检查Ollama连接
await ollama_client.health_check()

# 检查模型加载状态
face_recognizer.check_models()
```

## 故障排除

### 常见问题
1. **Ollama连接失败**: 检查服务是否运行
2. **模型加载失败**: 确认模型文件存在
3. **GPU内存不足**: 降低批处理大小
4. **推理超时**: 调整超时设置

### 回退机制
1. GPU失败 → CPU模式
2. 主引擎失败 → 备用引擎
3. 网络失败 → 本地缓存

## 扩展开发

新增AI功能时请：
1. 遵循模块化设计原则
2. 添加适当的配置选项
3. 实现性能监控
4. 提供回退机制
5. 添加完整的测试覆盖
6. 更新文档和配置
