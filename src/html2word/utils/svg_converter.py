"""
纯Python SVG转PNG转换器
不依赖cairo等系统库，使用PIL直接渲染简单SVG元素
"""
import re
import io
import logging
from typing import Optional, Tuple
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


class SimpleSVGConverter:
    """
    简单的SVG到PNG转换器

    支持的SVG元素:
    - rect (矩形)
    - circle (圆形)
    - text (文本)
    - line (线条)
    - path (基本路径)
    """

    def __init__(self):
        self.namespace = {'svg': 'http://www.w3.org/2000/svg'}

    def convert(self, svg_content: str, width: int, height: int) -> Optional[bytes]:
        """
        转换SVG内容为PNG

        Args:
            svg_content: SVG XML字符串
            width: 目标宽度（像素）
            height: 目标高度（像素）

        Returns:
            PNG图片数据（bytes）或None
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 解析SVG
            root = ET.fromstring(svg_content)

            # 创建画布
            img = Image.new('RGBA', (width, height), color=(255, 255, 255, 255))
            draw = ImageDraw.Draw(img)

            # 渲染SVG元素
            self._render_element(root, draw, width, height)

            # 转为PNG bytes
            output = io.BytesIO()
            img.save(output, format='PNG')
            output.seek(0)

            logger.info(f"SimpleSVGConverter: Successfully converted SVG to PNG ({width}x{height})")
            return output.getvalue()

        except Exception as e:
            logger.error(f"SimpleSVGConverter failed: {e}")
            return None

    def _render_element(self, element: ET.Element, draw, width: int, height: int):
        """递归渲染SVG元素"""
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag

        if tag == 'svg':
            # 处理子元素
            for child in element:
                self._render_element(child, draw, width, height)

        elif tag == 'rect':
            self._render_rect(element, draw)

        elif tag == 'circle':
            self._render_circle(element, draw)

        elif tag == 'ellipse':
            self._render_ellipse(element, draw)

        elif tag == 'line':
            self._render_line(element, draw)

        elif tag == 'text':
            self._render_text(element, draw)

        elif tag == 'path':
            self._render_path(element, draw)

        elif tag == 'g':
            # 组元素，渲染子元素
            for child in element:
                self._render_element(child, draw, width, height)

    def _render_rect(self, element: ET.Element, draw):
        """渲染矩形"""
        try:
            x = float(element.get('x', '0'))
            y = float(element.get('y', '0'))
            w = float(element.get('width', '0'))
            h = float(element.get('height', '0'))

            fill = self._parse_color(element.get('fill', 'black'))
            stroke = self._parse_color(element.get('stroke'))
            stroke_width = int(float(element.get('stroke-width', '1')))

            # 绘制填充
            if fill:
                draw.rectangle([(x, y), (x + w, y + h)], fill=fill)

            # 绘制边框
            if stroke:
                draw.rectangle([(x, y), (x + w, y + h)], outline=stroke, width=stroke_width)

        except Exception as e:
            logger.debug(f"Failed to render rect: {e}")

    def _render_circle(self, element: ET.Element, draw):
        """渲染圆形"""
        try:
            cx = float(element.get('cx', '0'))
            cy = float(element.get('cy', '0'))
            r = float(element.get('r', '0'))

            fill = self._parse_color(element.get('fill', 'black'))
            stroke = self._parse_color(element.get('stroke'))
            stroke_width = int(float(element.get('stroke-width', '1')))

            bbox = [(cx - r, cy - r), (cx + r, cy + r)]

            if fill:
                draw.ellipse(bbox, fill=fill)
            if stroke:
                draw.ellipse(bbox, outline=stroke, width=stroke_width)

        except Exception as e:
            logger.debug(f"Failed to render circle: {e}")

    def _render_ellipse(self, element: ET.Element, draw):
        """渲染椭圆"""
        try:
            cx = float(element.get('cx', '0'))
            cy = float(element.get('cy', '0'))
            rx = float(element.get('rx', '0'))
            ry = float(element.get('ry', '0'))

            fill = self._parse_color(element.get('fill', 'black'))
            stroke = self._parse_color(element.get('stroke'))
            stroke_width = int(float(element.get('stroke-width', '1')))

            bbox = [(cx - rx, cy - ry), (cx + rx, cy + ry)]

            if fill:
                draw.ellipse(bbox, fill=fill)
            if stroke:
                draw.ellipse(bbox, outline=stroke, width=stroke_width)

        except Exception as e:
            logger.debug(f"Failed to render ellipse: {e}")

    def _render_line(self, element: ET.Element, draw):
        """渲染线条"""
        try:
            x1 = float(element.get('x1', '0'))
            y1 = float(element.get('y1', '0'))
            x2 = float(element.get('x2', '0'))
            y2 = float(element.get('y2', '0'))

            stroke = self._parse_color(element.get('stroke', 'black'))
            stroke_width = int(float(element.get('stroke-width', '1')))

            draw.line([(x1, y1), (x2, y2)], fill=stroke, width=stroke_width)

        except Exception as e:
            logger.debug(f"Failed to render line: {e}")

    def _render_text(self, element: ET.Element, draw):
        """渲染文本"""
        try:
            x = float(element.get('x', '0'))
            y = float(element.get('y', '0'))
            text = element.text or ""

            fill = self._parse_color(element.get('fill', 'black'))
            font_size = int(float(element.get('font-size', '12')))

            # 使用默认字体
            try:
                from PIL import ImageFont
                # 尝试使用系统字体
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = None

            # 调整y坐标（SVG的y是基线，PIL是顶部）
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                y = y - (bbox[3] - bbox[1])

            draw.text((x, y), text, fill=fill, font=font)

        except Exception as e:
            logger.debug(f"Failed to render text: {e}")

    def _render_path(self, element: ET.Element, draw):
        """渲染基本路径（仅支持简单的M、L命令）"""
        try:
            d = element.get('d', '')
            fill = self._parse_color(element.get('fill'))
            stroke = self._parse_color(element.get('stroke'))
            stroke_width = int(float(element.get('stroke-width', '1')))

            # 解析路径命令（简化版本）
            points = self._parse_path(d)

            if len(points) < 2:
                return

            # 绘制路径
            if fill:
                draw.polygon(points, fill=fill)
            if stroke:
                draw.line(points, fill=stroke, width=stroke_width)

        except Exception as e:
            logger.debug(f"Failed to render path: {e}")

    def _parse_path(self, d: str) -> list:
        """解析SVG路径（简化版本，仅支持M和L命令）"""
        points = []

        # 简单的路径解析
        commands = re.findall(r'[MLZ][\d\s,.-]+', d, re.IGNORECASE)

        for cmd in commands:
            cmd_type = cmd[0]
            coords = re.findall(r'-?\d+\.?\d*', cmd[1:])

            if cmd_type.upper() == 'M' or cmd_type.upper() == 'L':
                # Move或Line命令
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords):
                        points.append((float(coords[i]), float(coords[i + 1])))

        return points

    def _parse_color(self, color_str: Optional[str]) -> Optional[Tuple[int, int, int, int]]:
        """解析颜色字符串为RGBA元组"""
        if not color_str or color_str == 'none':
            return None

        color_str = color_str.strip().lower()

        # Hex颜色
        if color_str.startswith('#'):
            hex_color = color_str[1:]
            if len(hex_color) == 3:
                # 短格式 #RGB
                hex_color = ''.join([c * 2 for c in hex_color])
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b, 255)

        # RGB/RGBA
        if color_str.startswith('rgb'):
            match = re.search(r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)', color_str)
            if match:
                r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                a = int(float(match.group(4)) * 255) if match.group(4) else 255
                return (r, g, b, a)

        # 命名颜色
        named_colors = {
            'black': (0, 0, 0, 255),
            'white': (255, 255, 255, 255),
            'red': (255, 0, 0, 255),
            'green': (0, 255, 0, 255),
            'blue': (0, 0, 255, 255),
            'yellow': (255, 255, 0, 255),
            'cyan': (0, 255, 255, 255),
            'magenta': (255, 0, 255, 255),
            'gray': (128, 128, 128, 255),
            'grey': (128, 128, 128, 255),
        }

        return named_colors.get(color_str)
