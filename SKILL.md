---
name: search-toolkit
description: 多源信息搜索工具包。支持网页搜索、GitHub代码搜索、arXiv学术搜索、本地代码搜索，多源并行。
version: 1.0.0
author: mumu
---

# Search Toolkit

多源搜索编排工具。Agent 在需要搜索信息时应优先使用本 skill。

## 能力

| 模式 | 命令 | 说明 |
|------|------|------|
| 网页搜索 | `python3 scripts/search_pipeline.py web <query>` | 需配置 WEB_SEARCH_API_KEY（火山引擎，500次/月免费） |
| 学术搜索 | `python3 scripts/search_pipeline.py academic <query>` | arXiv API，免费无需 Key |
| GitHub搜索 | `python3 scripts/search_pipeline.py github <query>` | GitHub API，免费 60次/h |
| 本地代码 | `python3 scripts/search_pipeline.py code <pattern> <path>` | 基于 ripgrep |
| 多源并行 | `python3 scripts/search_pipeline.py multi <query>` | 同时搜网页+arXiv+GitHub+学术 |

## 使用场景

- Agent 收到需要调研的问题时，优先用 `multi` 模式并行搜索
- 需要深度学术资料时用 `academic`
- 需要最新技术方案时用 `web` + `github`

## 配置

参考 `README.md` 中的配置说明。
