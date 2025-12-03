# HTML2Word 项目介绍与快速开始

> 版本: 0.1.0
> 许可证: MIT

## 概述

**HTML2Word** 是一个功能强大的 HTML 到 Word (.docx) 转换器，能够在转换过程中保留 CSS 样式。该项目可以将 HTML 文档（包括复杂的 CSS 样式、表格、图片等）转换为格式良好的 Microsoft Word 文档。

### 核心特性

- **完整的 HTML 支持**: 支持 `p`, `h1-h6`, `div`, `span`, `table`, `ul/ol`, `img` 等常见 HTML 元素
- **CSS 样式保留**: 内联样式、`<style>` 标签样式完整解析
- **样式继承**: 遵循 CSS 继承机制
- **表格支持**: 支持复杂表格，包括单元格合并
- **图片处理**: 支持本地图片、网络图片、SVG 转换
- **链接保留**: 超链接保持可点击
- **页眉页脚**: 可配置的页眉页脚
- **Element UI 兼容**: 支持 `el-table` 等组件
- **ECharts 支持**: SVG 图表转换

## 技术栈

| 类别 | 技术/库 | 版本要求 |
|------|---------|----------|
| **语言** | Python | >= 3.8 |
| **HTML 解析** | BeautifulSoup4 | >= 4.12.0 |
| **HTML 解析 (底层)** | lxml | >= 5.0.0 |
| **CSS 解析** | tinycss2 | >= 1.2.0 |
| **Word 生成** | python-docx | >= 1.1.0 |
| **图像处理** | Pillow | >= 10.0.0 |
| **网络请求** | requests | >= 2.31.0 |
| **配置管理** | PyYAML | >= 6.0.0 |

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd html2word

# 安装依赖
pip install -e .

# 安装开发依赖 (可选)
pip install -e ".[dev]"
```

### 依赖安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 命令行使用 (CLI)

安装后，可以直接使用 `html2word` 命令：

```bash
# 基本转换
html2word input.html -o output.docx

# 带调试日志
html2word input.html -o output.docx --log-level DEBUG

# 指定资源基础路径 (用于解析相对路径的图片等)
html2word input.html -o output.docx --base-path /path/to/resources
```

#### CLI 参数说明

| 参数 | 说明 | 必需 |
|------|------|------|
| `input` | 输入 HTML 文件路径 | 是 |
| `-o, --output` | 输出 Word 文件路径 | 是 |
| `--base-path` | 资源基础路径，用于解析相对路径 | 否 |
| `--log-level` | 日志级别: DEBUG, INFO, WARNING, ERROR | 否 (默认 INFO) |
| `--version` | 显示版本号 | 否 |

### Python API 使用

```python
from html2word import HTML2WordConverter

# 创建转换器
converter = HTML2WordConverter()

# 方式一: 文件转换
converter.convert_file("input.html", "output.docx")

# 方式二: 字符串转换
html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        h1 { color: #333; font-size: 24pt; }
        p { font-family: Arial; line-height: 1.5; }
    </style>
</head>
<body>
    <h1>Hello World</h1>
    <p>这是一个示例段落。</p>
</body>
</html>
"""
converter.convert_string(html_content, "output.docx")

# 方式三: 指定资源基础路径
converter = HTML2WordConverter(base_path="/path/to/resources")
converter.convert_file("input.html", "output.docx")
```

### API 方法详解

#### `HTML2WordConverter` 类

```python
class HTML2WordConverter:
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化转换器。

        Args:
            base_path: 资源基础路径，用于解析 HTML 中的相对路径。
                       默认为当前工作目录。
        """

    def convert(self, html_input: str, output_path: str,
                input_type: str = "file") -> str:
        """
        通用转换方法。

        Args:
            html_input: HTML 文件路径或 HTML 字符串
            output_path: 输出 .docx 文件路径
            input_type: 输入类型 - "file" 或 "string"

        Returns:
            输出文件的绝对路径
        """

    def convert_file(self, html_file: str, output_file: str) -> str:
        """文件转换快捷方法。"""

    def convert_string(self, html_string: str, output_file: str) -> str:
        """字符串转换快捷方法。"""
```

## 转换流程概览

HTML2Word 的转换过程分为四个阶段：

```
┌─────────────────┐
│   HTML 输入     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 1: 解析   │  HTMLParser → DOM Tree
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 2: 样式   │  StyleResolver → 样式继承 + 标准化
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 3: 构建   │  DocumentBuilder → Word Document
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 4: 保存   │  document.save()
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   .docx 输出    │
└─────────────────┘
```

## 项目结构

```
html2word/
├── src/html2word/           # 源代码主目录
│   ├── __init__.py          # 包入口
│   ├── cli.py               # 命令行接口
│   ├── converter.py         # 主转换器
│   ├── parser/              # HTML/CSS 解析模块
│   ├── style/               # 样式处理模块
│   ├── elements/            # 元素转换器
│   ├── word_builder/        # Word 文档构建模块
│   ├── utils/               # 工具函数
│   └── config/              # 配置模块
├── config/                  # 配置文件
│   ├── default_styles.yaml  # 默认样式
│   └── font_mapping.yaml    # 字体映射
├── tests/                   # 测试目录
├── pyproject.toml           # 项目配置
└── requirements.txt         # 依赖列表
```

## 下一步

- [整体架构设计](02_Architecture.md) - 深入了解系统架构
- [解析器模块](03_Parser_Module.md) - HTML/CSS 解析原理
- [样式处理模块](04_Style_Module.md) - 样式继承与计算
- [Word 构建模块](05_Word_Builder.md) - Word 文档生成

---

*此文档由 Claude Code 自动生成*
