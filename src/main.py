"""
主入口模块
提供FastAPI应用和运行配置
"""
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入配置
from src.config.app_config import get_config

# 创建FastAPI应用
app = FastAPI(
    title="AI弹窗项目",
    description="AI人脸合成与处理服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取配置
config = get_config()

@app.get("/")
def read_root():
    """根路径"""
    return {
        "message": "欢迎使用AI弹窗项目",
        "version": config.version,
        "env": config.env
    }

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}

@app.get("/config")
def get_app_config():
    """获取应用配置（不包含敏感信息）"""
    return {
        "name": config.name,
        "version": config.version,
        "env": config.env,
        "api_host": config.api_host,
        "api_port": config.api_port,
        "assets_dir": str(config.assets_dir),
        "models_dir": str(config.models_dir),
        "output_dir": str(config.output_dir),
    }

def main():
    """主函数"""
    print(f"启动AI弹窗项目...")
    print(f"环境: {config.env}")
    print(f"版本: {config.version}")
    print(f"资源目录: {config.assets_dir}")
    print(f"模型目录: {config.models_dir}")
    print(f"API服务: http://{config.api_host}:{config.api_port}")
    
    uvicorn.run(
        app, 
        host=config.api_host, 
        port=config.api_port,
        reload=config.api_debug
    )

if __name__ == "__main__":
    main()

