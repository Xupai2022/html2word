# HTML2Word 离线部署包

## 包内容

- `venv/` - 完整的Python虚拟环境（包含所有依赖）
- `src/` - 项目源代码
- `activate_venv.bat` - Windows环境激活脚本
- `activate_venv.sh` - Linux/Mac环境激活脚本
- `html2word-converter.bat` - Windows转换器快捷方式
- `oversear_monthly_report_part1.html` - 测试文件

## 使用方法

### Windows系统

1. **直接运行转换器**
   ```bash
   html2word-converter.bat --help
   ```

2. **激活虚拟环境后运行**
   ```bash
   activate_venv.bat
   python src/html2word/converter.py oversear_monthly_report_part1.html output.docx
   ```

### Linux/Mac系统

1. **激活虚拟环境后运行**
   ```bash
   chmod +x activate_venv.sh
   source activate_venv.sh
   python src/html2word/converter.py oversear_monthly_report_part1.html output.docx
   ```

## 验证安装

运行测试脚本验证所有功能：

```bash
# Windows
venv\Scripts\python test_svg_implementation.py

# Linux/Mac
venv/bin/python test_svg_implementation.py
```

## 注意事项

- 此包在 2025-11-22 23:34:06 创建
- Python版本: 3.9.7 (default, Sep 16 2021, 16:59:28) [MSC v.1916 64 bit (AMD64)]
- ChromeDriver已包含在包中（如适用）
- 所有依赖已预安装，无需联网

## 故障排除

如果Chrome浏览器渲染失败：
1. 确保系统已安装Chrome浏览器
2. ChromeDriver版本与Chrome浏览器版本匹配
3. 使用其他转换方法（cairosvg/svglib会自动fallback）

对于其他问题，请参考项目README.md文档。
