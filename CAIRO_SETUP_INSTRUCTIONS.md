# Cairo Graphics 安装指南

## 背景
你的代码使用 `cairosvg` 库来转换SVG图片为PNG格式。`cairosvg` 需要 **Cairo Graphics 库**作为依赖（**注意**：这不是 StarkWare 的 Cairo 编程语言）。

## 快速安装步骤

### 方法1：运行自动安装脚本（推荐）

1. **双击运行 `run_setup.bat`**
   - 这个脚本会自动：
     - 解压 `cairo-windows.zip`
     - 配置系统环境变量 PATH
     - 安装必要的 Python 包（pycairo, cairosvg）
     - 测试安装是否成功

2. **如果脚本完成显示成功**
   - 完成！你现在可以转换 SVG 图片了
   - 如果提示需要重启终端/IDE，请重启

### 方法2：手动安装

如果自动脚本失败，可以手动操作：

#### 步骤1：解压 cairo-windows.zip

使用解压工具解压 `cairo-windows.zip`，得到一个文件夹（比如 `cairo_install`）。

#### 步骤2：配置系统环境变量

1. 找到解压后的 `bin` 目录（通常在 `cairo_install/bin` 或 `cairo_install/cairo/bin`）

2. 添加到系统 PATH：
   - 按 `Win + X`，选择"系统"
   - 点击"高级系统设置"
   - 点击"环境变量"
   - 在"系统变量"中找到 `Path`，点击"编辑"
   - 点击"新建"，添加 cairo 的 `bin` 目录路径
   - 一路点击"确定"保存

#### 步骤3：安装 Python 包

打开命令提示符（CMD）或 PowerShell，运行：

```bash
pip install pycairo cairosvg
```

#### 步骤4：验证安装

```python
python -c "import cairosvg; print('✓ cairosvg works:', cairosvg.__version__)"
```

## 故障排查

### 问题1：`cairosvg` 导入失败

**错误**：`OSError: no library called "cairo" was found`

**解决**：
1. 检查 PATH 是否包含 cairo 的 bin 目录
2. 重新打开终端/IDE（环境变量需要重启才能生效）
3. 验证 DLL 文件存在：
   ```bash
   where cairo.dll
   where libcairo-2.dll
   ```

### 问题2：找不到 cairo-windows.zip

**解决**：
1. 从以下地址下载：
   - https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - 或 https://www.cairographics.org/download/

2. 推荐下载方式：
   - GTK+ for Windows Runtime Environment（官方推荐）
   - 或使用 MSYS2：
     ```bash
     pacman -S mingw-w64-x86_64-cairo
     ```

### 问题3：64位 vs 32位不匹配

**错误**：DLL load 失败

**解决**：
- 确保你的 Python 版本（64位/32位）与 Cairo 库匹配
- 查看 Python 版本：
  ```bash
  python -c "import sys; print('64-bit' if sys.maxsize > 2**32 else '32-bit')"
  ```

## 替代方案

如果你的 SVG 转换仍然有问题，代码已经提供了多个后备方案：

1. **BrowserSVGConverter** - 使用浏览器引擎渲染（最佳质量，需要 Playwright）
2. **svglib + reportlab** - 纯 Python 方案（无需 cairo）

安装后备方案：
```bash
pip install svglib reportlab
# 或
pip install playwright
playwright install
```

## 测试 SVG 转换

运行测试脚本：
```bash
python test_svg_basic.html  # 或者你已有的测试文件
```

## 联系方式

如果仍然有问题，请检查：
- 项目文档中的 SVG 转换说明
- Python 错误日志
- Cairo Graphics 官方文档: https://www.cairographics.org/
