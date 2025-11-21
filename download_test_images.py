#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
下载所有测试图片到本地images目录
"""

import os
import re
import urllib.request
from pathlib import Path

def extract_image_ids(html_file):
    """提取HTML中所有image参数的值"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找所有 ?image= 参数
    pattern = r'picsum\.photos/[^?]+\?image=(\d+)'
    matches = re.findall(pattern, content)

    # 转换为整数并去重
    image_ids = sorted(list(set([int(m) for m in matches])))
    return image_ids

def download_image(image_id, size, output_dir):
    """下载单张图片"""
    url = f"https://picsum.photos/{size}?image={image_id}"
    filename = f"{image_id}.jpg"
    filepath = os.path.join(output_dir, filename)

    # 如果文件已存在，跳过
    if os.path.exists(filepath):
        print(f"  [SKIP] {filename} 已存在")
        return True

    try:
        print(f"  [下载] 图片 ID {image_id} ({size})... ", end="")
        urllib.request.urlretrieve(url, filepath)
        print(f"完成 ({os.path.getsize(filepath)} bytes)")
        return True
    except Exception as e:
        print(f"失败: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("  测试图片下载工具")
    print("=" * 70)
    print()

    # 创建图片目录
    base_dir = Path(__file__).parent
    images_dir = base_dir / "images"
    images_dir.mkdir(exist_ok=True)
    print(f"图片目录: {images_dir}")
    print()

    # 要处理的HTML文件
    html_files = [
        'test_images_comprehensive.html',
        'test_images_advanced.html'
    ]

    total_downloaded = 0
    total_skipped = 0
    total_failed = 0

    for html_file in html_files:
        print(f"处理文件: {html_file}")
        print("-" * 70)

        if not os.path.exists(html_file):
            print(f"[WARN] 文件不存在，跳过: {html_file}")
            continue

        # 提取image ID
        image_ids = extract_image_ids(html_file)
        print(f"找到 {len(image_ids)} 个不同的图片ID: {image_ids[:10]}...")
        print()

        # 下载图片（根据使用场景设置尺寸）
        # 基础测试：主要使用 400x300 和 300x200
        # 高级测试：各种尺寸都有
        downloaded = 0
        skipped = 0
        failed = 0

        for img_id in image_ids:
            # 根据ID范围决定尺寸（简化处理，统一用400x300）
            # 实际在HTML中显示时会通过CSS控制
            size = "400x300"
            success = download_image(img_id, size, images_dir)

            if success:
                if os.path.exists(images_dir / f"{img_id}.jpg"):
                    file_size = os.path.getsize(images_dir / f"{img_id}.jpg")
                    if file_size > 0:
                        downloaded += 1
                    else:
                        skipped += 1
                else:
                    downloaded += 1
            else:
                failed += 1

        print()
        print(f"结果: 下载 {downloaded}, 跳过 {skipped}, 失败 {failed}")
        print()

        total_downloaded += downloaded
        total_skipped += skipped
        total_failed += failed

    # 最终总结
    print("=" * 70)
    print("下载完成总结:")
    print(f"  总下载: {total_downloaded} 张")
    print(f"  已存在跳过: {total_skipped} 张")
    print(f"  失败: {total_failed} 张")
    print()
    print(f"图片保存在: {images_dir}")
    print("=" * 70)

    if total_failed > 0:
        print("[WARN] 部分图片下载失败，请检查网络连接")
        return 1
    else:
        print("[OK] 所有图片下载成功！")
        return 0

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
