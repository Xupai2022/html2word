"""
页眉页脚配置文件 - Header/Footer Configuration

这个文件包含Word文档页眉页脚的所有配置。
您可以直接编辑此文件来修改页眉页脚的内容和样式。

This file contains all configuration for Word document headers and footers.
You can directly edit this file to modify header/footer content and styles.
"""

from pathlib import Path
import os


class HeaderFooterConfig:
    """页眉页脚配置类 - Header/Footer Configuration Class"""

    # ==================== 总体开关 Master Switch ====================

    # 是否启用页眉页脚 (Master switch for headers and footers)
    ENABLE_HEADER_FOOTER = True  # True=启用, False=禁用

    # 是否启用页眉 (Enable header)
    ENABLE_HEADER = True

    # 是否启用页脚 (Enable footer)
    ENABLE_FOOTER = True

    # ==================== 封面图片配置 Cover Image Configuration ====================

    # 是否启用封面图片 (Enable cover image on first page)
    ENABLE_COVER_IMAGE = True

    # 封面图片路径 (Cover image path)
    # 相对于项目根目录的路径 (Path relative to project root)
    COVER_IMAGE_PATH = "pic/cover.png"

    # 封面图片宽度（英寸）(Cover image width in inches)
    # 设置为 None 时会自动计算以适应页面宽度
    COVER_IMAGE_WIDTH = 5  # inches - 默认为页面内容区域宽度

    # 封面图片高度（英寸）(Cover image height in inches)
    # 设置为 None 时会按比例自动计算
    COVER_IMAGE_HEIGHT = None  # inches - None 表示按比例自动计算

    # 封面图片后是否添加分页符 (Add page break after cover image)
    COVER_ADD_PAGE_BREAK = False

    # 封面图片对齐方式 (Cover image alignment)
    # 可选: "LEFT", "CENTER", "RIGHT"
    COVER_IMAGE_ALIGNMENT = "CENTER"

    # 封面图片下方间距（磅）(Space below cover image in points)
    COVER_IMAGE_SPACE_AFTER = 12  # pt

    # ==================== 页眉配置 Header Configuration ====================

    # === 页眉图片设置 Header Image Settings ===

    # 左侧页眉图片路径 (Left header image path)
    # 相对于项目根目录的路径 (Path relative to project root)
    # 留空字符串 "" 表示不显示左侧图片
    HEADER_LEFT_IMAGE = "pic/header.PNG"

    # 是否显示左侧页眉图片 (Whether to show left header image)
    SHOW_HEADER_LEFT_IMAGE = True

    # 右侧页眉图片路径 (Right header image path)
    # 相对于项目根目录的路径 (Path relative to project root)
    # 留空字符串 "" 表示不显示右侧图片
    HEADER_RIGHT_IMAGE = "pic/header2.png"

    # 是否显示右侧页眉图片 (Whether to show right header image)
    SHOW_HEADER_RIGHT_IMAGE = True

    # 页眉图片最大高度（英寸）(Maximum header image height in inches)
    # 调整此值来控制页眉图片的大小 (Adjust to control header image size)
    HEADER_IMAGE_MAX_HEIGHT = 0.8  # inches

    # 页眉图片最大宽度（英寸）(Maximum header image width in inches)
    HEADER_LEFT_IMAGE_MAX_WIDTH = 2.5   # inches - 左侧图片最大宽度
    HEADER_RIGHT_IMAGE_MAX_WIDTH = 1.5  # inches - 右侧图片最大宽度

    # 页眉图片对齐方式 (Header image alignment)
    # 可选: "TOP", "MIDDLE", "BOTTOM"
    HEADER_IMAGE_VERTICAL_ALIGN = "MIDDLE"

    # === 页眉文字设置（可选）Header Text Settings (Optional) ===

    # 是否在页眉显示文字 (Whether to show text in header)
    SHOW_HEADER_TEXT = False

    # 页眉中间文字 (Center text in header)
    HEADER_CENTER_TEXT = ""

    # 页眉文字字体 (Header text font)
    HEADER_FONT_NAME = "Arial"

    # 页眉文字大小（磅）(Header text size in points)
    HEADER_FONT_SIZE = 10

    # 页眉文字颜色 RGB (Header text color)
    HEADER_TEXT_COLOR = (0, 0, 0)  # 黑色 (Black)

    # 页眉距离页面顶部的距离（英寸）(Header distance from top of page)
    HEADER_DISTANCE_FROM_TOP = 0.5  # inches

    # ==================== 页脚配置 Footer Configuration ====================

    # === 页脚文字设置 Footer Text Settings ===

    # 是否显示页脚左侧文字 (Whether to show footer left text)
    SHOW_FOOTER_LEFT_TEXT = True

    # 页脚左侧文字内容 (Footer left text content)
    # 可以包含多行，使用 \n 换行
    FOOTER_LEFT_TEXT = "Tel:+60 123457289 / Email: mdr@sangfor.com / Website: www.sangfor.com"

    # 页脚左侧文字对齐方式 (Footer left text alignment)
    # 可选: "LEFT", "CENTER", "RIGHT"
    FOOTER_LEFT_ALIGN = "LEFT"

    # 页脚文字颜色 (Footer text color)
    # 使用RGB格式 (Use RGB format): (R, G, B) where each value is 0-255
    FOOTER_TEXT_COLOR = (128, 128, 128)  # 灰色 (Gray)

    # 页脚文字字体 (Footer text font)
    FOOTER_FONT_NAME = "Arial"

    # 页脚文字字号（磅）(Footer text font size in points)
    FOOTER_FONT_SIZE = 9  # pt

    # 页脚文字是否加粗 (Whether footer text is bold)
    FOOTER_TEXT_BOLD = False

    # 页脚文字是否斜体 (Whether footer text is italic)
    FOOTER_TEXT_ITALIC = False

    # === 页脚中间文字设置（可选）Footer Center Text Settings (Optional) ===

    # 是否显示页脚中间文字 (Whether to show footer center text)
    SHOW_FOOTER_CENTER_TEXT = False

    # 页脚中间文字内容 (Footer center text content)
    FOOTER_CENTER_TEXT = ""

    # 页脚中间文字颜色 RGB
    FOOTER_CENTER_TEXT_COLOR = (128, 128, 128)

    # === 页码设置 Page Number Settings ===

    # 页脚是否显示页码 (Whether to show page numbers in footer)
    SHOW_PAGE_NUMBERS = True

    # 页码位置 (Page number position)
    # 可选: "LEFT", "CENTER", "RIGHT"
    PAGE_NUMBER_POSITION = "RIGHT"

    # 页码格式 (Page number format)
    # 可选项 Options:
    # - "X" - 仅显示页码：1, 2, 3...
    # - "Page X" - 显示：Page 1, Page 2...
    # - "第 X 页" - 显示：第 1 页, 第 2 页...
    # - "X/Y" - 显示当前页/总页数：1/5, 2/5...
    # - "Page X of Y" - 显示：Page 1 of 5...
    # - "第 X 页，共 Y 页" - 显示：第 1 页，共 5 页...
    PAGE_NUMBER_FORMAT = "X/Y"  # Shows current page / total pages

    # 页码字体 (Page number font)
    PAGE_NUMBER_FONT_NAME = "Arial"

    # 页码字体大小（磅）(Page number font size in points)
    PAGE_NUMBER_FONT_SIZE = 10  # pt

    # 页码颜色 (Page number color)
    # 使用RGB格式 (Use RGB format): (R, G, B) where each value is 0-255
    PAGE_NUMBER_COLOR = (0, 0, 0)  # 黑色 (Black)

    # 页码是否加粗 (Whether page number is bold)
    PAGE_NUMBER_BOLD = False

    # 页码是否斜体 (Whether page number is italic)
    PAGE_NUMBER_ITALIC = False

    # === 页脚间距设置 Footer Spacing Settings ===

    # 页脚距离页面底部的距离（英寸）(Footer distance from bottom of page)
    FOOTER_DISTANCE_FROM_BOTTOM = 0.3  # inches

    # 页脚内容之间的间距（磅）(Spacing between footer elements)
    FOOTER_INTERNAL_SPACING = 6  # pt

    # ==================== 应用设置 Application Settings ====================

    # === 页面范围设置 Page Range Settings ===

    # 是否应用到首页 (Whether to apply to first page)
    APPLY_TO_FIRST_PAGE = True

    # 是否应用到偶数页 (Whether to apply to even pages)
    APPLY_TO_EVEN_PAGES = True

    # 是否应用到奇数页 (Whether to apply to odd pages)
    APPLY_TO_ODD_PAGES = True

    # === 特殊页面设置 Special Page Settings ===

    # 是否为奇偶页使用不同的页眉页脚 (Use different headers/footers for odd/even pages)
    DIFFERENT_ODD_EVEN = False

    # 是否为首页使用不同的页眉页脚 (Use different header/footer for first page)
    DIFFERENT_FIRST_PAGE = False

    # 首页特殊设置（当 DIFFERENT_FIRST_PAGE = True 时生效）
    # Special settings for first page (effective when DIFFERENT_FIRST_PAGE = True)

    # 首页是否显示页眉 (Show header on first page)
    FIRST_PAGE_SHOW_HEADER = False

    # 首页是否显示页脚 (Show footer on first page)
    FIRST_PAGE_SHOW_FOOTER = True

    # 首页页眉内容（可选）(First page header content - optional)
    FIRST_PAGE_HEADER_TEXT = ""

    # 首页页脚内容（可选）(First page footer content - optional)
    FIRST_PAGE_FOOTER_TEXT = ""

    # === 页边距设置 Margin Settings ===

    # 页边距（英寸）- 影响页眉页脚的可用空间
    # Page margins (inches) - affects available space for headers/footers

    # 顶部边距 (Top margin)
    TOP_MARGIN = 1.0  # inches

    # 底部边距 (Bottom margin)
    BOTTOM_MARGIN = 1.0  # inches

    # 左边距 (Left margin)
    LEFT_MARGIN = 1.0  # inches

    # 右边距 (Right margin)
    RIGHT_MARGIN = 1.0  # inches

    # === 表格布局设置 Table Layout Settings ===

    # 页眉页脚使用表格布局的列宽比例
    # Column width ratio for header/footer table layout

    # 页眉表格列宽比例 [左, 中, 右]
    HEADER_TABLE_WIDTH_RATIO = [4.5, 0, 2.0]  # 中间列为0表示不使用

    # 页脚表格列宽比例 [左, 中, 右]
    FOOTER_TABLE_WIDTH_RATIO = [5.0, 0, 1.5]  # 中间列为0表示不使用

    # === 线条和边框设置 Lines and Borders Settings ===

    # 是否在页眉下方添加横线 (Add line below header)
    HEADER_LINE_BELOW = False

    # 页眉横线颜色 RGB
    HEADER_LINE_COLOR = (0, 0, 0)  # 黑色

    # 页眉横线宽度（磅）
    HEADER_LINE_WIDTH = 0.5  # pt

    # 是否在页脚上方添加横线 (Add line above footer)
    FOOTER_LINE_ABOVE = False

    # 页脚横线颜色 RGB
    FOOTER_LINE_COLOR = (0, 0, 0)  # 黑色

    # 页脚横线宽度（磅）
    FOOTER_LINE_WIDTH = 0.5  # pt

    # ==================== 方法 Methods ====================

    @classmethod
    def get_cover_image_path(cls, base_path: str = None) -> Path:
        """
        获取封面图片的完整路径
        Get full path for cover image

        Args:
            base_path: 项目根目录路径 (Project root path)

        Returns:
            完整的图片路径 (Full image path)
        """
        if base_path is None:
            base_path = os.getcwd()
        return Path(base_path) / cls.COVER_IMAGE_PATH

    @classmethod
    def get_header_left_image_path(cls, base_path: str = None) -> Path:
        """
        获取左侧页眉图片的完整路径
        Get full path for left header image

        Args:
            base_path: 项目根目录路径 (Project root path)

        Returns:
            完整的图片路径 (Full image path)
        """
        if base_path is None:
            base_path = os.getcwd()
        return Path(base_path) / cls.HEADER_LEFT_IMAGE

    @classmethod
    def get_header_right_image_path(cls, base_path: str = None) -> Path:
        """
        获取右侧页眉图片的完整路径
        Get full path for right header image

        Args:
            base_path: 项目根目录路径 (Project root path)

        Returns:
            完整的图片路径 (Full image path)
        """
        if base_path is None:
            base_path = os.getcwd()
        return Path(base_path) / cls.HEADER_RIGHT_IMAGE

    @classmethod
    def validate_config(cls, base_path: str = None) -> bool:
        """
        验证配置是否有效（检查图片文件是否存在）
        Validate configuration (check if image files exist)

        Args:
            base_path: 项目根目录路径 (Project root path)

        Returns:
            配置是否有效 (Whether config is valid)
        """
        left_image = cls.get_header_left_image_path(base_path)
        right_image = cls.get_header_right_image_path(base_path)

        if not left_image.exists():
            print(f"警告 Warning: 左侧页眉图片不存在 Left header image not found: {left_image}")
            return False

        if not right_image.exists():
            print(f"警告 Warning: 右侧页眉图片不存在 Right header image not found: {right_image}")
            return False

        return True