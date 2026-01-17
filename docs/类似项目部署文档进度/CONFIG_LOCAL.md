/workspaces/AISP/CONFIG_LOCAL.md
</path>
<parameter name="content"># AISP 本地配置说明

## 运行模式

本项目支持以下运行模式：

### 1. 本地离线模式（推荐）
```bash
# 启动所有服务
python3 scripts/main.py --all

# 或分别启动
python3 scripts/start_server.sh    # 后端API
python3 scripts/start_gui.sh       # GUI界面
python3 scripts/health_check.py    # 健康检查
```

### 2. 轻量模式（无需GPU）
```bash
# 使用CPU模式
python3 scripts/main.py --server --cpu-only
```

### 3. 纯Web模式（无GUI）
```bash
python3 web/web_api.py
```

## 环境变量配置

在 `.env` 文件中配置：

```bash
# 核心配置
AISP_PROJECT_ROOT=/workspaces/AISP
AISP_MODE=local

# AI配置（本地离线）
OLLAMA_HOST=localhost:11434
USE_LOCAL_AI=true

# 路径配置
AISP_DATA_DIR=/workspaces/AISP/data
AISP_LOGS_DIR=/workspaces/AISP/logs
AISP_MODELS_DIR=/workspaces/AISP/models

# GPU配置（可选）
CUDA_VISIBLE_DEVICES=
```

## 服务端口

| 服务 | 端口 | 说明 |
|-----|------|------|
| 后端API | 8000 | FastAPI主服务 |
| 健康检查 | 8080 | Web监控界面 |
| GUI界面 | 5000 | 图形界面 |
| Ollama | 11434 | 本地AI模型 |

## 离线使用

无需网络连接，所有依赖已打包：

1. **Python依赖**：使用 `requirements.txt`
2. **AI模型**：本地模型文件位于 `models/`
3. **配置文件**：位于 `config/`

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动后端
python3 scripts/start_server.sh &

# 3. 启动GUI（可选）
python3 scripts/start_gui.sh &

# 4. 访问
# - API文档: http://localhost:8000/docs
# - Web界面: http://localhost:8080
