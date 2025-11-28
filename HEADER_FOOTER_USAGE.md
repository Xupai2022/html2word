# 页眉页脚功能使用说明

## 功能概述

本项目已实现Word文档的页眉页脚功能，支持：

- **页眉**：左侧和右侧各显示一个图片，支持文字（可选）
- **页脚**：左侧显示联系信息（灰色），右侧显示页码（黑色，格式：当前页/总页数）
- **完整配置**：所有选项都可通过配置文件自定义

## 文件结构

```
html2word/
├── pic/                                    # 图片目录
│   ├── header.PNG                         # 页眉左侧图片
│   └── header2.png                        # 页眉右侧图片
├── src/html2word/
│   ├── config/
│   │   ├── __init__.py
│   │   └── header_footer_config.py        # 📌 页眉页脚配置文件（主要编辑这个！）
│   └── word_builder/
│       ├── document_builder.py            # 文档构建器（已集成页眉页脚）
│       └── header_footer_builder.py       # 页眉页脚构建器
└── test_header_footer.py                  # 测试脚本
```

## 快速开始

### 1. 默认使用（自动启用页眉页脚）

```python
from html2word.converter import HTML2WordConverter

# 创建转换器（默认启用页眉页脚）
converter = HTML2WordConverter()

# 转换HTML文件
converter.convert_file("input.html", "output.docx")
```

### 2. 禁用页眉页脚

```python
converter = HTML2WordConverter()

# 禁用页眉页脚
converter.document_builder.disable_header_footer()

# 转换
converter.convert_file("input.html", "output.docx")
```

### 3. 在代码中自定义配置

```python
converter = HTML2WordConverter()

# 动态修改配置
converter.document_builder.configure_header_footer(
    FOOTER_LEFT_TEXT="新的联系信息",
    FOOTER_FONT_SIZE=10,
    PAGE_NUMBER_FONT_SIZE=11
)

# 转换
converter.convert_file("input.html", "output.docx")
```

## 配置文件完整选项

主配置文件位置：`src/html2word/config/header_footer_config.py`

### 🔧 总体控制

```python
# ===== 总体开关 =====
ENABLE_HEADER_FOOTER = True  # 总开关：True=启用, False=禁用
ENABLE_HEADER = True          # 是否显示页眉
ENABLE_FOOTER = True          # 是否显示页脚
```

### 📷 页眉图片配置

```python
# ===== 页眉图片 =====
# 左侧图片
HEADER_LEFT_IMAGE = "pic/header.PNG"      # 图片路径（留空""不显示）
SHOW_HEADER_LEFT_IMAGE = True             # 是否显示左图
HEADER_LEFT_IMAGE_MAX_WIDTH = 2.5         # 最大宽度（英寸）

# 右侧图片
HEADER_RIGHT_IMAGE = "pic/header2.png"    # 图片路径（留空""不显示）
SHOW_HEADER_RIGHT_IMAGE = True            # 是否显示右图
HEADER_RIGHT_IMAGE_MAX_WIDTH = 1.5        # 最大宽度（英寸）

# 图片大小
HEADER_IMAGE_MAX_HEIGHT = 0.8             # 最大高度（英寸）
HEADER_IMAGE_VERTICAL_ALIGN = "MIDDLE"    # 垂直对齐：TOP/MIDDLE/BOTTOM

# 页眉文字（可选）
SHOW_HEADER_TEXT = False                  # 是否显示页眉文字
HEADER_CENTER_TEXT = ""                   # 页眉中间文字
HEADER_FONT_NAME = "Arial"                # 字体
HEADER_FONT_SIZE = 10                     # 字号（磅）
HEADER_TEXT_COLOR = (0, 0, 0)            # RGB颜色
```

### 📝 页脚文字配置

```python
# ===== 页脚左侧文字 =====
SHOW_FOOTER_LEFT_TEXT = True              # 是否显示
FOOTER_LEFT_TEXT = "Tel:+60 123457289 / Email: mdr@sangfor.com / Website: www.sangfor.com"
FOOTER_LEFT_ALIGN = "LEFT"                # 对齐：LEFT/CENTER/RIGHT

# 文字样式
FOOTER_TEXT_COLOR = (128, 128, 128)       # RGB灰色
FOOTER_FONT_NAME = "Arial"                # 字体
FOOTER_FONT_SIZE = 9                      # 字号（磅）
FOOTER_TEXT_BOLD = False                  # 是否加粗
FOOTER_TEXT_ITALIC = False                # 是否斜体

# ===== 页脚中间文字（可选）=====
SHOW_FOOTER_CENTER_TEXT = False           # 是否显示
FOOTER_CENTER_TEXT = ""                   # 中间文字内容
FOOTER_CENTER_TEXT_COLOR = (128, 128, 128)  # RGB颜色
```

### 🔢 页码配置

