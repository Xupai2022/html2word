"""
Position calculator for element positioning.

Handles CSS position property calculations.
"""

import logging
from typing import Optional, Dict, Any
from html2word.parser.dom_tree import DOMNode
from html2word.utils.units import UnitConverter

logger = logging.getLogger(__name__)


class PositionCalculator:
    """Calculates element positions and offsets."""

    @classmethod
    def get_position_type(cls, node: DOMNode) -> str:
        """
        Get CSS position type.

        Args:
            node: DOM node

        Returns:
            Position type: 'static', 'relative', 'absolute', 'fixed', 'sticky'
        """
        return node.computed_styles.get('position', 'static')

    @classmethod
    def is_static(cls, node: DOMNode) -> bool:
        """Check if element has static positioning."""
        return cls.get_position_type(node) == 'static'

    @classmethod
    def is_relative(cls, node: DOMNode) -> bool:
        """Check if element has relative positioning."""
        return cls.get_position_type(node) == 'relative'

    @classmethod
    def is_absolute(cls, node: DOMNode) -> bool:
        """Check if element has absolute positioning."""
        return cls.get_position_type(node) == 'absolute'

    @classmethod
    def is_fixed(cls, node: DOMNode) -> bool:
        """Check if element has fixed positioning."""
        return cls.get_position_type(node) == 'fixed'

    @classmethod
    def get_offsets(cls, node: DOMNode) -> Dict[str, Optional[float]]:
        """
        Get position offsets (top, right, bottom, left).

        Args:
            node: DOM node

        Returns:
            Dictionary with offset values in pt (None for auto)
        """
        offsets = {}

        for prop in ['top', 'right', 'bottom', 'left']:
            value = node.computed_styles.get(prop, 'auto')

            if value == 'auto' or not value:
                offsets[prop] = None
            else:
                try:
                    offsets[prop] = UnitConverter.to_pt(value)
                except:
                    offsets[prop] = None

        return offsets

    @classmethod
    def get_float_value(cls, node: DOMNode) -> str:
        """
        Get CSS float value.

        Args:
            node: DOM node

        Returns:
            Float value: 'none', 'left', 'right'
        """
        return node.computed_styles.get('float', 'none')

    @classmethod
    def is_floated(cls, node: DOMNode) -> bool:
        """
        Check if element is floated.

        Args:
            node: DOM node

        Returns:
            True if element has float left or right
        """
        return cls.get_float_value(node) in ('left', 'right')

    @classmethod
    def should_warn_absolute_position(cls, node: DOMNode) -> bool:
        """
        Check if we should warn about absolute positioning.

        Word doesn't support absolute positioning well, so we warn
        when converting elements with non-static positioning.

        Args:
            node: DOM node

        Returns:
            True if we should warn
        """
        if cls.is_absolute(node) or cls.is_fixed(node):
            logger.warning(
                f"Element '{node.tag}' has {cls.get_position_type(node)} positioning. "
                "This will be converted to normal flow layout in Word."
            )
            return True

        if cls.is_floated(node):
            logger.warning(
                f"Element '{node.tag}' is floated. "
                "Float layout may not be preserved accurately in Word."
            )
            return True

        return False
