# HTML2Word

一个强大的 HTML 到 Word (.docx) 转换器，支持 CSS 样式保留、表格、图片、列表等复杂布局。

## ✨ 特性

- 🎨 **CSS 样式保留**: 自动解析并应用 CSS 样式（字体、颜色、对齐、边距等）
- 📊 **表格支持**: 完整支持 HTML 表格转换，包括合并单元格、边框样式
- 🖼️ **图片处理**: 支持本地图片和网络图片，自动调整尺寸
- 📝 **列表转换**: 支持有序列表和无序列表
- 🔗 **超链接**: 保留 HTML 中的超链接
- 🎯 **布局智能识别**: 自动识别 Grid/Flex 布局并转换为表格
- 🏷️ **特殊徽章**: 支持蓝色胶囊徽章等特殊样式元素
- 🖼️ **背景图片+文字**: 支持将背景图片与文字合成

## 📋 系统要求

- Python >= 3.8
- 操作系统: Windows / Linux / macOS

## 🚀 快速开始

### 1. 安装

**⚠️ 注意：本项目尚未发布到 PyPI，请使用本地安装方式**

```bash
# 1. 获取项目代码（从 Git 克隆或解压缩包）
cd html2word

# 2. 本地安装
pip install -e .

# 这会自动：
# ✓ 安装所有依赖包（beautifulsoup4, python-docx, lxml 等）
# ✓ 创建 html2word 命令行工具
# ✓ 使代码修改立即生效（开发模式）
```

**或者**，如果只想手动安装依赖：
```bash
pip install -r requirements.txt

# 然后使用模块方式运行：
python -m html2word.cli input.html -o output.docx
```

### 2. 使用方式

#### 命令行使用

安装后，可以直接使用 `html2word` 命令：

```bash
# 基本用法
html2word input.html -o output.docx

# 开启调试日志
html2word input.html -o output.docx --log-level DEBUG

```

#### Python 代码使用

```python
from html2word import HTML2WordConverter

# 创建转换器实例，base_path可选暂时用不到
converter = HTML2WordConverter(base_path='/path/to/html/directory')

# 方式一：转换 HTML 文件
converter.convert_file('input.html', 'output.docx')

# 方式二：转换 HTML 字符串
html_content = """
<html>
<head>
    <style>
        h1 { color: blue; font-size: 24pt; }
        p { color: #333; line-height: 1.5; }
    </style>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a <strong>test</strong> document.</p>
</body>
</html>
"""
converter.convert_string(html_content, 'output.docx')
```



## 🔧 配置说明

### 环境变量

项目支持以下环境变量进行配置：

```bash
# 设置日志级别
export HTML2WORD_LOG_LEVEL=DEBUG

# 并行处理（默认）
export HTML2WORD_PARALLEL=true

# 设置截图缩放比例提高清晰度（默认）
export HTML2WORD_SCREENSHOT_SCALE=2

# 并行worker数量（默认）
export HTML2WORD_WORKERS=4
```

### 配置文件

可以在项目根目录创建 `config/html2word.yaml` 配置文件：

```yaml
# 默认字体设置
font:
  default_family: 'Arial'
  default_size: 11

# 表格样式
table:
  default_border: true
  default_border_color: '#000000'
  default_border_width: 1

# 图片处理
image:
  max_width: 600
  max_height: 400
  quality: 95
```

## 📁 项目结构

```
html2word/
├── src/
│   └── html2word/
│       ├── __init__.py          # 包入口
│       ├── converter.py         # 核心转换器
│       ├── parser.py            # HTML 解析器
│       ├── style_parser.py      # CSS 样式解析器
│       ├── word_builder.py      # Word 文档构建器
│       ├── cli.py               # 命令行接口
│       └── utils/               # 工具模块
├── tests/                       # 测试文件
├── config/                      # 配置文件
├── requirements.txt             # 依赖列表
├── setup.py                     # 安装脚本
├── pyproject.toml               # 项目元数据
└── README.md                    # 本文档
```



## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/Xupai2022/html2word.git
cd html2word

# 安装开发依赖
pip install -e /path/to/your/html2word
html2word input.html -o output.docx  # 命令行直接转换

from html2word import HTML2WordConverter  # SDK
converter = HTML2WordConverter()
converter.convert_file('input.html', 'output.docx')
```

## 📝 更新日志

### v0.1.0 (2024-12-05)
- ✨ 初始版本发布
- 支持基本 HTML 到 Word 转换
- CSS 样式解析和应用
- 表格、图片、列表支持
- 命令行工具

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

- **Xu Pai** - [xupai2024@163.com](mailto:xupai2024@163.com)

## 🙏 致谢

本项目使用了以下优秀的开源库：
- [python-docx](https://python-docx.readthedocs.io/) - Word 文档操作
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析
- [tinycss2](https://doc.courtbouillon.org/tinycss2/) - CSS 解析
- [Pillow](https://python-pillow.org/) - 图片处理

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- Email: xupai2024@163.com
- GitHub Issues: https://github.com/Xupai2022/html2word/issues

---

⭐ 如果这个项目对你有帮助，请给个 Star！
