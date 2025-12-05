# 09 - 配置系统 (Configuration System)

本文档详细介绍 html2word 的配置系统，包括 YAML 配置文件、Python 配置类和环境变量。

---

## 目录

1. [配置架构概览](#配置架构概览)
2. [YAML 配置文件](#yaml-配置文件)
3. [Python 配置类](#python-配置类)
4. [环境变量](#环境变量)
5. [配置加载机制](#配置加载机制)
6. [自定义配置](#自定义配置)

---

## 配置架构概览

html2word 采用分层配置架构：

```
┌─────────────────────────────────────────────────────────┐
│                     配置系统架构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────────┐   ┌─────────────────┐            │
│   │  YAML 配置文件   │   │  Python 配置类  │            │
│   │                 │   │                 │            │
│   │ • 字体映射       │   │ • 页眉页脚配置   │            │
│   │ • 默认样式       │   │ • 封面配置      │            │
│   └────────┬────────┘   └────────┬────────┘            │
│            │                     │                     │
│            └──────────┬──────────┘                     │
│                       ▼                                │
│            ┌─────────────────────┐                     │
│            │     环境变量覆盖     │                     │
│            │                     │                     │
│            │ • HTML2WORD_*       │                     │
│            │ • 运行时参数         │                     │
│            └──────────┬──────────┘                     │
│                       ▼                                │
│            ┌─────────────────────┐                     │
│            │    最终配置值        │                     │
│            └─────────────────────┘                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 配置文件位置

```
html2word/
├── config/                          # YAML 配置目录
│   ├── font_mapping.yaml           # 字体映射配置
│   └── default_styles.yaml         # 默认元素样式
│
└── src/html2word/config/           # Python 配置模块
    ├── __init__.py
    └── header_footer_config.py     # 页眉页脚配置类
```

---

## YAML 配置文件

### font_mapping.yaml - 字体映射配置

将 Web 字体映射到 Word 支持的字体。

**文件路径**: `config/font_mapping.yaml`

```yaml
Arial: "Arial"
Helvetica: "Arial"
"Helvetica Neue": "Arial"
default: "Calibri"
```

---

### default_styles.yaml - 默认元素样式

定义 HTML 元素的默认样式，基于 [W3C CSS2 默认样式规范](https://www.w3.org/TR/CSS2/sample.html)。

**文件路径**: `config/default_styles.yaml`

```yaml
# HTML元素默认样式（基于浏览器默认样式）

body:
  margin: 8px
  color: "#000000"
  line-height: 1.2

# 标题元素
h1:
  font-size: 2em
  font-weight: bold
  margin-top: 0.67em
  margin-bottom: 0.67em

# 段落
p:
  margin-top: 1em
  margin-bottom: 1em

# 文本样式
strong:
  font-weight: bold

b:
  font-weight: bold

# 列表
ul:
  margin-top: 1em
  margin-bottom: 1em
  margin-left: 40px
  list-style-type: disc

# 表格
table:
  display: table
  border-collapse: separate
  border-spacing: 2px


# 其他元素
hr:
  margin-top: 0.5em
  margin-bottom: 0.5em
  border-width: 1px
  border-style: solid
  border-color: "#000000"
```
---

## Python 配置类

### HeaderFooterConfig - 页眉页脚配置

**文件路径**: `src/html2word/config/header_footer_config.py`

这是一个功能完整的页眉页脚配置类，提供双语注释（中英文）。

#### 配置分类

```python
from html2word.config import HeaderFooterConfig

# 查看所有配置项
print(HeaderFooterConfig.ENABLE_HEADER_FOOTER)  # True
print(HeaderFooterConfig.HEADER_IMAGE_MAX_HEIGHT)  # 0.8 inches
```

#### 1. 总体开关 (Master Switch)

```python
class HeaderFooterConfig:
    # 是否启用页眉页脚
    ENABLE_HEADER_FOOTER = True

    # 是否启用页眉
    ENABLE_HEADER = True

    # 是否启用页脚
    ENABLE_FOOTER = True
```

#### 2. 封面图片配置 (Cover Image)

```python
    # 是否启用封面图片
    ENABLE_COVER_IMAGE = True

    # 封面图片路径（相对于项目根目录）
    COVER_IMAGE_PATH = "pic/cover.png"

    # 封面图片宽度（英寸），None 表示自动适应页面宽度
    COVER_IMAGE_WIDTH = 5

    # 封面图片高度（英寸），None 表示按比例自动计算
    COVER_IMAGE_HEIGHT = None

    # 封面图片后是否添加分页符
    COVER_ADD_PAGE_BREAK = False

    # 封面图片对齐方式: "LEFT", "CENTER", "RIGHT"
    COVER_IMAGE_ALIGNMENT = "CENTER"

    # 封面图片下方间距（磅）
    COVER_IMAGE_SPACE_AFTER = 12
```

#### 3. 页眉配置 (Header)

```python
    # === 页眉图片设置 ===

    # 左侧页眉图片路径
    HEADER_LEFT_IMAGE = "pic/header.PNG"
    SHOW_HEADER_LEFT_IMAGE = True

    # 右侧页眉图片路径
    HEADER_RIGHT_IMAGE = "pic/header2.png"
    SHOW_HEADER_RIGHT_IMAGE = True

    # 页眉图片尺寸限制（英寸）
    HEADER_IMAGE_MAX_HEIGHT = 0.8
    HEADER_LEFT_IMAGE_MAX_WIDTH = 2.5
    HEADER_RIGHT_IMAGE_MAX_WIDTH = 1.5

    # 页眉图片垂直对齐: "TOP", "MIDDLE", "BOTTOM"
    HEADER_IMAGE_VERTICAL_ALIGN = "MIDDLE"

    # === 页眉文字设置（可选）===

    SHOW_HEADER_TEXT = False
    HEADER_CENTER_TEXT = ""
    HEADER_FONT_NAME = "Arial"
    HEADER_FONT_SIZE = 10  # pt
    HEADER_TEXT_COLOR = (0, 0, 0)  # RGB

    # 页眉距离页面顶部的距离（英寸）
    HEADER_DISTANCE_FROM_TOP = 0.5
```

#### 4. 页脚配置 (Footer)

```python
    # === 页脚文字设置 ===

    SHOW_FOOTER_LEFT_TEXT = True
    FOOTER_LEFT_TEXT = "Tel:+60 123457289 / Email: mdr@sangfor.com / Website: www.sangfor.com"
    FOOTER_LEFT_ALIGN = "LEFT"  # "LEFT", "CENTER", "RIGHT"

    FOOTER_TEXT_COLOR = (128, 128, 128)  # 灰色 RGB
    FOOTER_FONT_NAME = "Arial"
    FOOTER_FONT_SIZE = 9  # pt
    FOOTER_TEXT_BOLD = False
    FOOTER_TEXT_ITALIC = False

    # === 页脚中间文字（可选）===

    SHOW_FOOTER_CENTER_TEXT = False
    FOOTER_CENTER_TEXT = ""
    FOOTER_CENTER_TEXT_COLOR = (128, 128, 128)

    # === 页码设置 ===

    SHOW_PAGE_NUMBERS = True
    PAGE_NUMBER_POSITION = "RIGHT"  # "LEFT", "CENTER", "RIGHT"

    # 页码格式选项:
    # - "X"                  -> 1, 2, 3...
    # - "Page X"             -> Page 1, Page 2...
    # - "第 X 页"            -> 第 1 页, 第 2 页...
    # - "X/Y"                -> 1/5, 2/5...
    # - "Page X of Y"        -> Page 1 of 5...
    # - "第 X 页，共 Y 页"    -> 第 1 页，共 5 页...
    PAGE_NUMBER_FORMAT = "X/Y"

    PAGE_NUMBER_FONT_NAME = "Arial"
    PAGE_NUMBER_FONT_SIZE = 10  # pt
    PAGE_NUMBER_COLOR = (0, 0, 0)  # 黑色
    PAGE_NUMBER_BOLD = False
    PAGE_NUMBER_ITALIC = False

    # 页脚距离页面底部的距离（英寸）
    FOOTER_DISTANCE_FROM_BOTTOM = 0.3
    FOOTER_INTERNAL_SPACING = 6  # pt
```

#### 5. 页面设置 (Page Settings)

```python
    # === 页面范围设置 ===

    APPLY_TO_FIRST_PAGE = True
    APPLY_TO_EVEN_PAGES = True
    APPLY_TO_ODD_PAGES = True

    # === 特殊页面设置 ===

    # 是否为奇偶页使用不同的页眉页脚
    DIFFERENT_ODD_EVEN = False

    # 是否为首页使用不同的页眉页脚
    DIFFERENT_FIRST_PAGE = False

    # 首页特殊设置
    FIRST_PAGE_SHOW_HEADER = False
    FIRST_PAGE_SHOW_FOOTER = True
    FIRST_PAGE_HEADER_TEXT = ""
    FIRST_PAGE_FOOTER_TEXT = ""

    # === 页边距设置（英寸）===

    TOP_MARGIN = 1.0
    BOTTOM_MARGIN = 1.0
    LEFT_MARGIN = 1.0
    RIGHT_MARGIN = 1.0

    # === 表格布局设置 ===

    # 页眉表格列宽比例 [左, 中, 右]
    HEADER_TABLE_WIDTH_RATIO = [4.5, 0, 2.0]  # 中间列为0表示不使用

    # 页脚表格列宽比例 [左, 中, 右]
    FOOTER_TABLE_WIDTH_RATIO = [5.0, 0, 1.5]

    # === 线条和边框设置 ===

    HEADER_LINE_BELOW = False
    HEADER_LINE_COLOR = (0, 0, 0)
    HEADER_LINE_WIDTH = 0.5  # pt

    FOOTER_LINE_ABOVE = False
    FOOTER_LINE_COLOR = (0, 0, 0)
    FOOTER_LINE_WIDTH = 0.5  # pt
```

#### 配置类方法

```python
from pathlib import Path
from html2word.config import HeaderFooterConfig

# 获取封面图片完整路径
cover_path: Path = HeaderFooterConfig.get_cover_image_path(base_path="/project")

# 获取页眉图片路径
left_header: Path = HeaderFooterConfig.get_header_left_image_path(base_path="/project")
right_header: Path = HeaderFooterConfig.get_header_right_image_path(base_path="/project")

# 验证配置有效性（检查图片文件是否存在）
is_valid: bool = HeaderFooterConfig.validate_config(base_path="/project")
```

---

## 环境变量

html2word 支持通过环境变量覆盖默认配置，便于运行时调整。

### 支持的环境变量

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `HTML2WORD_LOG_LEVEL` | `INFO` | 日志级别: DEBUG, INFO, WARNING, ERROR |
| `HTML2WORD_SCREENSHOT_SCALE` | `2` | 截图缩放因子（用于浏览器渲染） |
| `HTML2WORD_PARALLEL` | `true` | 是否启用并行处理 |
| `HTML2WORD_WORKERS` | `4` | 并行工作线程数 |
| `HTML2WORD_MONITOR` | `true` | 是否启用性能监控 |

### 使用示例

#### Windows (CMD)

```cmd
set HTML2WORD_LOG_LEVEL=DEBUG
set HTML2WORD_PARALLEL=true
set HTML2WORD_WORKERS=8
html2word input.html -o output.docx
```

#### Windows (PowerShell)

```powershell
$env:HTML2WORD_LOG_LEVEL = "DEBUG"
$env:HTML2WORD_PARALLEL = "true"
$env:HTML2WORD_WORKERS = "8"
html2word input.html -o output.docx
```

#### Linux/macOS

```bash
export HTML2WORD_LOG_LEVEL=DEBUG
export HTML2WORD_PARALLEL=true
export HTML2WORD_WORKERS=8
html2word input.html -o output.docx

# 或者单行命令
HTML2WORD_LOG_LEVEL=DEBUG HTML2WORD_PARALLEL=true html2word input.html -o output.docx
```

#### Python 代码中设置

```python
import os

# 设置环境变量（必须在导入 html2word 之前）
os.environ['HTML2WORD_LOG_LEVEL'] = 'DEBUG'
os.environ['HTML2WORD_PARALLEL'] = 'true'
os.environ['HTML2WORD_WORKERS'] = '8'

from html2word import HTML2WordConverter

converter = HTML2WordConverter()
converter.convert_file("input.html", "output.docx")
```

---

## 配置加载机制

### 加载顺序

配置按以下优先级加载（后者覆盖前者）：

```
1. 代码内硬编码默认值
       ↓
2. YAML 配置文件 (config/*.yaml)
       ↓
3. Python 配置类 (HeaderFooterConfig)
       ↓
4. 环境变量 (HTML2WORD_*)
       ↓
5. CLI 参数 (--log-level, --base-path)
```

---

## 自定义配置

### 方式一：修改 YAML 配置文件

直接编辑 `config/` 目录下的 YAML 文件：

```yaml
# config/font_mapping.yaml
# 添加自定义字体映射
"My Custom Font": "Arial"
"公司专用字体": "Microsoft YaHei"
```

### 方式二：继承配置类

```python
from html2word.config import HeaderFooterConfig

class MyConfig(HeaderFooterConfig):
    """自定义页眉页脚配置"""

    # 覆盖默认值
    ENABLE_COVER_IMAGE = False
    HEADER_LEFT_IMAGE = "assets/my_logo.png"
    FOOTER_LEFT_TEXT = "© 2024 My Company"
    PAGE_NUMBER_FORMAT = "Page X of Y"

    # 自定义页边距
    TOP_MARGIN = 0.75
    BOTTOM_MARGIN = 0.75
```

### 方式三：运行时修改配置

```python
from html2word.config import HeaderFooterConfig

# 直接修改类属性（影响全局）
HeaderFooterConfig.ENABLE_COVER_IMAGE = False
HeaderFooterConfig.FOOTER_LEFT_TEXT = "Custom Footer Text"
HeaderFooterConfig.PAGE_NUMBER_FORMAT = "第 X 页，共 Y 页"

# 然后进行转换
from html2word import HTML2WordConverter
converter = HTML2WordConverter()
converter.convert_file("input.html", "output.docx")
```

### 方式四：使用环境变量脚本

创建配置脚本 `convert.sh` (Linux/macOS) 或 `convert.bat` (Windows):

**Linux/macOS (`convert.sh`)**:
```bash
#!/bin/bash
export HTML2WORD_LOG_LEVEL=DEBUG
export HTML2WORD_PARALLEL=true
export HTML2WORD_WORKERS=8
export HTML2WORD_SCREENSHOT_SCALE=3

html2word "$@"
```

**Windows (`convert.bat`)**:
```batch
@echo off
set HTML2WORD_LOG_LEVEL=DEBUG
set HTML2WORD_PARALLEL=true
set HTML2WORD_WORKERS=8
set HTML2WORD_SCREENSHOT_SCALE=3

html2word %*
```

---

## 配置最佳实践

### 1. 生产环境配置

```python
# 禁用调试功能，优化性能
import os
os.environ['HTML2WORD_LOG_LEVEL'] = 'WARNING'
os.environ['HTML2WORD_PARALLEL'] = 'true'
os.environ['HTML2WORD_WORKERS'] = '4'
os.environ['HTML2WORD_MONITOR'] = 'false'
```

### 2.高质量输出配置

```python
# 提高图片渲染质量
import os
os.environ['HTML2WORD_SCREENSHOT_SCALE'] = '3'  # 更高分辨率
```

---

## 配置参考表

### 完整环境变量列表

| 变量名 | 类型 | 默认值 | 有效值 | 描述 |
|-------|------|-------|--------|------|
| `HTML2WORD_LOG_LEVEL` | string | `INFO` | DEBUG, INFO, WARNING, ERROR | 日志级别 |
| `HTML2WORD_PARALLEL` | bool | `true` | true, false | 并行处理开关 |
| `HTML2WORD_WORKERS` | int | `4` | 1-N | 工作线程数 |
| `HTML2WORD_MONITOR` | bool | `true` | true, false | 性能监控开关 |
| `HTML2WORD_SCREENSHOT_SCALE` | int | `2` | 1-4 | 截图缩放因子 |

### 配置文件路径

| 配置类型 | 文件路径 | 格式 |
|---------|---------|------|
| 字体映射 | `config/font_mapping.yaml` | YAML |
| 默认样式 | `config/default_styles.yaml` | YAML |
| 页眉页脚 | `src/html2word/config/header_footer_config.py` | Python |

---

