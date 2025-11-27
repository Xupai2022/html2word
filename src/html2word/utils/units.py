"""
Unit conversion utilities.

Handles conversion between various CSS units (px, pt, em, rem, %, in, cm, mm)
to Word's native point (pt) unit.
"""

import re
from typing import Union, Optional, Dict, Any


class UnitConverter:
    """Converter for CSS units to Word pt (point) unit."""

    # Conversion constants
    PX_TO_PT = 0.75  # 1px = 0.75pt at 96 DPI
    PT_PER_INCH = 72
    PT_PER_CM = 28.35
    PT_PER_MM = 2.835
    DEFAULT_FONT_SIZE_PT = 12  # Default font size in pt
    DEFAULT_FONT_SIZE_PX = 16  # Default font size in px (browser default)

    # Unit pattern regex
    UNIT_PATTERN = re.compile(
        r'^([+-]?(?:\d+\.?\d*|\.\d+))([a-z%]+)?$',
        re.IGNORECASE
    )

    @classmethod
    def parse_value(cls, value: Union[str, int, float]) -> tuple[float, str]:
        """
        Parse a CSS value into number and unit.

        Args:
            value: CSS value (e.g., "12px", "1.5em", "100%", 12)

        Returns:
            Tuple of (numeric_value, unit_string)

        Examples:
            parse_value("12px") -> (12.0, "px")
            parse_value("1.5em") -> (1.5, "em")
            parse_value(12) -> (12.0, "")
        """
        if isinstance(value, (int, float)):
            return float(value), ""

        value_str = str(value).strip()
        if not value_str:
            return 0.0, ""

        match = cls.UNIT_PATTERN.match(value_str)
        if not match:
            return 0.0, ""

        num_str, unit = match.groups()
        num = float(num_str)
        unit = unit.lower() if unit else ""

        return num, unit

    @classmethod
    def to_pt(
        cls,
        value: Union[str, int, float],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Convert any CSS unit to pt (point).

        Args:
            value: CSS value with unit
            context: Optional context dict with:
                - parent_font_size: Parent element font size in pt
                - root_font_size: Root element font size in pt
                - base_value: Base value for percentage calculations
                - container_width: Container width for percentage width

        Returns:
            Value in pt

        Examples:
            to_pt("12px") -> 9.0
            to_pt("1em", {"parent_font_size": 16}) -> 16.0
            to_pt("50%", {"base_value": 200}) -> 100.0
        """
        if context is None:
            context = {}

        num, unit = cls.parse_value(value)

        if not unit or unit == "pt":
            return num

        elif unit == "px":
            return num * cls.PX_TO_PT

        elif unit == "em":
            parent_font_size = context.get("parent_font_size", cls.DEFAULT_FONT_SIZE_PT)
            return num * parent_font_size

        elif unit == "rem":
            root_font_size = context.get("root_font_size", cls.DEFAULT_FONT_SIZE_PT)
            return num * root_font_size

        elif unit == "%":
            base_value = context.get("base_value", 0)
            return base_value * num / 100

        elif unit == "in":
            return num * cls.PT_PER_INCH

        elif unit == "cm":
            return num * cls.PT_PER_CM

        elif unit == "mm":
            return num * cls.PT_PER_MM

        else:
            # Unknown unit, return as-is
            return num

    @classmethod
    def to_twips(cls, value: Union[str, int, float], context: Optional[Dict[str, Any]] = None) -> int:
        """
        Convert CSS unit to twips (1/1440 inch, used by python-docx for spacing).

        Args:
            value: CSS value with unit
            context: Optional context dict

        Returns:
            Value in twips (integer)
        """
        pt_value = cls.to_pt(value, context)
        return int(pt_value * 20)  # 1 pt = 20 twips

    @classmethod
    def to_emu(cls, value: Union[str, int, float], context: Optional[Dict[str, Any]] = None) -> int:
        """
        Convert CSS unit to EMU (English Metric Unit, used for images).

        Args:
            value: CSS value with unit
            context: Optional context dict

        Returns:
            Value in EMU (integer)
        """
        pt_value = cls.to_pt(value, context)
        inches = pt_value / cls.PT_PER_INCH
        return int(inches * 914400)  # 1 inch = 914400 EMU

    @classmethod
    def parse_box_values(cls, value: Union[str, int, float]) -> Dict[str, float]:
        """
        Parse CSS box values (margin, padding) into top, right, bottom, left.

        Args:
            value: CSS box value (e.g., "10px", "10px 20px", "10px 20px 30px 40px")

        Returns:
            Dict with keys: top, right, bottom, left (in original units)

        Examples:
            parse_box_values("10px") -> {"top": 10, "right": 10, "bottom": 10, "left": 10}
            parse_box_values("10px 20px") -> {"top": 10, "right": 20, "bottom": 10, "left": 20}
        """
        if isinstance(value, (int, float)):
            return {"top": value, "right": value, "bottom": value, "left": value}

        parts = str(value).strip().split()
        if not parts:
            return {"top": 0, "right": 0, "bottom": 0, "left": 0}

        # Parse each value
        nums = []
        units = []
        for part in parts:
            num, unit = cls.parse_value(part)
            nums.append(num)
            units.append(unit)

        # Apply CSS box model rules
        if len(nums) == 1:
            # All sides same
            return {"top": nums[0], "right": nums[0], "bottom": nums[0], "left": nums[0]}
        elif len(nums) == 2:
            # top/bottom, left/right
            return {"top": nums[0], "right": nums[1], "bottom": nums[0], "left": nums[1]}
        elif len(nums) == 3:
            # top, left/right, bottom
            return {"top": nums[0], "right": nums[1], "bottom": nums[2], "left": nums[1]}
        else:
            # top, right, bottom, left
            return {"top": nums[0], "right": nums[1], "bottom": nums[2], "left": nums[3]}

    @classmethod
    def parse_border_width(cls, value: Union[str, int, float]) -> float:
        """
        Parse CSS border width value.

        Handles keywords: thin, medium, thick

        Args:
            value: Border width value

        Returns:
            Width in original unit
        """
        if isinstance(value, (int, float)):
            return float(value)

        value_str = str(value).strip().lower()

        # Handle keywords
        # NOTE: Changed "medium" from 3 to 1 to match typical browser rendering
        # where default table borders appear thin rather than medium-weight
        keyword_map = {
            "thin": 1,
            "medium": 1,  # Changed from 3 to 1 for thinner default borders
            "thick": 5
        }

        if value_str in keyword_map:
            return float(keyword_map[value_str])

        num, unit = cls.parse_value(value_str)
        return num
