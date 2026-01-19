#!/usr/bin/env python3
"""
路径验证脚本
验证项目路径配置是否正确
"""
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

try:
    from src.utils.path_resolver import PathResolver, ensure_project_structure
    path_resolver = PathResolver()
except ImportError:
    # 如果导入失败，尝试直接导入
    import importlib.util
    path_resolver_path = PROJECT_ROOT / 'src' / 'utils' / 'path_resolver.py'
    spec = importlib.util.spec_from_file_location("path_resolver", path_resolver_path)
    path_resolver_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(path_resolver_module)
    path_resolver = path_resolver_module.PathResolver()
    ensure_project_structure = path_resolver_module.ensure_project_structure

def main():
    """主函数"""
    print("=" * 60)
    print("AI弹窗项目 - 路径验证")
    print("=" * 60)
    
    # 获取项目根目录
    project_root = path_resolver.get_project_root()
    print(f"\n项目根目录: {project_root}")
    print(f"项目名称: {project_root.name}")
    
    # 验证是否为正确的项目目录
    if project_root.name != "my_ai_popup_project":
        print(f"\n⚠️ 警告: 项目目录名称不是 'my_ai_popup_project'")
        print(f"当前名称: {project_root.name}")
        return False
    
    # 确保目录结构完整
    print("\n检查目录结构...")
    ensure_project_structure()
    
    # 显示所有关键路径
    print("\n关键路径:")
    print(f"  项目根目录: {path_resolver.get_project_root()}")
    print(f"  资源目录: {path_resolver.get_assets_dir()}")
    print(f"  模型目录: {path_resolver.get_models_dir()}")
    print(f"  图片目录: {path_resolver.get_images_dir()}")
    print(f"  视频目录: {path_resolver.get_videos_dir()}")
    print(f"  输出目录: {path_resolver.get_output_dir()}")
    print(f"  日志目录: {path_resolver.get_logs_dir()}")
    print(f"  源代码目录: {path_resolver.get_src_dir()}")
    print(f"  临时目录: {path_resolver.get_temp_dir()}")
    
    # 检查子模块目录
    print("\n子模块路径:")
    print(f"  Deep-Live-Cam: {path_resolver.get_deep_live_cam_dir()}")
    print(f"  FaceFusion: {path_resolver.get_facefusion_dir()}")
    print(f"  iRoopDeepFaceCam: {path_resolver.get_iroop_deepfacecam_dir()}")
    
    # 验证关键目录是否存在
    print("\n验证目录存在性...")
    critical_dirs = [
        ("资源目录", path_resolver.get_assets_dir()),
        ("模型目录", path_resolver.get_models_dir()),
        ("日志目录", path_resolver.get_logs_dir()),
        ("源代码目录", path_resolver.get_src_dir()),
    ]
    
    all_ok = True
    for name, dir_path in critical_dirs:
        exists = dir_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {name}: {dir_path}")
        if not exists:
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ 路径验证成功!")
        print("=" * 60)
        return True
    else:
        print("✗ 路径验证失败，某些关键目录不存在")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

