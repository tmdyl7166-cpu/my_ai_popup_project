# 配置模块 (config/)

## 概述

`config/` 模块负责整个系统的配置管理，是系统的"配置中心"，提供统一的配置加载、验证和访问接口。

## 目录结构

```
config/
├── __init__.py                    # 模块初始化文件
├── config_config.json            # 配置模块配置定义文件
├── config_README.md              # 配置模块说明文档
└── app_config.py                 # 应用配置管理类
```

## 核心职责

1. **配置加载**: 从多种来源加载配置
2. **环境适配**: 根据环境调整配置
3. **配置验证**: 验证配置的正确性和完整性
4. **配置访问**: 提供类型安全的配置访问

## 模块组成

### app_config.py - 应用配置
- **功能**: 主应用配置管理
- **特性**:
  - 数据类配置定义
  - 环境变量支持
  - 类型验证
  - 单例模式

### settings.json - JSON配置
- **功能**: 静态配置存储
- **内容**: 应用设置、UI配置、默认值

### 环境配置
- **.env**: 环境变量文件
- **环境特定配置**: 开发/生产环境配置

## 配置层次

### 1. 默认配置 (代码中)
```python
@dataclass
class AppConfig:
    name: str = "AI弹窗项目"
    version: str = "1.0.0"
    # ... 其他默认值
```

### 2. 环境变量覆盖
```bash
export APP_NAME="自定义名称"
export API_PORT=9000
```

### 3. 配置文件覆盖
```json
{
  "app": {
    "name": "配置文件名称",
    "debug": true
  }
}
```

### 4. 运行时覆盖
```python
config = get_config()
config.api_port = 9000  # 运行时修改
```

## 配置加载流程

```
启动应用 → 加载默认配置 → 读取环境变量 → 加载配置文件 → 验证配置 → 初始化完成
```

## 配置分类

### 应用配置
- **应用信息**: 名称、版本、环境
- **服务配置**: 主机、端口、调试模式
- **性能配置**: 工作线程数、超时时间

### AI配置
- **Ollama设置**: 主机、模型、超时
- **人脸识别**: 默认引擎、备用引擎
- **GPU配置**: 内存分配、设备选择

### 路径配置
- **项目路径**: 根目录、资源目录
- **输出路径**: 结果保存目录
- **临时路径**: 临时文件目录

### UI配置
- **界面设置**: 主题、语言、布局
- **窗口配置**: 大小、位置、状态

## 开发指南

### 使用配置
```python
from src.config.app_config import get_config

# 获取配置实例
config = get_config()

# 访问配置值
app_name = config.name
api_port = config.api_port
ollama_host = config.ollama_host
```

### 修改配置
```python
# 运行时修改
config.api_debug = True

# 重新加载配置
from src.config.app_config import reload_config
reload_config()
```

### 添加新配置
1. 在 `AppConfig` 类中添加字段
2. 设置默认值和类型
3. 添加环境变量支持
4. 更新文档

## 配置验证

### 类型验证
- 使用 `dataclass` 自动类型检查
- Pydantic 模型验证
- 自定义验证函数

### 值验证
```python
def validate_config(config: AppConfig) -> bool:
    """验证配置值"""
    if config.api_port < 1024 or config.api_port > 65535:
        raise ValueError("API端口必须在1024-65535之间")

    if config.max_workers < 1:
        raise ValueError("最大工作线程数必须大于0")

    return True
```

## 环境管理

### 开发环境
```bash
# .env.development
APP_ENV=development
API_DEBUG=true
LOG_LEVEL=DEBUG
```

### 生产环境
```bash
# .env.production
APP_ENV=production
API_DEBUG=false
LOG_LEVEL=INFO
```

### 配置切换
```python
if config.env == "development":
    # 开发环境特殊配置
    pass
elif config.env == "production":
    # 生产环境特殊配置
    pass
```

## 安全考虑

### 敏感信息
- **密码**: 使用环境变量，不写入代码
- **密钥**: 加密存储，运行时解密
- **路径**: 验证路径安全性

### 访问控制
- **只读配置**: 防止运行时意外修改
- **权限检查**: 验证文件访问权限
- **审计日志**: 记录配置变更

## 性能优化

### 缓存策略
- **配置缓存**: 单例模式避免重复加载
- **热重载**: 支持配置热更新
- **懒加载**: 按需加载大型配置

### 内存管理
- **对象复用**: 复用配置对象
- **垃圾回收**: 及时清理旧配置
- **内存监控**: 监控配置对象大小

## 监控和调试

### 配置状态
```python
# 查看当前配置
print(config)

# 导出配置
config_dict = config.to_dict()

# 验证配置
is_valid = validate_config(config)
```

### 调试支持
- **配置转储**: 输出所有配置值
- **变更跟踪**: 记录配置修改历史
- **错误诊断**: 详细的验证错误信息

## 故障排除

### 常见问题
1. **配置加载失败**: 检查文件路径和权限
2. **环境变量无效**: 验证变量名和值
3. **类型错误**: 检查配置值的类型
4. **路径不存在**: 验证目录结构

### 调试技巧
1. **启用调试日志**: 查看配置加载过程
2. **手动验证**: 逐个检查配置值
3. **回滚配置**: 恢复到默认配置

## 最佳实践

### 配置设计
- **分层配置**: 不同层级不同配置
- **默认值**: 提供合理的默认值
- **文档化**: 详细注释配置用途
- **验证**: 严格的配置验证

### 维护建议
- **版本控制**: 配置变更纳入版本控制
- **文档同步**: 更新代码时同步更新配置文档
- **定期review**: 定期检查配置合理性
- **自动化测试**: 配置相关的自动化测试

## 扩展开发

新增配置时请：
1. 确定配置的作用域和生命周期
2. 设计合理的默认值
3. 添加类型提示和验证
4. 提供环境变量支持
5. 更新文档和示例
6. 添加单元测试