```python
# ===== 页码设置 =====
SHOW_PAGE_NUMBERS = True                  # 是否显示页码
PAGE_NUMBER_POSITION = "RIGHT"            # 位置：LEFT/CENTER/RIGHT

# 页码格式（重要！）
PAGE_NUMBER_FORMAT = "X/Y"                # 格式选项：
# "X"            → 1, 2, 3...
# "Page X"       → Page 1, Page 2...
# "第 X 页"       → 第 1 页, 第 2 页...
# "X/Y"          → 1/5, 2/5...（当前）
# "Page X of Y"  → Page 1 of 5...
# "第 X 页，共 Y 页" → 第 1 页，共 5 页...

# 页码样式
PAGE_NUMBER_FONT_NAME = "Arial"           # 字体
PAGE_NUMBER_FONT_SIZE = 10                # 字号（磅）
PAGE_NUMBER_COLOR = (0, 0, 0)            # RGB黑色
PAGE_NUMBER_BOLD = False                  # 是否加粗
PAGE_NUMBER_ITALIC = False                # 是否斜体
```

### 📐 间距和边距

```python
# ===== 间距设置 =====
HEADER_DISTANCE_FROM_TOP = 0.5           # 页眉距顶部（英寸）
FOOTER_DISTANCE_FROM_BOTTOM = 0.5        # 页脚距底部（英寸）
FOOTER_INTERNAL_SPACING = 6              # 页脚内部间距（磅）

# ===== 页边距 =====
TOP_MARGIN = 1.0                         # 顶部边距（英寸）
BOTTOM_MARGIN = 1.0                      # 底部边距（英寸）
LEFT_MARGIN = 1.0                        # 左边距（英寸）
RIGHT_MARGIN = 1.0                       # 右边距（英寸）
```

### 📑 特殊页面设置

```python
# ===== 页面范围 =====
APPLY_TO_FIRST_PAGE = True               # 应用到首页
APPLY_TO_EVEN_PAGES = True               # 应用到偶数页
APPLY_TO_ODD_PAGES = True                # 应用到奇数页

# ===== 首页特殊设置 =====
DIFFERENT_FIRST_PAGE = False             # 首页使用不同设置
FIRST_PAGE_SHOW_HEADER = False           # 首页显示页眉
FIRST_PAGE_SHOW_FOOTER = True            # 首页显示页脚
FIRST_PAGE_HEADER_TEXT = ""              # 首页页眉文字
FIRST_PAGE_FOOTER_TEXT = ""              # 首页页脚文字

# ===== 奇偶页不同 =====
DIFFERENT_ODD_EVEN = False                # 奇偶页使用不同设置
```

### 📏 线条和边框

```python
# ===== 页眉横线 =====
HEADER_LINE_BELOW = False                # 页眉下方添加横线
HEADER_LINE_COLOR = (0, 0, 0)           # 横线颜色 RGB
HEADER_LINE_WIDTH = 0.5                  # 横线宽度（磅）

# ===== 页脚横线 =====
FOOTER_LINE_ABOVE = False                # 页脚上方添加横线
FOOTER_LINE_COLOR = (0, 0, 0)           # 横线颜色 RGB
FOOTER_LINE_WIDTH = 0.5                  # 横线宽度（磅）
```

### 🎨 表格布局（高级）

```python
# ===== 列宽比例 =====
HEADER_TABLE_WIDTH_RATIO = [4.5, 0, 2.0]  # [左, 中, 右] 0表示不使用
FOOTER_TABLE_WIDTH_RATIO = [5.0, 0, 1.5]  # [左, 中, 右] 0表示不使用
```

## 测试功能

运行测试脚本：

```bash
python test_header_footer.py
```

这会生成三个测试文档：
1. `test_output_with_header_footer.docx` - 带页眉页脚
2. `test_output_custom_header_footer.docx` - 自定义配置
3. `test_output_no_header_footer.docx` - 无页眉页脚

## 常见问题

### Q: 如何更换页眉图片？

1. 将新图片放入 `pic/` 目录
2. 编辑 `src/html2word/config/header_footer_config.py`
3. 修改 `HEADER_LEFT_IMAGE` 或 `HEADER_RIGHT_IMAGE` 的值

### Q: 如何修改页脚联系信息？

编辑 `src/html2word/config/header_footer_config.py` 中的 `FOOTER_LEFT_TEXT`

### Q: 如何调整页眉图片大小？

修改配置文件中的：
- `HEADER_IMAGE_MAX_HEIGHT` - 控制高度
- `HEADER_LEFT_IMAGE_MAX_WIDTH` - 控制左图宽度
- `HEADER_RIGHT_IMAGE_MAX_WIDTH` - 控制右图宽度

### Q: 如何改变页脚文字颜色？

修改 `FOOTER_TEXT_COLOR`，使用RGB值：
- `(128, 128, 128)` - 灰色（当前）
- `(0, 0, 0)` - 黑色
- `(255, 0, 0)` - 红色

### Q: 图片文件不存在怎么办？

程序会跳过缺失的图片，但会记录警告。确保图片文件存在于指定路径。

## 注意事项

1. **图片格式**：支持 PNG、JPG、JPEG 等常见格式
2. **路径**：图片路径相对于项目根目录
3. **页码更新**：在Word中打开文档后，页码会自动更新
4. **兼容性**：生成的文档兼容Microsoft Word和WPS

## 扩展功能

如需更复杂的功能（如奇偶页不同、首页特殊等），可以修改配置：

```python
# 在 header_footer_config.py 中
DIFFERENT_ODD_EVEN = False      # 奇偶页不同
DIFFERENT_FIRST_PAGE = False    # 首页不同
```

注意：这些高级功能可能需要额外的代码实现。