# AISP子文件夹配置文件创建计划

## 任务目标
为AISP中的每个子文件夹对应的项目在以自身子文件夹中创建对应的JSON配置和README.md

## L1 元目标层
保持并提升整个项目的结构一致性、逻辑一致性与可演化性。

## L2 全局理解层
### 已识别的子文件夹结构：
1. `backend` - 后端服务层
2. `gui` - GUI本地用户界面层
3. `engines` - 引擎基类
4. `docs` - 文档目录
5. `containers` - Docker容器配置
6. `scripts` - 自动化脚本目录
7. `virtual_cam` - 虚拟摄像头
8. `obs_integration` - OBS集成
9. `web` - 全项目Web监控层
10. `models` - 模型目录（空目录）
11. `.devcontainer` - 开发容器配置
12. `ollama-models` - Ollama模型目录（空目录）

### 排除的目录：
- `.venv` 和 `venv` - Python虚拟环境
- `.git` - Git仓库
- `__pycache__` - Python缓存目录

## L3 约束层
1. 配置文件必须使用JSON格式
2. README.md必须使用中文描述
3. 配置内容必须准确反映子文件夹的实际功能
4. 保持与directory_structure.json的一致性
5. 配置文件命名统一为 `config.json`

## L4 决策层
### 为每个子文件夹创建：
1. **JSON配置** (`config.json`)
   - 项目名称和版本
   - 目录路径和描述
   - 模块列表和功能说明
   - 依赖关系
   - 配置参数

2. **README.md**
   - 项目概述
   - 主要功能
   - 文件结构
   - 使用说明
   - 依赖关系

### 执行顺序（按重要性排序）：
1. backend（核心后端服务）
2. gui（用户界面）
3. engines（引擎基类）
4. docs（文档目录）
5. containers（容器配置）
6. scripts（脚本目录）
7. virtual_cam（虚拟摄像头）
8. obs_integration（OBS集成）
9. web（Web监控层）
10. models（模型目录）
11. .devcontainer（开发容器）
12. ollama-models（模型目录）

## L5 执行层
### 步骤：
1. 逐个子文件夹创建 `config.json`
2. 逐个子文件夹创建 `README.md`
3. 验证配置文件的正确性
4. 确保JSON格式有效
5. 更新目录结构文档

## 验证标准
- 所有子文件夹都有对应的配置文件
- JSON格式有效
- README内容准确
- 与现有项目结构保持一致

