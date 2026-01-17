# AI弹窗项目 - 智能人脸合成与视频处理平台

## 📊 项目状态

**🎉 全局运行检测完成 - 生产就绪状态**

✅ **所有测试通过** - 项目已完全准备好进行生产部署  
**部署进度**: 75% | **版本**: 1.0.0 | **最后更新**: 2026-01-16

---

## 项目概述

这是一个以「本地 AI + 弹窗 GUI」为入口，通过「自然语言 → 任务理解 → 规则决策 → AI/视频处理执行 → 实时/离线输出」的多模块联动系统。

**本质**: AI 指挥中枢 + 多开源人脸系统的统一调度平台 + 前端实时交互 + 后端任务编排 + AI 理解执行的闭环系统

---

## 核心目录结构

### 1. my_ai_popup_project/web - 全局统一入口 ⭐
作为管理员整体项目部署的全局统一入口，实现对全局的实时健康监控以及所有子目录子项目功能脚本和自动化脚本的映射。

- **功能**: 实时健康监控、脚本状态映射、系统资源可视化
- **访问地址**: `http://localhost:8080`
- **启动命令**: `python web/start_monitor.py --auto-install`

### 2. src - AI弹窗项目核心 ⭐
包含AI弹窗项目的各配置功能核心源码，按照分层架构组织为多个功能模块。

```
src/
├── frontend/     # 用户前端窗口功能部署 (PyQt5 + QSS)
├── backend/      # 后端服务 (FastAPI + WebSocket)
├── ai/           # AI命令理解 (Ollama集成)
├── processing/   # 处理引擎 (实时/图片/视频/批量)
├── integrations/ # 第三方AI集成 (Deep-Live-Cam/FaceFusion/iRoop)
├── config/       # 配置模块
└── utils/        # 工具模块
```

### 3. rules - 规则配置系统 ⭐
所有JSON配置内容代表整个项目运行的逻辑和执行规则，采用五层架构：

| 层级 | 文件 | 作用 |
|------|------|------|
| L1 | meta-goal.json | 元目标层 - 项目愿景和价值观 |
| L2 | understanding.json | 全局理解层 - 架构设计和数据流 |
| L3 | constraints.json | 约束层 - 技术规范和依赖关系 |
| L4 | decisions.json | 决策层 - 设计决策和技术选型 |
| L5 | execution.json | 执行层 - 具体操作和任务分配 |

### 4. docs - 项目文档 ⭐
包含整个项目的详细说明以及任务部署的详细说明情况。

