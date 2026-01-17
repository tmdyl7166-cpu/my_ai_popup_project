# Utils 工具模块说明文档

## 概述

Utils 模块是 AI 弹窗项目的核心工具库，提供项目运行所需的基础功能和通用工具。该模块包含日志记录、文件操作、图片视频处理、线程管理和路径解析等功能，为整个项目的各个模块提供底层支持和服务。

## 目录结构

```
utils/
├── __init__.py                    # 模块初始化文件
├── utils_config.json             # 工具模块配置定义文件
├── utils_README.md               # 工具模块说明文档
├── logger.py                     # 日志记录工具类
├── file_utils.py                 # 文件操作工具类
├── image_utils.py                # 图片处理工具类
├── video_utils.py                # 视频处理工具类
├── thread_utils.py               # 线程管理工具类
└── path_resolver.py              # 路径解析工具类
```

## 核心功能

### 1. 日志记录 (Logger)

**功能描述：**
- 提供统一的日志记录接口
- 支持多级别日志输出
- 控制台和文件双重输出
- 性能监控和错误追踪

**主要特性：**
- 结构化日志格式
- 自动日志轮转
- 分类日志级别
- 性能监控集成

### 2. 文件操作 (FileUtils)

**功能描述：**
- 文件和目录的基本操作
- 支持多种文件格式识别
- 文件信息获取和格式化
- 批量文件处理功能

**支持的文件格式：**
- **图片格式：** JPG, JPEG, PNG, BMP, GIF, TIFF, WebP
- **视频格式：** MP4, AVI, MOV, MKV, WebM, FLV, WMV
- **模型格式：** PT, PTH, ONNX, H5, BIN, SafeTensors, CKPT

**核心功能：**
- 文件类型检测
- 大小格式化
- 目录遍历
- 文件复制/移动/删除

### 3. 图片处理 (ImageUtils)

**功能描述：**
- 图片读取、保存和转换
- 图像增强和预处理
- 批量图片处理
- 内存优化和缓存

**支持的后端：**
- **OpenCV：** 主要后端，支持复杂处理
- **Pillow：** 备用后端，轻量级处理
- **Scikit-Image：** 科学图像处理

**处理能力：**
- 多格式支持
- 质量控制
- 尺寸调整
- 色彩空间转换

### 4. 视频处理 (VideoUtils)

**功能描述：**
- 视频信息获取和帧提取
- 视频编码和解码
- 实时视频流处理
- 视频文件转换

**核心功能：**
- 视频信息解析
- 帧级处理
- 批量帧提取
- 视频合成
- 实时处理支持

### 5. 线程管理 (ThreadUtils)

**功能描述：**
- 异步任务执行
- 线程池管理
- 进度跟踪
- 任务队列处理

**组件：**
- **ThreadUtils：** 线程工具主类
- **TaskQueue：** 任务队列管理
- **ProgressTracker：** 进度追踪器

**特性：**
- 后台任务执行
- 异步协程支持
- 进度回调机制
- 资源池管理

### 6. 路径解析 (PathResolver)

**功能描述：**
- 统一的项目路径管理
- 相对路径解析
- 目录结构验证
- 自动路径初始化

**路径管理：**
- 项目根目录定位
- 标准目录结构
- 第三方资源路径
- 临时文件管理

## 技术架构

### 配置管理

**配置文件结构：**
```json
{
  "logging": {...},
  "file_operations": {...},
  "image_processing": {...},
  "video_processing": {...},
  "threading": {...},
  "path_resolution": {...}
}
```

### 模块初始化

**导入结构：**
```python
from src.utils import (
    Logger,           # 日志工具
    FileUtils,        # 文件工具
    VideoUtils,       # 视频工具
    ImageUtils,       # 图片工具
    ThreadUtils,      # 线程工具
    PathResolver      # 路径解析器
)
```

### 依赖关系

**外部依赖：**
- **OpenCV：** 计算机视觉处理
- **Pillow：** 图像处理
- **NumPy：** 数值计算
- **TQDM：** 进度条显示

**内部依赖：**
- **config：** 配置管理
- **logger：** 日志记录

## 性能优化

### 内存管理
- **对象池复用：** 减少内存分配
- **延迟加载：** 按需加载资源
- **缓存机制：** 文件和数据缓存
- **垃圾回收：** 自动内存清理

