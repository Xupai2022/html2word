"""
Diagnose which SVGs are causing parsing errors.
"""

import re
import sys
import xml.etree.ElementTree as ET

# 读取HTML
with open('oversear_monthly_report_part1_final.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有SVG
svg_pattern = r'<svg[^>]*>.*?</svg>'
svgs = re.findall(svg_pattern, content, re.DOTALL | re.IGNORECASE)

print(f'Found {len(svgs)} SVG elements\n')

# 测试每个SVG
failed_count = 0
passed_count = 0
problem_svgs = []

for i, svg in enumerate(svgs):
    try:
        ET.fromstring(svg)
        passed_count += 1
    except ET.ParseError as e:
        failed_count += 1
        problem_svgs.append((i, svg, str(e)))
        print(f'ERROR: SVG #{i+1} failed at position {e.position}')
        print(f'  Error: {e}')
        print(f'  Length: {len(svg)}')
        print(f'  Preview: {svg[:200]}')
        print()

print(f'\nSummary:')
print(f'  Passed: {passed_count}')
print(f'  Failed: {failed_count}')
print(f'  Total: {len(svgs)}')

# 保存失败的SVG以便进一步分析
if problem_svgs:
    with open('problem_svgs.txt', 'w', encoding='utf-8') as f:
        for idx, svg, error in problem_svgs:
            f.write(f'=== SVG #{idx+1} ===\n')
            f.write(f'Error: {error}\n')
            f.write(f'Content:\n{svg}\n')
            f.write('\n' + '='*80 + '\n\n')
    print('\nSaved problem SVGs to problem_svgs.txt')
