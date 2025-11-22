#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
离线部署包创建脚本
在联网设备上运行，创建完整的虚拟环境并打包所有依赖和ChromeDriver
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime


def log(msg):
    """打印带时间戳的日志"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
    except UnicodeEncodeError:
        # 对于非UTF-8终端，过滤Unicode字符
        clean_msg = msg.encode('gbk', errors='ignore').decode('gbk')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {clean_msg}", flush=True)


def run_command(cmd, cwd=None, check=True, use_proxy=False):
    """运行系统命令"""
    log(f"执行: {cmd}")

    # 设置环境变量
    env = os.environ.copy()
    if use_proxy:
        # 配置代理（7897端口）
        proxy_url = "http://127.0.0.1:7897"
        env['HTTP_PROXY'] = proxy_url
        env['HTTPS_PROXY'] = proxy_url
        env['http_proxy'] = proxy_url
        env['https_proxy'] = proxy_url
        log(f"使用代理: {proxy_url}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            env=env,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            log(f"输出: {result.stdout[:500]}")
        return result
    except subprocess.CalledProcessError as e:
        log(f"[ERROR] 命令失败: {e}")
        if e.stdout:
            log(f"stdout: {e.stdout}")
        if e.stderr:
            log(f"stderr: {e.stderr}")
        raise


def get_python_executable():
    """获取Python可执行文件路径"""
    return sys.executable


def create_venv(venv_path):
    """创建虚拟环境"""
    log("=" * 70)
    log("步骤1: 创建虚拟环境")
    log("=" * 70)

    python_exe = get_python_executable()
    log(f"使用Python: {python_exe}")

    if venv_path.exists():
        log(f"虚拟环境已存在，删除: {venv_path}")
        shutil.rmtree(venv_path)

    run_command(f'"{python_exe}" -m venv "{venv_path}"')
    log(f"[OK] 虚拟环境创建完成: {venv_path}")


def get_venv_python(venv_path):
    """获取虚拟环境的Python可执行文件路径"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Linux/Mac
        return venv_path / "bin" / "python"


def get_venv_pip(venv_path):
    """获取虚拟环境的pip可执行文件路径"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        return venv_path / "bin" / "pip"


def install_dependencies(venv_path):
    """安装项目依赖"""
    log("=" * 70)
    log("步骤2: 安装项目依赖")
    log("=" * 70)

    pip_exe = get_venv_pip(venv_path)
    python_exe = get_venv_python(venv_path)

    # 检查pip版本（跳过升级，避免网络问题）
    log("检查pip版本...")
    try:
        result = run_command(f'"{python_exe}" -m pip --version', check=False, use_proxy=True)
        if result.returncode == 0:
            log(f"pip版本: {result.stdout.strip()}")
        else:
            log("[WARN] 无法检查pip版本，但继续安装...")
    except:
        log("[WARN] pip检查失败，但继续安装...")

    # 安装虚拟环境基础包
    log("安装wheel和setuptools...")
    try:
        run_command(f'"{python_exe}" -m pip install wheel setuptools', check=False, use_proxy=True)
    except:
        log("[WARN] wheel/setuptools安装失败，尝试继续...")

    # 读取requirements.txt
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        log("[ERROR] requirements.txt 不存在")
        sys.exit(1)

    # 安装核心依赖
    log("安装项目核心依赖...")
    run_command(f'"{pip_exe}" install -r requirements.txt', use_proxy=True)

    # 安装SVG转换相关依赖
    log("安装SVG转换相关依赖...")
    svg_dependencies = [
        "selenium>=4.0.0",
        "webdriver-manager",
        "cairosvg",
        "svglib",
        "reportlab",
    ]

    for dep in svg_dependencies:
        log(f"安装 {dep}...")
        run_command(f'"{pip_exe}" install {dep}', use_proxy=True)

    log("[OK] 所有依赖安装完成")


def download_chromedriver(venv_path):
    """下载ChromeDriver"""
    log("=" * 70)
    log("步骤3: 下载ChromeDriver")
    log("=" * 70)

    python_exe = get_venv_python(venv_path)

    # 创建一个临时脚本来下载ChromeDriver
    download_script = """
