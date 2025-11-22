# HTML2Word 离线部署完整指南

## 概述

本指南介绍如何在完全离线的设备上部署和使用HTML2Word工具，特别是支持完整的SVG图表转换功能。

## 方案总览

我们采用**虚拟环境打包**方案：
- 在一台联网的计算机上创建完整的Python虚拟环境
- 安装所有依赖并下载ChromeDriver
- 将整个环境打包成zip文件
- 传输到离线设备解压使用
- **无需在离线设备上执行任何联网操作**

## 部署流程

### 阶段1: 在联网设备上创建部署包

#### 步骤1.1: 准备工作

确保联网设备满足以下条件：
- 已安装Python 3.8+
- 可以访问互联网
- 至少1GB可用磁盘空间（用于创建虚拟环境）

#### 步骤1.2: 运行创建脚本

```bash
# 确保在html2word项目根目录
python create_offline_package.py
```

脚本会自动执行以下操作：

1. ✅ 创建虚拟环境
2. ✅ 安装核心依赖（beautifulsoup4, python-docx, Pillow等）
3. ✅ 安装SVG转换依赖：
   - selenium + webdriver-manager（浏览器方案）
   - cairosvg（高质量方案）
   - svglib + reportlab（兼容性方案）
4. ✅ 下载ChromeDriver（匹配系统Chrome版本）
5. ✅ 复制项目文件和配置
6. ✅ 创建激活脚本和说明文档
7. ✅ 打包成zip文件

#### 步骤1.3: 获取部署包

脚本运行完成后，会生成类似这样的文件：
```
html2word-offline-package-20251123_143022.zip
```

**文件大小**：约150-300MB（包含所有依赖和虚拟环境）

**包内结构**：
```
html2word-offline/
├── activate_venv.bat          # Windows激活脚本
├── activate_venv.sh           # Linux/Mac激活脚本
├── html2word-converter.bat    # Windows转换器快捷方式
├── OFFLINE_PACKAGE_README.md  # 使用说明
├── requirements.txt           # 依赖列表
├── src/                       # 项目源代码
├── venv/                      # 完整的虚拟环境（包含所有依赖）
└── ...其他项目文件...
```

#### 步骤1.4: 验证部署包（可选但推荐）

在联网设备上验证部署包是否正常：

```bash
python deploy_offline_package.py html2word-offline-package-20251123_143022.zip
```

此脚本会测试：
- 包结构完整性
- 虚拟环境可运行性
- 所有依赖是否可用
- SVG转换功能
- 完整转换测试

### 阶段2: 在离线设备上部署

#### 步骤2.1: 传输部署包

将zip文件传输到离线设备（通过U盘、移动硬盘等物理介质）

#### 步骤2.2: 解压部署包

```bash
# Linux/Mac
unzip html2word-offline-package-20251123_143022.zip

# Windows（右键解压或使用PowerShell）
Expand-Archive -Path html2word-offline-package-20251123_143022.zip -DestinationPath html2word-offline
```

#### 步骤2.3: 验证安装（必须在离线设备上运行）

```bash
cd html2word-offline
python deploy_offline_package.py html2word-offline-package-20251123_143022.zip ./deployed
```

或直接查看验证报告：

```bash
# 激活虚拟环境后运行验证脚本
cd deployed

# Windows
activate_venv.bat
python verify_installation.py

# Linux/Mac
source activate_venv.sh
python verify_installation.py
```

验证脚本会检查：
- 所有依赖是否正确安装
- 各项SVG转换方案是否可用
- 完整转换流程是否正常

#### 步骤2.4: 开始使用

**Windows系统：**

方法1（推荐）：使用快捷方式
```cmd
rem 直接运行转换器
html2word-converter.bat input.html output.docx

rem 查看帮助
html2word-converter.bat --help
```

方法2：先激活环境再运行
```cmd
rem 激活虚拟环境
activate_venv.bat

rem 运行转换
python src\html2word\converter.py input.html output.docx
```

**Linux/Mac系统：**

```bash
# 激活虚拟环境
source activate_venv.sh

# 运行转换
python src/html2word/converter.py input.html output.docx
```

### 阶段3: 验证SVG转换功能

运行测试脚本验证SVG功能：

```bash
# 激活虚拟环境后（Windows示例）
activate_venv.bat

# 运行验证脚本
python verify_installation.py

# 或使用快速验证（更快但测试较少）
python verify_installation.py --quick
```

或使用集成测试脚本：

```bash
# 激活虚拟环境后
activate_venv.bat

# 运行完整的SVG转换测试
python test_svg_implementation.py
```

这将测试：
- 基础SVG元素转换
- 复杂SVG图表（如ECharts图表）
- 所有4层fallback机制

## 常见问题

### Q1: SVG转换时提示ChromeDriver错误

**问题**：浏览器渲染方案无法使用
```
Chrome executable needs to be in PATH
```

**解决方案**：
- 确保系统已安装Chrome浏览器（虽然设备离线，但可能预装了Chrome）
- 如果未安装Chrome，不影响其他方案（cairosvg和svglib会自动接管）
- 如需使用浏览器方案，在联网设备上提前下载Chrome浏览器安装包并离线安装

### Q2: 某些SVG转换失败

**问题**：某些复杂SVG图表转换失败

