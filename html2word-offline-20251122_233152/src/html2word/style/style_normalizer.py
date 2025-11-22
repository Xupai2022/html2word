"""
CSS style normalization.

Normalizes CSS values to standard formats for easier processing.
"""

import logging
import re
from typing import Any, Dict, Optional
from html2word.utils.units import UnitConverter
from html2word.utils.colors import ColorConverter

logger = logging.getLogger(__name__)


class StyleNormalizer:
    """Normalizes CSS style values."""

    # Font weight keywords to numeric values
    FONT_WEIGHT_MAP = {
        'normal': 400,
        'bold': 700,
        'bolder': 900,  # Simplified
        'lighter': 300,  # Simplified
    }

    # Text decoration values
    TEXT_DECORATION_VALUES = {
        'none', 'underline', 'overline', 'line-through', 'blink'
    }

    # Text align values
    TEXT_ALIGN_VALUES = {
        'left', 'right', 'center', 'justify', 'start', 'end'
    }

    # Vertical align values
    VERTICAL_ALIGN_VALUES = {
        'baseline', 'top', 'middle', 'bottom', 'sub', 'super',
        'text-top', 'text-bottom'
    }

    @classmethod
    def normalize_styles(
        cls,
        styles: Dict[str, str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Normalize all styles in a dictionary.

        Args:
            styles: Dictionary of CSS properties
            context: Context for unit conversion

        Returns:
            Dictionary of normalized styles
        """
        if context is None:
            context = {}

        normalized = {}

        for prop, value in styles.items():
            normalized_value = cls.normalize_property(prop, value, context)
            if normalized_value is not None:
                normalized[prop] = normalized_value

        return normalized

    @classmethod
    def normalize_property(
        cls,
        prop_name: str,
        prop_value: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Normalize a single CSS property value.

        Args:
            prop_name: CSS property name
            prop_value: CSS property value
            context: Context for unit conversion

        Returns:
            Normalized value
        """
        if context is None:
            context = {}

        prop_name = prop_name.lower()
        prop_value = str(prop_value).strip()

        # Font properties
        if prop_name == 'font-weight':
            return cls.normalize_font_weight(prop_value)

        elif prop_name == 'font-size':
            return cls.normalize_length(prop_value, context)

        elif prop_name == 'line-height':
            return cls.normalize_line_height(prop_value, context)

        # Color properties
        elif prop_name in ('color', 'background-color', 'border-color'):
            return cls.normalize_color(prop_value)

        # Length properties
        elif prop_name in (
            'width', 'height', 'max-width', 'max-height', 'min-width', 'min-height',
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'border-width', 'border-top-width', 'border-right-width',
            'border-bottom-width', 'border-left-width',
            'text-indent', 'letter-spacing', 'word-spacing'
        ):
            return prop_value  # Keep as string for later conversion

        # Text properties
        elif prop_name == 'text-decoration':
            return cls.normalize_text_decoration(prop_value)

        elif prop_name == 'text-align':
            return cls.normalize_text_align(prop_value)

        elif prop_name == 'vertical-align':
            return cls.normalize_vertical_align(prop_value)

        elif prop_name == 'text-transform':
            return cls.normalize_text_transform(prop_value)

        # Font family
        elif prop_name == 'font-family':
            return cls.normalize_font_family(prop_value)

        # Default: return as-is
        else:
            return prop_value

    @classmethod
    def normalize_font_weight(cls, value: str) -> int:
        """
        Normalize font-weight to numeric value.

        Args:
            value: Font weight value

        Returns:
            Numeric font weight (100-900)
        """
        value_lower = value.lower()

        if value_lower in cls.FONT_WEIGHT_MAP:
            return cls.FONT_WEIGHT_MAP[value_lower]

        # Try to parse as number
        try:
            weight = int(value)
            # Clamp to valid range
            return max(100, min(900, weight))
        except ValueError:
            # Default to normal
            return 400

    @classmethod
    def normalize_length(
        cls,
        value: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Normalize length value to pt.

        Args:
            value: Length value with unit
            context: Context for conversion

        Returns:
            Value in pt
        """
        return UnitConverter.to_pt(value, context)

    @classmethod
    def normalize_line_height(
        cls,
        value: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Normalize line-height value.

        Args:
            value: Line height value
            context: Context for conversion

        Returns:
            Numeric multiplier or pt value
        """
        if context is None:
            context = {}

        value = value.strip().lower()

        # Keyword
        if value == 'normal':
            return 1.2

        # Unitless number (multiplier)
        try:
            return float(value)
        except ValueError:
            pass

        # Length with unit
        return UnitConverter.to_pt(value, context)

    @classmethod
    def normalize_color(cls, value: str) -> Optional[str]:
        """
        Normalize color to hex format.

        Args:
            value: Color value

        Returns:
            Hex color string or None
        """
        hex_color = ColorConverter.to_hex(value)
        return hex_color if hex_color else value

    @classmethod
    def normalize_text_decoration(cls, value: str) -> str:
        """
        Normalize text-decoration value.

        Args:
            value: Text decoration value

        Returns:
            Normalized value
        """
        value_lower = value.lower().strip()

        # Handle multiple values
        parts = value_lower.split()

        # Extract decoration type (underline, line-through, etc.)
        for part in parts:
            if part in cls.TEXT_DECORATION_VALUES:
                return part

        return 'none'

    @classmethod
    def normalize_text_align(cls, value: str) -> str:
        """
        Normalize text-align value.

        Args:
            value: Text align value

        Returns:
            Normalized value
        """
        value_lower = value.lower().strip()

        if value_lower in cls.TEXT_ALIGN_VALUES:
            # Map 'start' and 'end' to left/right (LTR assumed)
            if value_lower == 'start':
                return 'left'
            elif value_lower == 'end':
                return 'right'
            return value_lower

        return 'left'

    @classmethod
    def normalize_vertical_align(cls, value: str) -> str:
        """
        Normalize vertical-align value.

        Args:
            value: Vertical align value

        Returns:
            Normalized value
        """
        value_lower = value.lower().strip()

        if value_lower in cls.VERTICAL_ALIGN_VALUES:
            return value_lower

        # Default
        return 'baseline'

    @classmethod
    def normalize_text_transform(cls, value: str) -> str:
        """
        Normalize text-transform value.

        Args:
            value: Text transform value

        Returns:
            Normalized value
        """
        value_lower = value.lower().strip()

        if value_lower in ('none', 'capitalize', 'uppercase', 'lowercase'):
            return value_lower

        return 'none'

    @classmethod
    def normalize_font_family(cls, value: str) -> str:
        """
        Normalize font-family value.

        Args:
            value: Font family value

        Returns:
            Normalized font family (without quotes)
        """
        # Remove quotes
        value = value.strip()
        value = re.sub(r'^["\']|["\']$', '', value)

        return value

    @classmethod
    def apply_text_transform(cls, text: str, transform: str) -> str:
        """
        Apply text-transform to text.

        Args:
            text: Original text
            transform: Transform type (none, capitalize, uppercase, lowercase)

        Returns:
            Transformed text
        """
        if transform == 'uppercase':
            return text.upper()
        elif transform == 'lowercase':
            return text.lower()
        elif transform == 'capitalize':
            return text.title()
        else:
            return text
