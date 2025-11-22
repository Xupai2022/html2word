#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML2Word 安装验证脚本
验证所有依赖和SVG转换功能是否正常工作
"""

import sys
import os
import importlib
import subprocess
import platform
from pathlib import Path


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @classmethod
    def print(cls, color, msg):
        if os.name != 'nt':  # 非Windows系统支持颜色
            print(f"{color}{msg}{cls.RESET}")
        else:
            print(msg)


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def pass_test(self, name, msg=""):
        self.passed += 1
        Colors.print(Colors.GREEN, f"  ✓ {name}")
        if msg:
            print(f"    {msg}")

    def fail_test(self, name, error=""):
        self.failed += 1
        Colors.print(Colors.RED, f"  ✗ {name}")
        if error:
            print(f"    错误: {error}")

    def warn_test(self, name, msg=""):
        self.warnings += 1
        Colors.print(Colors.YELLOW, f"  ⚠ {name}")
        if msg:
            print(f"    {msg}")

    def print_summary(self):
        print()
        print("=" * 70)
        Colors.print(Colors.BOLD, "验证结果:")
        print(f"  通过: {self.passed}")
        if self.failed > 0:
            Colors.print(Colors.RED, f"  失败: {self.failed}")
        if self.warnings > 0:
            Colors.print(Colors.YELLOW, f"  警告: {self.warnings}")
        print("=" * 70)

        if self.failed == 0:
            Colors.print(Colors.GREEN, "\n✅ 所有关键组件验证成功！")
            if self.warnings > 0:
                Colors.print(Colors.YELLOW, "⚠  有部分警告，但核心功能可用")
        else:
            Colors.print(Colors.RED, "\n❌ 有验证失败项，请检查错误信息")
            return False

        return True


def test_python_environment():
    """测试Python环境"""
    print()
    Colors.print(Colors.BLUE, "=" * 70)
    Colors.print(Colors.BOLD, "1. Python环境验证")
    Colors.print(Colors.BLUE, "=" * 70)

    result = TestResult()

    # Python版本
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        result.pass_test(f"Python版本: {version}", f"Python {version} 支持良好")
    else:
        result.fail_test(f"Python版本: {version}", "需要Python 3.8或更高版本")

    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        result.pass_test("虚拟环境", "已激活虚拟环境")
    else:
        result.warn_test("虚拟环境", "未检测到虚拟环境，可能影响依赖调用")

    result.print_summary()
    return result.failed == 0


def test_core_dependencies():
    """测试核心依赖"""
    print()
    Colors.print(Colors.BLUE, "=" * 70)
    Colors.print(Colors.BOLD, "2. 核心依赖验证")
    Colors.print(Colors.BLUE, "=" * 70)

    result = TestResult()

    core_deps = [
        ("bs4", "BeautifulSoup4", "HTML解析"),
        ("docx", "python-docx", "Word文档生成"),
        ("PIL", "Pillow", "图像处理"),
        ("lxml", "lxml", "XML解析"),
        ("requests", "requests", "HTTP请求"),
        ("tinycss2", "tinycss2", "CSS解析"),
        ("yaml", "PyYAML", "YAML配置"),
    ]

    for module_name, package_name, description in core_deps:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, '__version__'):
                version = module.__version__
            else:
                version = "未知"
            result.pass_test(f"{description}: {package_name}", f"版本: {version}")
        except ImportError as e:
            result.fail_test(f"{description}: {package_name}", f"导入失败: {e}")

    result.print_summary()
    return result.failed == 0


def test_svg_conversion_dependencies():
    """测试SVG转换依赖"""
    print()
    Colors.print(Colors.BLUE, "=" * 70)
    Colors.print(Colors.BOLD, "3. SVG转换依赖验证")
    Colors.print(Colors.BLUE, "=" * 70)

    result = TestResult()

    # 方案1: cairosvg
    try:
        import cairosvg
        if hasattr(cairosvg, '__version__'):
            version = cairosvg.__version__
        else:
            version = "已安装"
        result.pass_test("转换方案1: cairosvg", f"版本: {version} - 高质量SVG渲染")
    except ImportError as e:
        result.fail_test("转换方案1: cairosvg", f"未安装: {e}")

    # 方案2: svglib + reportlab
    try:
        import svglib
        result.pass_test("转换方案2: svglib", "svglib已安装")
    except ImportError as e:
        result.fail_test("转换方案2: svglib", f"未安装: {e}")

    try:
        import reportlab
        version = getattr(reportlab, 'Version', '已安装')
        result.pass_test("转换方案2: reportlab", f"版本: {version}")
    except ImportError as e:
        result.fail_test("转换方案2: reportlab", f"未安装: {e}")

    # 浏览器方案: selenium + webdriver
    try:
        import selenium
        version = getattr(selenium, '__version__', '已安装')
        result.pass_test("转换方案3: selenium", f"版本: {version} - 浏览器自动化")
    except ImportError as e:
        result.fail_test("转换方案3: selenium", f"未安装: {e}")

    try:
        import webdriver_manager
        result.pass_test("转换方案3: webdriver-manager", "已安装 - ChromeDriver管理")
    except ImportError as e:
        result.warn_test("转换方案3: webdriver-manager", f"未安装（浏览器方案可能无法使用）: {e}")

    # 方案4: PIL (fallback)
    try:
        from PIL import Image, ImageDraw
        result.pass_test("Fallback方案: PIL", "PIL可用 - 基础图像生成")
    except ImportError as e:
        result.fail_test("Fallback方案: PIL", f"PIL导入失败: {e} (严重问题)")

    # 检查ChromeDriver
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service

        # 尝试查找ChromeDriver
        chromedriver_paths = []
        if os.name == 'nt':  # Windows
            # 在venv中查找
            venv_paths = [
                "venv/Scripts/chromedriver.exe",
                "venv/bin/chromedriver.exe",
            ]
            chromedriver_paths.extend(venv_paths)
        else:  # Linux/Mac
            venv_paths = [
                "venv/bin/chromedriver",
            ]
            chromedriver_paths.extend(venv_paths)

        chromedriver_found = False
        for path in chromedriver_paths:
            if os.path.exists(path):
                chromedriver_found = True
                result.pass_test("ChromeDriver", f"找到: {path}")
                break

        if not chromedriver_found:
            result.warn_test("ChromeDriver", "未找到（可能未随部署包分发）")

    except ImportError:
        result.warn_test("ChromeDriver检查", "无法检查（selenium未安装）")

    result.print_summary()
    return result.failed == 0


def test_svg_conversion(actually_test=True):
    """测试SVG转换功能"""
    print()
    Colors.print(Colors.BLUE, "=" * 70)
    Colors.print(Colors.BOLD, "4. SVG转换功能验证")
    Colors.print(Colors.BLUE, "=" * 70)

    result = TestResult()

    # 测试SVG字符串
    test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="50" fill="blue" stroke="black" stroke-width="2"/>
  <text x="100" y="110" text-anchor="middle" fill="white">测试</text>
</svg>"""

    # 创建测试SVG文件
    test_file = Path("verify_test.svg")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_svg)
    except Exception as e:
        result.fail_test("创建测试SVG文件", str(e))
        result.print_summary()
        return False

    if not actually_test:
        result.warn_test("实际转换测试", "跳过实际转换测试（使用--quick跳过）")
        result.print_summary()
        return True

    # 测试方案1: cairosvg
    try:
        import cairosvg
        import io

        output = io.BytesIO()
        cairosvg.svg2png(url=str(test_file), write_to=output)
        output.seek(0)
        if output.getvalue():
            size = len(output.getvalue())
            result.pass_test("SVG转换 - cairosvg", f"成功转换 ({size} 字节)")
        else:
            result.fail_test("SVG转换 - cairosvg", "生成空文件")
    except Exception as e:
        result.fail_test("SVG转换 - cairosvg", str(e)[:100])

    # 测试方案2: svglib
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM

        drawing = svg2rlg(str(test_file))
        if drawing:
            result.pass_test("SVG解析 - svglib", "成功解析SVG")
        else:
            result.fail_test("SVG解析 - svglib", "无法解析SVG")
    except Exception as e:
        result.fail_test("SVG解析 - svglib", str(e)[:100])

    # 测试方案4: PIL
    try:
        from PIL import Image, ImageDraw

        img = Image.new('RGB', (200, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.ellipse([50, 50, 150, 150], fill='blue', outline='black', width=2)

        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        if output.getvalue():
            size = len(output.getvalue())
            result.pass_test("图像生成 - PIL", f"成功生成占位图 ({size} 字节)")
        else:
            result.fail_test("图像生成 - PIL", "生成空文件")
    except Exception as e:
        result.fail_test("图像生成 - PIL", str(e)[:100])

    # 清理
    try:
        test_file.unlink()
    except:
        pass

    result.print_summary()
    return result.failed == 0


def test_project_structure():
    """测试项目结构"""
    print()
    Colors.print(Colors.BLUE, "=" * 70)
    Colors.print(Colors.BOLD, "5. 项目结构验证")
    Colors.print(Colors.BLUE, "=" * 70)

    result = TestResult()

    # 检查关键文件
    required_files = [
        ("src/html2word/converter.py", "主转换器脚本"),
        ("src/html2word/word_builder/image_builder.py", "图像构建器"),
        ("src/html2word/utils/browser_svg_converter.py", "浏览器SVG转换器"),
        ("src/html2word/utils/image_utils.py", "图像处理工具"),
    ]

    for file_path, description in required_files:
        if os.path.exists(file_path):
            result.pass_test(f"{description}: {file_path}")
        else:
            result.fail_test(f"{description}: {file_path}")

    # 检查测试文件
    if os.path.exists("test_svg_implementation.py"):
        result.pass_test("集成测试脚本", "test_svg_implementation.py")
    else:
        result.warn_test("集成测试脚本", "test_svg_implementation.py 未找到")

    result.print_summary()
    return result.failed == 0


def run_integration_test(quick=False):
    """运行集成测试"""
    print()
    Colors.print(Colors.BLUE, "=" * 70)
    Colors.print(Colors.BOLD, "6. 集成测试")
    Colors.print(Colors.BLUE, "=" * 70)

    result = TestResult()

    if quick:
        result.warn_test("集成测试", "使用--quick跳过集成测试")
        result.print_summary()
        return True

    # 查找测试文件
    test_files = []
    if os.path.exists("oversear_monthly_report_part1.html"):
        test_files.append("oversear_monthly_report_part1.html")
    elif os.path.exists("test_svg_basic.html"):
        test_files.append("test_svg_basic.html")
    else:
        # 创建简单测试HTML
        test_html = """<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>
    <h1>集成测试</h1>
    <svg width="200" height="50">
        <rect width="200" height="50" fill="green"/>
        <text x="100" y="25" text-anchor="middle" fill="white">测试SVG转换</text>
    </svg>
</body>
</html>"""
        with open("test_integration.html", 'w', encoding='utf-8') as f:
            f.write(test_html)
        test_files.append("test_integration.html")

    for test_file in test_files:
        output_file = f"test_verify_{Path(test_file).stem}.docx"

        try:
            import time
            start_time = time.time()

            result_code = subprocess.run(
                [sys.executable, "-m", "html2word.converter", test_file, output_file],
                capture_output=True,
                text=True,
                timeout=180  # 3分钟超时
            )

            elapsed = time.time() - start_time

            if result_code.returncode == 0:
                if os.path.exists(output_file):
                    size = Path(output_file).stat().st_size
                    result.pass_test(
                        f"完整转换: {Path(test_file).name}",
                        f"成功（{size} 字节，耗时 {elapsed:.1f} 秒）"
                    )
                else:
                    result.fail_test(f"完整转换: {Path(test_file).name}", "输出文件未生成")
            else:
                stderr = result_code.stderr
                result.fail_test(f"完整转换: {Path(test_file).name}", stderr[:200])

        except subprocess.TimeoutExpired:
            result.fail_test(f"完整转换: {Path(test_file).name}", "转换超时（超过3分钟）")
        except Exception as e:
            result.fail_test(f"完整转换: {Path(test_file).name}", str(e)[:200])

        # 清理测试文件
        try:
            if os.path.exists(output_file):
                os.unlink(output_file)
        except:
            pass

    try:
        if os.path.exists("test_integration.html"):
            os.unlink("test_integration.html")
    except:
        pass

    result.print_summary()
    return result.failed == 0


def print_environment_info():
    """打印环境信息"""
    print()
    Colors.print(Colors.BLUE, "=" * 70)
    Colors.print(Colors.BOLD, "环境信息")
    Colors.print(Colors.BLUE, "=" * 70)
    print()

    # Python信息
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"平台: {platform.platform()}")

    # 是否为虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("虚拟环境: 是")
    else:
        print("虚拟环境: 否（可能影响依赖加载）")

    # 检查Chrome
    chrome_paths = []
    if os.name == 'nt':  # Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    else:  # Linux/Mac
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]

    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"Chrome浏览器: 已安装 ({path})")
            chrome_found = True
            break

    if not chrome_found:
        Colors.print(Colors.YELLOW, "Chrome浏览器: 未检测到（浏览器渲染方案将无法使用）")

    print()


