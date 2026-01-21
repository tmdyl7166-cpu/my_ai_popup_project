# 🔗 Web API 接口映射与配置说明

## 概述

本文档定义了 web 应用中所有 API 接口的映射关系，包括：

- 前端模块与后端脚本的对应关系
- 接口配置规则说明
- 统一的 JSON 配置结构

## 目录结构

```
web/api/
├── README.md              # 本文档
├── api_mapping.json       # 接口映射配置
└── frontend_mapping.md    # 前端模块映射说明
```

## 快速开始

```bash
# 启动 Web 服务
python3 web/app.py --host 0.0.0.0 --port 8080

# 访问 API 文档
# GET http://localhost:8080/api/scripts/list
```

## 接口映射配置

接口映射配置存储在 `api_mapping.json` 文件中，包含：

- 接口路径
- 调用的后端脚本
- 配置规则
- 参数说明

## 详细文档

请参考以下文档：

- `api_mapping.json` - 完整的接口映射配置
- 父目录 `docs/project_docs/API接口说明.md` - 完整的 API 接口说明

---

_最后更新: 2026-01-21_
