#!/bin/bash
echo "正在激活虚拟环境..."
export PYTHONPATH="$(dirname "$0")/venv/lib/python3.9/site-packages:\$PYTHONPATH"
export PATH="$(dirname "$0")/venv/bin:\$PATH"
echo "虚拟环境已激活！"
echo ""
echo "你可以运行 Python 脚本:"
echo "  python src/html2word/converter.py"
echo ""
