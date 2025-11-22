"""
Style mapper - maps CSS styles to Word styles.

Converts computed CSS styles to python-docx formatting.
"""

import logging
from typing import Optional, Dict, Any
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_UNDERLINE
from docx.enum.table import WD_ALIGN_VERTICAL

from html2word.utils.colors import ColorConverter
from html2word.utils.fonts import FontMapper
from html2word.utils.units import UnitConverter
from html2word.utils.font_utils import apply_uniform_font

logger = logging.getLogger(__name__)


class StyleMapper:
    """Maps CSS styles to Word formatting."""

    def __init__(self):
        """Initialize style mapper."""
        self.font_mapper = FontMapper()

    def apply_run_style(self, run, styles: Dict[str, Any]):
        """
        Apply text run styles.

        Args:
            run: python-docx Run object
            styles: Computed CSS styles
        """
        # Font family
        if 'font-family' in styles:
            font_name = self.font_mapper.map_font(styles['font-family'])
            # Use uniform font application to ensure consistent display across character types
            apply_uniform_font(run, font_name)

        # Font size
        if 'font-size' in styles:
            try:
                font_size_pt = self._get_font_size_pt(styles['font-size'])
                if font_size_pt:
                    run.font.size = Pt(font_size_pt)
            except Exception as e:
                logger.warning(f"Error setting font size: {e}")

        # Font weight (bold)
        if 'font-weight' in styles:
            weight = styles.get('font-weight', 400)
            if isinstance(weight, str):
                try:
                    weight = int(weight)
                except:
                    weight = 700 if weight == 'bold' else 400
            run.font.bold = weight >= 600

        # Font style (italic)
        if 'font-style' in styles:
            run.font.italic = styles['font-style'] in ('italic', 'oblique')

        # Color
        if 'color' in styles:
            rgb_color = ColorConverter.to_rgb_color(styles['color'])
            if rgb_color:
                run.font.color.rgb = rgb_color

        # Text decoration
        if 'text-decoration' in styles:
            decoration = styles['text-decoration']
            if 'underline' in decoration:
                run.font.underline = WD_UNDERLINE.SINGLE
            if 'line-through' in decoration:
                run.font.strike = True

        # Background color (highlighting)
        if 'background-color' in styles:
            # Note: python-docx has limited background color support
            # We can use highlighting, but it has limited colors
            pass

    def apply_paragraph_style(self, paragraph, styles: Dict[str, Any], box_model=None, prev_margin_bottom: float = 0):
        """
        Apply paragraph styles with proper margin collapse.

        Args:
            paragraph: python-docx Paragraph object
            styles: Computed CSS styles
            box_model: BoxModel object (optional)
            prev_margin_bottom: Previous element's margin-bottom in pt (for margin collapse)
        """
        fmt = paragraph.paragraph_format

        # Text alignment
        if 'text-align' in styles:
            alignment = self._map_text_align(styles['text-align'])
            if alignment is not None:
                fmt.alignment = alignment

        # Line height
        if 'line-height' in styles:
            line_height = styles['line-height']
            try:
                if isinstance(line_height, (int, float)):
                    # Multiplier
                    fmt.line_spacing = float(line_height)
                else:
                    # Try to parse as pt
                    pt_value = UnitConverter.to_pt(str(line_height))
                    if pt_value:
                        fmt.line_spacing = Pt(pt_value)
            except:
                pass

        # Margins (spacing) - Implement true CSS margin collapse
        # CSS spec: Adjacent vertical margins collapse to the LARGER of the two values
        # Example: element A has margin-bottom: 30pt, element B has margin-top: 50pt
        #          → Actual spacing between A and B is max(30, 50) = 50pt (NOT 80pt)
        if box_model:
            margin_top = box_model.margin.top
            margin_bottom = box_model.margin.bottom

            # True margin collapse: compare current margin-top with previous margin-bottom
            # Take the larger value
            if margin_top > prev_margin_bottom:
                # Current element's margin-top is larger than previous element's margin-bottom
                # Need to add extra spacing via space_before to reach the correct total
                extra_spacing = margin_top - prev_margin_bottom
                if extra_spacing > 0:
                    fmt.space_before = Pt(extra_spacing)
                    logger.debug(f"Margin collapse: margin-top {margin_top}pt > prev margin-bottom {prev_margin_bottom}pt, adding space_before={extra_spacing}pt")
            # else: Previous margin-bottom already provides enough spacing (it was larger)

            # Always set margin-bottom as space_after for next element
            if margin_bottom > 0:
                fmt.space_after = Pt(margin_bottom)

            # Left indent (margin-left)
            if box_model.margin.left > 0:
                fmt.left_indent = Pt(box_model.margin.left)

            # Right indent (margin-right)
            if box_model.margin.right > 0:
                fmt.right_indent = Pt(box_model.margin.right)

        # First line indent
        if 'text-indent' in styles:
            try:
                indent_pt = UnitConverter.to_pt(styles['text-indent'])
                if indent_pt != 0:
                    fmt.first_line_indent = Pt(indent_pt)
            except:
                pass

        # Background color (shading) with opacity support
        if 'background-color' in styles:
            try:
                bg_color = styles['background-color']
                # Apply opacity if present
                if 'opacity' in styles:
                    bg_color = self._apply_opacity_to_color(bg_color, styles['opacity'])

                rgb_color = ColorConverter.to_rgb_color(bg_color)
                if rgb_color:
                    from docx.oxml import parse_xml
                    from docx.oxml.ns import nsdecls

                    # Add shading element
                    shd = parse_xml(
                        f'<w:shd {nsdecls("w")} w:fill="{ColorConverter.to_hex(bg_color)[1:]}"/>'
                    )
                    paragraph._element.get_or_add_pPr().append(shd)
            except Exception as e:
                logger.warning(f"Error setting paragraph background: {e}")

        # Handle box-shadow by adding subtle border (degradation)
        if 'box-shadow' in styles and box_model:
            try:
                self._apply_box_shadow_degradation(paragraph, styles['box-shadow'])
            except Exception as e:
                logger.warning(f"Error applying box-shadow degradation: {e}")

    def apply_table_cell_style(self, cell, styles: Dict[str, Any], box_model=None):
        """
        Apply table cell styles.

        Args:
            cell: python-docx Cell object
            styles: Computed CSS styles
            box_model: BoxModel object (optional)
        """
        # Vertical alignment
        if 'vertical-align' in styles:
            v_align = self._map_vertical_align(styles['vertical-align'])
            if v_align is not None:
                cell.vertical_alignment = v_align

        # Background color
        if 'background-color' in styles:
            try:
                from docx.oxml import parse_xml
                from docx.oxml.ns import nsdecls

                hex_color = ColorConverter.to_hex(styles['background-color'])
                if hex_color:
                    shd = parse_xml(
                        f'<w:shd {nsdecls("w")} w:fill="{hex_color[1:]}"/>'
                    )
                    cell._element.get_or_add_tcPr().append(shd)
            except Exception as e:
                logger.warning(f"Error setting cell background: {e}")

        # Cell borders
        if box_model and box_model.border.has_border():
            self._apply_cell_borders(cell, box_model.border)

        # Cell padding - apply CSS padding as Word cell margins
        if box_model and (box_model.padding.top > 0 or box_model.padding.right > 0 or
                         box_model.padding.bottom > 0 or box_model.padding.left > 0):
            self._apply_cell_padding(cell, box_model.padding)

    def _apply_cell_borders(self, cell, border):
        """Apply borders to table cell."""
        try:
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls

            tc = cell._element
            tcPr = tc.get_or_add_tcPr()

            # Build border elements for each side
            border_elements = []

            # Process each side
            for side_name, border_edge in [('top', border.top), ('left', border.left),
                                            ('bottom', border.bottom), ('right', border.right)]:
                if border_edge.width > 0 and border_edge.style != 'none':
                    # Convert pt to eighths of a point
                    sz = int(border_edge.width * 8)

                    # Map CSS border style to Word border style
                    word_style = self._map_border_style(border_edge.style)

                    # Get color
                    color = ColorConverter.to_hex(border_edge.color)
                    if color:
                        color = color[1:]  # Remove #
                    else:
                        color = '000000'  # Default to black

                    # Add border element
                    border_elements.append(
                        f'<w:{side_name} w:val="{word_style}" w:sz="{sz}" w:color="{color}"/>'
                    )

            # Only add tcBorders if we have at least one border
            if border_elements:
                tcBorders_xml = f'''
                    <w:tcBorders {nsdecls("w")}>
                        {chr(10).join(border_elements)}
                    </w:tcBorders>
                '''
                tcBorders = parse_xml(tcBorders_xml)
                tcPr.append(tcBorders)

        except Exception as e:
            logger.warning(f"Error applying cell borders: {e}")

    def _apply_cell_padding(self, cell, padding):
        """
        Apply padding to table cell as Word cell margins.

        Args:
            cell: python-docx Cell object
            padding: BoxEdge object with padding values in pt
        """
        try:
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls
            from docx.shared import Pt

            tc = cell._element
            tcPr = tc.get_or_add_tcPr()

            # Word uses cell margins instead of padding
            # Convert pt to twips (1 pt = 20 twips)
            margin_elements = []

            if padding.top > 0:
                twips = int(padding.top * 20)
                margin_elements.append(f'<w:top w:w="{twips}" w:type="dxa"/>')

            if padding.left > 0:
                twips = int(padding.left * 20)
                margin_elements.append(f'<w:left w:w="{twips}" w:type="dxa"/>')

            if padding.bottom > 0:
                twips = int(padding.bottom * 20)
                margin_elements.append(f'<w:bottom w:w="{twips}" w:type="dxa"/>')

            if padding.right > 0:
                twips = int(padding.right * 20)
                margin_elements.append(f'<w:right w:w="{twips}" w:type="dxa"/>')

            if margin_elements:
                tcMar_xml = f'''
                    <w:tcMar {nsdecls("w")}>
                        {chr(10).join(margin_elements)}
                    </w:tcMar>
                '''
                tcMar = parse_xml(tcMar_xml)
                tcPr.append(tcMar)
                logger.debug(f"Applied cell padding: top={padding.top}pt, right={padding.right}pt, bottom={padding.bottom}pt, left={padding.left}pt")

        except Exception as e:
            logger.warning(f"Error applying cell padding: {e}")

    def _map_border_style(self, css_style: str) -> str:
        """
        Map CSS border style to Word border style.

        Args:
            css_style: CSS border style (solid, dashed, dotted, double, etc.)

        Returns:
            Word border style name
        """
        style_map = {
            'solid': 'single',
            'dashed': 'dashed',
            'dotted': 'dotted',
            'double': 'double',
            'groove': 'threeDEngrave',
            'ridge': 'threeDEmboss',
            'inset': 'inset',
            'outset': 'outset',
            'none': 'none',
            'hidden': 'none'
        }
        return style_map.get(css_style.lower(), 'single')

    def _get_font_size_pt(self, font_size) -> Optional[float]:
        """Get font size in pt."""
        if isinstance(font_size, (int, float)):
            return float(font_size)

        try:
            return UnitConverter.to_pt(str(font_size))
        except:
            return None

    def _map_text_align(self, css_align: str) -> Optional[WD_ALIGN_PARAGRAPH]:
        """Map CSS text-align to Word alignment."""
        align_map = {
            'left': WD_ALIGN_PARAGRAPH.LEFT,
            'center': WD_ALIGN_PARAGRAPH.CENTER,
            'right': WD_ALIGN_PARAGRAPH.RIGHT,
            'justify': WD_ALIGN_PARAGRAPH.JUSTIFY,
        }
        return align_map.get(css_align.lower())

    def _map_vertical_align(self, css_align: str) -> Optional[WD_ALIGN_VERTICAL]:
        """Map CSS vertical-align to Word vertical alignment."""
        align_map = {
            'top': WD_ALIGN_VERTICAL.TOP,
            'middle': WD_ALIGN_VERTICAL.CENTER,
            'center': WD_ALIGN_VERTICAL.CENTER,
            'bottom': WD_ALIGN_VERTICAL.BOTTOM,
        }
        return align_map.get(css_align.lower())

    def _apply_opacity_to_color(self, color: str, opacity: Any) -> str:
        """
        Apply opacity to a color by blending with white background.

        Args:
            color: Color value (hex, rgb, rgba, or named)
            opacity: Opacity value (0.0-1.0 or string)

        Returns:
            Color with opacity applied (as hex or rgb)
        """
        try:
            # Parse opacity value
            if isinstance(opacity, str):
                opacity = float(opacity)
            elif isinstance(opacity, (int, float)):
                opacity = float(opacity)
            else:
                return color

            # Clamp opacity to 0.0-1.0
            opacity = max(0.0, min(1.0, opacity))

            # If opacity is 1.0, no change needed
            if opacity >= 0.99:
                return color

            # Convert color to RGB
            rgb_color = ColorConverter.to_rgb_color(color)
            if not rgb_color:
                return color

            # Blend with white background (255, 255, 255)
            r = int(rgb_color.r * opacity + 255 * (1 - opacity))
            g = int(rgb_color.g * opacity + 255 * (1 - opacity))
            b = int(rgb_color.b * opacity + 255 * (1 - opacity))

            # Return as hex color
            return f'#{r:02x}{g:02x}{b:02x}'

        except Exception as e:
            logger.warning(f"Error applying opacity to color: {e}")
            return color

    def _apply_box_shadow_degradation(self, paragraph, box_shadow_value: str):
        """
        Degrade box-shadow to a subtle border for visual approximation.

        Args:
            paragraph: python-docx Paragraph object
            box_shadow_value: CSS box-shadow value

        Note:
            Word doesn't support shadows, so we approximate with a light gray border.
        """
        try:
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls

            # Parse box-shadow to detect if it's significant
            # Format: h-offset v-offset blur spread color
            # For simplicity, we just add a subtle border if box-shadow exists
            if box_shadow_value and box_shadow_value.lower() != 'none':
                # Add a subtle gray border to approximate shadow
                pPr = paragraph._element.get_or_add_pPr()

                # Check if borders already exist
                pBdr = pPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pBdr')
                if pBdr is None:
                    # Add subtle bottom and right borders to simulate shadow
                    borders_xml = f'''
                        <w:pBdr {nsdecls("w")}>
                            <w:bottom w:val="single" w:sz="4" w:space="1" w:color="D3D3D3"/>
                            <w:right w:val="single" w:sz="4" w:space="1" w:color="D3D3D3"/>
                        </w:pBdr>
                    '''
                    pBdr = parse_xml(borders_xml)
                    pPr.append(pBdr)

        except Exception as e:
            logger.warning(f"Error in box-shadow degradation: {e}")
