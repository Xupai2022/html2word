#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SimpleSVGConverter
"""
import sys
import logging
from pathlib import Path

# 启用调试日志
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

sys.path.insert(0, str(Path(__file__).parent / "src"))

from html2word import HTML2WordConverter

html_content = '''
<!DOCTYPE html>
<html>
<head><title>SVG Test</title></head>
<body>
<h2>SVG Conversion Test</h2>

<svg width="300" height="150">
    <rect x="10" y="10" width="280" height="130" fill="#567DF5" stroke="#000" stroke-width="2"/>
    <text x="150" y="80" text-anchor="middle" fill="white" font-size="20">Test Chart</text>
</svg>

<p>Text after SVG</p>

<svg width="200" height="200">
    <circle cx="100" cy="100" r="80" fill="#FF6B6B" stroke="#333" stroke-width="3"/>
    <text x="100" y="105" text-anchor="middle" fill="white" font-size="16">Circle</text>
</svg>

</body>
</html>
'''

output_file = Path(__file__).parent / "test_svg_simple_result.docx"

print("Converting HTML with SVG using SimpleSVGConverter...")
converter = HTML2WordConverter()
converter.convert(html_content, str(output_file), input_type="string")

print(f"\n[OK] Conversion completed!")
print(f"Output: {output_file}")
print(f"\nCheck the document to verify SVG rendering")