- **project_docs/**: 项目架构文档、运行时逻辑、依赖配置
- **deployment_progress/**: 部署进度跟踪、任务清单、优化机会

### 5. assets - 资源文件 ⭐
项目所需的所有资源文件、第三方开源项目和媒体数据。

```
assets/
├── models/                    # AI模型文件
├── images/                    # 图片资源
│   ├── source/               # 源图片
│   ├── templates/            # 模板
│   └── output/               # 输出图片
├── videos/                   # 视频资源
│   ├── source/               # 源视频
│   └── output/               # 输出视频
├── Deep-Live-Cam-main/       # 实时换脸引擎
├── facefusion-master/        # 高质量视频换脸引擎
└── iRoopDeepFaceCam-main/    # 表情姿态换脸引擎
```

### 6. scripts - 自动化脚本 ⭐
对全局项目的自动化脚本，用于环境验证、依赖安装、健康检查、部署等任务。

```
scripts/
├── health_monitor/           # 健康监控脚本
├── core/                     # 核心功能脚本
├── deploy/                   # 部署脚本
├── utils/                    # 工具脚本
└── test/                     # 测试脚本
```

---

## 整体运行分层逻辑

```
用户
 ↓
GUI（PyQt 弹窗） / Web界面 ⭐
 ↓
AI命令理解（Ollama）
 ↓
规则系统（L1-L5）
 ↓
任务调度 / 任务管理
 ↓
处理引擎（实时 / 图片 / 视频 / 批量）
 ↓
第三方AI集成（Deep-Live-Cam / Facefusion / iRoop）
 ↓
结果回流（视频 / 图像 / 实时画面）
```

---

## 任务部署模式

### 简单模式
用户选择次要合成文件类型，AI简单的调度处理引擎直接进行合成。

- 图片 ↔ 图片合成
- 图片 → 视频合成
- 图片 → 实时摄像头合成

### 高级模式
用户仅选择主要文件后与AI产生自然语言的交流，让AI深度理解分析识别输入的任务内容，根据主要参数与任务要求，结合所有引擎和学习库创造出合成内容。

**示例命令**:
```
"把这张照片的脸换到视频里"
"开始实时摄像头换脸"
"处理批量图片"
```

---

## 核心功能

1. **实时人脸合成** - 图片合成到实时摄像头 (Deep-Live-Cam)
2. **视频处理** - 图片合成到视频 (FaceFusion)
3. **图像处理** - 图片合成到图片、批量处理
4. **AI命令理解** - 自然语言命令解析 (Ollama)
5. **Web监控中心** - 统一的Web管理界面

---

## 技术栈概览

| 领域 | 技术 |
|------|------|
| 前端 | PyQt5, Bootstrap 5 + Vanilla JS |
| 后端 | FastAPI, Uvicorn, WebSocket |
| AI | Ollama (LLaMA 3.2:3b), InsightFace, face_recognition |
| 处理 | OpenCV, MoviePy, Pillow, NumPy |
| 第三方 | Deep-Live-Cam, FaceFusion, iRoop |
| 监控 | 6个独立健康监控脚本, Web实时监控 |

---

## 快速开始

### 🚀 一键启动 (推荐)

```bash
# 方式1: Web监控中心 (推荐) ⭐
python web/start_monitor.py --auto-install

# 方式2: 传统GUI模式
python src/main.py

# 方式3: 使用启动脚本
./start.sh
```

**访问地址**: `http://localhost:8080` (Web监控中心)

### 📋 系统要求

- **Python**: 3.10.0 - 3.11.9
- **内存**: 8GB+ (推荐 16GB)
- **存储**: 20GB+ 可用空间
- **GPU**: CUDA兼容GPU (可选，推荐 4GB+ VRAM)
- **OS**: Windows 10+, Ubuntu 20.04+, macOS 12+

---

## 项目结构总览

```
my_ai_popup_project/
├── project_config.json      # 项目全局配置
├── README.md                # 项目说明
├── requirements.txt         # Python依赖
│
├── assets/                  # 资源文件
│   ├── models/              # AI模型
│   ├── images/              # 图片资源
│   ├── videos/              # 视频资源
│   └── [第三方引擎]          # Deep-Live-Cam/FaceFusion/iRoop
│
├── src/                     # 核心源码 ⭐
│   ├── frontend/            # 前端UI
│   ├── backend/             # 后端服务
│   ├── ai/                  # AI模块
│   ├── processing/          # 处理引擎
│   ├── integrations/        # 集成模块
│   └── utils/               # 工具模块
│
├── web/                     # Web监控中心 ⭐
│   ├── app.py               # Web应用主程序
│   ├── templates/           # HTML模板
│   └── static/              # 静态资源
│
├── rules/                   # 规则配置系统 ⭐ (L1-L5)
│   ├── L1-meta-goal.json
│   ├── L2-understanding.json
│   ├── L3-constraints.json
│   ├── L4-decisions.json
│   └── L5-execution.json
│
├── scripts/                 # 自动化脚本 ⭐
│   ├── health_monitor/      # 健康监控
│   ├── core/                # 核心脚本
│   ├── deploy/              # 部署脚本
│   └── utils/               # 工具脚本
│
├── docs/                    # 项目文档 ⭐
│   ├── project_docs/        # 项目文档
│   └── deployment_progress/ # 部署进度
│
└── tests/                   # 测试模块
```

---

## Web监控中心功能

- 📊 **实时仪表板** - 系统资源监控、脚本状态总览
- 🔧 **脚本管理** - 自动化脚本的启动、停止、监控
- 💻 **系统监控** - CPU/内存/磁盘实时图表和警报
- 🚀 **部署进度** - 各组件部署状态和配置进度
- ⚙️ **配置管理** - 在线查看和编辑项目配置
- 📝 **日志查看** - 实时日志流和历史查询

---

## 文档资源

| 文档 | 位置 |
|------|------|
| 项目架构 | `docs/project_docs/01-project-architecture.md` |
| 运行时逻辑 | `docs/project_docs/02-runtime-logic.md` |
| 部署进度 | `docs/deployment_progress/01-整体进度.md` |
| API文档 | `docs/project_docs/04-frontend-backend-api.md` |

---

## 重要提醒

### ⚖️ 规则遵循
本项目严格遵循**五层规则配置系统**，所有开发和部署活动必须符合规则约束。

### 🚀 快速启动
```bash
python web/start_monitor.py --auto-install
```

---

**🎉 项目已达到生产就绪状态**

- ✅ **技术架构**: 模块化设计，依赖关系清晰
- ✅ **配置系统**: 五层规则完整，配置联动正确
- ✅ **监控体系**: 自动化脚本完善，Web监控可用
- ✅ **系统稳定性**: 异常处理完善，容错机制健全

