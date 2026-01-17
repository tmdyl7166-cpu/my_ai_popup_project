"""
系统监控器
负责系统资源监控和状态检查
"""
import psutil
import time
from typing import Dict, Any

class SystemMonitor:
    """系统监控器"""
    
    def get_system_resources(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'timestamp': time.time()
            }
        except Exception as e:
            return {'error': str(e)}
