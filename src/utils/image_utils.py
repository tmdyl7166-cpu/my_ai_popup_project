"""
图像工具模块
提供图像处理和操作的功能
"""
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import cv2


class ImageUtils:
    """图像工具类"""
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """加载图片"""
        img = cv2.imread(image_path)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str, quality: int = 95) -> bool:
        """保存图片"""
        if image is None:
            return False
        
        # 转换颜色空间
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 保存图片
        return cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    
    @staticmethod
    def resize_image(
        image: np.ndarray,
        target_size: Tuple[int, int],
        maintain_aspect_ratio: bool = True
    ) -> np.ndarray:
        """调整图片大小"""
        if image is None:
            return None
        
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        if maintain_aspect_ratio:
            # 保持宽高比
            ratio = min(target_w / w, target_h / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
        else:
            new_w, new_h = target_w, target_h
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def crop_image(
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> np.ndarray:
        """裁剪图片"""
        if image is None:
            return None
        
        h, w = image.shape[:2]
        
        # 确保坐标在范围内
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        width = min(width, w - x)
        height = min(height, h - y)
        
        return image[y:y + height, x:x + width]
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """旋转图片"""
        if image is None:
            return None
        
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # 计算旋转矩阵
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 旋转图片
        return cv2.warpAffine(
            image, matrix, (w, h),
            borderMode=cv2.BORDER_REFLECT
        )
    
    @staticmethod
    def flip_image(image: np.ndarray, horizontal: bool = True, vertical: bool = False) -> np.ndarray:
        """翻转图片"""
        if image is None:
            return None
        
        flags = []
        if horizontal:
            flags.append(1)
        if vertical:
            flags.append(0)
        
        for flag in flags:
            image = cv2.flip(image, flag)
        
        return image
    
    @staticmethod
    def adjust_brightness(image: np.ndarray, factor: float) -> np.ndarray:
        """调整亮度"""
        if image is None:
            return None
        
        img = Image.fromarray(image)
        enhancer = ImageEnhance.Brightness(img)
        return np.array(enhancer.enhance(factor))
    
    @staticmethod
    def adjust_contrast(image: np.ndarray, factor: float) -> np.ndarray:
        """调整对比度"""
        if image is None:
            return None
        
        img = Image.fromarray(image)
        enhancer = ImageEnhance.Contrast(img)
        return np.array(enhancer.enhance(factor))
    
    @staticmethod
    def adjust_saturation(image: np.ndarray, factor: float) -> np.ndarray:
        """调整饱和度"""
        if image is None:
            return None
        
        img = Image.fromarray(image)
        enhancer = ImageEnhance.Color(img)
        return np.array(enhancer.enhance(factor))
    
    @staticmethod
    def apply_blur(image: np.ndarray, radius: float = 5) -> np.ndarray:
        """应用模糊"""
        if image is None:
            return None
        
        img = Image.fromarray(image)
        blurred = img.filter(ImageFilter.GaussianBlur(radius))
        return np.array(blurred)
    
    @staticmethod
    def apply_sharpness(image: np.ndarray, factor: float) -> np.ndarray:
        """应用锐化"""
        if image is None:
            return None
        
        img = Image.fromarray(image)
        enhancer = ImageEnhance.Sharpness(img)
        return np.array(enhancer.enhance(factor))
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """转换为灰度图"""
        if image is None:
            return None
        
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    @staticmethod
    def convert_to_rgb(image: np.ndarray) -> np.ndarray:
        """转换为RGB格式"""
        if image is None:
            return None
        
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        return image
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """获取图片信息"""
        img = ImageUtils.load_image(image_path)
        if img is None:
            return {}
        
        h, w = img.shape[:2]
        
        return {
            "path": image_path,
            "width": w,
            "height": h,
            "channels": img.shape[2] if len(img.shape) == 3 else 1,
            "dtype": str(img.dtype),
            "size": img.nbytes,
        }
    
    @staticmethod
    def create_thumbnail(
        image_path: str,
        output_path: str,
        max_size: Tuple[int, int] = (200, 200)
    ) -> bool:
        """创建缩略图"""
        img = ImageUtils.load_image(image_path)
        if img is None:
            return False
        
        # 调整大小
        thumbnail = ImageUtils.resize_image(img, max_size)
        
        # 保存
        return ImageUtils.save_image(thumbnail, output_path, quality=85)
    
    @staticmethod
    def concatenate_images(
        images: List[np.ndarray],
        direction: str = "horizontal",
        spacing: int = 10,
        background_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> np.ndarray:
        """拼接多张图片"""
        if not images:
            return None
        
        if direction == "horizontal":
            # 水平拼接
            total_width = sum(img.shape[1] for img in images) + spacing * (len(images) - 1)
            max_height = max(img.shape[0] for img in images)
            
            result = np.full(
                (max_height, total_width, 3),
                background_color,
                dtype=np.uint8
            )
            
            x_offset = 0
            for img in images:
                h, w = img.shape[:2]
                y_offset = (max_height - h) // 2
                result[y_offset:y_offset + h, x_offset:x_offset + w] = img
                x_offset += w + spacing
        
        else:
            # 垂直拼接
            total_height = sum(img.shape[0] for img in images) + spacing * (len(images) - 1)
            max_width = max(img.shape[1] for img in images)
            
            result = np.full(
                (total_height, max_width, 3),
                background_color,
                dtype=np.uint8
            )
            
            y_offset = 0
            for img in images:
                h, w = img.shape[:2]
                x_offset = (max_width - w) // 2
                result[y_offset:y_offset + h, x_offset:x_offset + w] = img
                y_offset += h + spacing
        
        return result

