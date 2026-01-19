# VS Code 扩展推荐文档

## 项目概述

本项目是一个基于 Python 的 AI 弹窗项目，涉及前端（PyQt5）、后端（FastAPI）、AI 处理（Ollama）、视频处理（OpenCV、MoviePy）以及第三方集成（Deep-Live-Cam、FaceFusion 等）。为确保高效开发和部署，以下是针对该项目的 VS Code 扩展推荐列表。

## 当前安装的扩展

以下是当前 VS Code 环境中已安装的扩展，按类别分组列出，每个扩展包括其作用、设置建议和使用说明。

### Python 开发相关

1. **ms-python.python** - Python 官方扩展
   - **作用**: 提供 Python 语言支持、代码高亮、语法检查等基础功能。
   - **设置**: 在 settings.json 中设置 Python 解释器路径。
   - **使用**: 自动检测虚拟环境，支持代码运行和调试。

2. **ms-python.vscode-pylance** - Pylance (基于 Pyright)
   - **作用**: 提供高级 Python 语言服务，包括类型检查、自动补全、智能提示。
   - **设置**: 启用 "python.languageServer": "Pylance"，配置类型检查级别为 "basic"。
   - **使用**: 提供更准确的代码提示和错误检测。

3. **ms-python.debugpy** - Python 调试器
   - **作用**: 提供 Python 代码调试功能，支持断点、变量查看等。
   - **设置**: 默认配置即可，支持 launch.json 中的调试配置。
   - **使用**: 在代码中设置断点，按 F5 启动调试。

4. **ms-python.flake8** - Flake8 代码检查
   - **作用**: 代码风格和错误检查工具。
   - **设置**: 在 settings.json 中启用 "python.linting.flake8Enabled": true。
   - **使用**: 自动检查代码风格问题。

5. **ms-python.vscode-python-envs** - Python 环境管理
   - **作用**: 管理多个 Python 环境和虚拟环境。
   - **设置**: 自动检测环境，无需额外配置。
   - **使用**: 在状态栏选择 Python 解释器。

6. **sourcery.sourcery** - AI 代码重构
   - **作用**: 提供智能代码重构建议。
   - **设置**: 登录 Sourcery 账户以启用高级功能。
   - **使用**: 右键选择 "Sourcery" 重构选项。

7. **cameron.vscode-pytest** - Pytest 测试运行器
   - **作用**: 运行和调试 Pytest 测试。
   - **设置**: 配置测试目录路径。
   - **使用**: 在测试文件中运行单个测试或全部测试。

### Git 和版本控制

8. **eamodio.gitlens** - GitLens
   - **作用**: 增强 Git 功能，提供 blame、历史记录等。
   - **设置**: 启用 "gitlens.currentLine.enabled": false 以减少干扰。
   - **使用**: 查看文件历史，按 Ctrl+Shift+G 打开 GitLens 面板。

9. **mhutchie.git-graph** - Git Graph
   - **作用**: 可视化 Git 提交图。
   - **设置**: 默认配置。
   - **使用**: 在命令面板中搜索 "Git Graph" 打开。

10. **gruntfuggly.todo-tree** - TODO Tree
    - **作用**: 高亮显示代码中的 TODO 注释。
    - **设置**: 配置标签如 "TODO", "FIXME"。
    - **使用**: 在侧边栏查看 TODO 列表。

11. **github.vscode-github-actions** - GitHub Actions
    - **作用**: 支持 GitHub Actions 工作流。
    - **设置**: 关联 GitHub 账户。
    - **使用**: 编辑和运行 Actions 工作流。

### Web 开发相关

12. **dbaeumer.vscode-eslint** - ESLint
    - **作用**: JavaScript/TypeScript 代码检查。
    - **设置**: 配置 .eslintrc 文件。
    - **使用**: 自动修复代码风格问题。

13. **esbenp.prettier-vscode** - Prettier
    - **作用**: 代码格式化工具。
    - **设置**: 设置默认格式化器为 Prettier。
    - **使用**: 保存时自动格式化，或手动格式化。

14. **christian-kohler.npm-intellisense** - NPM IntelliSense
    - **作用**: NPM 包自动补全。
    - **设置**: 默认启用。
    - **使用**: 在 package.json 中输入包名时提供补全。

15. **rangav.vscode-thunder-client** - Thunder Client
    - **作用**: API 测试工具，替代 Postman。
    - **设置**: 默认配置。
    - **使用**: 在侧边栏创建和运行 API 请求。

### Docker 和容器化

16. **ms-azuretools.vscode-containers** - Docker 容器扩展
    - **作用**: 管理 Docker 容器和镜像。
    - **设置**: 连接 Docker daemon。
    - **使用**: 在侧边栏查看容器状态。

