#!/usr/bin/env python3
"""
my_ai_popup_project FastAPI服务器

提供REST API接口，支持实时通信和任务管理。
"""

import asyncio
import json
import os
import signal
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from ...utils.logger import get_logger
from .state_manager import state_manager
from .pipeline_manager import pipeline_manager


# 请求/响应模型
class TaskRequest(BaseModel):
    """任务请求"""
    task_type: str = Field(..., description="任务类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="任务参数")
    priority: int = Field(1, description="任务优先级", ge=1, le=10)


class PipelineRequest(BaseModel):
    """管道请求"""
    name: str
    tasks: List[Dict[str, Any]] = Field(..., description="任务列表")
    metadata: Optional[Dict[str, Any]] = None


class StatusResponse(BaseModel):
    """状态响应"""
    status: str
    timestamp: float
    data: Dict[str, Any]


# 全局变量
logger = get_logger(__name__)
active_connections: List[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("启动 my_ai_popup_project API服务器")

    # 初始化状态管理器
    await state_manager.initialize()

    # 注册服务
    state_manager.register_service("api_server", port=8000)

    # 设置信号处理
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，开始关闭服务器")
        asyncio.create_task(shutdown_server())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    yield

    # 关闭时
    logger.info("关闭 my_ai_popup_project API服务器")
    await state_manager.cleanup()
    state_manager.unregister_service("api_server")


async def shutdown_server():
    """关闭服务器"""
    logger.info("执行服务器关闭流程")

    # 取消所有运行中的管道
    for pipeline_id in list(pipeline_manager.get_all_pipelines().keys()):
        try:
            await pipeline_manager.cancel_pipeline(pipeline_id)
        except Exception as e:
            logger.error(f"取消管道 {pipeline_id} 失败: {e}")

    # 关闭所有WebSocket连接
    for connection in active_connections[:]:
        try:
            await connection.close()
        except Exception:
            pass

    # 强制退出
    os._exit(0)


# 创建FastAPI应用
app = FastAPI(
    title="my_ai_popup_project API",
    description="AI弹窗项目的REST API接口",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 路由处理器
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "my_ai_popup_project API服务器",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    system_info = state_manager.get_system_info()

    return StatusResponse(
        status="healthy" if system_info["services_count"] > 0 else "degraded",
        timestamp=time.time(),
        data={
            "system": system_info,
            "services": state_manager.get_all_services(),
            "pipelines": pipeline_manager.get_stats()
        }
    )


@app.get("/status")
async def get_status():
    """获取系统状态"""
    return StatusResponse(
        status="ok",
        timestamp=time.time(),
        data={
            "system": state_manager.get_system_info(),
            "services": state_manager.get_all_services(),
            "pipelines": pipeline_manager.get_stats()
        }
    )


@app.post("/pipelines")
async def create_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """创建处理管道"""
    try:
        pipeline_id = f"pipeline_{int(time.time())}_{len(pipeline_manager.get_all_pipelines())}"

        pipeline = await pipeline_manager.create_pipeline(
            pipeline_id=pipeline_id,
            name=request.name,
            tasks=request.tasks,
            metadata=request.metadata
        )

        # 启动管道执行
        background_tasks.add_task(execute_pipeline_background, pipeline_id)

        return {
            "pipeline_id": pipeline_id,
            "status": "created",
            "message": f"管道 '{request.name}' 已创建并开始执行"
        }

    except Exception as e:
        logger.error(f"创建管道失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建管道失败: {str(e)}")


async def execute_pipeline_background(pipeline_id: str):
    """后台执行管道"""
    try:
        await pipeline_manager.execute_pipeline(pipeline_id)
        logger.info(f"管道 {pipeline_id} 执行完成")

        # 广播状态更新
        await broadcast_status_update({
            "type": "pipeline_completed",
            "pipeline_id": pipeline_id
        })

    except Exception as e:
        logger.error(f"管道 {pipeline_id} 执行失败: {e}")

        # 广播错误
        await broadcast_status_update({
            "type": "pipeline_failed",
            "pipeline_id": pipeline_id,
            "error": str(e)
        })


@app.get("/pipelines")
async def list_pipelines():
    """列出所有管道"""
    pipelines = pipeline_manager.get_all_pipelines()

    return {
        "pipelines": [
            {
                "id": pid,
                "name": pipeline.name,
                "status": pipeline.status.value,
                "progress": pipeline.progress,
                "created_at": pipeline.start_time
            }
            for pid, pipeline in pipelines.items()
        ]
    }


@app.get("/pipelines/{pipeline_id}")
async def get_pipeline(pipeline_id: str):
    """获取管道详情"""
    status = pipeline_manager.get_pipeline_status(pipeline_id)

    if not status:
        raise HTTPException(status_code=404, detail=f"管道 {pipeline_id} 不存在")

    return status


@app.delete("/pipelines/{pipeline_id}")
async def cancel_pipeline(pipeline_id: str):
    """取消管道执行"""
    success = await pipeline_manager.cancel_pipeline(pipeline_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"管道 {pipeline_id} 不存在或无法取消")

    return {"message": f"管道 {pipeline_id} 已取消"}


@app.post("/tasks")
async def create_task(request: TaskRequest):
    """创建单个任务"""
    try:
        # 创建单任务管道
        pipeline_id = f"task_{int(time.time())}_{hash(str(request.dict()))}"

        task_data = {
            "id": "main_task",
            "name": f"{request.task_type} 任务",
            "callback": get_task_callback(request.task_type),
            "parameters": request.parameters
        }

        pipeline = await pipeline_manager.create_pipeline(
            pipeline_id=pipeline_id,
            name=f"单任务: {request.task_type}",
            tasks=[task_data]
        )

        # 异步执行
        asyncio.create_task(execute_pipeline_background(pipeline_id))

        return {
            "task_id": pipeline_id,
            "status": "accepted",
            "message": f"任务 '{request.task_type}' 已接受处理"
        }

    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


def get_task_callback(task_type: str):
    """获取任务回调函数"""
    # 这里应该根据任务类型返回相应的处理函数
    # 暂时返回一个模拟函数

    async def mock_task(**kwargs):
        await asyncio.sleep(1)  # 模拟处理时间
        return {"result": f"任务 {task_type} 已完成", "parameters": kwargs}

    return mock_task


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "welcome",
            "message": "已连接到 my_ai_popup_project WebSocket",
            "timestamp": time.time()
        })

        while True:
            # 接收消息
            data = await websocket.receive_json()

            # 处理消息
            response = await handle_websocket_message(data)
            await websocket.send_json(response)

    except WebSocketDisconnect:
        logger.info("WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


async def handle_websocket_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """处理WebSocket消息"""
    message_type = data.get("type", "unknown")

    if message_type == "ping":
        return {
            "type": "pong",
            "timestamp": time.time()
        }

    elif message_type == "get_status":
        system_info = state_manager.get_system_info()
        return {
            "type": "status",
            "data": system_info,
            "timestamp": time.time()
        }

    elif message_type == "subscribe_pipeline":
        pipeline_id = data.get("pipeline_id")
        if pipeline_id:
            # 这里可以实现管道状态订阅逻辑
            return {
                "type": "subscribed",
                "pipeline_id": pipeline_id,
                "timestamp": time.time()
            }

    return {
        "type": "error",
        "message": f"未知消息类型: {message_type}",
        "timestamp": time.time()
    }


async def broadcast_status_update(data: Dict[str, Any]):
    """广播状态更新到所有WebSocket连接"""
    disconnected = []

    for connection in active_connections:
        try:
            await connection.send_json({
                "type": "status_update",
                "data": data,
                "timestamp": time.time()
            })
        except Exception:
            disconnected.append(connection)

    # 清理断开的连接
    for connection in disconnected:
        if connection in active_connections:
            active_connections.remove(connection)


# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "detail": str(exc),
            "timestamp": time.time()
        }
    )


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="my_ai_popup_project API服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")

    args = parser.parse_args()

    logger.info(f"启动服务器: {args.host}:{args.port}")

    # 配置uvicorn
    config = uvicorn.Config(
        app=app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

    server = uvicorn.Server(config)

    # 运行服务器
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭服务器")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
