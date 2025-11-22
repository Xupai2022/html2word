#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析oversear_monthly_report_cut10.html的结构
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

def analyze_html(html_file):
    """分析HTML文件，找出关键部分"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    print("=" * 80)
    print("HTML 结构分析")
    print("=" * 80)

    # 1. 查找 "Monthly Security Report"
    print("\n1. Monthly Security Report 标题:")
    print("-" * 80)
    monthly_report = soup.find(string=re.compile(r'Monthly Security Report'))
    if monthly_report:
        parent = monthly_report.parent
        print(f"  标签: {parent.name}")
        print(f"  文本: {parent.get_text(strip=True)[:50]}")
        print(f"  样式: {parent.get('style', 'N/A')[:200]}")
        # 查找父元素的样式
        for p in [parent] + list(parent.parents)[:3]:
            if p.get('style'):
                print(f"  父元素 {p.name} 样式: {p.get('style')[:200]}")

    # 2. 查找 "Security Rating"
    print("\n2. Security Rating 部分:")
    print("-" * 80)
    security_rating = soup.find(string=re.compile(r'Security Rating'))
    if security_rating:
        parent = security_rating.parent
        print(f"  标签: {parent.name}")
        print(f"  文本: {parent.get_text(strip=True)[:50]}")
        print(f"  样式: {parent.get('style', 'N/A')[:200]}")
        # 查找父容器
        for p in [parent] + list(parent.parents)[:3]:
            if p.get('style'):
                print(f"  父元素 {p.name} 样式: {p.get('style')[:200]}")

    # 3. 查找 2x2 表格
    print("\n3. 2x2 表格（Statistics区域）:")
    print("-" * 80)
    tables = soup.find_all(['table', 'div'], class_=re.compile(r'grid|table'))
    if tables:
        for i, table in enumerate(tables[:3]):
            print(f"\n  表格 {i+1}:")
            print(f"    标签: {table.name}")
            print(f"    类名: {table.get('class')}")
            print(f"    样式: {table.get('style', 'N/A')[:200]}")

    # 4. 查找图片
    print("\n4. 图片元素:")
    print("-" * 80)
    images = soup.find_all(['img', 'svg'])
    print(f"  总计: {len(images)} 个图片/SVG元素")
    for i, img in enumerate(images[:5]):
        print(f"\n  图片 {i+1}:")
        print(f"    标签: {img.name}")
        if img.name == 'img':
            src = img.get('src', '')[:100]
            print(f"    src: {src}")
        print(f"    样式: {img.get('style', 'N/A')[:200]}")
        # 查找父元素样式
        parent = img.parent
        if parent and parent.get('style'):
            print(f"    父元素 {parent.name} 样式: {parent.get('style')[:200]}")

    # 5. 查找 "Detection and Response"
    print("\n5. Detection and Response 部分:")
    print("-" * 80)
    detection = soup.find(string=re.compile(r'1\.1.*Detection and Response'))
    if detection:
        parent = detection.parent
        print(f"  标签: {parent.name}")
        print(f"  文本: {parent.get_text(strip=True)[:50]}")
        # 查找之前的兄弟元素（可能包含图片）
        prev_sibling = parent.find_previous_sibling()
        if prev_sibling:
            print(f"  前一个兄弟元素: {prev_sibling.name}")
            print(f"  前一个兄弟元素内容: {str(prev_sibling)[:200]}")

    # 6. 查找图表相关的 SVG/Canvas
    print("\n6. 图表元素（SVG/Canvas）:")
    print("-" * 80)
    charts = soup.find_all(['svg', 'canvas'])
    print(f"  总计: {len(charts)} 个图表元素")
    for i, chart in enumerate(charts[:5]):
        print(f"\n  图表 {i+1}:")
        print(f"    标签: {chart.name}")
        print(f"    样式: {chart.get('style', 'N/A')[:200]}")
        # 查找附近的标题
        parent = chart.parent
        for _ in range(3):
            if parent:
                text = parent.get_text(strip=True)
                if any(keyword in text for keyword in ['Network', 'Log', 'Trend', 'Attacker', 'Location']):
                    print(f"    相关标题: {text[:50]}")
                    break
                parent = parent.parent

    # 7. 查找 "Assets Requiring Attention" 表格
    print("\n7. Assets Requiring Attention 表格:")
    print("-" * 80)
    assets_text = soup.find(string=re.compile(r'Assets Requiring Attention'))
    if assets_text:
        # 查找后续的表格
        parent = assets_text.parent
        for _ in range(5):
            if parent:
                table = parent.find_next('table')
                if table:
                    print(f"  找到表格")
                    print(f"    样式: {table.get('style', 'N/A')[:200]}")
                    print(f"    类名: {table.get('class')}")
                    # 查找表格的行
                    rows = table.find_all('tr')
                    print(f"    行数: {len(rows)}")
                    if rows:
                        first_row = rows[0]
                        print(f"    第一行样式: {first_row.get('style', 'N/A')[:200]}")
                        cols = first_row.find_all(['td', 'th'])
                        print(f"    列数: {len(cols)}")
                    break
                parent = parent.parent

if __name__ == "__main__":
    html_file = Path(__file__).parent / "oversear_monthly_report_cut10.html"
    analyze_html(html_file)
