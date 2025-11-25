"""
Color conversion utilities.

Handles conversion between various CSS color formats (hex, rgb, rgba, color names)
to Word's RGB format.
"""

import re
from typing import Optional, Tuple
from docx.shared import RGBColor


class ColorConverter:
    """Converter for CSS color values to Word RGBColor."""

    # CSS color name to RGB mapping (extended color keywords)
    COLOR_NAMES = {
        # Basic colors
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "lime": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "silver": (192, 192, 192),
        "gray": (128, 128, 128),
        "grey": (128, 128, 128),
        "maroon": (128, 0, 0),
        "olive": (128, 128, 0),
        "green": (0, 128, 0),
        "purple": (128, 0, 128),
        "teal": (0, 128, 128),
        "navy": (0, 0, 128),
        # Extended colors
        "orange": (255, 165, 0),
        "pink": (255, 192, 203),
        "brown": (165, 42, 42),
        "gold": (255, 215, 0),
        "violet": (238, 130, 238),
        "indigo": (75, 0, 130),
        "coral": (255, 127, 80),
        "crimson": (220, 20, 60),
        "darkblue": (0, 0, 139),
        "darkgreen": (0, 100, 0),
        "darkred": (139, 0, 0),
        "lightblue": (173, 216, 230),
        "lightgreen": (144, 238, 144),
        "lightgray": (211, 211, 211),
        "lightgrey": (211, 211, 211),
        "darkgray": (169, 169, 169),
        "darkgrey": (169, 169, 169),
        "transparent": (255, 255, 255),  # Treat as white
    }

    # Regex patterns
    HEX_PATTERN = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')
    RGB_PATTERN = re.compile(r'^rgba?\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$')

    @classmethod
    def parse_color(cls, color_string: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse CSS color string to RGB tuple.

        Args:
            color_string: CSS color value (hex, rgb, rgba, or color name)

        Returns:
            RGB tuple (r, g, b) or None if invalid

        Examples:
            parse_color("#FF0000") -> (255, 0, 0)
            parse_color("rgb(255, 0, 0)") -> (255, 0, 0)
            parse_color("red") -> (255, 0, 0)
        """
        if not color_string:
            return None

        color_str = color_string.strip().lower()

        # Try hex format
        if color_str.startswith("#"):
            return cls._parse_hex(color_str)

        # Try rgb/rgba format
        if color_str.startswith("rgb"):
            return cls._parse_rgb(color_str)

        # Try color name
        if color_str in cls.COLOR_NAMES:
            return cls.COLOR_NAMES[color_str]

        return None

    @classmethod
    def _parse_hex(cls, hex_string: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse hex color format.

        Args:
            hex_string: Hex color (e.g., "#FF0000" or "#F00")

        Returns:
            RGB tuple or None
        """
        match = cls.HEX_PATTERN.match(hex_string)
        if not match:
            return None

        hex_digits = match.group(1)

        # Convert 3-digit to 6-digit format
        if len(hex_digits) == 3:
            hex_digits = "".join([c * 2 for c in hex_digits])

        r = int(hex_digits[0:2], 16)
        g = int(hex_digits[2:4], 16)
        b = int(hex_digits[4:6], 16)

        return (r, g, b)

    @classmethod
    def _parse_rgb(cls, rgb_string: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse rgb/rgba color format.

        Args:
            rgb_string: RGB color (e.g., "rgb(255, 0, 0)" or "rgba(255, 0, 0, 0.5)")

        Returns:
            RGB tuple or None (alpha channel is ignored)
        """
        match = cls.RGB_PATTERN.match(rgb_string)
        if not match:
            return None

        r, g, b = match.groups()[:3]
        # Convert to int, handling both "255" and "255.0" formats
        return (int(float(r)), int(float(g)), int(float(b)))

    @classmethod
    def to_rgb_color(cls, color_string: str) -> Optional[RGBColor]:
        """
        Convert CSS color to Word RGBColor object.

        Args:
            color_string: CSS color value

        Returns:
            RGBColor object or None if invalid
        """
        rgb = cls.parse_color(color_string)
        if rgb is None:
            return None

        return RGBColor(rgb[0], rgb[1], rgb[2])

    @classmethod
    def to_hex(cls, color_string: str) -> Optional[str]:
        """
        Convert CSS color to hex format.

        Args:
            color_string: CSS color value

        Returns:
            Hex color string (e.g., "#FF0000") or None
        """
        rgb = cls.parse_color(color_string)
        if rgb is None:
            return None

        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    @classmethod
    def is_light_color(cls, color_string: str) -> bool:
        """
        Determine if a color is light (for contrast calculations).

        Args:
            color_string: CSS color value

        Returns:
            True if the color is considered light
        """
        rgb = cls.parse_color(color_string)
        if rgb is None:
            return True

        # Calculate perceived brightness
        # Formula: sqrt(0.299*R^2 + 0.587*G^2 + 0.114*B^2)
        brightness = (0.299 * rgb[0]**2 + 0.587 * rgb[1]**2 + 0.114 * rgb[2]**2) ** 0.5
        return brightness > 127.5