def main():
    """主函数"""
    print()
    Colors.print(Colors.BOLD, "=" * 70)
    Colors.print(Colors.BOLD, "HTML2Word 安装验证工具")
    Colors.print(Colors.BOLD, "=" * 70)

    print_environment_info()

    # 参数解析
    quick_mode = "--quick" in sys.argv
    run_integration = not quick_mode

    # 运行各项测试
    all_passed = True

    all_passed &= test_python_environment()
    all_passed &= test_core_dependencies()
    all_passed &= test_svg_conversion_dependencies()
    all_passed &= test_svg_conversion(actually_test=run_integration)
    all_passed &= test_project_structure()

    if run_integration:
        all_passed &= run_integration_test(quick=not run_integration)

    # 总结
    print()
    Colors.print(Colors.BOLD, "=" * 70)
    if all_passed:
        Colors.print(Colors.GREEN, "✅ 所有验证通过！系统已准备好进行HTML转Word转换")
        Colors.print(Colors.GREEN, "特别是SVG图表转换功能正常工作")
    else:
        Colors.print(Colors.RED, "❌ 有验证失败项，请检查错误信息")
        print()
        print("提示:")
        print("1. 确保已在项目根目录或虚拟环境中运行此脚本")
        print("2. 如果使用离线部署包，运行: source activate_venv.sh 或 activate_venv.bat")
        print("3. 如果使用开发环境，确保已安装所有依赖: pip install -r requirements.txt")

    Colors.print(Colors.BOLD, "=" * 70)
    print()

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n意外错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
