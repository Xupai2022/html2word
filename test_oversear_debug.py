#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试oversear_monthly_report_cut10.html的转换问题
"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from html2word import HTML2WordConverter

def main():
    html_file = project_root / "oversear_monthly_report_cut10.html"
    output_file = project_root / "oversear_monthly_report_cut10_debug.docx"

    print(f"转换文件: {html_file}")
    print(f"输出到: {output_file}")

    if not html_file.exists():
        print(f"错误: HTML文件不存在: {html_file}")
        return

    try:
        # 执行转换
        converter = HTML2WordConverter()
        converter.convert_file(str(html_file), str(output_file))
        print(f"\n[SUCCESS] Conversion completed!")
        print(f"Output: {output_file}")
    except Exception as e:
        print(f"\n[ERROR] Conversion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
