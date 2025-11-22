#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
综合测试所有修复
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from html2word import HTML2WordConverter

# 测试用例
test_cases = {
    "1_absolute_positioning": """
<!DOCTYPE html>
<html>
<head>
<style>
.container { position: relative; height: 300px; background: #f0f0f0; }
.absolute-text { position: absolute; top: 100px; left: 50px; color: red; }
.normal-text { padding: 20px; }
</style>
</head>
<body>
<div class="container">
    <div class="absolute-text">This should NOT appear (position: absolute)</div>
    <div class="normal-text">This SHOULD appear (normal flow)</div>
</div>
</body>
</html>
""",

    "2_svg_fallback": """
<!DOCTYPE html>
<html>
<head><title>SVG Test</title></head>
<body>
<h2>SVG Chart Placeholder Test</h2>
<svg width="400" height="200">
    <rect x="0" y="0" width="400" height="200" fill="#567DF5"/>
    <text x="200" y="100" text-anchor="middle" fill="white">Chart</text>
</svg>
<p>Text after SVG</p>
</body>
</html>
""",

    "3_table_row_height": """
<!DOCTYPE html>
<html>
<head>
<style>
table { width: 100%; border-collapse: collapse; }
tr { height: 30px; }
td { border: 1px solid #ddd; padding: 8px; }
</style>
</head>
<body>
<table>
    <tr><td>Row 1, Cell 1</td><td>Row 1, Cell 2</td></tr>
    <tr><td>Row 2, Cell 1</td><td>Row 2, Cell 2</td></tr>
</table>
</body>
</html>
""",

    "4_gradient_background": """
<!DOCTYPE html>
<html>
<head>
<style>
.header {
    background: linear-gradient(90deg, #567DF5 0%, rgba(86, 125, 245, 0) 100%);
    padding: 15px;
    color: #333;
    font-weight: bold;
    margin: 10px 0;
}
</style>
</head>
<body>
<div class="header">Security Rating (with gradient background)</div>
<p>Content below header</p>
</body>
</html>
""",

    "5_image_centering": """
<!DOCTYPE html>
<html>
<head>
<style>
.center-container {
    text-align: center;
    padding: 20px;
    background: #f5f5f5;
}
img {
    width: 200px;
    height: 100px;
}
</style>
</head>
<body>
<div class="center-container">
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" alt="Test">
</div>
<p>Image above should be centered</p>
</body>
</html>
""",

    "6_padding_top": """
<!DOCTYPE html>
<html>
<head>
<style>
.padded-container {
    padding-top: 100px;
    padding-bottom: 50px;
    background: #f0f0f0;
}
h1 {
    margin: 0;
    padding: 0;
}
</style>
</head>
<body>
<div class="padded-container">
    <h1>Title with Large Top Padding</h1>
    <p>This container should have significant top padding</p>
</div>
</body>
</html>
"""
}

def test_case(name, html_content):
    """测试单个案例"""
    output_file = Path(__file__).parent / f"test_fix_{name}.docx"

    try:
        converter = HTML2WordConverter()
        converter.convert(html_content, str(output_file), input_type="string")
        print(f"[OK] {name}")
        return True
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False

def main():
    print("=" * 80)
    print("Testing All Fixes")
    print("=" * 80)

    results = {}
    for name, html in test_cases.items():
        results[name] = test_case(name, html)

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests PASSED!")
    else:
        print(f"\n✗ {total - passed} test(s) FAILED")

if __name__ == "__main__":
    main()
