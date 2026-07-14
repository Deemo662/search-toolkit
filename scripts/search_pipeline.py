#!/usr/bin/env python3
"""
search_pipeline.py — 系统性搜索辅助脚本

用法：
  # 网页搜索（默认）
  python3 search_pipeline.py web "你的查询"

  # 学术搜索
  python3 search_pipeline.py academic "transformer architecture"

  # 代码搜索（本地）
  python3 search_pipeline.py code "pattern" /path/to/search

  # B站搜索
  python3 search_pipeline.py bili "搜索关键词"

  # 多源并行搜索
  python3 search_pipeline.py multi "自然语言处理 最新进展"
"""

import sys
import json
import time
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

import os
import subprocess

try:
    import requests
except ImportError:
    print("Error: 需要 requests 库，运行: pip3 install requests")
    sys.exit(1)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) SearchPipeline/1.0"

# ============================================================
# 源后端
# ============================================================

def search_semantic_scholar(query: str, limit: int = 5) -> list:
    """Semantic Scholar API — subprocess + curl 绕开 Python requests 的 header 差异"""
    import json as _json, random as _rnd
    scheme = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = f"query={requests.utils.quote(query)}&limit={limit}&fields=title%2Cyear%2CcitationCount%2Curl%2Cabstract"
    url = f"{scheme}?{params}"
    cmd = ["curl", "-s", "-H", "User-Agent: Mozilla/5.0 (compatible; SearchPipeline/1.0)",
           "--max-time", "15", url]
    base_wait = 1.0
    for attempt in range(3):
        try:
            time.sleep(base_wait + _rnd.random() * 0.5)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if result.returncode != 0:
                if attempt < 2:
                    base_wait *= 2; time.sleep(base_wait); continue
                return [{"source": "Semantic Scholar", "error": result.stderr[:200]}]
            data = _json.loads(result.stdout)
            if "message" in data and "Too Many" in data.get("message", ""):
                if attempt < 2:
                    base_wait *= 2; time.sleep(base_wait); continue
                return [{"source": "Semantic Scholar", "error": data["message"][:100]}]
            results = []
            for p in data.get("data", []):
                results.append({
                    "source": "Semantic Scholar",
                    "title": p.get("title", ""),
                    "year": p.get("year"),
                    "citations": p.get("citationCount"),
                    "url": p.get("url", ""),
                    "abstract": (p.get("abstract") or "")[:200],
                })
            return results
        except Exception as e:
            if attempt == 2:
                return [{"source": "Semantic Scholar", "error": str(e)}]
            base_wait *= 2; time.sleep(base_wait)


def search_arxiv(query: str, limit: int = 5) -> list:
    """arXiv API — 免费，无需 Key"""
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "max_results": limit}
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(r.content)
        results = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            results.append({
                "source": "arXiv",
                "title": (title.text or "").strip().replace("\n", " ") if title is not None else "",
                "abstract": (summary.text or "").strip().replace("\n", " ")[:200] if summary is not None else "",
                "url": entry.find("atom:id", ns).text if entry.find("atom:id", ns) is not None else "",
                "published": entry.find("atom:published", ns).text[:10] if entry.find("atom:published", ns) is not None else "",
            })
        return results
    except Exception as e:
        return [{"source": "arXiv", "error": str(e)}]


def search_github(query: str, limit: int = 5) -> list:
    """GitHub 搜索 — 60 req/h 未认证"""
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": "stars", "per_page": limit}
    try:
        r = requests.get(url, params=params, headers={"Accept": "application/vnd.github.v3+json"}, timeout=15)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "source": "GitHub",
                "name": item.get("full_name", ""),
                "description": item.get("description", ""),
                "stars": item.get("stargazers_count", 0),
                "url": item.get("html_url", ""),
                "language": item.get("language", ""),
            })
        return results
    except Exception as e:
        return [{"source": "GitHub", "error": str(e)}]


def search_jina_read(url: str) -> str:
    """jina.ai Reader — 把网页转成 LLM 友好文本"""
    reader_url = f"https://r.jina.ai/{url}"
    try:
        r = requests.get(reader_url, timeout=30)
        r.raise_for_status()
        return r.text[:3000]
    except Exception as e:
        return f"[jina reader error] {e}"