17. **ms-vscode-remote.remote-containers** - Remote-Containers
    - **作用**: 在容器中开发。
    - **设置**: 使用 .devcontainer 配置。
    - **使用**: 重新打开文件夹在容器中。

### 其他工具

18. **blackboxapp.blackbox** - Blackbox AI
    - **作用**: AI 编程助手。
    - **设置**: 登录账户。
    - **使用**: 生成代码片段和解释代码。

19. **blackboxapp.blackboxagent** - Blackbox Agent
    - **作用**: AI 代理工具。
    - **设置**: 配置代理设置。
    - **使用**: 自动化任务。

20. **davidanson.vscode-markdownlint** - Markdown Lint
    - **作用**: Markdown 文件检查。
    - **设置**: 默认规则。
    - **使用**: 检查和修复 Markdown 语法。

21. **redhat.vscode-yaml** - YAML 支持
    - **作用**: YAML 文件语法高亮和验证。
    - **设置**: 默认启用。
    - **使用**: 编辑 YAML 配置文件。

22. **zainchen.json** - JSON 工具
    - **作用**: JSON 文件格式化和验证。
    - **设置**: 默认配置。
    - **使用**: 格式化 JSON 文件。

23. **aaron-bond.better-comments** - Better Comments
    - **作用**: 增强注释样式。
    - **设置**: 配置注释标签颜色。
    - **使用**: 使用特殊注释语法。

24. **ms-ceintl.vscode-language-pack-zh-hans** - 中文语言包
    - **作用**: VS Code 中文界面。
    - **设置**: 安装后重启。
    - **使用**: 自动启用中文界面。

## 推荐额外扩展

基于项目需求，以下是推荐安装的额外扩展，以提升开发效率。

### Python 增强

1. **ms-python.black-formatter** - Black 代码格式化
   - **作用**: 自动格式化 Python 代码。
   - **设置**: 设置为默认格式化器。
   - **推荐理由**: 保持代码风格一致。

2. **ms-python.isort** - isort 导入排序
   - **作用**: 自动排序 Python 导入语句。
   - **设置**: 启用 "python.sortImports.args": ["--profile", "black"]。
   - **推荐理由**: 改善代码可读性。

3. **ms-python.mypy-type-checker** - MyPy 类型检查
   - **作用**: 静态类型检查。
   - **设置**: 配置 mypy.ini 文件。
   - **推荐理由**: 提高代码质量。

### Web 开发

4. **ms-vscode.vscode-live-server** - Live Server
   - **作用**: 本地 Web 服务器，支持热重载。
   - **设置**: 默认配置。
   - **推荐理由**: 快速预览 HTML/JS 项目。

5. **bradlc.vscode-tailwindcss** - Tailwind CSS IntelliSense
   - **作用**: Tailwind CSS 类名补全。
   - **设置**: 检测 Tailwind 配置。
   - **推荐理由**: 项目使用 Bootstrap，可扩展到 Tailwind。

### Docker 增强

6. **ms-azuretools.vscode-docker** - Docker 扩展
   - **作用**: Docker 文件编辑和构建。
   - **设置**: 连接 Docker。
   - **推荐理由**: 项目涉及容器化部署。

### AI 和生产力

7. **github.copilot** - GitHub Copilot
   - **作用**: AI 代码补全。
   - **设置**: 登录 GitHub 账户。
   - **推荐理由**: 加速编码，尤其对 AI 项目有用。

8. **github.copilot-chat** - Copilot Chat
   - **作用**: AI 聊天助手。
   - **设置**: 与 Copilot 集成。
   - **推荐理由**: 代码解释和问题解决。

### 项目管理

9. **ms-vscode.vscode-json** - JSON 语言支持
   - **作用**: 增强 JSON 编辑。
   - **设置**: 默认启用。
   - **推荐理由**: 项目有大量 JSON 配置文件。

10. **redhat.vscode-xml** - XML 工具
    - **作用**: XML 文件支持。
    - **设置**: 默认配置。
    - **推荐理由**: 处理 XML 格式数据。

## 安装和配置建议

1. **批量安装**: 使用命令行安装多个扩展：
   ```bash
   code --install-extension ms-python.black-formatter ms-python.isort github.copilot
   ```

2. **设置同步**: 启用 VS Code 设置同步，确保多设备一致性。

3. **工作区设置**: 在项目根目录创建 .vscode/settings.json，配置项目特定设置：
   ```json
   {
     "python.defaultInterpreterPath": "./.venv/bin/python",
     "python.linting.enabled": true,
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "ms-python.black-formatter"
   }
   ```

4. **快捷键**: 自定义快捷键以提高效率，如格式化代码 (Shift+Alt+F)。

## 注意事项

- 某些扩展可能需要重启 VS Code 后生效。
- 根据项目具体需求调整扩展列表。
- 定期更新扩展以获取最新功能和修复。

此文档将根据项目发展持续更新。如有新需求，请及时添加相关扩展推荐。
