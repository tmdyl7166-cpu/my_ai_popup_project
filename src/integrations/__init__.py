"""集成模块"""
from src.integrations.deep_live_cam import DeepLiveCam
from src.integrations.facefusion import FaceFusion
from src.integrations.iroop_deepfacecam import IRoopDeepFaceCam

__all__ = ["DeepLiveCam", "FaceFusion", "IRoopDeepFaceCam"]

