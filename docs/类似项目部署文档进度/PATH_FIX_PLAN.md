# AISP 路径修复计划

## 问题描述
修复路径挂载和路径指向问题，不使用挂载路径，所有文件和脚本的指向都使用硬连接以及整个项目AISP作为根目录的绝对路径。

## 根目录定义
- **项目根目录**: `/workspaces/AISP`
- **后端目录**: `/workspaces/AISP/backend`
- **配置目录**: `/workspaces/AISP/config`
- **数据目录**: `/workspaces/AISP/data`
- **日志目录**: `/workspaces/AISP/logs`
- **模型目录**: `/workspaces/AISP/models`

## 需要修改的文件

### 1. config/config_loader.py
**问题**: 硬编码容器路径 `/app/data`, `/app/logs`, `/app/models`
**修复**: 使用 `PROJECT_ROOT / "data"`, `PROJECT_ROOT / "logs"`, `PROJECT_ROOT / "models"`

**修改内容**:
```python
# 修改前
if IS_CONTAINER:
    data_dir = Path(os.environ.get("AISP_DATA_DIR", "/app/data"))
else:
    data_dir = PROJECT_ROOT / "data"

# 修改后
data_dir = PROJECT_ROOT / "data"
```

### 2. backend/path_utils.py (可能需要调整)
**问题**: 需要确保动态检测返回正确的 `/workspaces/AISP`
**检查**: 确保 `_detect_project_root()` 函数正确检测项目根目录

### 3. 验证并确保统一使用路径工具
确保所有模块使用 `from backend.path_utils import get_project_root` 获取路径

## 修改步骤

### 步骤1: 修复 config/config_loader.py
- [ ] 移除 `IS_CONTAINER` 检测逻辑
- [ ] 将所有容器挂载路径改为相对于 PROJECT_ROOT
- [ ] 确保数据、日志、模型目录都指向项目内目录

### 步骤2: 验证路径检测
- [ ] 验证 `backend/path_utils.py` 正确检测 `/workspaces/AISP`
- [ ] 确认没有其他地方使用硬编码路径

### 步骤3: 测试验证
- [ ] 执行 `python3 -c "import backend; print('backend导入成功')"`
- [ ] 验证配置加载器正常工作
- [ ] 验证所有路径指向正确

## 修改后预期结果
1. 所有路径使用 `/workspaces/AISP` 作为根目录
2. 不依赖任何挂载路径
3. `import backend` 可以正常导入
4. 配置加载器可以正常加载配置

