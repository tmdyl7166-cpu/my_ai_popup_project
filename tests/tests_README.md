# 测试系统 (tests/)

## 概述

本目录包含项目的完整测试套件，包括单元测试、集成测试、端到端测试和性能测试。测试系统采用模块化设计，确保代码质量和系统稳定性。

## 目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── tests_config.json        # 测试配置
├── tests_README.md          # 本文档
├── test_ai/                 # AI模块测试
├── test_api/                # API接口测试
├── test_processing/         # 处理引擎测试
└── test_ui/                 # UI界面测试
```

## 测试类型

### 1. 单元测试 (Unit Tests)
- **位置**: `test_*.py`
- **范围**: 单个函数/方法
- **目的**: 验证代码逻辑正确性
- **覆盖率目标**: 85%

### 2. 集成测试 (Integration Tests)
- **位置**: `test_integration_*.py`
- **范围**: 模块间交互
- **目的**: 验证模块协作
- **覆盖率目标**: 75%

### 3. 端到端测试 (E2E Tests)
- **位置**: `test_e2e_*.py`
- **范围**: 完整用户流程
- **目的**: 验证完整功能
- **覆盖率目标**: 70%

### 4. 性能测试 (Performance Tests)
- **位置**: `test_performance_*.py`
- **范围**: 系统性能指标
- **目的**: 验证性能要求
- **覆盖率目标**: N/A

## 执行方式

### 本地执行

```bash
# 运行所有测试
pytest

# 运行特定测试模块
pytest tests/test_ai/
pytest tests/test_api/

# 运行带覆盖率报告
pytest --cov=src --cov-report=html

# 运行性能测试
pytest tests/test_performance_*.py -v
```

### CI/CD 执行

测试在以下时机自动执行：
- **Pre-commit**: 单元测试
- **Daily**: 单元测试 + 集成测试
- **Weekly**: 全量测试
- **Release**: 全量测试 + 90%覆盖率检查

## 测试配置

详细配置请参考 `tests_config.json`：

- **框架**: pytest + 插件
- **覆盖率**: 最低80%
- **并行化**: 自动检测CPU核心数
- **报告**: HTML/XML/JSON格式

## 编写测试

### 单元测试示例

```python
import pytest
from src.ai.ollama_client import OllamaClient

class TestOllamaClient:
    def test_initialization(self):
        client = OllamaClient()
        assert client.host == "http://localhost:11434"

    def test_command_parsing(self):
        client = OllamaClient()
        result = client.parse_command("将图片A合成到视频B")
        assert "action" in result
        assert result["action"] == "image_to_video"
```

### 集成测试示例

```python
import pytest
from src.backend.task_manager import TaskManager
from src.processing.batch_processor import BatchProcessor

class TestTaskProcessingIntegration:
    def test_task_creation_and_processing(self):
        manager = TaskManager()
        processor = BatchProcessor()

        # 创建任务
        task_id = manager.create_task({
            "type": "image_to_video",
            "source": "test.jpg",
            "target": "test.mp4"
        })

        # 处理任务
        result = processor.process_task(task_id)

        assert result["status"] == "completed"
        assert "output_path" in result
```

## 模拟和Mock

### 外部依赖Mock

```python
import pytest
from unittest.mock import Mock, patch

class TestWithMocks:
    @patch('src.ai.ollama_client.OllamaClient.call_api')
    def test_api_call_with_mock(self, mock_call):
        mock_call.return_value = {"status": "success"}

        client = OllamaClient()
        result = client.process_request("test")

        assert result["status"] == "success"
        mock_call.assert_called_once()
```

## 测试数据

### 测试资源位置

- **测试图片**: `assets/images/test/`
- **测试视频**: `assets/videos/test/`
- **测试模型**: `assets/models/test/`
- **配置文件**: `tests/test_data/`

### 数据生成

```python
import numpy as np
from PIL import Image

def create_test_image(width=640, height=480):
    """生成测试图片"""
    return Image.fromarray(np.random.randint(0, 255, (height, width, 3), dtype=np.uint8))

def create_test_video(duration=5, fps=30):
    """生成测试视频"""
    # 实现视频生成逻辑
    pass
```

## 性能基准

### 关键性能指标

| 测试类型 | 指标 | 目标值 | 当前值 |
|---------|------|--------|--------|
| 图像处理 | 处理时间 | <2s | - |
| 视频处理 | 处理速度 | >5fps | - |
| 实时处理 | 延迟 | <100ms | - |
| 内存使用 | 峰值内存 | <2GB | - |

### 性能测试执行

```bash
# 运行性能基准测试
pytest tests/test_performance_*.py --benchmark-only

# 生成性能报告
pytest tests/test_performance_*.py --benchmark-histogram
```

## 持续集成

### GitHub Actions 配置

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 维护指南

### 添加新测试

1. 在相应目录创建测试文件
2. 遵循命名约定: `test_*.py`
3. 添加必要的mock和fixture
4. 更新覆盖率目标

### 测试失败处理

1. 检查测试环境配置
2. 验证依赖项版本
3. 查看详细错误日志
4. 更新测试用例或代码

### 清理和归档

- 测试报告保留30天
- 覆盖率报告保留90天
- 性能基准数据永久保留

## 相关链接

- [pytest 文档](https://docs.pytest.org/)
- [覆盖率配置](https://coverage.readthedocs.io/)
- [CI/CD 配置](../.github/workflows/)
- [项目配置](../project_config.json)
