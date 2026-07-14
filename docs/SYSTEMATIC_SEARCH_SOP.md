# Systematic Search SOP

> 系统性信息搜集标准流程 — 多源、可审计、可复现
> 版本 1.0 | 2026-07-14

---

## 工作流总览

[Intake] -> [Decompose] -> [Route] -> [Execute] -> [Triangulate] -> [Synthesize] -> [Archive]
    ^                                                                                   |
    +--------------------------- 不够就回退 ----------------------------------------------+

7 个阶段，每个阶段有明确入口标准和完成标准。不满足完成标准就回退到前一个阶段。

---

## Phase 0: Intake（任务接单）

**入口**：收到一个需要搜索的问题

**动作**：

1. **澄清问题** -- 用 1-2 句话确认实际需求，避免理解偏差
2. **类型标注** -- 给问题打标签（可多选）：
   - [code] -- 代码/技术方案
   - [web] -- 网页/文章
   - [social] -- 中文社媒（小红书/B站/知乎/微博）
   - [academic] -- 学术文献
   - [financial] -- 金融/投资/公司
   - [osint] -- 开源情报/综合调研
3. **深度估计**：
   - Quick（< 5 分钟：1-2 个来源，单轮搜索）
   - Standard（15-30 分钟：多来源，并行搜索）
   - Deep（1h+：Systematic Review 级别，跨语言多轮）

**完成标准**：问题已澄清 + 类型已标注 + 深度已确定

---

## Phase 1: Decompose（问题分解）

**入口**：已明确问题 + 类型

**动作**：

1. **拆子问题** -- 把大问题拆成 3-7 个互斥的子问题
2. **关键词提取** -- 每个子问题提 2-3 组关键词（中英文）
3. **同义词/翻译** -- 对中文问题补充英文关键词，反之亦然

**示例**：

问题: "XX 公司最近一轮融资情况"
子问题:
  - Q1: 融资金额和时间
  - Q2: 投资方构成
  - Q3: 估值变化趋势
  - Q4: 业务基本面支撑了什么估值

**完成标准**：每个子问题有至少 2 组可执行的查询关键词

---

## Phase 2: Route（路由编排）

**入口**：子问题列表 + 关键词

**动作**：按类型映射到可用工具链

### 路由表

| 分类 | 首选工具 | 备选工具 | 适用场景 |
|------|---------|---------|---------|
| [web] 网页搜索 | byted-web-search | mcporter -> Exa / Brave API | 通用网页信息 |
| [web] 单页阅读 | curl "https://r.jina.ai/URL" | python3 + bs4 | 提取单篇文章内容 |
| [code] 本地代码 | rg -n "pattern" | git log --all -S"pattern" | 代码库内搜 |
| [code] GitHub | curl "https://api.github.com/search/..." | gh search | 开源项目/代码 |
| [social] B站 | bili search "query" -n 5 | byted-web-search + site:bilibili.com | 视频/UP主内容 |
| [social] 小红书 | byted-web-search + site:xiaohongshu.com | agent-reach | 种草/体验/用户反馈 |
| [social] 知乎 | byted-web-search + site:zhihu.com | curl 知乎 API | 深度问答 |
| [academic] 通用 | Semantic Scholar API | arXiv API / Google Scholar | 论文搜索 |
| [academic] 引用分析 | Semantic Scholar /citation 端点 | Scite（付费） | 追踪引用链 |
| [financial] 公司信息 | Crunchbase API（curl） | PitchBook（付费）/ 企查查 | 融资/估值/竞品 |
| [financial] 行研 | byted-web-search | CB Insights / 36Kr | 行业分析报告 |
| [osint] 综合 | 组合 3+ 来源并行 | RSS feeds | 复杂多面调研 |



### ⚠️ 网页搜索计费说明

