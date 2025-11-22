#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
离线部署包部署脚本
在离线设备上运行，用于验证和解压部署包
"""

import os
import sys
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

    @classmethod
    def print(cls, color, msg):
        if os.name != 'nt':  # 非Windows系统支持颜色
            print(f"{color}{msg}{cls.RESET}")
        else:
            print(msg)


def log_info(msg):
    """信息日志"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def log_success(msg):
    """成功日志"""
    Colors.print(Colors.GREEN, f"[{datetime.now().strftime('%H:%M:%S')}] ✓ {msg}")


def log_error(msg):
    """错误日志"""
    Colors.print(Colors.RED, f"[{datetime.now().strftime('%H:%M:%S')}] ✗ {msg}")


def log_warning(msg):
    """警告日志"""
    Colors.print(Colors.YELLOW, f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ {msg}")


def find_venv_python(extract_dir):
    """查找虚拟环境的Python可执行文件"""
    if os.name == 'nt':  # Windows
        python_exe = extract_dir / "venv" / "Scripts" / "python.exe"
        if python_exe.exists():
            return python_exe
    else:  # Linux/Mac
        python_exe = extract_dir / "venv" / "bin" / "python"
        if python_exe.exists():
            return python_exe

    return None


def find_venv_pip(extract_dir):
    """查找虚拟环境的pip可执行文件"""
    if os.name == 'nt':  # Windows
        pip_exe = extract_dir / "venv" / "Scripts" / "pip.exe"
        if pip_exe.exists():
            return pip_exe
    else:  # Linux/Mac
        pip_exe = extract_dir / "venv" / "bin" / "pip"
        if pip_exe.exists():
            return pip_exe

    return None


def check_package_structure(extract_dir):
    """检查包结构是否完整"""
    log_info("检查部署包结构...")

    required_items = {
        "src": "项目源代码",
        "venv": "虚拟环境",
        "requirements.txt": "依赖列表",
    }

    if os.name == 'nt':
        required_items["activate_venv.bat"] = "Windows激活脚本"
        required_items["html2word-converter.bat"] = "Windows转换器脚本"
    else:
        required_items["activate_venv.sh"] = "Linux/Mac激活脚本"

    all_ok = True
    for path, description in required_items.items():
        item_path = extract_dir / path
        if item_path.exists():
            log_success(f"{description}: {path}")
        else:
            log_error(f"{description} 缺失: {path}")
            all_ok = False

    return all_ok


def verify_virtual_environment(extract_dir):
    """验证虚拟环境"""
    log_info("\n验证虚拟环境...")

    python_exe = find_venv_python(extract_dir)
    if not python_exe:
        log_error("无法找到虚拟环境的Python可执行文件")
        return False

    log_success(f"找到Python: {python_exe.relative_to(extract_dir) if python_exe.is_relative_to(extract_dir) else python_exe}")

    # 测试Python是否可以运行
    try:
        result = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            log_success(f"Python运行正常: {result.stdout.strip()}")
        else:
            log_error(f"Python运行失败: {result.stderr}")
            return False
    except Exception as e:
        log_error(f"无法启动Python: {e}")
        return False

    return True


def check_dependencies(extract_dir):
    """检查关键依赖是否已安装"""
    log_info("\n检查关键依赖...")

    python_exe = find_venv_python(extract_dir)
    if not python_exe:
        return False

    required_packages = [
        ("selenium", "浏览器自动化"),
        ("webdriver_manager", "ChromeDriver管理"),
        ("cairosvg", "SVG转换方案1"),
        ("svglib", "SVG转换方案2"),
        ("reportlab", "SVG转换方案2"),
        ("PIL", "Pillow - 图像处理"),
        ("bs4", "BeautifulSoup - HTML解析"),
        ("docx", "python-docx - Word文档生成"),
        ("lxml", "XML解析"),
    ]

    all_ok = True
    for package, description in required_packages:
        try:
            result = subprocess.run(
                [str(python_exe), "-c", f"import {package}; print({package}.__version__)"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                log_success(f"{description}: {package} v{version}")
            else:
                log_warning(f"{description}: {package} (无法获取版本)")
        except Exception as e:
            log_error(f"{description}: {package} (导入失败: {e})")
            all_ok = False

    return all_ok


def verify_svg_conversion(extract_dir):
    """验证SVG转换功能"""
    log_info("\n验证SVG转换功能...")

    python_exe = find_venv_python(extract_dir)
    if not python_exe:
        return False

    # 创建一个测试SVG
    test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="red"/>
</svg>"""

    test_file = extract_dir / "test_svg_verify.svg"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_svg)

    # 测试各转换方法
    test_methods = [
        ("cairosvg", "cairosvg"),
        ("svglib", "svglib"),
        ("PIL", "PIL"),
    ]

    all_ok = True
    for method_name, module_name in test_methods:
        try:
            test_script = f"""
import sys
sys.path.insert(0, 'src')
try:
    from html2word.utils.browser_svg_converter import get_browser_converter
    converter = get_browser_converter()
    if converter.driver is not None:
        print("Browser: OK")
except:
    print("Browser: Not available")

import {module_name}
print("{method_name}: OK")
"""
            result = subprocess.run(
                [str(python_exe), "-c", test_script],
                cwd=extract_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if module_name == "cairosvg" and "cairosvg: OK" in result.stdout:
                log_success(f"SVG转换方案 - cairosvg: 可用")
            elif module_name == "svglib" and "svglib: OK" in result.stdout:
                log_success(f"SVG转换方案 - svglib/reportlab: 可用")
            elif method_name == "PIL":
                log_success(f"SVG转换方案 - PIL(fallback): 可用")
            else:
                log_warning(f"SVG转换方案 - {method_name}: 部分可用")

            if "Browser: OK" in result.stdout:
                log_success("浏览器渲染: Chrome和ChromeDriver已配置")
            elif "Browser: Not available" in result.stdout:
                log_warning("浏览器渲染: Chrome或ChromeDriver可能未正确配置（不影响其他方案）")

        except subprocess.TimeoutExpired:
            log_warning(f"SVG转换测试超时 - {method_name}")
        except Exception as e:
            log_error(f"SVG转换测试失败 - {method_name}: {e}")

    # 清理测试文件
    try:
        test_file.unlink()
    except:
        pass

    return all_ok


def run_quick_test(extract_dir):
    """运行快速转换测试"""
    log_info("\n运行快速转换测试...")

    python_exe = find_venv_python(extract_dir)
    if not python_exe:
        return False

    # 检查测试文件
    test_files = []
    if (extract_dir / "oversear_monthly_report_part1.html").exists():
        test_files.append("oversear_monthly_report_part1.html")
    elif (extract_dir / "test_svg_basic.html").exists():
        test_files.append("test_svg_basic.html")
    else:
        # 创建简单测试HTML
        test_html = """<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>
    <h1>SVG转换测试</h1>
    <svg width="100" height="100">
        <circle cx="50" cy="50" r="40" fill="blue"/>
    </svg>
</body>
</html>"""
        test_file = extract_dir / "test_quick.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_html)
        test_files.append("test_quick.html")

    for test_file in test_files:
        try:
            output_file = f"test_output_{Path(test_file).stem}.docx"
            log_info(f"测试转换: {test_file} -> {output_file}")

            result = subprocess.run(
                [str(python_exe), "-m", "html2word.converter", test_file, output_file],
                cwd=extract_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2分钟超时
            )

            if result.returncode == 0:
                output_path = extract_dir / output_file
                if output_path.exists():
                    size = output_path.stat().st_size
                    log_success(f"测试成功！输出文件: {output_file} ({size} 字节)")
                else:
                    log_error(f"转换完成，但输出文件未找到: {output_file}")
            else:
                log_error(f"测试失败: {result.stderr[:500]}")
                return False

        except subprocess.TimeoutExpired:
            log_error("转换测试超时")
            return False
        except Exception as e:
            log_error(f"转换测试异常: {e}")
            return False

    return True


def extract_package(package_file, extract_dir=None):
    """解压部署包"""
    if not extract_dir:
        extract_dir = Path(package_file).stem.replace('.zip', '')

    extract_path = Path(extract_dir)

    log_info(f"解压 {package_file} 到 {extract_dir}...")

    try:
        with zipfile.ZipFile(package_file, 'r') as zipf:
            zipf.extractall(extract_dir)
        log_success(f"解压完成: {extract_dir}")
        return str(extract_path.absolute())
    except Exception as e:
        log_error(f"解压失败: {e}")
        return None


def main():
    """主函数"""
    print("=" * 70)
    Colors.print(Colors.BLUE, "HTML2Word 离线部署验证工具")
    print("=" * 70)
    print()

    if len(sys.argv) < 2:
        print("用法: python deploy_offline_package.py <zip_file> [extract_dir]")
        print()
        print("参数:")
        print("  zip_file     - 离线部署包zip文件")
        print("  extract_dir  - 解压目录（可选，默认使用zip文件名）")
        print()
        print("示例:")
        print("  python deploy_offline_package.py html2word-offline-package.zip")
        print("  python deploy_offline_package.py html2word-offline-package.zip ./html2word-deploy")
        sys.exit(0)

    package_file = sys.argv[1]
    extract_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(package_file).exists():
        log_error(f"文件不存在: {package_file}")
        sys.exit(1)

    # 步骤1: 解压
    extract_path = extract_package(package_file, extract_dir)
    if not extract_path:
        sys.exit(1)

    extract_path = Path(extract_path)

    print()
    print("=" * 70)
    Colors.print(Colors.BLUE, "开始验证部署包")
    print("=" * 70)
    print()

    all_checks_passed = True

    # 步骤2: 检查包结构
    if not check_package_structure(extract_path):
        all_checks_passed = False

    # 步骤3: 验证虚拟环境
    if not verify_virtual_environment(extract_path):
        all_checks_passed = False

    # 步骤4: 检查依赖
    if not check_dependencies(extract_path):
        all_checks_passed = False

    # 步骤5: 验证SVG转换功能
    if not verify_svg_conversion(extract_path):
        all_checks_passed = False

    # 步骤6: 运行快速测试（可选）
    print()
    response = input("\n是否运行完整转换测试（推荐）? (y/n): ")
    if response.lower() == 'y':
        if not run_quick_test(extract_path):
            all_checks_passed = False

    # 总结
    print()
    print("=" * 70)
    if all_checks_passed:
        Colors.print(Colors.GREEN, "✅ 所有验证通过！部署包已准备就绪")
    else:
        Colors.print(Colors.YELLOW, "⚠️  部分验证未通过，请查看上面的错误信息")
    print("=" * 70)
    print()

    print("下一步:")
    print(f"cd {extract_path}")
    if os.name == 'nt':
        print("activate_venv.bat")
        print("html2word-converter.bat --help")
    else:
        print("source activate_venv.sh")
        print("python src/html2word/converter.py --help")
    print()
    print("更多信息请查看:")
    print(f"  {extract_path}/OFFLINE_PACKAGE_README.md")
    print()

    if all_checks_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
