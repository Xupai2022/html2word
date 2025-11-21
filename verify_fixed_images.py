#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证测试文件是否使用固定图片
"""

import re

def check_file(filename):
    """检查文件中的图片URL"""
    print(f"\n检查文件: {filename}")
    print("-" * 60)

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找所有图片URL
    img_pattern = r'src="([^"]+)"'
    matches = re.findall(img_pattern, content)

    print(f"找到 {len(matches)} 个src属性:\n")

    # 分类统计
    random_imgs = []
    image_imgs = []
    data_uri_imgs = []
    other_imgs = []

    for url in matches:
        if '?random=' in url:
            random_imgs.append(url)
        elif '?image=' in url:
            image_imgs.append(url)
        elif url.startswith('data:image'):
            data_uri_imgs.append(url)
        else:
            other_imgs.append(url)

    # 打印统计结果
    if random_imgs:
        print(f"[WARN] 发现随机图片 (?random=): {len(random_imgs)} 个")
        for url in random_imgs[:3]:  # 只显示前3个
            print(f"  - {url}")
        if len(random_imgs) > 3:
            print(f"  ... 还有 {len(random_imgs) - 3} 个")
        print()

    if image_imgs:
        print(f"[OK] 发现固定图片 (?image=): {len(image_imgs)} 个 [OK]")
        print(f"  这是正确的配置！图片URL包含 ?image= 参数")
        print(f"  例如: {image_imgs[0][:80]}...")
        print()

    if data_uri_imgs:
        print(f"[INFO] 发现Data URI图片: {len(data_uri_imgs)} 个")
        print(f"  这些是内联Base64编码图片")
        print()

    if other_imgs:
        print(f"[INFO] 其他类型图片: {len(other_imgs)} 个")
        for url in other_imgs[:3]:
            print(f"  - {url}")
        print()

    # 总结
    print("=" * 60)
    if random_imgs:
        print("[结论] 文件包含随机图片参数 ?random=")
        print("建议: 将 ?random= 替换为 ?image= 以获得固定图片")
        return False
    elif image_imgs:
        print("[结论] 文件配置正确！使用固定图片参数 ?image=")
        print("效果: 每次打开HTML都会看到相同的图片")
        print("好处: 测试更稳定，对比更清晰")
        return True
    else:
        print("[结论] 未发现标准的 picsum.photos 图片")
        print("状态: 可能是自定义图片或其他来源")
        return True

def main():
    print("=" * 60)
    print("  固定图片验证工具")
    print("=" * 60)
    print("")
    print("验证测试文件是否使用固定图片 (?image=)")
    print("而非随机图片 (?random=)")

    files = [
        'test_images_comprehensive.html',
        'test_images_advanced.html'
    ]

    all_good = True
    for filename in files:
        if not check_file(filename):
            all_good = False

    print("\n" + "=" * 60)
    print("最终总结:")
    if all_good:
        print("[OK] 所有文件都使用了固定图片配置")
        print("[OK] 可以开始进行一致的测试")
    else:
        print("[WARN] 部分文件使用了随机图片")
        print("[WARN] 建议修改为 ?image= 参数")
    print("=" * 60)

if __name__ == '__main__':
    main()