def search_bili_cli(query: str, limit: int = 5) -> list:
    """bili CLI — 本地已安装"""
    try:
        result = subprocess.run(
            ["bili", "search", query, "--type", "video", "-n", str(limit)],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return [{"source": "B站", "raw": line} for line in result.stdout.strip().split("\n") if line.strip()]
        else:
            return [{"source": "B站", "error": result.stderr[:200]}]
    except FileNotFoundError:
        return [{"source": "B站", "error": "bili CLI 未安装"}]
    except Exception as e:
        return [{"source": "B站", "error": str(e)}]


def search_local_code(pattern: str, path: str = ".", file_type: str = None, limit: int = 20) -> list:
    """rg 本地代码搜索"""
    cmd = ["rg", "-n", "-i", pattern, "--max-count", str(limit)]
    if file_type:
        cmd.extend(["--type", file_type])
    cmd.append(path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().split("\n")
        return [{"source": "本地代码", "match": line[:200]} for line in lines if line.strip()][:limit]
    except FileNotFoundError:
        return [{"source": "本地代码", "error": "rg 未安装"}]
    except Exception as e:
        return [{"source": "本地代码", "error": str(e)}]


# ============================================================
# 多源并行
# ============================================================


def search_web(query: str, count: int = 5) -> list:
    """网页搜索 — 用 byted-web-search（火山引擎，500 次/月免费，之后按量计费）"""
    api_key = os.environ.get("WEB_SEARCH_API_KEY")
    if not api_key:
        return [{"source": "网页搜索", "note": "未配 Key，网页搜索不可用。用默认搜索代替。"},
                {"source": "网页搜索", "tip": "其他功能（学术/GitHub/代码/多源）不受影响，可直接使用。"}]

    web_search_script = "/Users/mumu/.agents/skills/byted-web-search/scripts/web_search.py"
    if not os.path.exists(web_search_script):
        return [{"source": "网页搜索", "error": f"脚本不存在: {web_search_script}"}]

    results = []
    try:
        result = subprocess.run(
            ["python3", web_search_script, query, "--count", str(count)],
            capture_output=True, text=True, timeout=30
        )
        raw = result.stdout.strip()
        # 提取结果行（跳过统计行）
        for line in raw.split("\n"):
            line = line.strip()
            if not line or line.startswith(("结果数", "---", "耗时")):
                continue
            results.append({"source": "Byted", "raw": line})
    except Exception as e:
        return [{"source": "网页搜索", "error": str(e)}]

    if not results:
        return [{"source": "网页搜索", "warning": "byted-web-search 返回空（可能免费额度已用完）",
                 "error": "empty results"}]
    return results


def search_multi(query: str) -> dict:
    """并行调多个源，每源最多等 30 秒"""
    print(f"\n{'='*60}")
    print(f"  多源搜索: {query}")
    print(f"{'='*60}\n")

    sources = {
        "网页搜索 (Byted)": lambda: search_web(query),
        "学术 (arXiv)": lambda: search_arxiv(query),
        "开源 (GitHub)": lambda: search_github(query),
        "学术 (Semantic Scholar)": lambda: search_semantic_scholar(query),
    }

    results = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fn): name for name, fn in sources.items()}
        from concurrent.futures import wait as _wait, ALL_COMPLETED as _ALL
        done, _ = _wait(futures.keys(), timeout=35, return_when=_ALL)
        for future in done:
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = [{"error": str(e)}]
        # 超时的标记为超时
        for future in set(futures.keys()) - done:
            name = futures[future]
            results[name] = [{"error": "TIMEOUT (35s)"}]

    for name, items in results.items():
        print(f"\n--- {name} ---")
        if not items:
            print("  (无结果)")
            continue
        for item in items[:5]:
            if "error" in item:
                print(f"  [{item.get('source','?')}] {item['error']}")
                continue
            if "note" in item or "tip" in item:
                print(f"  {item.get('note','')} {item.get('tip','')}")
                continue
            if "title" in item:
                print(f"  {item['title']}")
                if item.get("year"):
                    print(f"    Year: {item['year']} | Citations: {item.get('citations', 'N/A')}")
                if item.get("url"):
                    print(f"    {item['url']}")
            elif "name" in item:
                print(f"  {item['name']} (stars: {item.get('stars', 0)})")
                if item.get("description"):
                    print(f"    {item['description']}")
                print(f"    {item.get('url', '')}")
            elif "match" in item:
                print(f"  {item['match']}")
            elif "raw" in item:
                print(f"  {item['raw']}")
    return results


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1].lower()
    query = sys.argv[2]

    if mode == "web":
        results = search_web(query)
        print("\n=== 网页搜索 ===\n")
        for r in results:
            if "error" in r:
                print(f"  [ERROR] {r['error']}")
            else:
                print(f"  {r['raw']}")


    elif mode == "academic":
        print("\n=== Semantic Scholar ===")
        for r in search_semantic_scholar(query):
            if "error" in r:
                print(f"  [ERROR] {r['error']}")
                continue
            print(f"  [{r.get('year','?')}] {r['title']} (citations: {r.get('citations','?')})")
            if r.get("url"):
                print(f"    {r['url']}")

        print("\n=== arXiv ===")
        for r in search_arxiv(query):
            if "error" in r:
                print(f"  [ERROR] {r['error']}")
                continue
            print(f"  [{r.get('published','?')}] {r['title']}")
            if r.get("url"):
                print(f"    {r['url']}")

    elif mode == "code":
        path = sys.argv[3] if len(sys.argv) > 3 else "."
        ftype = sys.argv[4] if len(sys.argv) > 4 else None
        results = search_local_code(query, path, ftype)
        for r in results:
            if "error" in r:
                print(f"  [ERROR] {r['error']}")
            else:
                print(f"  {r['match']}")

    elif mode == "github":
        for r in search_github(query):
            print(f"  {r['name']} (stars: {r.get('stars', 0)}, lang: {r.get('language', '?')})")
            if r.get("description"):
                print(f"    {r['description']}")
            print(f"    {r.get('url', '')}")

    elif mode == "bili":
        for r in search_bili_cli(query):
            if "error" in r:
                print(f"  [ERROR] {r['error']}")
            else:
                print(f"  {r['raw']}")

    elif mode == "multi":
        results = search_multi(query)
        # 汇总
        print(f"\n{'='*60}")
        print(f"  搜索完成。结果来自 {len(results)} 个源")
        print(f"{'='*60}")

        # — 提示下步 —
        print(f"\n下一步请按 SOP Phase 4 (Triangulate) 做交叉验证：")
        print(f"  1. 对比各源对同一问题的回答是否一致")
        print(f"  2. 给每个关键发现打置信度标签")
        print(f"  3. 标记矛盾点需要进一步调查")
        print(f"  完成结构化输出后请按 Phase 6 归档到 ~/Documents/Codex/_我的记忆/搜索沉淀/")

    elif mode == "help":
        print(__doc__)
    else:
        print(f"未知模式: {mode}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
