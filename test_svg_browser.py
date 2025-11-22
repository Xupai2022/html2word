#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试BrowserSVGConverter转换SVG图表
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from html2word.converter import HTML2WordConverter
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_svg_conversion():
    """测试SVG转换"""
    print("=" * 60)
    print("测试BrowserSVGConverter转换SVG图表")
    print("=" * 60)

    # 输入文件
    input_html = "test_svg_basic.html"
    output_docx = "test_svg_basic_browser_output.docx"

    if not os.path.exists(input_html):
        print(f"错误: 找不到输入文件 {input_html}")
        return

    print(f"输入文件: {input_html}")
    print(f"输出文件: {output_docx}")
    print("-" * 60)

    try:
        # 创建转换器
        converter = HTML2WordConverter(base_path='.')

        # 执行转换
        print("开始转换...")
        converter.convert(input_html, output_docx, 'file')

        print("-" * 60)
        print(f"✓ 转换完成！")
        print(f"输出文件: {os.path.abspath(output_docx)}")
        print("=" * 60)

        # 检查输出文件
        if os.path.exists(output_docx):
            size = os.path.getsize(output_docx)
            print(f"输出文件大小: {size / 1024:.2f} KB")
        else:
            print("错误: 输出文件未生成")

    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_svg_conversion()
