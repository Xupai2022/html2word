#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成测试图片到本地images目录
"""

from PIL import Image, ImageDraw, ImageFont
import os

def generate_solid_image(width, height, color, text, filename):
    """生成纯色背景图片，带文字"""
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)

    # 尝试画文字（如果字体可用）
    try:
        # 根据不同系统选择合适的字体
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"  # Linux
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, min(width, height) // 5)
                break
        if font:
            # 计算文字位置（居中）
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill='white', font=font)
        else:
            # 使用简单文字
            draw.text((width // 4, height // 3), text, fill='white')
    except:
        # 如果出错，只画色块
        pass

    # 创建输出目录
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img.save(filename, 'JPEG', quality=95)
    print(f"  生成: {filename} ({width}x{height}, 颜色: {color})")

def main():
    print("=" * 70)
    print("  生成测试图片")
    print("=" * 70)
    print()

    # 创建images目录
    if not os.path.exists('images'):
        os.makedirs('images')
        print("创建目录: images/")
    print()

    # 定义要生成的图片列表
    # 格式: (id, 宽度, 高度, 颜色RGB, 文字)
    test_images = [
        (1, 400, 300, (76, 175, 80), "图片 1"),
        (2, 400, 300, (33, 150, 243), "图片 2"),
        (3, 800, 400, (255, 0, 0), "图片 3"),
        (4, 350, 250, (255, 107, 107), "图片 4"),
        (5, 200, 200, (52, 152, 219), "图片 5"),
        (6, 600, 300, (155, 89, 182), "图片 6"),
        (7, 250, 200, (52, 73, 94), "图片 7"),
        (8, 150, 150, (231, 76, 60), "图片 8"),
        (9, 150, 150, (46, 204, 113), "图片 9"),
        (10, 300, 200, (241, 196, 15), "图片 10"),
        (11, 150, 150, (142, 68, 173), "图片 11"),
        (12, 150, 150, (26, 188, 156), "图片 12"),
        (13, 150, 150, (52, 73, 94), "图片 13"),
        (14, 150, 150, (230, 126, 34), "图片 14"),
        (15, 300, 200, (149, 165, 166), "图片 15"),
        (16, 300, 200, (22, 160, 133), "图片 16"),
        (17, 300, 200, (39, 174, 96), "图片 17"),
        (18, 300, 200, (241, 148, 138), "图片 18"),
        (19, 300, 200, (243, 156, 18), "图片 19"),
        (20, 300, 200, (52, 73, 94), "图片 20"),
        (21, 80, 80, (231, 76, 60), "产品1"),
        (22, 80, 80, (52, 152, 219), "产品2"),
        (23, 80, 80, (46, 204, 113), "产品3"),
        (24, 80, 80, (155, 89, 182), "产品4"),
        (25, 100, 80, (241, 196, 15), "堆叠1"),
        (26, 100, 80, (26, 188, 156), "堆叠2"),
        (27, 100, 80, (52, 73, 94), "堆叠3"),
        (28, 100, 80, (230, 126, 34), "堆叠4"),
        (29, 500, 300, (52, 152, 219), "安全图表"),
        (30, 450, 250, (22, 160, 133), "攻击分布"),
        (31, 300, 200, (39, 174, 96), "行业分布"),
        (32, 300, 200, (243, 156, 18), "区域分布"),
        (33, 300, 200, (142, 68, 173), "安全监控"),
        (34, 300, 200, (241, 148, 138), "威胁分析"),
        (35, 300, 200, (149, 165, 166), "应急响应"),
        (36, 600, 350, (33, 150, 243), "总体态势"),
        (37, 400, 200, (155, 89, 182), "时间线"),
        (38, 200, 150, (231, 76, 60), "指标1"),
        (39, 200, 150, (52, 152, 219), "指标2"),
        (40, 200, 150, (46, 204, 113), "指标3"),
        (41, 200, 150, (241, 196, 15), "指标4"),
        (42, 500, 250, (230, 126, 34), "行业影响"),
        (43, 550, 300, (76, 175, 80), "攻击路径"),
        (44, 450, 200, (33, 150, 243), "预测图表"),
        (45, 600, 200, (26, 188, 156), "总结图表"),
    ]

    print(f"准备生成 {len(test_images)} 张测试图片...")
    print()

    generated = 0
    for img_id, width, height, color, text in test_images:
        filename = f'images/{img_id}.jpg'
        generate_solid_image(width, height, color, text, filename)
        generated += 1

    print()
    print("=" * 70)
    print(f"[OK] 成功生成 {generated} 张测试图片")
    print(f"图片保存在: images/ 目录下")
    print("=" * 70)

if __name__ == '__main__':
    main()
