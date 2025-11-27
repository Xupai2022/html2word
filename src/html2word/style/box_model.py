"""
CSS box model calculation.

Handles calculation of element box model (margin, padding, border, content).
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from html2word.parser.dom_tree import DOMNode
from html2word.utils.units import UnitConverter

logger = logging.getLogger(__name__)


@dataclass
class BoxEdge:
    """Represents one edge of a box (top, right, bottom, left)."""
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'top': self.top,
            'right': self.right,
            'bottom': self.bottom,
            'left': self.left
        }


@dataclass
class BorderEdge:
    """Represents border properties for each edge."""
    width: float = 0.0
    style: str = 'none'
    color: str = '#000000'


class Border:
    """Represents border properties."""
    top: BorderEdge
    right: BorderEdge
    bottom: BorderEdge
    left: BorderEdge

    def __init__(self):
        """Initialize border with default edges."""
        self.top = BorderEdge()
        self.right = BorderEdge()
        self.bottom = BorderEdge()
        self.left = BorderEdge()

    def has_border(self) -> bool:
        """Check if border is visible."""
        return any([
            self.top.width > 0 and self.top.style != 'none',
            self.right.width > 0 and self.right.style != 'none',
            self.bottom.width > 0 and self.bottom.style != 'none',
            self.left.width > 0 and self.left.style != 'none'
        ])


class BoxModel:
    """Represents the CSS box model for an element."""

    def __init__(
        self,
        node: DOMNode,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize box model from DOM node.

        Args:
            node: DOM node
            context: Context for unit conversion
        """
        self.node = node
        self.context = context or {}
        self.styles = node.computed_styles

        # Box model components (in pt)
        self.margin = BoxEdge()
        self.padding = BoxEdge()
        self.border = Border()
        self.width: Optional[float] = None
        self.height: Optional[float] = None
        self.box_sizing = 'content-box'

        # Calculate box model
        self._calculate()

    def _calculate(self):
        """Calculate all box model properties."""
        self._calculate_margin()
        self._calculate_padding()
        self._calculate_border()
        self._calculate_dimensions()
        self._get_box_sizing()

    def _calculate_margin(self):
        """Calculate margin values."""
        margin = self._parse_box_property('margin')
        self.margin = BoxEdge(
            top=margin['top'],
            right=margin['right'],
            bottom=margin['bottom'],
            left=margin['left']
        )

    def _calculate_padding(self):
        """Calculate padding values."""
        padding = self._parse_box_property('padding')
        self.padding = BoxEdge(
            top=padding['top'],
            right=padding['right'],
            bottom=padding['bottom'],
            left=padding['left']
        )

    def _calculate_border(self):
        """Calculate border properties."""
        import logging
        logger = logging.getLogger(__name__)

        # First, parse shorthand border properties for individual sides (e.g., border-left: 1px solid #ddd)
        self._parse_border_shorthand()

        # Border width for each side
        border_width = self._parse_box_property('border', 'width')

        # DEBUG: Log border width parsing for table cells
        if 'border-left-width' in self.styles or 'border-width' in self.styles or 'border-left' in self.styles:
            logger.debug(f"BORDER DEBUG: styles keys with 'border': {[k for k in self.styles.keys() if 'border' in k]}")
            if 'border-left-width' in self.styles:
                logger.debug(f"BORDER DEBUG: border-left-width = {self.styles['border-left-width']}")
            if 'border-width' in self.styles:
                logger.debug(f"BORDER DEBUG: border-width = {self.styles['border-width']}")
            if 'border-left' in self.styles:
                logger.debug(f"BORDER DEBUG: border-left (shorthand) = {self.styles['border-left']}")
            logger.debug(f"BORDER DEBUG: parsed border_width = {border_width}")

        # Border style for each side
        border_style = self._parse_border_styles()

        # Border color for each side
        border_color = self._parse_border_colors()

        # Debug final values before setting
        logger.debug(f"BORDER FINAL VALUES: width={border_width}, style={border_style}, color={border_color}")

        # Set top border
        self.border.top.width = border_width['top']
        self.border.top.style = border_style['top']
        self.border.top.color = border_color['top']

        # Set right border
        self.border.right.width = border_width['right']
        self.border.right.style = border_style['right']
        self.border.right.color = border_color['right']

        # Set bottom border
        self.border.bottom.width = border_width['bottom']
        self.border.bottom.style = border_style['bottom']
        self.border.bottom.color = border_color['bottom']

        # Set left border
        self.border.left.width = border_width['left']
        self.border.left.style = border_style['left']
        self.border.left.color = border_color['left']

        # Debug final border edges
        logger.debug(f"BORDER EDGES: left=(width={self.border.left.width}, style={self.border.left.style}, color={self.border.left.color})")
        logger.debug(f"BORDER EDGES: right=(width={self.border.right.width}, style={self.border.right.style}, color={self.border.right.color})")

    def _parse_border_shorthand(self):
        """Parse border shorthand properties for individual sides."""
        import logging
        import re
        logger = logging.getLogger(__name__)

        # Check for individual side shorthand (e.g., border-left: 1px solid #ddd)
        for side in ['top', 'right', 'bottom', 'left']:
            shorthand_key = f'border-{side}'
            if shorthand_key in self.styles:
                value = self.styles[shorthand_key]
                logger.debug(f"Parsing border shorthand: {shorthand_key} = {value}")

                # Parse the shorthand value (e.g., "1px solid #ddd")
                # Pattern matches: width (optional), style (optional), color (optional)
                # Common patterns: "1px solid #ddd", "solid", "#ddd", "1px solid"
                parts = str(value).strip().split()

                width_val = None
                style_val = None
                color_val = None

                for part in parts:
                    # Check if it's a width (contains px, pt, em, etc. or is a number)
                    if re.match(r'^\d+(\.\d+)?(px|pt|em|rem|%)?$', part) or part in ['thin', 'medium', 'thick']:
                        width_val = part
                    # Check if it's a style keyword
                    elif part in ['none', 'solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'inset', 'outset', 'hidden']:
                        style_val = part
                    # Otherwise assume it's a color
                    elif (part.startswith('#') or part.startswith('rgb') or part.startswith('hsl') or
                          part in ['transparent', 'black', 'white', 'red', 'blue', 'green', 'yellow',
                                   'gray', 'grey', 'silver', 'maroon', 'purple', 'fuchsia', 'lime',
                                   'olive', 'navy', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite',
                                   'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet',
                                   'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral',
                                   'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
                                   'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki',
                                   'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred',
                                   'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray',
                                   'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
                                   'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite',
                                   'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow',
                                   'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender',
                                   'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral',
                                   'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey',
                                   'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray',
                                   'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen',
                                   'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple',
                                   'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise',
                                   'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin',
                                   'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod',
                                   'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff',
                                   'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown',
                                   'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue',
                                   'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle',
                                   'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen',
                                   # Common CSS color shortcuts
                                   '#ccc', '#ddd', '#eee', '#aaa', '#bbb', '#fff', '#000']):
                        color_val = part

                # Apply the parsed values to individual properties
                if width_val:
                    self.styles[f'border-{side}-width'] = width_val
                    logger.debug(f"Set border-{side}-width = {width_val}")
                if style_val:
                    self.styles[f'border-{side}-style'] = style_val
                    logger.debug(f"Set border-{side}-style = {style_val}")
                if color_val:
                    self.styles[f'border-{side}-color'] = color_val
                    logger.debug(f"Set border-{side}-color = {color_val}")

                # Remove the shorthand property after expanding it
                del self.styles[shorthand_key]

        # Also handle the general border shorthand (e.g., border: 1px solid #ddd)
        if 'border' in self.styles:
            value = self.styles['border']
            logger.debug(f"Parsing general border shorthand: border = {value}")

            # Parse the shorthand value
            parts = str(value).strip().split()

            width_val = None
            style_val = None
            color_val = None

            for part in parts:
                # Check if it's a width
                if re.match(r'^\d+(\.\d+)?(px|pt|em|rem|%)?$', part) or part in ['thin', 'medium', 'thick']:
                    width_val = part
                # Check if it's a style keyword
                elif part in ['none', 'solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'inset', 'outset', 'hidden']:
                    style_val = part
                # Otherwise assume it's a color
                elif part.startswith('#') or part.startswith('rgb') or part in ['transparent', 'black', 'white', 'red', 'blue', 'green', 'yellow', 'gray', 'grey']:
                    color_val = part

            # Apply to all sides
            if width_val and 'border-width' not in self.styles:
                self.styles['border-width'] = width_val
                logger.debug(f"Set border-width = {width_val}")
            if style_val and 'border-style' not in self.styles:
                self.styles['border-style'] = style_val
                logger.debug(f"Set border-style = {style_val}")
            if color_val and 'border-color' not in self.styles:
                self.styles['border-color'] = color_val
                logger.debug(f"Set border-color = {color_val}")

            # Remove the shorthand property after expanding it
            del self.styles['border']

    def _parse_border_styles(self) -> Dict[str, str]:
        """Parse border styles for each side."""
        result = {'top': 'none', 'right': 'none', 'bottom': 'none', 'left': 'none'}

        # Check individual side styles first
        for side in ['top', 'right', 'bottom', 'left']:
            key = f'border-{side}-style'
            if key in self.styles:
                result[side] = self.styles[key]

        # Check for border-style shorthand
        if 'border-style' in self.styles:
            values = self.styles['border-style'].split()
            if len(values) == 1:
                # All sides
                for side in result:
                    if result[side] == 'none':
                        result[side] = values[0]
            elif len(values) == 2:
                # top/bottom, left/right
                for side in ['top', 'bottom']:
                    if result[side] == 'none':
                        result[side] = values[0]
                for side in ['left', 'right']:
                    if result[side] == 'none':
                        result[side] = values[1]
            elif len(values) == 3:
                # top, left/right, bottom
                if result['top'] == 'none':
                    result['top'] = values[0]
                for side in ['left', 'right']:
                    if result[side] == 'none':
                        result[side] = values[1]
                if result['bottom'] == 'none':
                    result['bottom'] = values[2]
            elif len(values) == 4:
                # top, right, bottom, left
                sides = ['top', 'right', 'bottom', 'left']
                for i, side in enumerate(sides):
                    if result[side] == 'none':
                        result[side] = values[i]

        return result

    def _parse_border_colors(self) -> Dict[str, str]:
        """Parse border colors for each side."""
        result = {'top': '#000000', 'right': '#000000', 'bottom': '#000000', 'left': '#000000'}

        # Check individual side colors first
        for side in ['top', 'right', 'bottom', 'left']:
            key = f'border-{side}-color'
            if key in self.styles:
                result[side] = self.styles[key]

        # Check for border-color shorthand
        if 'border-color' in self.styles:
            values = self.styles['border-color'].split()
            if len(values) == 1:
                # All sides
                for side in result:
                    if result[side] == '#000000':
                        result[side] = values[0]
            elif len(values) == 2:
                # top/bottom, left/right
                for side in ['top', 'bottom']:
                    if result[side] == '#000000':
                        result[side] = values[0]
                for side in ['left', 'right']:
                    if result[side] == '#000000':
                        result[side] = values[1]
            elif len(values) == 3:
                # top, left/right, bottom
                if result['top'] == '#000000':
                    result['top'] = values[0]
                for side in ['left', 'right']:
                    if result[side] == '#000000':
                        result[side] = values[1]
                if result['bottom'] == '#000000':
                    result['bottom'] = values[2]
            elif len(values) == 4:
                # top, right, bottom, left
                sides = ['top', 'right', 'bottom', 'left']
                for i, side in enumerate(sides):
                    if result[side] == '#000000':
                        result[side] = values[i]

        return result

    def _calculate_dimensions(self):
        """Calculate width and height."""
        # Width
        if 'width' in self.styles:
            self.width = UnitConverter.to_pt(self.styles['width'], self.context)

        # Height
        if 'height' in self.styles:
            self.height = UnitConverter.to_pt(self.styles['height'], self.context)

    def _get_box_sizing(self):
        """Get box-sizing value."""
        self.box_sizing = self.styles.get('box-sizing', 'content-box')

    def _parse_box_property(
        self,
        prop_prefix: str,
        prop_suffix: str = ''
    ) -> Dict[str, float]:
        """
        Parse box property (margin, padding, border-width).

        Args:
            prop_prefix: Property prefix ('margin', 'padding', 'border')
            prop_suffix: Property suffix ('', 'width', 'style', 'color')

        Returns:
            Dictionary with top, right, bottom, left values in pt
        """
        suffix = f'-{prop_suffix}' if prop_suffix else ''

        # Try shorthand property first
        shorthand_prop = f'{prop_prefix}{suffix}'
        if shorthand_prop in self.styles:
            value = self.styles[shorthand_prop]

            # For border-width, handle keywords and preserve units
            if prop_suffix == 'width' and prop_prefix == 'border':
                # Split the value into parts
                parts = str(value).strip().split()
                if not parts:
                    return {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}

                # Convert each part preserving units
                converted = []
                for part in parts:
                    # Pass the complete value with units to to_pt
                    pt_value = UnitConverter.to_pt(part, self.context)
                    # Debug logging
                    import logging
                    logging.debug(f"Border width conversion: '{part}' -> {pt_value}pt")
                    converted.append(pt_value)

                # Apply CSS box model rules
                if len(converted) == 1:
                    return {'top': converted[0], 'right': converted[0], 'bottom': converted[0], 'left': converted[0]}
                elif len(converted) == 2:
                    return {'top': converted[0], 'right': converted[1], 'bottom': converted[0], 'left': converted[1]}
                elif len(converted) == 3:
                    return {'top': converted[0], 'right': converted[1], 'bottom': converted[2], 'left': converted[1]}
                else:
                    return {'top': converted[0], 'right': converted[1], 'bottom': converted[2], 'left': converted[3]}
            else:
                # For other properties, parse as before but preserve units
                parts = str(value).strip().split()
                if not parts:
                    return {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}

                # Convert each part preserving units
                converted = []
                for part in parts:
                    converted.append(UnitConverter.to_pt(part, self.context))

                # Apply CSS box model rules
                if len(converted) == 1:
                    return {'top': converted[0], 'right': converted[0], 'bottom': converted[0], 'left': converted[0]}
                elif len(converted) == 2:
                    return {'top': converted[0], 'right': converted[1], 'bottom': converted[0], 'left': converted[1]}
                elif len(converted) == 3:
                    return {'top': converted[0], 'right': converted[1], 'bottom': converted[2], 'left': converted[1]}
                else:
                    return {'top': converted[0], 'right': converted[1], 'bottom': converted[2], 'left': converted[3]}

        # Try individual properties
        result = {}
        for edge in ['top', 'right', 'bottom', 'left']:
            prop_name = f'{prop_prefix}-{edge}{suffix}'
            if prop_name in self.styles:
                value = self.styles[prop_name]
                pt_value = UnitConverter.to_pt(value, self.context)
                # Debug logging for individual properties
                import logging
                logging.debug(f"Individual border width '{prop_name}': '{value}' -> {pt_value}pt")
                result[edge] = pt_value
            else:
                result[edge] = 0.0

        return result

    def get_total_width(self) -> Optional[float]:
        """
        Calculate total width including padding and border.

        Returns:
            Total width in pt, or None if width not specified
        """
        if self.width is None:
            return None

        if self.box_sizing == 'border-box':
            # Width includes padding and border
            return self.width
        else:
            # Content-box: add padding and border
            return (
                self.width +
                self.padding.left + self.padding.right +
                self.border.width.left + self.border.width.right
            )

    def get_content_width(self) -> Optional[float]:
        """
        Calculate content width (excluding padding and border).

        Returns:
            Content width in pt, or None if width not specified
        """
        if self.width is None:
            return None

        if self.box_sizing == 'border-box':
            # Subtract padding and border
            return (
                self.width -
                self.padding.left - self.padding.right -
                self.border.width.left - self.border.width.right
            )
        else:
            # Content-box: width is already content width
            return self.width

    def get_total_height(self) -> Optional[float]:
        """
        Calculate total height including padding and border.

        Returns:
            Total height in pt, or None if height not specified
        """
        if self.height is None:
            return None

        if self.box_sizing == 'border-box':
            return self.height
        else:
            return (
                self.height +
                self.padding.top + self.padding.bottom +
                self.border.width.top + self.border.width.bottom
            )

    def get_horizontal_spacing(self) -> float:
        """
        Get total horizontal spacing (margin + padding + border).

        Returns:
            Total horizontal spacing in pt
        """
        return (
            self.margin.left + self.margin.right +
            self.padding.left + self.padding.right +
            self.border.width.left + self.border.width.right
        )

    def get_vertical_spacing(self) -> float:
        """
        Get total vertical spacing (margin + padding + border).

        Returns:
            Total vertical spacing in pt
        """
        return (
            self.margin.top + self.margin.bottom +
            self.padding.top + self.padding.bottom +
            self.border.width.top + self.border.width.bottom
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert box model to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'margin': self.margin.to_dict(),
            'padding': self.padding.to_dict(),
            'border': {
                'width': self.border.width.to_dict(),
                'style': self.border.style,
                'color': self.border.color
            },
            'width': self.width,
            'height': self.height,
            'box_sizing': self.box_sizing,
            'total_width': self.get_total_width(),
            'content_width': self.get_content_width(),
            'total_height': self.get_total_height(),
        }
