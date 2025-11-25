#!/usr/bin/env python
"""测试图片居中对齐功能"""

from src.html2word import HTML2WordConverter

def test_image_centering():
    """测试Security Rating图片是否正确居中"""
    html_file = "oversear_monthly_report_part1.html"
    output_file = "test_image_center_output.docx"

    print("开始转换HTML...")
    print(f"输入文件: {html_file}")
    print(f"输出文件: {output_file}")

    converter = HTML2WordConverter()
    converter.convert(html_file, output_file)

    print("\n转换完成！")
    print(f"请打开 {output_file} 检查:")
    print("1. 找到 'Security Rating' 章节")
    print("2. 确认其下方的图片是否居中显示")
    print("3. 对比原HTML文件中该图片的位置")

if __name__ == "__main__":
    test_image_centering()
