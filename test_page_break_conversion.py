#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试分页功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from html2word.converter import HTML2WordConverter

def test_page_break():
    """测试分页功能"""
    print("开始测试分页功能...")

    # 创建转换器
    converter = HTML2WordConverter()

    # 输入文件
    input_file = "test_page_break.html"
    output_file = "test_page_break_output.docx"

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        return False

    try:
        # 转换文件
        print(f"正在转换 {input_file} 到 {output_file}...")
        result = converter.convert_file(input_file, output_file)

        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"[OK] 转换成功！输出文件：{result}")
            print(f"[OK] 文件大小：{file_size} 字节")

            # 打开 Word 文档检查（在 Windows 上）
            if sys.platform == 'win32':
                try:
                    os.system(f'start "" "{output_file}"')
                    print(f"[OK] 已尝试在 Word 中打开文件，请检查分页效果")
                except:
                    print(f"[OK] 文件已生成，请手动打开查看")

            return True
        else:
            print(f"[FAIL] 转换失败：输出文件未创建")
            return False

    except Exception as e:
        print(f"[ERROR] 转换出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_page_break()
    sys.exit(0 if success else 1)
