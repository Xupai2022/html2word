#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字体一致性 - 验证转换后的Word文档中字体是否统一
"""

from docx import Document
import sys
import io

# 设置标准输出为UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_font_consistency(docx_path):
    """
    检查Word文档中的字体一致性

    Args:
        docx_path: Word文档路径
    """
    doc = Document(docx_path)

    print(f"检查文档: {docx_path}\n")

    # 检查每个段落
    for i, para in enumerate(doc.paragraphs):
        if not para.text.strip():
            continue

        # 收集段落中所有run的字体
        fonts_in_para = []
        for run in para.runs:
            if run.text.strip():
                font_name = run.font.name
                font_size = run.font.size.pt if run.font.size else "未设置"
                fonts_in_para.append((font_name, font_size, run.text[:20]))

        # 检查是否存在字体不一致
        if fonts_in_para:
            unique_fonts = set((f[0], f[1]) for f in fonts_in_para)

            if len(unique_fonts) > 1:
                print(f"⚠️  段落 {i+1} 存在字体不一致:")
                print(f"   文本: {para.text[:50]}...")
                print(f"   字体详情:")
                for font_name, font_size, text in fonts_in_para:
                    print(f"      - {font_name} ({font_size}pt): '{text}'")
                print()
            else:
                # 显示所有字体一致的段落
                font_name, font_size = list(unique_fonts)[0]
                print(f"✓  段落 {i+1} 字体一致:")
                print(f"   文本: {para.text[:80]}...")
                print(f"   字体: {font_name} ({font_size}pt)")
                print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = "test_output_fixed.docx"

    check_font_consistency(docx_path)
