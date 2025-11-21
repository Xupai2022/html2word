#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成高级测试图片（101-152号）
"""

from PIL import Image, ImageDraw
import os

def generate_image_with_number(image_id, width, height):
    """生成带编号的测试图片"""
    # 多种背景颜色
    colors = [
        (52, 152, 219), (231, 76, 60), (46, 204, 113),
        (155, 89, 182), (241, 196, 15), (26, 188, 156),
        (52, 73, 94), (230, 126, 34), (149, 165, 166),
        (22, 160, 133), (39, 174, 96), (243, 156, 18),
        (142, 68, 173), (76, 175, 80), (33, 150, 243),
        (255, 107, 107), (52, 73, 94), (255, 99, 72)
    ]

    # 根据ID选择颜色
    color = colors[image_id % len(colors)]

    # 创建图片
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)

    # 添加文字
    try:
        font = None
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                from PIL import ImageFont
                font = ImageFont.truetype(font_path, min(width, height) // 4)
                break

        if font:
            text = f"#{image_id}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill='white', font=font)
        else:
            font = ImageFont.load_default()
            text = str(image_id)
            draw.text((width // 3, height // 3), text, fill='white', font=font)
    except:
        pass

    # 保存
    output_dir = 'images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f'{output_dir}/{image_id}.jpg'
    img.save(filename, 'JPEG', quality=95)
    print(f"  生成: {filename} ({width}x{height})")

def generate_for_advanced_test():
    """为高级测试生成图片"""
    print("=" * 70)
    print("  生成高级测试图片（101-152号）")
    print("=" * 70)
    print()

    # 定义高级测试需要的图片
    # 格式: (id, width, height)
    advanced_images = [
        (101, 100, 100), (102, 100, 100),
        (103, 300, 200), (103, 600, 400), (103, 900, 600),  # 同一ID重复
        (104, 600, 400), (104, 200, 133), (104, 400, 267), (104, 800, 533),
        (105, 150, 150), (106, 150, 150), (107, 150, 150),
        (108, 150, 150), (109, 150, 150), (110, 150, 150),
        (111, 150, 100), (112, 150, 100), (113, 150, 100),
        (114, 400, 300), (115, 400, 300),
        (116, 600, 350), (117, 250, 150), (118, 250, 150),
        (119, 150, 100), (120, 150, 100), (121, 150, 100),
        (122, 400, 300),
        (123, 640, 360), (124, 360, 640), (125, 300, 300),
        (126, 800, 200),
        (127, 400, 250), (128, 350, 200), (129, 500, 300),
        (130, 200, 150),
        (151, 300, 200), (152, 80, 60),
    ]

    generated = 0
    for item in advanced_images:
        image_id, width, height = item
        generate_image_with_number(image_id, width, height)
        generated += 1

    # 去重统计
    unique_ids = len(set([img[0] for img in advanced_images]))

    print()
    print("=" * 70)
    print(f"[OK] 成功生成 {generated} 个规格的图片")
    print(f"     覆盖 {unique_ids} 个不同的图片ID")
    print(f"     图片ID范围: 101 - 152")
    print("=" * 70)

if __name__ == '__main__':
    generate_for_advanced_test()
