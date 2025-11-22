# SVG转换库安装指南

HTML2Word支持多种SVG转换方法，按优先级排序：

## 方法1: CairoSVG（推荐 - 最高质量）

### Windows安装

```bash
# 1. 下载GTK3运行时
# 访问: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
# 下载并安装最新版本的gtk3-runtime-x.x.x-x-x-x-ts-win64.exe

# 2. 安装Python包
pip install cairosvg
```

### Linux安装

```bash
# Ubuntu/Debian
sudo apt-get install libcairo2-dev libgirepository1.0-dev
pip install cairosvg

# Fedora/RHEL
sudo dnf install cairo-devel gobject-introspection-devel
pip install cairosvg
```

### macOS安装

```bash
# 使用Homebrew
brew install cairo pkg-config
pip install cairosvg
```

## 方法2: svglib + reportlab（备选 - 良好兼容性）

```bash
pip install svglib reportlab
```

**优点**:
- 纯Python实现，无需系统依赖
- 安装简单
- 跨平台兼容性好

**缺点**:
- 复杂SVG支持有限
- 渲染质量略低于cairosvg

## 方法3: PIL占位符（自动fallback）

如果以上两种方法都不可用，系统会自动生成占位符图片：
- 灰色背景 + 边框
- 显示"[Chart/SVG]"文字
- 保持原始尺寸

**无需安装**，PIL已包含在基础依赖中。

## 推荐配置

### 开发环境
```bash
# 安装所有选项以获得最佳效果
pip install cairosvg svglib reportlab
```

### 生产环境（Windows）
```bash
# 如果可以配置GTK3
pip install cairosvg

# 如果无法配置GTK3
pip install svglib reportlab
```

### 生产环境（Linux/Docker）
```bash
# Dockerfile示例
FROM python:3.9
RUN apt-get update && apt-get install -y libcairo2-dev libgirepository1.0-dev
RUN pip install cairosvg svglib reportlab
```

## 验证安装

运行测试脚本验证SVG转换功能：

```bash
python test_svg_conversion.py
```

## 性能对比

| 方法 | 质量 | 速度 | 复杂度支持 | 安装难度 |
|------|------|------|------------|----------|
| cairosvg | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| svglib | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| PIL占位符 | ⭐⭐ | ⭐⭐⭐⭐⭐ | N/A | ⭐⭐⭐⭐⭐ |

## 常见问题

### Q: Windows上cairosvg安装失败？
A: 确保已安装GTK3运行时。如果仍然失败，使用svglib作为替代。

### Q: 某些SVG显示为占位符？
A: 检查日志输出，查看具体错误。可能是SVG内容过于复杂或包含不支持的特性。

### Q: 如何强制使用特定方法？
A: 修改 `image_builder.py` 中的 `build_svg` 方法，注释掉不需要的转换尝试。

## 技术支持

如有问题，请查看：
- 项目文档: README.md
- 问题跟踪: GitHub Issues
- 日志输出: 包含详细的转换尝试信息
