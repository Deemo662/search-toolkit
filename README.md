# Search Toolkit — 多源搜索工具包

> 一个 Codex Skill 包，让 AI 能同时从网页、学术论文、GitHub 多个来源搜索信息。

## 给你朋友装了什么？

一个搜索工具箱，她可以在 Codex 里让 AI 帮她：

```bash
# 多源搜索（推荐，一次搜4个来源）
python3 scripts/search_pipeline.py multi "AI agent 最新进展"

# 搜学术论文
python3 scripts/search_pipeline.py academic "transformer architecture"

# 搜 GitHub 开源项目
python3 scripts/search_pipeline.py github "RAG agent"
```

## 网页搜索说明

**需要配置 API Key 才能用**，不配 Key 的话网页搜索不可用（直接用 Codex 默认搜索代替）。
其他功能（学术、GitHub、本地代码、多源）装好即用，不需要任何配置。

需要网页搜索的话 → 申请免费 Key：
1. 打开 https://console.volcengine.com/search-infinity/api-key
2. 用抖音/头条账号登录，创建 API Key（每月 500 次免费）
3. 设到环境变量：

```bash
export WEB_SEARCH_API_KEY="你的Key"
```

## 安装步骤

### 一步安装（推荐）

```bash
# 在 Codex 终端里运行
bash install.sh
```

### 手动安装

```bash
# 1. 复制到 skill 目录
cp -r search-toolkit-for-codex ~/.agents/skills/search-toolkit

# 2. 装依赖
pip3 install requests
```

## 配置网页搜索（可选，但推荐）

学术搜索和 GitHub 搜索装好即用，不需要任何配置。
网页搜索需要申请一个免费 API Key：

1. 打开 https://console.volcengine.com/search-infinity/api-key
2. 登录（可以用抖音/头条账号）
3. 创建一个 API Key（每月 500 次免费查询）
4. 把 Key 加到 shell 配置里：

```bash
# 编辑 ~/.zshrc，加一行
export WEB_SEARCH_API_KEY="你的Key"
```

## 验证

```bash
python3 scripts/search_pipeline.py academic "information retrieval"
# 应该能看到 arXiv 论文结果
```

## 文件结构

```
search-toolkit/
├── SKILL.md                 # Codex skill 声明
├── README.md                # 本文件
├── install.sh               # 一键安装
├── scripts/
│   ├── search_pipeline.py   # 主程序
│   └── requirements.txt     # Python 依赖
└── docs/
    └── SYSTEMATIC_SEARCH_SOP.md  # 完整使用方法（中文）
```
