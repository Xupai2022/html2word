#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试特定问题的HTML片段
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from html2word import HTML2WordConverter

# 测试用例
test_cases = {
    "1_monthly_report_padding": """
<!DOCTYPE html>
<html>
<head>
<style>
.cover-info--wrapper {
    padding-top: 100px !important;
    padding-bottom: 50px;
}
.cover-info--title {
    font-size: 24px;
    font-weight: bold;
}
</style>
</head>
<body>
<div class="cover-info--wrapper">
    <p class="cover-info--title">Monthly Security Report</p>
    <p class="cover-info--sub"></p>
    <table class="cover-info-table">
        <tr><td style="width: 140px;">Customer</td><td>XDR_TEST</td></tr>
        <tr><td>Time Period</td><td>2025-10</td></tr>
    </table>
</div>
</body>
</html>
""",

    "2_security_rating_background": """
<!DOCTYPE html>
<html>
<head>
<style>
.chart-panel-header {
    background: linear-gradient(90deg, #567DF5 0%, rgba(86, 125, 245, 0) 100%);
    padding: 10px;
    color: #333;
    font-weight: bold;
}
</style>
</head>
<body>
<div class="chart-panel-header">Security Rating</div>
<p>Content below the header</p>
</body>
</html>
""",

    "3_absolute_positioned_text": """
<!DOCTYPE html>
<html>
<head>
<style>
.data-text {
    position: absolute;
    top: 142px;
    left: 204px;
}
.count__small {
    font-size: 24px;
    font-weight: bold;
}
</style>
</head>
<body>
<div style="position: relative; height: 300px;">
    <div class="data-text">
        <span class="count__small">2K+</span> logs
    </div>
</div>
</body>
</html>
""",

    "4_image_centering": """
<!DOCTYPE html>
<html>
<head>
<style>
.image-container {
    text-align: center;
    padding: 20px;
}
.image-container img {
    width: 300px;
    height: auto;
}
</style>
</head>
<body>
<div class="image-container">
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" alt="Test">
</div>
</body>
</html>
""",

    "5_table_sizing": """
<!DOCTYPE html>
<html>
<head>
<style>
table {
    width: 693px;
    border-collapse: collapse;
}
td, th {
    border: 1px solid #ddd;
    padding: 8px;
}
</style>
</head>
<body>
<table>
    <tr>
        <th>Column 1</th>
        <th>Column 2</th>
        <th>Column 3</th>
        <th>Column 4</th>
        <th>Column 5</th>
    </tr>
    <tr>
        <td>Data 1</td>
        <td>Data 2</td>
        <td>Data 3</td>
        <td>Data 4</td>
        <td>Data 5</td>
    </tr>
</table>
</body>
</html>
"""
}

def test_case(name, html_content):
    """测试单个案例"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print('='*80)

    output_file = Path(__file__).parent / f"test_{name}.docx"

    try:
        converter = HTML2WordConverter()
        converter.convert(html_content, str(output_file), input_type="string")
        print(f"[OK] Generated: {output_file.name}")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Testing specific HTML conversion issues...")

    for name, html in test_cases.items():
        test_case(name, html)

    print(f"\n{'='*80}")
    print("All tests completed!")
    print('='*80)

if __name__ == "__main__":
    main()
