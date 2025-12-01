"""
基于浏览器的SVG转PNG转换器
使用Chrome headless模式渲染SVG，获得完美的图表质量
"""
import base64
import io
import logging
import tempfile
import time
import subprocess
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, List, Tuple, Dict

logger = logging.getLogger(__name__)


class BrowserSVGConverter:
    """
    使用浏览器渲染SVG的转换器
    支持复杂的SVG图表（如echarts、d3.js等）
    """

    def __init__(self):
        self.driver = None
        # SVG转换结果缓存 (svg_hash -> png_bytes)
        self._svg_cache: Dict[str, bytes] = {}

    def _get_svg_hash(self, svg_content: str, width: int, height: int) -> str:
        """生成SVG内容的唯一标识"""
        key = f"{svg_content}_{width}_{height}"
        return hashlib.md5(key.encode()).hexdigest()

    def convert_batch(self, svg_list: List[Tuple[str, int, int]], max_workers: int = 4) -> Dict[str, bytes]:
        """
        批量并行转换多个SVG为PNG

        Args:
            svg_list: [(svg_content, width, height), ...] 列表
            max_workers: 最大并行工作线程数

        Returns:
            {svg_hash: png_bytes} 字典
        """
        if not svg_list:
            return {}

        # 过滤已缓存的SVG
        to_convert = []
        for svg_content, width, height in svg_list:
            svg_hash = self._get_svg_hash(svg_content, width, height)
            if svg_hash not in self._svg_cache:
                to_convert.append((svg_hash, svg_content, width, height))

        if not to_convert:
            logger.info(f"All {len(svg_list)} SVGs already cached")
            return self._svg_cache

        logger.info(f"Batch converting {len(to_convert)} SVGs with {max_workers} workers...")
        start_time = time.time()
        completed_count = 0

        def convert_single(args):
            svg_hash, svg_content, width, height = args
            png_data = self._convert_with_chrome_subprocess(svg_content, width, height)
            return svg_hash, png_data

        # 使用线程池并行转换，设置总体超时
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(convert_single, item): item for item in to_convert}

            # 使用带超时的迭代，每个future最多等待15秒
            try:
                for future in as_completed(futures, timeout=120):  # 总体超时120秒
                    try:
                        svg_hash, png_data = future.result(timeout=15)
                        completed_count += 1
                        if png_data:
                            self._svg_cache[svg_hash] = png_data
                        # 进度日志
                        if completed_count % 5 == 0:
                            logger.info(f"SVG batch progress: {completed_count}/{len(to_convert)}")
                    except Exception as e:
                        completed_count += 1
                        logger.warning(f"SVG conversion failed: {e}")
            except TimeoutError:
                logger.warning(f"SVG batch conversion timeout after 120s, {completed_count}/{len(to_convert)} completed")
                # 取消剩余的futures
                for future in futures:
                    future.cancel()

        elapsed = time.time() - start_time
        success_count = sum(1 for h, _, _, _ in to_convert if h in self._svg_cache)
        logger.info(f"Batch converted {success_count}/{len(to_convert)} SVGs in {elapsed:.2f}s")

        return self._svg_cache

    def get_cached(self, svg_content: str, width: int, height: int) -> Optional[bytes]:
        """从缓存获取已转换的PNG"""
        svg_hash = self._get_svg_hash(svg_content, width, height)
        return self._svg_cache.get(svg_hash)

    def convert(self, svg_content: str, width: int, height: int) -> Optional[bytes]:
        """
        使用浏览器渲染SVG并转换为PNG

        Args:
            svg_content: SVG XML字符串
            width: 目标宽度（像素）
            height: 目标高度（像素）

        Returns:
            PNG图片数据（bytes）或None
        """
        # 先检查缓存
        cached = self.get_cached(svg_content, width, height)
        if cached:
            logger.debug(f"SVG cache hit for {width}x{height}")
            return cached

        # 优先使用subprocess方法（不需要Selenium）
        result = self._convert_with_chrome_subprocess(svg_content, width, height)
        if result:
            # 存入缓存
            svg_hash = self._get_svg_hash(svg_content, width, height)
            self._svg_cache[svg_hash] = result
            return result

        # 回退到Selenium方法
        try:
            # 初始化浏览器（如果需要）
            if not self.driver:
                self._init_driver()

            if not self.driver:
                return None

            # 创建HTML包装
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: white;
        }}
        #svg-container {{
            width: {width}px;
            height: {height}px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div id="svg-container">
        {svg_content}
    </div>
    <canvas id="canvas" width="{width}" height="{height}" style="display:none;"></canvas>
    <script>
        function svgToCanvas() {{
            var svg = document.querySelector('svg');
            if (!svg) return null;

            // 确保SVG有正确的尺寸
            svg.setAttribute('width', '{width}');
            svg.setAttribute('height', '{height}');

            var canvas = document.getElementById('canvas');
            var ctx = canvas.getContext('2d');

            // 将SVG转换为data URL
            var svgData = new XMLSerializer().serializeToString(svg);
            var svgBlob = new Blob([svgData], {{type: 'image/svg+xml;charset=utf-8'}});
            var url = URL.createObjectURL(svgBlob);

            var img = new Image();
            img.onload = function() {{
                ctx.drawImage(img, 0, 0);
                URL.revokeObjectURL(url);
                window.conversionComplete = true;
            }};
            img.src = url;
        }}

        window.conversionComplete = false;
        setTimeout(svgToCanvas, 100);
    </script>
