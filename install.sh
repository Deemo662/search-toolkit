#!/bin/bash
# Search Toolkit 一键安装
# 用法: bash install.sh

set -e

SKILL_DIR="$HOME/.agents/skills/search-toolkit"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "📦 安装 Search Toolkit 到 $SKILL_DIR"

# 1. 创建目标目录
mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/docs"

# 2. 复制文件
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/"
cp "$SCRIPT_DIR/README.md" "$SKILL_DIR/"
cp "$SCRIPT_DIR/scripts/search_pipeline.py" "$SKILL_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/requirements.txt" "$SKILL_DIR/scripts/"
cp -r "$SCRIPT_DIR/docs/"* "$SKILL_DIR/docs/" 2>/dev/null || true

# 3. 设置执行权限
chmod +x "$SKILL_DIR/scripts/search_pipeline.py" 2>/dev/null || true

# 4. 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip3 install -r "$SCRIPT_DIR/scripts/requirements.txt" 2>/dev/null || pip3 install requests

echo ""
echo "✅ 安装完成！"
echo ""
echo "试试运行："
echo "  python3 $SKILL_DIR/scripts/search_pipeline.py academic "AI agent""
echo ""
echo "想让 Codex 自动使用这个 skill，重启 Codex 即可。"
