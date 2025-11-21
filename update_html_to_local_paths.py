#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新HTML文件，将网络图片URL改为本地相对路径
"""

import re
import sys
from pathlib import Path

def update_html_file(html_file, output_file=None):
    """
    更新HTML文件中的图片URL

    Args:
        html_file: 输入HTML文件路径
        output_file: 输出HTML文件路径（如果为None则覆盖原文件）
    """
    print(f"\n处理文件: {html_file}")
    print("-" * 70)

    # 读取HTML文件
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 替换 picsum.photos URL 为本地相对路径
    # 从: https://picsum.photos/400/300?image=1
    # 到:   images/1.jpg

    # 查找所有图片URL模式
    pattern = r'https://picsum\.photos/[^?]+\?image=(\d+)'

    def replace_url(match):
        image_id = match.group(1)
        replacement = f'images/{image_id}.jpg'
        print(f"  替换: {match.group(0)} -> {replacement}")
        return replacement

    # 替换所有匹配
    updated_content = re.sub(pattern, replace_url, content)

    # 统计替换数量
    original_count = len(re.findall(pattern, original_content))
    print(f"\n总共替换 {original_count} 个图片URL")

    # 确定输出文件
    if output_file is None:
        output_file = html_file
        print(f"覆盖原文件: {output_file}")
    else:
        print(f"保存到新文件: {output_file}")

    # 写入更新后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print("[OK] 更新完成")

    return True

def main():
    print("=" * 70)
    print("  HTML图片路径更新工具")
    print("=" * 70)
    print("\n将 picsum.photos 网络URL替换为本地相对路径")

    # 更新 comprehensive 文件
    update_html_file(
        'test_images_comprehensive.html',
        'test_images_comprehensive_local.html'
    )

    # 更新 advanced 文件
    update_html_file(
        'test_images_advanced.html',
        'test_images_advanced_local.html'
    )

    print("\n" + "=" * 70)
    print("完成！已生成新的HTML文件:")
    print("  - test_images_comprehensive_local.html")
    print("  - test_images_advanced_local.html")
    print("\n这些文件使用相对路径引用本地图片")
    print("=" * 70)

if __name__ == '__main__':
    main()