**解决方案**：
- 我们的系统有3层fallback机制
- 如果浏览器方案失败，自动尝试cairosvg
- 如果cairosvg失败，自动尝试svglib
- 如果都失败，生成占位图（总比没有强）
- 日志中会记录具体使用哪种方案

### Q3: 如何更新离线包

**场景**：项目更新了，需要同步到离线设备

**解决方案**：
1. 在联网设备上更新代码：`git pull`
2. 重新运行创建脚本：`python create_offline_package.py`
3. 将新的zip文件传输到离线设备
4. 删除旧版本，解压新版本即可

### Q4: 可以只安装部分SVG方案吗？

**答案**：可以！如果你不需要浏览器方案：

修改 `create_offline_package.py`，注释掉浏览器相关：
```python
# 不安装selenium和webdriver-manager
svg_dependencies = [
    # "selenium>=4.0.0",
    # "webdriver-manager",
    "cairosvg",
    "svglib",
    "reportlab",
]
```

这样可以减小部署包大小约50MB。

### Q5: Linux/Mac设备上ChromeDriver路径问题

**问题**：Linux/Mac上ChromeDriver不在@PATH环境变量中

**解决方案**：
创建激活脚本时会自动添加ChromeDriver路径到PATH，正常激活环境即可：
```bash
source activate_venv.sh
```

如果仍有路径问题，手动添加：
```bash
export PATH="/path/to/venv/bin:$PATH"
```

### Q6: 部署包太大，如何优化

**减小部署包大小的方法**：

1. 排除开发依赖：
```python
# 在create_offline_package.py中修改
# 只安装核心依赖，不安装pytest, black等
```

2. 只保留必要的SVG方案：
- 如果只需要cairosvg，不安装selenium和webdriver-manager
- 包大小可减少约100MB

3. 使用压缩率更高的格式：
```python
# 修改create_offline_package.py
with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
```

## 性能参考

### 部署包大小
- 完整包（所有方案）：250-300MB
- 仅cairosvg方案：150-200MB
- 仅核心功能（无SVG）：80-100MB

### 转换性能（典型配置）
- 简单SVG：1-2秒
- 中等复杂度图表：3-5秒
- 复杂ECharts图表：5-15秒（浏览器方案）
- fallback到PIL占位图：<1秒

## 故障排除

### 验证失败时的处理步骤

如果`verify_installation.py`报告失败：

1. **检查Python环境**
```bash
python --version  # 需要3.8+
python -c "import sys; print(sys.prefix)"  # 确认虚拟环境
```

2. **检查核心依赖**
```bash
python -c "import bs4; print('bs4 OK')"
python -c "import docx; print('docx OK')"
python -c "from PIL import Image; print('PIL OK')"
```

3. **检查SVG转换依赖**
```bash
# 方案1
python -c "import cairosvg; print('cairosvg OK')"

# 方案2
python -c "import svglib; print('svglib OK')"
python -c "import reportlab; print('reportlab OK')"

# 方案3
python -c "import selenium; print('selenium OK')"
```

4. **查看详细日志**
```bash
python -m html2word.converter --verbose input.html output.docx
```

### 提交Issue

如果在离线环境遇到无法解决的问题：

1. 运行：`python verify_installation.py > verification.log 2>&1`
2. 提供以下信息：
   - verification.log文件内容
   - 操作系统版本
   - Python版本
   - Chrome浏览器版本（如适用）
   - 部署包的创建日期

## 安全注意事项

### 离线部署的优势
- ✅ 无需从互联网下载任何组件
- ✅ 所有依赖已包含在包内
- ✅ 代码可以审计
- ✅ 不依赖外部服务

### 检查部署包完整性

在联网设备上创建zip文件时，可以计算校验和：

```bash
# Linux/Mac
shasum html2word-offline-package.zip > checksum.txt

# Windows (PowerShell)
Get-FileHash html2word-offline-package.zip -Algorithm SHA256 | Format-List
```

在离线设备上验证：

```bash
# Linux/Mac
shasum -c checksum.txt

# Windows (PowerShell)
Get-FileHash html2word-offline-package.zip -Algorithm SHA256
```

## 技术支持

### 文档资源
- `README.md` - 项目主文档
- `SVG_SETUP_GUIDE.md` - SVG配置详细指南
- `OFFLINE_PACKAGE_README.md` - 离线包使用说明（自动创建）

### 测试文件
项目包含多个测试HTML文件，可用于验证：
- `test_svg_basic.html` - 基础SVG测试
- `oversear_monthly_report_part1.html` - 真实世界复杂案例
- `test_svg_implementation.py` - 完整测试套件

### 日志和调试
启用详细日志：
```bash
python -m html2word.converter --log-level DEBUG input.html output.docx
```

日志中会显示：
- 使用的SVG转换方案
- 转换时间
- 任何错误或警告
- Fallback信息

## 结论

使用虚拟环境打包方案，你可以：
- ✅ 在完全离线的设备上使用完整功能
- ✅ 支持所有SVG转换方案（浏览器、cairosvg、svglib）
- ✅ 无需在离线设备上安装任何额外软件
- ✅ 部署过程简单，一次打包，多次使用
- ✅ 验证工具确保部署成功

唯一的前提是在联网设备上创建部署包，之后即可在任意数量的离线设备上部署使用。
