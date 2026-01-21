# 项目依赖和配置说明

> 本文档描述夜灵AR多功能合成软件的依赖管理和配置系统。

## 📦 依赖管理

### Python 环境要求

| 项目 | 要求 |
|------|------|
| Python 版本 | 3.10.0 - 3.11.9 (推荐 3.10.12) |
| 操作系统 | Windows 10+, Ubuntu 20.04+, macOS 12+ |
| 内存 | 8GB+ (推荐 16GB) |
| 存储 | 20GB+ 可用空间 |
| GPU | CUDA兼容GPU (可选，推荐 4GB+ VRAM) |

### 核心依赖

#### 核心框架

| 包名 | 版本 | 用途 |
|------|------|------|
| PyQt5 | >=5.15.10 | GUI框架 |
| PyQt5-sip | >=12.13.1 | PyQt5 SIP绑定 |
| fastapi | >=0.120.0 | Web框架 |
| uvicorn | >=0.30.0 | ASGI服务器 |
| python-multipart | >=0.0.6 | 多部分表单数据 |
| pydantic | >=2.10.0 | 数据验证 |
| pydantic-settings | >=2.5.0 | 设置管理 |

#### Web 相关

| 包名 | 版本 | 用途 |
|------|------|------|
| jinja2 | >=3.1.4 | 模板引擎 |
| aiofiles | >=24.0.0 | 异步文件操作 |
| websockets | >=14.0 | WebSocket支持 |
| python-socketio | >=5.12.0 | Socket.IO客户端 |
| schedule | >=1.2.2 | 任务调度 |

#### AI 相关

| 包名 | 版本 | 用途 |
|------|------|------|
| torch | >=2.5.0 | 深度学习框架 |
| torchvision | >=0.20.0 | PyTorch视觉库 |
| torchaudio | >=2.5.0 | PyTorch音频库 |
| ollama | >=0.3.0 | 本地LLM推理 |
| insightface | 0.7.3 | 人脸分析 |
| face-recognition | >=1.3.0 | 人脸识别 |
| dlib | >=19.24.0 | 人脸特征点检测 |
| deepface | >=0.0.90 | 深度人脸分析 |
| mediapipe | >=0.10.15 | 面部网格检测 |
| onnxruntime | >=1.17.0 | 推理加速 |

#### 媒体处理

| 包名 | 版本 | 用途 |
|------|------|------|
| opencv-python | >=4.10.0 | 图像/视频处理 |
| opencv-python-headless | >=4.10.0 | OpenCV无头版本 |
| Pillow | >=11.0.0 | 图像处理 |
| numpy | >=1.24.0,<2.0.0 | 数值计算 |
| scipy | >=1.14.0 | 科学计算 |
| imageio | >=2.36.0 | 图像I/O |
| moviepy | >=2.0.0 | 视频编辑 |
| imageio-ffmpeg | >=0.5.0 | FFmpeg绑定 |

#### 工具类

| 包名 | 版本 | 用途 |
|------|------|------|
| psutil | >=6.1.0 | 系统监控 |
| loguru | >=0.7.3 | 日志记录 |
| colorlog | >=6.9.0 | 彩色日志 |
| python-dotenv | >=1.0.1 | 环境变量 |
| pyyaml | >=6.0.2 | YAML解析 |
| watchdog | >=6.0.0 | 文件监控 |

### 可选依赖

#### GPU 加速

| 包名 | 版本 | 用途 |
|------|------|------|
| torch-cuda | >=2.5.0+cu121 | CUDA支持PyTorch |
| torch-directml | >=0.2.5 | DirectML支持 |
| onnxruntime-gpu | >=1.20.0 | GPU推理加速 |

#### 开发工具

| 包名 | 版本 | 用途 |
|------|------|------|
| pytest | >=8.3.0 | 测试框架 |
| pytest-asyncio | >=0.25.0 | 异步测试 |
| black | >=25.0.0 | 代码格式化 |
| mypy | >=1.12.0 | 类型检查 |

## ⚙️ 配置管理

### 配置文件层次

```
my_ai_popup_project/
├── project_config.json          # 项目全局配置 ⭐
│
├── rules/                       # 规则配置
│   ├── L1-meta-goal.json       # 元目标层
│   ├── L2-understanding.json   # 全局理解层
│   ├── L3-constraints.json     # 约束层
│   ├── L4-decisions.json       # 决策层
│   ├── L5-execution.json       # 执行层
│   └── rules.config.json       # 规则系统配置 ⭐
│
├── src/                         # 源码配置
│   ├── src_config.json         # 源码模块配置
│   ├── frontend/
│   │   └── frontend_config.json
│   ├── backend/
│   │   └── backend_config.json
│   ├── ai/
│   │   └── ai_config.json
│   ├── processing/
│   │   └── processing_config.json
│   ├── integrations/
│   │   └── integrations_config.json
│   ├── utils/
│   │   └── utils_config.json
│   └── config/
│       └── config_config.json
│
├── api/                         # API配置
│   ├── config/
│   │   └── api_config.json     # API配置 ⭐
│   ├── mapping/
│   │   ├── api_mapping.json    # API映射 ⭐
│   │   └── api_mapping.md
│   └── frontend/
│       └── api.js
│
├── scripts/                     # 脚本配置
│   ├── scripts_config.json     # 脚本配置 ⭐
│   └── ...
│
├── web/                         # Web配置
│   ├── web_config.json         # Web配置 ⭐
│   └── requirements.txt
│
├── assets/                      # 资源目录配置
│   └── assets_config.json
│
└── requirements.txt             # Python依赖清单
```

