"""
Block layout computation.

Handles layout calculations for block-level elements.
"""

import logging
from typing import Optional, Dict, Any
from html2word.parser.dom_tree import DOMNode

logger = logging.getLogger(__name__)


class BlockLayout:
    """Handles block layout computation."""

    @classmethod
    def compute_block_width(cls, node: DOMNode, container_width: Optional[float] = None) -> Optional[float]:
        """
        Compute the width of a block element.

        Args:
            node: Block element node
            container_width: Width of containing block

        Returns:
            Computed width in pt, or None for auto width
        """
        box_model = node.layout_info.get('box_model')
        if box_model is None:
            return None

        # If width is explicitly set
        if box_model.width is not None:
            return box_model.get_total_width()

        # Auto width: fill container minus margins
        if container_width is not None:
            horizontal_margin = box_model.margin.left + box_model.margin.right
            return container_width - horizontal_margin

        return None

    @classmethod
    def compute_vertical_margins(cls, node: DOMNode) -> Dict[str, float]:
        """
        Compute vertical margins with margin collapsing.

        Args:
            node: DOM node

        Returns:
            Dictionary with 'top' and 'bottom' margins in pt
        """
        box_model = node.layout_info.get('box_model')
        if box_model is None:
            return {'top': 0, 'bottom': 0}

        # For Word conversion, we don't implement full margin collapsing
        # as Word handles paragraph spacing differently
        return {
            'top': box_model.margin.top,
            'bottom': box_model.margin.bottom
        }

    @classmethod
    def should_clear_floats(cls, node: DOMNode) -> bool:
        """
        Check if element should clear floats.

        Args:
            node: DOM node

        Returns:
            True if element has clear property
        """
        clear_value = node.computed_styles.get('clear', 'none')
        return clear_value != 'none'

    @classmethod
    def is_positioned(cls, node: DOMNode) -> bool:
        """
        Check if element is positioned (not static).

        Args:
            node: DOM node

        Returns:
            True if position is not static
        """
        position = node.computed_styles.get('position', 'static')
        return position != 'static'

    @classmethod
    def get_stacking_context_level(cls, node: DOMNode) -> int:
        """
        Get z-index for stacking context.

        Args:
            node: DOM node

        Returns:
            Z-index value
        """
        z_index = node.computed_styles.get('z-index', 'auto')

        if z_index == 'auto':
            return 0

        try:
            return int(z_index)
        except (ValueError, TypeError):
            return 0
