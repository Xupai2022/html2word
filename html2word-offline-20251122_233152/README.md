# HTML2Word - HTML到Word转换工具

一个强大的 HTML 到 Word (.docx) 转换工具，能够高质量地保留 CSS 样式，将 HTML 文档转换为可编辑的 Word 文档。

## 🌟 核心特性

### 完整的样式支持
- ✅ **字体样式**：字体族、大小、粗细、斜体、颜色
- ✅ **文本装饰**：下划线、删除线
- ✅ **段落样式**：对齐方式、行高、缩进、间距
- ✅ **盒模型**：margin、padding、border
- ✅ **背景颜色**：段落和表格单元格背景
- ✅ **列表**：有序列表、无序列表、嵌套列表

### 复杂元素处理
- ✅ **表格转换**
  - 支持单元格合并（colspan / rowspan）
  - 表格边框和背景色
  - 列宽计算（固定宽度、百分比、自动）
  - 嵌套表格

- ✅ **图片处理**
  - 本地文件路径
  - 远程 URL
  - Base64 数据 URI
  - 自动格式转换（支持 PNG、JPEG、GIF、BMP）
  - 尺寸计算和缩放

### 架构设计

采用五层管道架构，确保高质量转换：

```
HTML输入 → [解析层] → [样式计算层] → [布局层] → [Word生成层] → .docx输出
```

1. **解析层**：使用 BeautifulSoup4 解析 HTML 结构和内联 CSS
2. **样式计算层**：处理样式继承、层叠、规范化
3. **布局层**：计算盒模型和流式布局
4. **Word生成层**：使用 python-docx 生成 Word 文档
5. **工具层**：单位转换、颜色处理、字体映射、图片处理

## 📦 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/Xupai2022/html2word.git
cd html2word

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 依赖项

- Python >= 3.8
- beautifulsoup4 >= 4.12.0
- python-docx >= 1.1.0
- lxml >= 5.0.0
- tinycss2 >= 1.2.0
- Pillow >= 10.0.0
- requests >= 2.31.0
- PyYAML >= 6.0.0

## 🚀 快速开始

### 命令行使用

```bash
# 基本用法
html2word input.html -o output.docx

# 指定基础路径（用于解析相对路径的图片等资源）
html2word input.html -o output.docx --base-path /path/to/resources

# 开启调试日志
html2word input.html -o output.docx --log-level DEBUG
```

### Python API 使用

```python
from html2word import HTML2WordConverter

# 创建转换器
converter = HTML2WordConverter()

# 转换 HTML 文件
converter.convert_file('input.html', 'output.docx')

# 转换 HTML 字符串
html_string = """
<html>
<body>
    <h1 style="color: #0066cc;">Hello World</h1>
    <p style="font-size: 14px;">This is a paragraph.</p>
</body>
</html>
"""
converter.convert_string(html_string, 'output.docx')
```

## 📖 示例

项目包含三个示例 HTML 文件，展示不同的功能：

### 1. 简单文本示例 (`examples/simple_text.html`)
- 基本文本格式（粗体、斜体、下划线）
- 标题层级
- 列表
- 背景色和边框

### 2. 表格示例 (`examples/with_table.html`)
- 基础表格
- 表头样式
- 单元格合并（colspan / rowspan）
- 表格边框和背景色

### 3. 综合示例 (`examples/comprehensive.html`)
- 完整的样式演示
- 多层级标题
- 复杂表格
- 多种文本对齐方式
- 颜色和背景效果

运行示例：

```bash
# 转换简单文本示例
html2word examples/simple_text.html -o output_simple.docx

# 转换表格示例
html2word examples/with_table.html -o output_table.docx

# 转换综合示例
html2word examples/comprehensive.html -o output_comprehensive.docx
```

## 🎨 样式映射

### CSS 到 Word 的样式映射表

| CSS 属性 | Word 实现 | 说明 |
|---------|----------|------|
| `font-family` | Run.font.name | 自动映射到 Word 支持的字体 |
| `font-size` | Run.font.size | 支持 px、pt、em、rem 等单位 |
| `font-weight` | Run.font.bold | ≥600 视为粗体 |
| `font-style` | Run.font.italic | italic/oblique 转为斜体 |
| `color` | Run.font.color.rgb | 支持 hex、rgb、颜色名称 |
| `text-decoration` | Run.font.underline/strike | 下划线、删除线 |
| `text-align` | Paragraph.alignment | left/center/right/justify |
| `line-height` | Paragraph.line_spacing | 倍数或绝对值 |
| `margin-*` | Paragraph.space_before/after/indent | 段落间距 |
| `padding` | 表格单元格 padding | 仅表格支持 |
| `border` | 段落/表格边框 | 边框样式、颜色、宽度 |
| `background-color` | Paragraph/Cell shading | 背景色 |
| `vertical-align` | Cell.vertical_alignment | 表格单元格垂直对齐 |