### 核心配置说明

#### project_config.json

```json
{
  "meta": { ... },
  "project": {
    "name": "夜灵AR多功能合成软件",
    "rootPath": "."
  },
  "deployment": {
    "paths": {
      "projectRoot": "./my_ai_popup_project",
      "sourceCode": "./src",
      "assets": "./assets",
      "config": "./rules",
      "output": "./output",
      "logs": "./logs"
    },
    "entryPoints": { ... },
    "environments": {
      "development": { "debug": true, "logLevel": "DEBUG" },
      "staging": { "debug": false, "logLevel": "INFO" },
      "production": { "debug": false, "logLevel": "WARNING" }
    }
  },
  "rules": { ... },
  "validation": { ... },
  "monitoring": { ... },
  "logging": { ... }
}
```

#### rules/rules.config.json

```json
{
  "layers": {
    "L1-meta-goal": { "file": "L1-meta-goal.json", "required": true },
    "L2-understanding": { "file": "L2-understanding.json", "required": true },
    "L3-constraints": { "file": "L3-constraints.json", "required": true },
    "L4-decisions": { "file": "L4-decisions.json", "required": true },
    "L5-execution": { "file": "L5-execution.json", "required": true }
  },
  "dependencies": {
    "L1": [],
    "L2": ["L1"],
    "L3": ["L1", "L2"],
    "L4": ["L1", "L2", "L3"],
    "L5": ["L1", "L2", "L3", "L4"]
  },
  "validation": {
    "strictMode": false,
    "checkLayerConsistency": true
  }
}
```

#### api/config/api_config.json

```json
{
  "version": "1.0.0",
  "base_url": "http://localhost:8080",
  "endpoints": {
    "health": { "path": "/api/health", "method": "GET" },
    "project_status": { "path": "/api/project/status", "method": "GET" },
    "scripts_list": { "path": "/api/scripts/list", "method": "GET" },
    ...
  },
  "websocket": {
    "path": "/ws",
    "channels": ["progress", "log", "data", "heartbeat"]
  }
}
```

#### scripts/scripts_config.json

```json
{
  "executionRules": {
    "scheduling": {
      "daily": { "time": "02:00", "scripts": ["health_monitor.py"] }
    },
    "errorHandling": {
      "retryPolicy": { "maxRetries": 3, "backoff": "exponential" }
    }
  },
  "monitoring": {
    "metrics": {
      "executionTime": { "enabled": true, "threshold": 300 },
      "successRate": { "enabled": true, "threshold": 95 }
    }
  }
}
```

#### web/web_config.json

```json
{
  "web": {
    "server": {
      "host": "0.0.0.0",
      "port": 8080
    },
    "modules": {
      "dashboard": { "enabled": true },
      "scripts": { "enabled": true },
      "system": { "enabled": true }
    }
  },
  "integration": {
    "project": {
      "configPath": "../project_config.json"
    }
  }
}
```

### 环境变量

#### .env 文件

```bash
# API 配置
API_HOST=0.0.0.0
API_PORT=8080
DEBUG=false

# AI 配置
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# 路径配置
ASSETS_PATH=./assets
OUTPUT_PATH=./output
LOGS_PATH=./logs

# GPU 配置
USE_GPU=true
GPU_DEVICE=0

# 日志配置
LOG_LEVEL=INFO
```

## 📋 依赖安装

### 使用 pip 安装

```bash
# 安装所有依赖
pip install -r requirements.txt

# 安装 GPU 支持（可选）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 使用虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 🔧 配置验证

### 验证脚本

```bash
# 验证项目配置
python scripts/validate_configs.py

# 验证路径配置
python scripts/verify_paths.py

# 验证虚拟环境
python scripts/verify_venv.py

# 运行健康检查
python scripts/health_check.py
```

### 验证项目

```bash
# 检查规则一致性
python scripts/health_monitor/config_validator.py --rules

# 检查配置合规性
python scripts/health_monitor/config_validator.py --compliance
```

## 📊 依赖更新

### 更新策略

1. **安全更新**: 立即更新
2. **功能更新**: 评估后更新
3. **版本更新**: 测试后更新
4. **重大更新**: 谨慎评估

### 更新流程

```bash
# 检查可更新包
pip list --outdated

# 更新单个包
pip install --upgrade <package_name>

# 锁定依赖版本
pip freeze > requirements.txt
```

## 📝 文档版本

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| 1.0 | 2026-01-19 | 初始版本 |

## 🔗 相关文档

- [项目整体架构设计](01-project-architecture.md)
- [系统运行时逻辑流程](02-runtime-logic.md)
- [API接口文档](04-frontend-backend-api.md)
- [自动化脚本说明](05-automation-scripts.md)