| 后端 | 免费额度 | 超出后 | 配置方式 |
|------|---------|--------|---------|
| **byted-web-search**（火山引擎） | 500 次/月 | 按量计费（需充值） | `WEB_SEARCH_API_KEY` |
| **Brave Search API** | 2,000 次/月 | 按量计费 | `BRAVE_API_KEY`，[免费注册](https://brave.com/search/api/) |

- byted-web-search 的 500 次/月对个人日常使用通常够用
- 可在[火山引擎控制台](https://console.volcengine.com/search-infinity/api-key)查看剩余额度
- 想换成纯免费方案的话：免费注册 **Brave Search**（无需信用卡），设 `BRAVE_API_KEY` 后 pipeline 可用

### 并行策略

对 Standard 和 Deep 深度，**同时调多个工具**并行执行。

**完成标准**：每个子问题至少映射到 2 个备选来源

---

## Phase 3: Execute（并行执行）

**入口**：路由表已制定

**动作**：

1. **优先用 API** -- 无头浏览器是最后手段
2. **限流配置** -- 对无 API key 的公共源加 sleep 1 间隔
3. **输出暂存** -- 原始结果先存为 JSON 到临时目录
4. **错误处理** -- 一个源挂了不影响其他源（并行 + || true）

### 快速命令速查

```bash
# 网页搜索（byted-web-search）
python3 /path/to/web_search.py "query" --count 5

# 学术搜索（Semantic Scholar - 免费，无需 Key）
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY&limit=5" | jq '.data[] | {title, year, citationCount, url}'

# 学术搜索（arXiv - 免费）
curl -s "http://export.arxiv.org/api/query?search_query=all:QUERY&max_results=5"

# 网页文章提取（jina.ai - 免费，无需 Key）
curl -sL "https://r.jina.ai/URL" | head -200

# GitHub 搜索
curl -s "https://api.github.com/search/repositories?q=QUERY&sort=stars&per_page=5"

# 本地代码搜索
rg -n -i "pattern" --type py --max-count 10

# B站搜索
bili search "query" --type video -n 5
```

**完成标准**：每个子问题至少有 1 个来源返回了非空结果；空结果的源已标记

---

## Phase 4: Triangulate（三角验证）

**入口**：原始搜索结果已收集

**动作**：

1. **置信度打分**：
   - High -- 2+ 独立来源一致，且来源可信（官方/学术/一手）
   - Medium -- 1 个来源 + 无矛盾
   - Low -- 单来源无可验证、来源可疑、来源间矛盾

2. **矛盾标记** -- 来源间冲突时不取平均值，列出各方主张 + 证据强度，标记需进一步调查

3. **覆盖检查** -- 对照 Phase 1 的子问题，确认没有遗漏

**完成标准**：每个子问题有置信度标签；矛盾已被标记

---

## Phase 5: Synthesize（结构化输出）

**入口**：原始结果 + 置信度标注

**输出格式**：

- **关键发现**: 每个发现一行 + 置信度标签
- **来源链路**: 每个发现对应哪些来源，交叉验证状态
- **矛盾/待确认**: 来源间冲突的具体差异
- **开放问题**: 未覆盖的信息方向
- **搜索回溯**: 本次使用的查询词、时间、工具清单

**完成标准**：输出包含以上所有字段，没有无依据陈述

---

## Phase 6: Archive（归档）

**入口**：结构化输出已生成

**动作**：

1. **保存到本地文件**（最低要求）：
   ```bash
   cat synthesis.md >> ./搜索沉淀_TOPIC.md
   ```

2. **整理到自己的知识库**（可选，推荐）：
   - Obsidian 用户 -> 放到 Obsidian vault 的对应目录
   - Notion 用户 -> 导入到 Notion 知识库
   - 飞书用户 -> 保存到飞书文档或云空间
   - 什么都不用 -> 留在工作目录的搜索沉淀_*.md 文件里

3. **重要知识提炼** -- 把这次搜到的可复用知识提取成独立笔记
   - 不要只留原始搜索结果，把"能用的是什么、怎么用"写清楚
   - 方便以后直接翻笔记而不是重新搜一遍

**完成标准**：搜索结果已保存到可再次找到的地方

---## 附录 A：工具安装清单

### pip3 可安装

```bash
pip3 install arxiv               # arXiv Python 客户端
pip3 install feedparser          # RSS 解析
pip3 install readability-lxml    # 文章正文提取
pip3 install duckduckgo_search   # DuckDuckGo 搜索（免费）
pip3 install scholarly           # Google Scholar（可能有验证码）
```

### ByWebSearch API Key（推荐）

```bash
# 去 https://console.volcengine.com/search-infinity/api-key 申请
# 每月 500 次免费
export WEB_SEARCH_API_KEY="your_key"
# 验证：python3 /path/to/web_search.py "test" --count 1
```

### 无需安装（curl 直调）

| 服务 | 方法 | 限制 |
|------|------|------|
| Semantic Scholar | curl API | 免费，无 Key |
| arXiv | curl API | 免费，无 Key |
| jina.ai Reader | curl | 免费，无 Key |
| GitHub API | curl | 60 req/h 未认证 |
| Hacker News | curl | 免费，无 Key |

---

## 附录 B：按场景的工作流速查

### 调研一个技术方案 [code] [web]
Decompose: 方案对比 -> 性能数据 -> 社区生态 -> 学习资源
Route:     GitHub stars + B站教程 -> arXiv 论文 -> 本地 rg 找现有代码
Execute:   并行跑全部
Verify:    GitHub 星数高 + 论文多 + 本地可复用 -> High

### 调研一个公司 [web] [financial]
Decompose: 融资 -> 产品 -> 竞争格局 -> 团队
Route:     Crunchbase + 36Kr -> 知乎评价 -> 官网 -> LinkedIn
注意:      公司信息时效性极强，关注数据日期

### 调研一个学术问题 [academic]
Decompose: 核心主张 -> 证据类型 -> 主流观点 -> 争议
Route:     Semantic Scholar 搜 -> arXiv 下载 -> 引文链追踪
流程:      PRISMA-light: 关键词搜 -> 筛标题 -> 读摘要 -> 读全文

### 调研社媒热点 [social]
Decompose: 事件经过 -> 各方立场 -> 数据验证 -> 时间线
Route:     B站 + 小红书 + 知乎并行（byted-web-search）
注意:      社媒信息信噪比低，至少 3 个独立用户/账号交叉验证
