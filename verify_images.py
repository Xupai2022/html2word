#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证所有引用的图片是否存在
"""

import re
import os
from pathlib import Path

def extract_image_refs(html_file):
    """提取HTML中引用的所有图片ID"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找 images/X.jpg 的引用
    pattern = r'images/(\d+)\.jpg'
    matches = re.findall(pattern, content)

    # 转换为整数并去重
    image_ids = sorted(list(set([int(m) for m in matches])))
    return image_ids

def check_images_exist(image_ids):
    """检查图片是否存在"""
    images_dir = Path('images')
    missing = []
    existing = []

    for img_id in image_ids:
        filename = f"{img_id}.jpg"
        filepath = images_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            existing.append((img_id, size))
        else:
            missing.append(img_id)

    return existing, missing

def main():
    print("=" * 70)
    print("  验证图片完整性")
    print("=" * 70)
    print()

    html_files = [
        ('test_images_comprehensive_local.html', '基础测试'),
        ('test_images_advanced_local.html', '高级测试')
    ]

    all_missing = []

    for html_file, test_name in html_files:
        print(f"检查 {test_name}: {html_file}")
        print("-" * 70)

        # 提取引用的图片
        image_ids = extract_image_refs(html_file)
        print(f"引用的图片ID总数: {len(image_ids)}")
        print(f"ID范围: {image_ids[:5]}...{image_ids[-5:]}")
        print()

        # 检查图片是否存在
        existing, missing = check_images_exist(image_ids)

        print(f"存在的图片: {len(existing)} 张")
        if missing:
            print(f"[WARN] 缺失的图片: {len(missing)} 张")
            print(f"  缺失的ID: {missing}")
            all_missing.extend(missing)
        else:
            print("[OK] 所有图片都存在！")
        print()

    # 最终总结
    print("=" * 70)
    print("最终总结:")
    if all_missing:
        print(f"[WARN] 总共缺失 {len(set(all_missing))} 张图片")
        print(f"缺失的ID: {sorted(set(all_missing))}")
        print()
        print("建议运行以下命令生成缺失图片:")
        for img_id in sorted(set(all_missing)):
            print(f"  # 需要生成 images/{img_id}.jpg")
    else:
        print("[OK] 所有引用的图片都存在！")
        print("可以正常测试了。")
    print("=" * 70)

if __name__ == '__main__':
    main()