from webdriver_manager.chrome import ChromeDriverManager
import os

print("开始下载ChromeDriver...")
try:
    driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver下载成功: {driver_path}")

    # 复制到虚拟环境目录
    venv_bin = os.path.join(os.environ.get('VENV_PATH', ''), 'bin' if os.name != 'nt' else 'Scripts')
    if venv_bin and os.path.exists(os.path.dirname(venv_bin)):
        import shutil
        target_path = os.path.join(os.path.dirname(venv_bin), 'chromedriver.exe' if os.name == 'nt' else 'chromedriver')
        if os.path.exists(driver_path):
            if os.path.isfile(driver_path):
                shutil.copy2(driver_path, target_path)
                print(f"ChromeDriver已复制到: {target_path}")
            else:
                # driver_path可能是目录，找里面的可执行文件
                for root, dirs, files in os.walk(driver_path):
                    for file in files:
                        if 'chromedriver' in file and (file.endswith('.exe') or not file.endswith('.')):
                            src = os.path.join(root, file)
                            shutil.copy2(src, target_path)
                            print(f"ChromeDriver已从{src}复制到: {target_path}")
                            break
except Exception as e:
    print(f"下载失败: {e}")
    import traceback
    traceback.print_exc()
"""

    # 设置环境变量传递venv路径
    env = os.environ.copy()
    env['VENV_PATH'] = str(venv_path)

    # 运行下载脚本
    try:
        result = subprocess.run(
            [str(python_exe), "-c", download_script],
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5分钟超时
        )
        log(result.stdout)
        if result.stderr:
            log(f"stderr: {result.stderr}")
        if result.returncode == 0:
            log("[OK] ChromeDriver下载完成")
        else:
            log("[WARN] ChromeDriver下载可能失败，但不影响其他功能")
    except subprocess.TimeoutExpired:
        log("[WARN] ChromeDriver下载超时，但不影响其他功能")
    except Exception as e:
        log(f"[WARN] ChromeDriver下载异常: {e}")


def create_activation_scripts(venv_path, package_dir):
    """创建激活脚本"""
    log("=" * 70)
    log("步骤4: 创建激活脚本")
    log("=" * 70)

    # Windows激活脚本
    if os.name == 'nt':
        activate_bat = package_dir / "activate_venv.bat"
        with open(activate_bat, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"echo 正在激活虚拟环境...\n")
            f.write(f"set PYTHONPATH=%~dp0venv\Lib\site-packages;%PYTHONPATH%\n")
            f.write(f"set PATH=%~dp0venv\\Scripts;%~dp0venv\\bin;%PATH%\n")
            f.write(f"echo 虚拟环境已激活！\n")
            f.write(f"echo.\n")
            f.write(f"echo 你可以直接运行 html2word-converter.exe\n")
            f.write(f"echo 或运行 Python 脚本:\n")
            f.write(f"echo   python src\\html2word\\converter.py\n")
            f.write(f"echo.\n")
        log(f"[OK] 创建Windows激活脚本: {activate_bat}")

        # 创建converter包装脚本
        converter_exe = package_dir / "html2word-converter.bat"
        with open(converter_exe, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"cd /d %~dp0\n")
            f.write(f"venv\\Scripts\\python -m html2word.converter %*\n")
        log(f"[OK] 创建转换器包装脚本: {converter_exe}")

    # Linux/Mac激活脚本
    activate_sh = package_dir / "activate_venv.sh"
    with open(activate_sh, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(f"echo \"正在激活虚拟环境...\"\n")
        f.write(f"export PYTHONPATH=\"$(dirname \"$0\")/venv/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages:\$PYTHONPATH\"\n")
        f.write(f"export PATH=\"$(dirname \"$0\")/venv/bin:\$PATH\"\n")
        f.write(f"echo \"虚拟环境已激活！\"\n")
        f.write(f"echo \"\"\n")
        f.write(f"echo \"你可以运行 Python 脚本:\"\n")
        f.write(f"echo \"  python src/html2word/converter.py\"\n")
        f.write(f"echo \"\"\n")
    os.chmod(activate_sh, 0o755)
    log(f"[OK] 创建Linux/Mac激活脚本: {activate_sh}")


def copy_project_files(package_dir):
    """复制项目文件"""
    log("=" * 70)
    log("步骤5: 复制项目文件")
    log("=" * 70)

    # 需要复制的文件和目录
    items_to_copy = [
        "src",
        "requirements.txt",
        "setup.py",
        "README.md",
        "test_svg_implementation.py",
        "oversear_monthly_report_part1.html",
    ]

    for item in items_to_copy:
        src_path = Path(item)
        dst_path = package_dir / item

        if not src_path.exists():
            log(f"跳过不存在的项目: {item}")
            continue

        if src_path.is_dir():
            log(f"复制目录: {item}")
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            log(f"复制文件: {item}")
            shutil.copy2(src_path, dst_path)

    log("[OK] 项目文件复制完成")


def create_readme(package_dir):
    """创建部署说明文档"""
    log("=" * 70)
    log("步骤6: 创建部署说明文档")
    log("=" * 70)

    readme_content = f"""# HTML2Word 离线部署包

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
venv\\Scripts\\python test_svg_implementation.py

