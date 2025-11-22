#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试浏览器SVG转换
"""
import sys
import logging
from pathlib import Path

# 启用详细日志
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

sys.path.insert(0, str(Path(__file__).parent / "src"))

# 先测试浏览器转换器本身
print("="*80)
print("Testing BrowserSVGConverter directly")
print("="*80)

try:
    from html2word.utils.browser_svg_converter import BrowserSVGConverter

    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="150">
    <rect x="10" y="10" width="280" height="130" fill="#567DF5" stroke="#000" stroke-width="2"/>
    <text x="150" y="80" text-anchor="middle" fill="white" font-size="20">Browser Test</text>
</svg>'''

    converter = BrowserSVGConverter()
    png_data = converter.convert(svg_content, 300, 150)

    if png_data:
        print(f"\n[SUCCESS] Browser converter works! PNG size: {len(png_data)} bytes")

        # 保存测试图片
        test_file = Path(__file__).parent / "test_browser_output.png"
        with open(test_file, 'wb') as f:
            f.write(png_data)
        print(f"Saved to: {test_file}")
    else:
        print("\n[FAIL] Browser converter returned None")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

# 测试完整HTML转换
print("\n" + "="*80)
print("Testing full HTML2Word conversion with browser")
print("="*80)

from html2word import HTML2WordConverter

html_content = '''
<!DOCTYPE html>
<html>
<body>
<h2>Browser SVG Test</h2>
<svg width="300" height="150">
    <rect x="10" y="10" width="280" height="130" fill="#FF6B6B" stroke="#000" stroke-width="2"/>
    <text x="150" y="80" text-anchor="middle" fill="white" font-size="20">Chart</text>
</svg>
</body>
</html>
'''

output_file = Path(__file__).parent / "test_browser_full.docx"

try:
    converter = HTML2WordConverter()
    converter.convert(html_content, str(output_file), input_type="string")
    print(f"\n[SUCCESS] Full conversion completed: {output_file}")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
