"""
基于浏览器的 HTML 转 PNG 转换器
使用 Chrome headless 模式渲染 HTML 片段（含背景图+绝对定位文字），获得像素级精确的截图
"""
import io
import logging
import tempfile
import subprocess
import os
import hashlib
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class BrowserHTMLConverter:
    """
    使用浏览器渲染 HTML 片段的转换器
    主要用于将带有背景图和绝对定位文字的 HTML 元素转换为 PNG 图片
    仅使用 Chrome subprocess 方式，无需 Selenium
    """

    def __init__(self):
        # HTML 转换结果缓存 (html_hash -> png_bytes)
        self._cache: Dict[str, bytes] = {}
        self._chrome_exe: Optional[str] = None

    def _find_chrome(self) -> Optional[str]:
        """查找 Chrome 可执行文件"""
        if self._chrome_exe:
            return self._chrome_exe

        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            # Linux paths
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            # Mac paths
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]

        for path in chrome_paths:
            if os.path.exists(path):
                self._chrome_exe = path
                logger.debug(f"Found Chrome at: {path}")
                return path

        logger.debug("Chrome executable not found")
        return None

    def _get_html_hash(self, html_content: str, width: int, height: int) -> str:
        """生成 HTML 内容的唯一标识"""
        key = f"{html_content}_{width}_{height}"
        return hashlib.md5(key.encode()).hexdigest()

    def get_cached(self, html_content: str, width: int, height: int) -> Optional[bytes]:
        """从缓存获取已转换的 PNG"""
        html_hash = self._get_html_hash(html_content, width, height)
        return self._cache.get(html_hash)

    def convert(self, html_content: str, width: int, height: int) -> Optional[bytes]:
        """
        使用 Chrome headless 渲染 HTML 并转换为 PNG

        Args:
            html_content: 完整的 HTML 文档字符串（包含 DOCTYPE、head、body）
            width: 目标宽度（像素）
            height: 目标高度（像素）

        Returns:
            PNG 图片数据（bytes）或 None
        """
        # 先检查缓存
        cached = self.get_cached(html_content, width, height)
        if cached:
            logger.debug(f"HTML cache hit for {width}x{height}")
            return cached

        # 使用 Chrome subprocess 方法
        result = self._convert_with_chrome(html_content, width, height)
        if result:
            # 存入缓存
            html_hash = self._get_html_hash(html_content, width, height)
            self._cache[html_hash] = result
            return result

        return None

    def _convert_with_chrome(self, html_content: str, width: int, height: int) -> Optional[bytes]:
        """
        使用 Chrome headless 模式直接截图

        Args:
            html_content: 完整的 HTML 文档
            width: 目标宽度（像素）
            height: 目标高度（像素）

        Returns:
            PNG 图片数据（bytes）或 None
        """
        try:
            chrome_exe = self._find_chrome()
            if not chrome_exe:
                logger.warning("Chrome not found, cannot render HTML")
                return None

            # 处理极小尺寸
            min_size = 16
            use_cropping = False
            target_width, target_height = width, height

            if width < min_size or height < min_size:
                use_cropping = True
                target_width = max(width, min_size)
                target_height = max(height, min_size)
                logger.debug(f"HTML size too small ({width}x{height}), scaling to {target_width}x{target_height}")

            # 创建临时 HTML 文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file = f.name

            # 创建临时 PNG 文件
            png_file = tempfile.mktemp(suffix='.png')

            try:
                # 使用 Chrome headless 截图
                cmd = [
                    chrome_exe,
                    '--headless',
                    '--disable-gpu',
                    '--no-sandbox',
                    '--hide-scrollbars',
                    '--force-device-scale-factor=1',
                    f'--window-size={target_width},{target_height}',
                    f'--screenshot={png_file}',
                    html_file
                ]

                logger.debug(f"Running Chrome for HTML screenshot {width}x{height}")

                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        timeout=15,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                except subprocess.TimeoutExpired:
                    logger.warning(f"Chrome subprocess timed out for HTML ({width}x{height})")
                    return None

                # 读取 PNG 文件
                if os.path.exists(png_file):
                    if use_cropping:
                        try:
                            from PIL import Image
                            with Image.open(png_file) as img:
                                cropped = img.crop((0, 0, width, height))
                                output = io.BytesIO()
                                cropped.save(output, format='PNG')
                                png_data = output.getvalue()
                                logger.debug(f"Cropped PNG from {target_width}x{target_height} to {width}x{height}")
                        except Exception as e:
                            logger.warning(f"Failed to crop image: {e}")
                            with open(png_file, 'rb') as f:
                                png_data = f.read()
                    else:
                        with open(png_file, 'rb') as f:
                            png_data = f.read()

                    logger.info(f"Chrome: Successfully rendered HTML to PNG ({width}x{height}, {len(png_data)} bytes)")
                    return png_data
                else:
                    stderr = result.stderr.decode('utf-8', errors='ignore') if result else 'None'
                    logger.debug(f"Chrome: PNG file not created. Stderr: {stderr}")
                    return None

            finally:
                # 清理临时文件
                try:
                    os.unlink(html_file)
                except:
                    pass
                try:
                    if os.path.exists(png_file):
                        os.unlink(png_file)
                except:
                    pass

        except Exception as e:
            logger.error(f"Chrome subprocess failed: {e}", exc_info=True)
            return None


# 全局单例
_browser_html_converter: Optional[BrowserHTMLConverter] = None


def get_browser_html_converter() -> BrowserHTMLConverter:
    """获取浏览器 HTML 转换器单例"""
    global _browser_html_converter
    if _browser_html_converter is None:
        _browser_html_converter = BrowserHTMLConverter()
    return _browser_html_converter
