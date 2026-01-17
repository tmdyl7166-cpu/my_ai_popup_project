"""
Ollama客户端模块
提供与本地Ollama AI模型的交互功能
"""
import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime


class OllamaClient:
    """Ollama客户端"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.model = "llama3.2:3b"
        self.timeout = 300  # 5分钟超时
    
    def set_model(self, model: str):
        """设置使用的模型"""
        self.model = model
    
    def is_available(self) -> bool:
        """检查Ollama是否可用"""
        try:
            response = requests.get(f"{self.host}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出可用模型"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except:
            return []
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成文本响应
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            stream: 是否流式输出
            **kwargs: 其他参数（temperature, top_p, max_tokens等）
        
        Returns:
            生成的结果
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        
        except requests.exceptions.Timeout:
            return {"error": "Timeout", "message": "Request timed out"}
        except Exception as e:
            return {"error": "Exception", "message": str(e)}
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天对话
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            stream: 是否流式输出
            **kwargs: 其他参数
        
        Returns:
            聊天结果
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        
        except Exception as e:
            return {"error": "Exception", "message": str(e)}
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        分析图片
        
        Args:
            image_path: 图片路径
            prompt: 分析提示
        
        Returns:
            分析结果
        """
        # 读取图片并转换为base64
        import base64
        
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data]
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def understand_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        理解自然语言命令
        
        Args:
            command: 用户命令
            context: 上下文信息
        
        Returns:
            解析后的命令结构
        """
        system_prompt = """
你是一个AI命令解析器，负责将用户的自然语言命令解析为结构化的操作指令。
请理解用户的意图，并返回JSON格式的操作指令。

可用的操作类型：
1. "image_to_camera" - 图片合成到实时摄像头
2. "image_to_video" - 图片合成到视频
3. "video_to_camera" - 视频呈现到实时摄像头
4. "image_to_image" - 图片合成到图片
5. "analyze" - AI分析与理解
6. "create" - AI创造新内容

请返回JSON格式：
{
    "operation": "操作类型",
    "source": "源文件路径",
    "target": "目标文件路径或摄像头ID",
    "parameters": {
        "face_region": "人脸区域（可选）",
        "quality": "质量设置",
        "speed": "处理速度"
    },
    "description": "操作描述"
}
"""
        
        context_str = json.dumps(context, ensure_ascii=False) if context else "{}"
        
        user_prompt = f"""
上下文信息：
{context_str}

用户命令：
{command}

请解析这个命令并返回JSON格式的结果。
"""
        
        result = self.generate(user_prompt, system_prompt)
        
        if "response" in result:
            try:
                # 尝试解析JSON
                json_str = result["response"]
                # 提取JSON
                start = json_str.find("{")
                end = json_str.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(json_str[start:end])
            except:
                pass
        
        return {
            "operation": "unknown",
            "raw_command": command,
            "error": "无法解析命令"
        }
    
    def suggest_parameters(self, task_type: str, content_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据任务类型和内容信息建议参数
        
        Args:
            task_type: 任务类型
            content_info: 内容信息
        
        Returns:
            建议的参数
        """
        prompt = f"""
任务类型：{task_type}
内容信息：{json.dumps(content_info, ensure_ascii=False)}

根据以上信息，建议最佳的AI处理参数，包括：
- 处理质量
- 处理速度
- 人脸检测参数
- 增强选项

请返回JSON格式的参数建议。
"""
        
        result = self.generate(prompt)
        
        if "response" in result:
            try:
                json_str = result["response"]
                start = json_str.find("{")
                end = json_str.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(json_str[start:end])
            except:
                pass
        
        return {}


# 全局客户端实例
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client(host: str = "http://localhost:11434") -> OllamaClient:
    """获取Ollama客户端实例"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient(host)
    return _ollama_client

