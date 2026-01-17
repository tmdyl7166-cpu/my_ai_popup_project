"""
视频工具模块
提供视频处理和操作的功能
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Callable
from tqdm import tqdm


class VideoUtils:
    """视频工具类"""
    
    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {}
        
        info = {
            "path": video_path,
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "duration": 0,
            "codec": None,
            "is_open": True
        }
        
        # 计算时长
        if info["fps"] > 0:
            info["duration"] = info["frame_count"] / info["fps"]
        
        # 获取编码器
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        info["codec"] = chr(fourcc & 0xFF) + chr((fourcc >> 8) & 0xFF) + \
                       chr((fourcc >> 16) & 0xFF) + chr((fourcc >> 24) & 0xFF)
        
        cap.release()
        
        return info
    
    @staticmethod
    def read_frame(video_path: str, frame_number: int = 0) -> Optional[np.ndarray]:
        """读取特定帧"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        cap.release()
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame if ret else None
    
    @staticmethod
    def read_frames(
        video_path: str,
        start_frame: int = 0,
        end_frame: Optional[int] = None,
        step: int = 1
    ) -> List[np.ndarray]:
        """读取帧序列"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        frames = []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        end_frame = end_frame or total_frames - 1
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        current_frame = start_frame
        while current_frame <= end_frame:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
            current_frame += step
            
            # 跳帧
            for _ in range(step - 1):
                cap.read()
        
        cap.release()
        
        return frames
    
    @staticmethod
    def extract_frames(
        video_path: str,
        output_dir: str,
        prefix: str = "frame",
        format_: str = "jpg",
        quality: int = 95,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[str]:
        """提取所有帧为图片"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        frames = []
        frame_count = 0
        
        pbar = tqdm(total=total_frames, desc="Extracting frames")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 保存帧
            frame_path = f"{output_dir}/{prefix}_{frame_count:06d}.{format_}"
            cv2.imwrite(
                frame_path,
                cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
                [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            
            frames.append(frame_path)
            frame_count += 1
            
            if progress_callback:
                progress_callback(frame_count, total_frames)
            
            pbar.update(1)
        
        cap.release()
        pbar.close()
        
        return frames
    
    @staticmethod
    def create_video(
        images: List[np.ndarray],
        output_path: str,
        fps: float = 30,
        codec: str = "mp4v",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """从图片序列创建视频"""
        if not images:
            return False
        
        # 获取图片尺寸
        first_img = images[0]
        height, width = first_img.shape[:2]
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            return False
        
        pbar = tqdm(total=len(images), desc="Creating video")
        
        for i, img in enumerate(images):
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            out.write(img)
            
            if progress_callback:
                progress_callback(i + 1, len(images))
            
            pbar.update(1)
        
        out.release()
        pbar.close()
        
        return True
    
    @staticmethod
    def process_video(
        video_path: str,
        output_path: str,
        process_func: Callable[[np.ndarray, int], np.ndarray],
        fps: Optional[float] = None,
        codec: str = "mp4v",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """处理视频（逐帧处理）"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return False
        
        # 获取视频信息
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 确定输出fps
        output_fps = fps if fps else original_fps
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
        
        if not out.isOpened():
            return False
        
        pbar = tqdm(total=total_frames, desc="Processing video")
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 处理帧
            processed_frame = process_func(frame, frame_number)
            
            if processed_frame is not None:
                if len(processed_frame.shape) == 3:
                    processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)
                else:
                    processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
                out.write(processed_frame)
            
            frame_number += 1
            
            if progress_callback:
                progress_callback(frame_number, total_frames)
            
            pbar.update(1)
        
        cap.release()
        out.release()
        pbar.close()
        
        return True
    
    @staticmethod
    def get_video_writer(
        output_path: str,
        width: int,
        height: int,
        fps: float = 30,
        codec: str = "mp4v"
    ) -> cv2.VideoWriter:
        """获取视频写入器"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*codec)
        return cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    @staticmethod
    def get_video_capture(source: int = 0) -> cv2.VideoCapture:
        """获取摄像头捕获器"""
        return cv2.VideoCapture(source)
    
    @staticmethod
    def get_video_capture_by_path(video_path: str) -> cv2.VideoCapture:
        """获取视频文件捕获器"""
        return cv2.VideoCapture(video_path)

