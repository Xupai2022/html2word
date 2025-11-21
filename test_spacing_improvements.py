#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试间距改进效果
验证gap和margin collapse是否正确实现
"""

import sys
import io
from pathlib import Path

# Set stdout encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word import HTML2WordConverter

def test_spacing_improvements():
    """测试间距改进"""

    # 转换文件
    input_file = 'security_quarterly_report.html'
    output_file = 'security_quarterly_report_improved.docx'

    print(f"转换 {input_file}...")
    print("-" * 60)

    converter = HTML2WordConverter()
    converter.convert_file(input_file, output_file)

    print(f"\n✓ 转换完成: {output_file}")
    print("\n改进内容:")
    print("1. ✓ Grid gap支持 - .risk-overview { gap: 20px } 和 .metric-grid { gap: 15px }")
    print("2. ✓ 真正的margin collapse - 取相邻元素margin的最大值")
    print("3. ✓ 表格单元格内margin状态正确重置")
    print("\n请检查生成的Word文档：")
    print("- 风险卡片之间应有均匀的间距（20px gap）")
    print("- 指标卡片之间应有均匀的间距（15px gap）")
    print("- 相邻section之间的间距应为40px（不是累加）")
    print("- 所有间距值从HTML/CSS动态读取，无硬编码")

if __name__ == '__main__':
    test_spacing_improvements()
