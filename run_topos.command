#!/bin/bash

# Topos Power - Cross-platform power timer

echo "🚀 正在启动 Topos Power..."
echo "────────────────────────────────────────"

# 进入脚本所在目录，避免从其他路径双击启动时找不到 src。
cd "$(dirname "$0")" || exit 1

# 优先使用项目虚拟环境，否则回退到系统 Python。
if [ -x ".venv/bin/python" ]; then
  echo "📦 找到 .venv，使用虚拟环境 Python..."
  PYTHON_CMD=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  echo "⚠️  未找到 .venv，使用系统 Python 3..."
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  echo "⚠️  未找到 .venv，使用系统 Python..."
  PYTHON_CMD="python"
else
  echo "❌ 未找到 Python，请安装 Python 3 或创建 .venv"
  read -r -p "按回车键关闭窗口..."
  exit 1
fi

# src 布局下，即使尚未执行 pip install -e . 也能直接运行。
export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"

echo "🎮 启动 Topos Power..."
echo "────────────────────────────────────────"
"$PYTHON_CMD" -m topos_power
EXIT_CODE=$?

echo ""
echo "ℹ️  程序已退出（代码: $EXIT_CODE）。按回车键关闭窗口..."
read -r
exit "$EXIT_CODE"