### 并发处理
- **线程池：** 控制并发数量
- **异步执行：** 非阻塞操作
- **任务队列：** 有序任务处理
- **进度跟踪：** 实时状态监控

### 缓存策略
- **文件缓存：** 文件信息缓存
- **图像缓存：** 处理结果缓存
- **路径缓存：** 解析结果缓存
- **LRU淘汰：** 智能缓存清理

## 使用指南

### 基本使用

**文件操作：**
```python
from src.utils import FileUtils

# 检查文件类型
if FileUtils.is_image("photo.jpg"):
    print("这是图片文件")

# 获取文件信息
info = FileUtils.get_file_info("video.mp4")
print(f"文件大小: {info['size_formatted']}")
```

**视频处理：**
```python
from src.utils import VideoUtils

# 获取视频信息
info = VideoUtils.get_video_info("input.mp4")
print(f"分辨率: {info['width']}x{info['height']}")

# 提取帧
frames = VideoUtils.extract_frames("input.mp4", "output_frames/")
```

**线程管理：**
```python
from src.utils import ThreadUtils

thread_utils = ThreadUtils()

# 后台执行任务
future = thread_utils.run_in_background(
    my_function,
    callback=result_callback,
    error_callback=error_callback,
    arg1=value1
)
```

**路径解析：**
```python
from src.utils import PathResolver

# 获取项目根目录
root = PathResolver.get_project_root()

# 解析资源路径
model_path = PathResolver.resolve_models("face_detector.onnx")
```

### 高级用法

**批量处理：**
```python
from src.utils import FileUtils, ThreadUtils

# 获取所有图片文件
image_files = FileUtils.list_files("input_dir/", extensions=[".jpg", ".png"])

# 并发处理
thread_utils = ThreadUtils()
for img_file in image_files:
    thread_utils.run_in_background(process_image, file_path=img_file)
```

**视频流处理：**
```python
from src.utils import VideoUtils

def process_frame(frame, frame_num):
    # 处理单帧
    processed = apply_filter(frame)
    return processed

# 处理整个视频
VideoUtils.process_video(
    "input.mp4",
    "output.mp4",
    process_frame,
    progress_callback=update_progress
)
```

## 配置说明

### 日志配置
```json
{
  "logging": {
    "level": "INFO",
    "handlers": {
      "file": {
        "path": "../logs/utils.log",
        "maxSize": "10MB"
      }
    }
  }
}
```

### 性能配置
```json
{
  "performance": {
    "monitoring": {
      "enabled": true,
      "metrics": ["cpu", "memory"]
    },
    "limits": {
      "maxMemoryUsage": "2GB",
      "maxConcurrentOperations": 10
    }
  }
}
```

### 缓存配置
```json
{
  "caching": {
    "global": {
      "maxSize": "5GB",
      "ttl": 3600
    }
  }
}
```

## 错误处理

### 异常类型
- **FileOperationError：** 文件操作异常
- **ImageProcessingError：** 图片处理异常
- **VideoProcessingError：** 视频处理异常
- **ThreadingError：** 线程管理异常
- **PathResolutionError：** 路径解析异常

### 错误恢复
- **自动重试：** 网络和I/O操作
- **降级处理：** 备用方法执行
- **用户提示：** 友好的错误信息
- **日志记录：** 详细错误追踪

## 测试和调试

### 单元测试
```bash
# 运行工具模块测试
python -m pytest tests/test_utils/ -v
```

### 性能测试
```bash
# 运行性能基准测试
python scripts/performance_test.py --module utils
```

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
from src.utils import logger
logger.setLevel(logging.DEBUG)
```

## 部署和分发

### 环境要求
- **Python：** 3.8+
- **内存：** 4GB+
- **磁盘：** 10GB+ 可用空间

### 依赖安装
```bash
pip install opencv-python pillow numpy tqdm
```

### 打包配置
- 包含所有工具类
- 排除测试文件
- 压缩分发包

## 维护和更新

### 版本管理
- 遵循语义化版本
- 向后兼容保证
- 定期依赖更新

### 性能监控
- 内存使用监控
- CPU使用率跟踪
- 操作耗时统计
- 错误率监控

### 文档更新
- API文档同步
- 使用示例更新
- 配置说明完善

---

*最后更新时间：2024-01-16*
*版本：1.0.0*
*作者：AI弹窗项目团队*
