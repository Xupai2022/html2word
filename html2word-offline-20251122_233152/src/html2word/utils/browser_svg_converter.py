"""
基于浏览器的SVG转PNG转换器
使用Selenium + Chrome headless模式渲染SVG，获得完美的图表质量
"""
import base64
import io
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserSVGConverter:
    """
    使用浏览器渲染SVG的转换器
    支持复杂的SVG图表（如echarts、d3.js等）
    """

    def __init__(self):
        self.driver = None

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

    def _init_driver(self):
        """初始化Chrome driver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            logger.info("Initializing Chrome driver for SVG conversion...")

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')

            # 禁用日志
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            try:
                # 尝试使用webdriver-manager自动下载
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"webdriver-manager failed: {e}, trying system Chrome...")
                # 尝试使用系统Chrome
                self.driver = webdriver.Chrome(options=chrome_options)

            logger.info("Chrome driver initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize Chrome driver: {e}")
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