# Linux/Mac
venv/bin/python test_svg_implementation.py
```

## 注意事项

- 此包在 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 创建
- Python版本: {sys.version}
- ChromeDriver已包含在包中（如适用）
- 所有依赖已预安装，无需联网

## 故障排除

如果Chrome浏览器渲染失败：
1. 确保系统已安装Chrome浏览器
2. ChromeDriver版本与Chrome浏览器版本匹配
3. 使用其他转换方法（cairosvg/svglib会自动fallback）

对于其他问题，请参考项目README.md文档。
"""

    readme_file = package_dir / "OFFLINE_PACKAGE_README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    log(f"[OK] 创建部署说明文档: {readme_file}")


def create_package_zip(package_dir):
    """创建zip压缩包"""
    log("=" * 70)
    log("步骤7: 创建压缩包")
    log("=" * 70)

    zip_file = f"html2word-offline-package-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    log(f"创建压缩包: {zip_file}")

    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            # 排除__pycache__和.pyc文件
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache']]

            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)

    log(f"[OK] 压缩包创建完成: {zip_file}")
    return zip_file


def main():
    """主函数"""
    print("=" * 70)
    print("HTML2Word 离线部署包创建工具")
    print("=" * 70)
    print()

    # 检查当前目录
    if not Path("requirements.txt").exists():
        log("[ERROR] 错误: 请在项目根目录运行此脚本")
        sys.exit(1)

    # 创建临时目录用于打包
    package_name = f"html2word-offline-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = Path(package_name)

    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()

    log(f"创建部署包目录: {package_dir}")

    try:
        # 步骤1: 创建虚拟环境
        venv_path = package_dir / "venv"
        create_venv(venv_path)

        # 步骤2: 安装依赖
        install_dependencies(venv_path)

        # 步骤3: 下载ChromeDriver
        download_chromedriver(venv_path)

        # 步骤4: 创建激活脚本
        create_activation_scripts(venv_path, package_dir)

        # 步骤5: 复制项目文件
        copy_project_files(package_dir)

        # 步骤6: 创建部署说明
        create_readme(package_dir)

        # 步骤7: 创建压缩包
        zip_file = create_package_zip(package_dir)

        print()
        print("=" * 70)
        print("[OK] 离线部署包创建成功！")
        print("=" * 70)
        print()
        print(f"压缩包文件: {zip_file}")
        print(f"文件大小: {Path(zip_file).stat().st_size / 1024 / 1024:.1f} MB")
        print()
        print("将此压缩包复制到离线设备，然后:")
        print("1. 解压缩到任意目录")
        print("2. 按照 OFFLINE_PACKAGE_README.md 中的说明运行")
        print()

    except Exception as e:
        log(f"[ERROR] 创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # 询问是否清理临时目录
        response = input(f"\n是否删除临时目录 '{package_dir}'? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(package_dir)
            log(f"已删除临时目录: {package_dir}")


if __name__ == "__main__":
    main()
