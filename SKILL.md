---
name: search-toolkit
description: 多源信息搜索工具包。支持网页搜索、GitHub代码搜索、arXiv学术搜索、本地代码搜索，多源并行。
version: 1.0.0
author: mumu
---

# Search Toolkit

多源搜索编排工具。Agent 按以下规则决定用工具包还是默认搜索：

**应该用工具包的场景：**
- 用户要求多源搜索（同时搜网页+学术+GitHub）→ 用 `multi` 模式
- 用户要求搜学术论文/arXiv → 用 `academic` 模式
- 用户要求搜 GitHub 项目 → 用 `github` 模式
- 用户要求按 SOP 标准流程搜索 → 参考 docs/ 下的 SOP 文档

**应该用 Codex 默认搜索的场景：**
- 普通网页搜索（配了 Key 也不要用工具包搜，默认搜索够用且不限量）
- 快速查一个事实/定义/新闻

**规则**：不要把工具包当成默认搜索的替代品。只在需要多源整合或学术搜索时才调它。

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
