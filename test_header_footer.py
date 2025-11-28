"""
测试页眉页脚功能的脚本
Test script for header and footer functionality

这个脚本展示了如何使用页眉页脚功能
This script demonstrates how to use the header and footer functionality
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from html2word.converter import HTML2WordConverter
from html2word.config.header_footer_config import HeaderFooterConfig


def test_basic_header_footer():
    """测试基本的页眉页脚功能"""

    # 创建简单的HTML内容用于测试
    html_content = """
    <html>
    <head>
        <style>
            h1 { color: #333; font-size: 24pt; }
            p { margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>测试文档 - Test Document</h1>
        <p>这是第一页的内容。This is the content of the first page.</p>
        <p>页眉会显示两个图片：左侧是 header.PNG，右侧是 header2.png</p>
        <p>页脚左侧显示联系信息（灰色），右侧显示页码（黑色，格式：当前页/总页数）</p>

        <div style="page-break-before: always;"></div>

        <h1>第二页 - Page Two</h1>
        <p>这是第二页的内容。This is the content of the second page.</p>
        <p>你应该能看到页码变成了 2/2</p>

        <h2>页眉页脚配置说明</h2>
        <ul>
            <li>页眉左图：pic/header.PNG</li>
            <li>页眉右图：pic/header2.png</li>
            <li>页脚左侧文字：Tel:+60 123457289 / Email: mdr@sangfor.com / Website: www.sangfor.com（灰色）</li>
            <li>页脚右侧页码：当前页/总页数（黑色）</li>
        </ul>
    </body>
    </html>
    """

    # 创建转换器（默认启用页眉页脚）
    converter = HTML2WordConverter()

    # 转换HTML到Word
    output_file = "test_output_with_header_footer.docx"
    converter.convert_string(html_content, output_file)

    print(f"✅ 已生成带页眉页脚的Word文档: {output_file}")
    print("请打开文档查看页眉页脚效果")


def test_custom_configuration():
    """测试自定义配置页眉页脚"""

    html_content = """
    <html>
    <body>
        <h1>自定义配置测试</h1>
        <p>这个例子展示了如何通过代码修改页眉页脚配置</p>
    </body>
    </html>
    """

    # 创建转换器
    converter = HTML2WordConverter()

    # 通过代码自定义页眉页脚配置
    converter.document_builder.configure_header_footer(
        # 修改页脚文字
        FOOTER_LEFT_TEXT="自定义联系方式 | Custom Contact Info",

        # 修改页脚字体大小
        FOOTER_FONT_SIZE=8,

        # 修改页码字体大小
        PAGE_NUMBER_FONT_SIZE=9,

        # 修改页眉图片最大高度
        HEADER_IMAGE_MAX_HEIGHT=0.6  # 缩小页眉图片
    )

    # 转换
    output_file = "test_output_custom_header_footer.docx"
    converter.convert_string(html_content, output_file)

    print(f"✅ 已生成自定义页眉页脚的Word文档: {output_file}")


def test_disable_header_footer():
    """测试禁用页眉页脚"""

    html_content = """
    <html>
    <body>
        <h1>无页眉页脚文档</h1>
        <p>这个文档禁用了页眉页脚功能</p>
    </body>
    </html>
    """

    # 创建转换器
    converter = HTML2WordConverter()

    # 禁用页眉页脚
    converter.document_builder.disable_header_footer()

    # 转换
    output_file = "test_output_no_header_footer.docx"
    converter.convert_string(html_content, output_file)

    print(f"✅ 已生成无页眉页脚的Word文档: {output_file}")


def validate_configuration():
    """验证配置文件是否正确"""
    config = HeaderFooterConfig()

    print("\n📋 当前页眉页脚配置：")
    print("-" * 50)

    # 页眉配置
    print("【页眉配置】")
    print(f"  左侧图片: {config.HEADER_LEFT_IMAGE}")
    print(f"  右侧图片: {config.HEADER_RIGHT_IMAGE}")
    print(f"  图片最大高度: {config.HEADER_IMAGE_MAX_HEIGHT} 英寸")
    print(f"  左图最大宽度: {config.HEADER_LEFT_IMAGE_MAX_WIDTH} 英寸")
    print(f"  右图最大宽度: {config.HEADER_RIGHT_IMAGE_MAX_WIDTH} 英寸")

    # 页脚配置
    print("\n【页脚配置】")
    print(f"  左侧文字: {config.FOOTER_LEFT_TEXT}")
    print(f"  文字颜色: RGB{config.FOOTER_TEXT_COLOR} (灰色)")
    print(f"  文字字体: {config.FOOTER_FONT_NAME}")
    print(f"  文字大小: {config.FOOTER_FONT_SIZE} pt")
    print(f"  显示页码: {config.SHOW_PAGE_NUMBERS}")
    print(f"  页码格式: {config.PAGE_NUMBER_FORMAT}")
    print(f"  页码大小: {config.PAGE_NUMBER_FONT_SIZE} pt")
    print(f"  页码颜色: RGB{config.PAGE_NUMBER_COLOR} (黑色)")

    # 验证图片文件是否存在
    print("\n【文件验证】")
    if config.validate_config():
        print("✅ 所有图片文件都存在")
    else:
        print("❌ 有图片文件缺失，请检查 pic/ 目录")

    print("-" * 50)


if __name__ == "__main__":
    print("=" * 60)
    print("页眉页脚功能测试")
    print("=" * 60)

    # 验证配置
    validate_configuration()

    # 运行测试
    print("\n开始测试...")

    # 1. 基本测试
    print("\n1. 测试基本页眉页脚功能")
    test_basic_header_footer()

    # 2. 自定义配置测试
    print("\n2. 测试自定义配置")
    test_custom_configuration()

    # 3. 禁用测试
    print("\n3. 测试禁用页眉页脚")
    test_disable_header_footer()

    print("\n" + "=" * 60)
    print("测试完成！请查看生成的Word文档")
    print("=" * 60)