## 🔧 配置

### 字体映射配置

编辑 `config/font_mapping.yaml` 自定义字体映射：

```yaml
Arial: "Arial"
Helvetica: "Arial"
"微软雅黑": "Microsoft YaHei"
# 添加自定义映射...
```

### 默认样式配置

编辑 `config/default_styles.yaml` 自定义 HTML 元素的默认样式：

```yaml
h1:
  font-size: 2em
  font-weight: bold
  margin-top: 0.67em
  margin-bottom: 0.67em
# 自定义其他元素样式...
```

## 📐 技术架构

### 核心模块

```
html2word/
├── parser/          # HTML/CSS 解析
│   ├── html_parser.py
│   ├── css_parser.py
│   └── dom_tree.py
├── style/           # 样式计算
│   ├── style_resolver.py
│   ├── inheritance.py
│   ├── box_model.py
│   └── style_normalizer.py
├── layout/          # 布局计算
│   ├── flow_layout.py
│   ├── block_layout.py
│   └── inline_layout.py
├── docx/            # Word 生成
│   ├── document_builder.py
│   ├── paragraph_builder.py
│   ├── table_builder.py
│   ├── image_builder.py
│   └── style_mapper.py
├── utils/           # 工具函数
│   ├── units.py     # 单位转换
│   ├── colors.py    # 颜色转换
│   ├── fonts.py     # 字体映射
│   └── image_utils.py
├── converter.py     # 主转换器
└── cli.py           # 命令行接口
```

### 转换流程

1. **HTML 解析**：BeautifulSoup4 解析 HTML，提取 DOM 树和内联样式
2. **样式计算**：计算样式继承、规范化样式值、构建盒模型
3. **布局分析**：分析元素的流式布局特性
4. **Word 生成**：使用 python-docx 创建段落、表格、图片
5. **样式应用**：将 CSS 样式映射为 Word 格式

## 🎯 设计原则

### 1. 零硬编码
- 所有样式基于原始 HTML 的内联 CSS
- 不使用任何固定的样式值
- 通过配置文件管理默认值和映射

### 2. 样式优先
- 优先保证样式的准确还原
- 性能是次要考虑因素
- 详细的日志记录转换过程

### 3. 流式布局
- HTML 的流式布局 → Word 的流式段落
- 不使用绝对定位
- 通过段落顺序、缩进、间距还原布局

## ⚠️ 限制与注意事项

### Word 不支持的样式
- `box-shadow`、`text-shadow` - 阴影效果
- `border-radius` - 圆角边框（图片除外）
- `transform`、`animation` - CSS3 变换和动画
- `float`、`position: absolute` - 复杂定位（会降级为流式布局）

### 图片处理限制
- 不支持 SVG（会尝试转换为 PNG）
- WebP 等新格式会自动转换为 PNG
- 远程图片下载有 10 秒超时限制
- 单张图片最大尺寸：4000x4000 像素

### 浏览器差异
- 转换基于标准 CSS 规范
- 某些浏览器特定效果可能无法完全还原

## 🔍 调试

启用详细日志：

```bash
html2word input.html -o output.docx --log-level DEBUG
```

日志会显示：
- HTML 解析统计
- 样式计算过程
- 元素转换细节
- 警告和错误信息

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
flake8 src/
```

### 类型检查

```bash
mypy src/
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

本项目使用了以下优秀的开源库：

- [python-docx](https://python-docx.readthedocs.io/) - Word 文档生成
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析
- [tinycss2](https://doc.courtbouillon.org/tinycss2/) - CSS 解析
- [Pillow](https://python-pillow.org/) - 图片处理

## 📧 联系方式

- 项目地址：https://github.com/Xupai2022/html2word
- 问题反馈：https://github.com/Xupai2022/html2word/issues

---

**HTML2Word** - 让 HTML 到 Word 的转换变得简单而优雅
