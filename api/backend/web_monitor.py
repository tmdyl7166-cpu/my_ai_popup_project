#!/usr/bin/env python3
"""
Web监控应用实例
提供统一的Web监控界面
"""

import os
import sys
import json
import asyncio
import logging
import socket
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import socketio
import psutil

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app_instance = FastAPI(title="AI弹窗项目监控中心", version="1.0.0")

# 配置CORS
app_instance.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO服务器
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app_instance)

# 模板和静态文件
templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "web" / "templates")
static_path = Path(__file__).parent.parent.parent / "web" / "static"

# 挂载静态文件
if static_path.exists():
    app_instance.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 全局状态
system_status = {
    "cpu_percent": 0,
    "memory_percent": 0,
    "disk_percent": 0,
    "services": {},
    "scripts": {},
    "last_update": None,
}


# Socket.IO事件处理
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await sio.emit("status_update", system_status, to=sid)


@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")


# API路由
@app_instance.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """主仪表板页面"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app_instance.get("/api/status")
async def get_status():
    """获取系统状态"""
    update_system_status()
    return JSONResponse(system_status)


@app_instance.get("/api/scripts")
async def get_scripts():
    """获取脚本状态"""
    scripts = scan_scripts()
    return JSONResponse({"scripts": scripts})


@app_instance.post("/api/scripts/{script_name}/run")
async def run_script(script_name: str, background_tasks: BackgroundTasks):
    """运行脚本"""
    script_path = PROJECT_ROOT / "scripts" / f"{script_name}.py"
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Script not found")

    background_tasks.add_task(run_script_background, script_path)
    return JSONResponse({"status": "running", "script": script_name})


@app_instance.get("/api/logs")
async def get_logs(lines: int = 100):
    """获取日志"""
    logs = []
    logs_dir = PROJECT_ROOT / "logs"
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.readlines()[-lines:]
                    logs.extend(
                        [f"{log_file.name}: {line.strip()}" for line in content]
                    )
            except Exception as e:
                logger.error(f"Error reading log {log_file}: {e}")

    return JSONResponse({"logs": logs[-lines:]})


@app_instance.get("/api/config")
async def get_config():
    """获取配置"""
    config_files = [
        "project_config.json",
        "rules/L1-meta-goal.json",
        "rules/L2-understanding.json",
        "rules/L3-constraints.json",
        "rules/L4-decisions.json",
        "rules/L5-execution.json",
    ]

    configs = {}
    for config_file in config_files:
        config_path = PROJECT_ROOT / config_file
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    configs[config_file] = json.load(f)
            except Exception as e:
                logger.error(f"Error reading config {config_file}: {e}")
                configs[config_file] = {"error": str(e)}

    return JSONResponse(configs)


@app_instance.get("/api/health")
async def health_check():
    """健康检查"""
    return JSONResponse(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {"web_monitor": "running", "system_monitor": "running"},
        }
    )


# 工具函数
def update_system_status():
    """更新系统状态"""
    global system_status

    try:
        system_status.update(
            {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "last_update": datetime.now().isoformat(),
            }
        )

        # 检查服务状态
        system_status["services"] = {
            "backend_api": check_service_status(5000),
            "web_monitor": "running",
            "database": "unknown",
        }

    except Exception as e:
        logger.error(f"Error updating system status: {e}")


def check_service_status(port: int) -> str:
    """检查服务端口状态"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        return "running" if result == 0 else "stopped"
    except:
        return "unknown"


def scan_scripts() -> List[Dict[str, Any]]:
    """扫描脚本文件"""
    scripts = []
    scripts_dir = PROJECT_ROOT / "scripts"

    if scripts_dir.exists():
        for script_file in scripts_dir.glob("*.py"):
            if script_file.name.startswith("__"):
                continue

            scripts.append(
                {
                    "name": script_file.stem,
                    "path": str(script_file),
                    "size": script_file.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        script_file.stat().st_mtime
                    ).isoformat(),
                }
            )

    return scripts


def run_script_background(script_path: Path):
    """后台运行脚本"""
    try:
        logger.info(f"Running script: {script_path}")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,
        )

        logger.info(
            f"Script {script_path.name} completed with return code: {result.returncode}"
        )

        # 通过Socket.IO广播结果
        asyncio.run(
            sio.emit(
                "script_result",
                {
                    "script": script_path.name,
                    "return_code": result.returncode,
                    "stdout": result.stdout[-1000:],  # 最后1000字符
                    "stderr": result.stderr[-1000:],
                },
            )
        )

    except subprocess.TimeoutExpired:
        logger.error(f"Script {script_path} timed out")
    except Exception as e:
        logger.error(f"Error running script {script_path}: {e}")


# 后台任务
def background_monitor():
    """后台监控任务"""
    while True:
        try:
            update_system_status()
            # 广播状态更新
            asyncio.run(sio.emit("status_update", system_status))
            time.sleep(5)  # 每5秒更新一次
        except Exception as e:
            logger.error(f"Background monitor error: {e}")
            time.sleep(10)


# 启动后台监控
monitor_thread = threading.Thread(target=background_monitor, daemon=True)
monitor_thread.start()


def run(host: str = "0.0.0.0", port: int = 8080):
    """运行应用"""
    logger.info(f"Starting web monitor on {host}:{port}")
    uvicorn.run(
        "api.backend.web_monitor:socket_app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
