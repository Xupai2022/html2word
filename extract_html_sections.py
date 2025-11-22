#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提取oversear HTML的关键部分
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

def extract_section(soup, keyword, context_lines=10):
    """提取包含关键字的部分及其上下文"""
    element = soup.find(string=re.compile(keyword))
    if element:
        parent = element.parent
        # 向上找到一个合适的容器
        for _ in range(5):
            if parent and parent.name in ['section', 'div', 'article']:
                html = str(parent)[:5000]  # 限制长度
                return html
            if parent:
                parent = parent.parent
        # 如果没找到容器，返回原始元素
        return str(element.parent)[:2000]
    return "Not found"

def main():
    html_file = Path(__file__).parent / "oversear_monthly_report_cut10.html"

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # 创建输出文件
    output = []

    # 1. Monthly Security Report
    output.append("=" * 80)
    output.append("1. MONTHLY SECURITY REPORT 区域")
    output.append("=" * 80)
    section = extract_section(soup, r'Monthly Security Report')
    output.append(section)
    output.append("")

    # 2. Security Rating
    output.append("=" * 80)
    output.append("2. SECURITY RATING 区域")
    output.append("=" * 80)
    section = extract_section(soup, r'Security Rating')
    output.append(section)
    output.append("")

    # 3. Statistics Grid (2x2)
    output.append("=" * 80)
    output.append("3. STATISTICS GRID (2x2表格)")
    output.append("=" * 80)
    # 查找包含 "2K+" 或类似统计数字的区域
    stats_element = soup.find(string=re.compile(r'2K\+|logs'))
    if stats_element:
        parent = stats_element.parent
        for _ in range(5):
            if parent and parent.name in ['section', 'div']:
                output.append(str(parent)[:3000])
                break
            if parent:
                parent = parent.parent
    output.append("")

    # 4. Detection and Response
    output.append("=" * 80)
    output.append("4. DETECTION AND RESPONSE 区域")
    output.append("=" * 80)
    section = extract_section(soup, r'Detection and Response')
    output.append(section)
    output.append("")

    # 5. 图表区域
    output.append("=" * 80)
    output.append("5. NETWORK-SIDE LOG TREND 图表")
    output.append("=" * 80)
    section = extract_section(soup, r'Network-Side Log Trend')
    output.append(section)
    output.append("")

    # 6. Top 5 Attacker
    output.append("=" * 80)
    output.append("6. TOP 5 ATTACKER LOCATIONS 图表")
    output.append("=" * 80)
    section = extract_section(soup, r'Top 5 Attacker')
    output.append(section)
    output.append("")

    # 7. Assets Requiring Attention Table
    output.append("=" * 80)
    output.append("7. ASSETS REQUIRING ATTENTION 表格")
    output.append("=" * 80)
    section = extract_section(soup, r'Assets Requiring Attention')
    output.append(section)
    output.append("")

    # 写入文件
    output_file = Path(__file__).parent / "oversear_html_sections.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"HTML sections extracted to: {output_file}")

if __name__ == "__main__":
    main()