</body>
</html>
"""

            # 保存临时HTML文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name

            try:
                # 加载HTML
                self.driver.get(f'file:///{temp_file.replace(chr(92), "/")}')

                # 等待转换完成
                max_wait = 5
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    complete = self.driver.execute_script('return window.conversionComplete;')
                    if complete:
                        break
                    time.sleep(0.1)

                # 获取canvas数据
                canvas_data = self.driver.execute_script('''
                    var canvas = document.getElementById('canvas');
                    return canvas.toDataURL('image/png').substring(22);
                ''')

                if canvas_data:
                    png_data = base64.b64decode(canvas_data)
                    logger.info(f"BrowserSVGConverter: Successfully converted SVG to PNG ({width}x{height})")
                    return png_data
                else:
                    logger.warning("BrowserSVGConverter: Failed to get canvas data")
                    return None

            finally:
                # 清理临时文件
                try:
                    Path(temp_file).unlink()
                except:
                    pass

        except Exception as e:
            logger.error(f"BrowserSVGConverter failed: {e}")
            return None

    def _convert_with_chrome_subprocess(self, svg_content: str, width: int, height: int) -> Optional[bytes]:
        """
        使用Chrome headless模式直接截图（不需要Selenium/chromedriver）

        Args:
            svg_content: SVG XML字符串
            width: 目标宽度（像素）
            height: 目标高度（像素）

        Returns:
            PNG图片数据（bytes）或None
        """
        try:
            # 查找Chrome可执行文件
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]

            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break

            if not chrome_exe:
                logger.debug("Chrome executable not found")
                return None

            # 处理极小尺寸：Chrome对于极小窗口(如1x1)可能无法正确渲染或挂起
            # 如果尺寸小于16px，强制使用16px窗口，渲染后裁剪
            min_size = 16
            use_cropping = False
            target_width, target_height = width, height
            
            if width < min_size or height < min_size:
                use_cropping = True
                target_width = max(width, min_size)
                target_height = max(height, min_size)
                logger.debug(f"SVG size too small ({width}x{height}), scaling window to {target_width}x{target_height} and cropping")

            # 创建HTML文件
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{
            width: {target_width}px;
            height: {target_height}px;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: white;
        }}
        svg {{
            display: block;
            /* 强制SVG保持原始请求尺寸，不随窗口放大 */
            width: {width}px !important;
            height: {height}px !important;
        }}
    </style>
</head>
<body>
    {svg_content}
</body>
</html>"""

            # 创建临时HTML文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file = f.name

            # 创建临时PNG文件
            png_file = tempfile.mktemp(suffix='.png')

            try:
                # 使用Chrome headless截图
                cmd = [
                    chrome_exe,
                    '--headless',
                    '--disable-gpu',
                    '--no-sandbox',
                    '--hide-scrollbars',  # 隐藏滚动条
                    '--force-device-scale-factor=1',  # 确保1:1像素比例
                    f'--window-size={target_width},{target_height}',
                    f'--screenshot={png_file}',
                    html_file
                ]

                logger.debug(f"Running Chrome subprocess for {width}x{height} (window: {target_width}x{target_height})")

                # 运行Chrome
                # 增加超时处理的健壮性，捕获所有可能的异常
                try:
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        timeout=15,  # 稍微放宽单次超时
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                except subprocess.TimeoutExpired:
                    logger.warning(f"Chrome subprocess timed out for SVG ({width}x{height})")
                    return None

                # 读取PNG文件
                if os.path.exists(png_file):
                    # 如果使用了裁剪，使用PIL裁剪图片
                    if use_cropping:
                        try:
                            from PIL import Image
                            with Image.open(png_file) as img:
                                # 裁剪回原始尺寸 (0, 0, width, height)
                                cropped = img.crop((0, 0, width, height))
                                output = io.BytesIO()
                                cropped.save(output, format='PNG')
                                png_data = output.getvalue()
                                logger.debug(f"Cropped PNG from {target_width}x{target_height} to {width}x{height}")
                        except ImportError:
                            logger.warning("PIL not installed, returning uncropped image")
                            with open(png_file, 'rb') as f:
                                png_data = f.read()
                        except Exception as e:
                            logger.warning(f"Failed to crop image: {e}")
                            # 回退到直接读取（可能带白边）
                            with open(png_file, 'rb') as f:
                                png_data = f.read()
                    else:
                        with open(png_file, 'rb') as f:
                            png_data = f.read()
                            
                    logger.info(f"Chrome subprocess: Successfully converted SVG to PNG ({width}x{height})")
                    return png_data
                else:
                    logger.debug(f"Chrome subprocess: PNG file not created. Stderr: {result.stderr.decode('utf-8', errors='ignore') if result else 'None'}")
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
            logger.debug(f"Chrome subprocess failed: {e}")
            return None

    def _init_driver(self):
        """初始化Chrome driver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            logger.info("Initializing Chrome driver for SVG conversion...")

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--headless=new')  # New headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')

            # 禁用日志
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_argument('--log-level=3')

            # Method 1: Try webdriver-manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Chrome driver initialized via webdriver-manager")
                return
            except Exception as e:
                logger.debug(f"webdriver-manager failed: {e}")

            # Method 2: Try Selenium Manager (Selenium 4.6+)
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("Chrome driver initialized via Selenium Manager")
                return
            except Exception as e:
                logger.debug(f"Selenium Manager failed: {e}")

            # Method 3: Try specific Chrome paths on Windows
            try:
                import os
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                ]

                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        chrome_options.binary_location = chrome_path
                        self.driver = webdriver.Chrome(options=chrome_options)
                        logger.info(f"Chrome driver initialized with binary: {chrome_path}")
                        return

            except Exception as e:
                logger.debug(f"Manual Chrome path detection failed: {e}")

            # All methods failed
            raise Exception("All Chrome initialization methods failed")

        except Exception as e:
            logger.warning(f"Failed to initialize Chrome driver: {e}")
            logger.info("SVG conversion will fall back to placeholder images")
            logger.info("To enable browser-based SVG conversion, ensure Chrome is installed")
            self.driver = None

    def __del__(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


# 全局单例
_browser_converter = None


def get_browser_converter() -> BrowserSVGConverter:
    """获取浏览器转换器单例"""
    global _browser_converter
    if _browser_converter is None:
        _browser_converter = BrowserSVGConverter()
    return _browser_converter
