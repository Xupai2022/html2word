"""
CSS style inheritance handling.

Implements CSS property inheritance from parent to child elements.
"""

import logging
from typing import Dict, Any, Optional
from html2word.parser.dom_tree import DOMNode

logger = logging.getLogger(__name__)


class StyleInheritance:
    """Handles CSS style inheritance."""

    # CSS properties that inherit by default
    INHERITED_PROPERTIES = {
        # Font properties
        'font-family',
        'font-size',
        'font-style',
        'font-weight',
        'font-variant',
        'font',
        # Text properties
        'color',
        'line-height',
        'letter-spacing',
        'word-spacing',
        'text-align',
        'text-indent',
        'text-transform',
        'white-space',
        'direction',
        # List properties
        'list-style-type',
        'list-style-position',
        'list-style-image',
        'list-style',
        # Table properties
        'border-collapse',
        'border-spacing',
        'caption-side',
        'empty-cells',
        # Other
        'visibility',
        'cursor',
        'quotes',
    }

    # CSS properties that do NOT inherit
    NON_INHERITED_PROPERTIES = {
        # Box model
        'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'border', 'border-width', 'border-style', 'border-color',
        'border-top', 'border-right', 'border-bottom', 'border-left',
        'width', 'height', 'max-width', 'max-height', 'min-width', 'min-height',
        # Background
        'background', 'background-color', 'background-image', 'background-position',
        'background-repeat', 'background-attachment',
        # Positioning
        'position', 'top', 'right', 'bottom', 'left',
        'float', 'clear', 'z-index',
        # Display
        'display', 'overflow', 'clip',
        # Other
        'vertical-align',
        'text-decoration',
    }

    @classmethod
    def is_inherited(cls, property_name: str) -> bool:
        """
        Check if a CSS property is inherited.

        Args:
            property_name: CSS property name

        Returns:
            True if property is inherited by default
        """
        return property_name in cls.INHERITED_PROPERTIES

    @classmethod
    def compute_inherited_styles(
        cls,
        node: DOMNode,
        parent_computed_styles: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compute inherited styles for a node.

        Args:
            node: DOM node
            parent_computed_styles: Computed styles from parent node

        Returns:
            Dictionary of inherited styles
        """
        inherited = {}

        if parent_computed_styles is None:
            parent_computed_styles = {}

        # Inherit properties from parent
        for prop in cls.INHERITED_PROPERTIES:
            # If node has explicit value, use it
            if prop in node.inline_styles:
                inherited[prop] = node.inline_styles[prop]
            # Otherwise, inherit from parent
            elif prop in parent_computed_styles:
                inherited[prop] = parent_computed_styles[prop]

        return inherited

    @classmethod
    def apply_inheritance(
        cls,
        tree_root: DOMNode,
        initial_styles: Optional[Dict[str, Any]] = None
    ):
        """
        Apply style inheritance to entire DOM tree.

        Args:
            tree_root: Root node of DOM tree
            initial_styles: Initial styles for root (e.g., from body element)
        """
        if initial_styles is None:
            initial_styles = {}

        def process_node(node: DOMNode, parent_styles: Dict[str, Any]):
            """Process a single node and its children."""
            if node.is_element:
                # Start with inherited styles from parent
                computed = cls.compute_inherited_styles(node, parent_styles)

                # Add non-inherited properties from inline styles
                for prop, value in node.inline_styles.items():
                    computed[prop] = value

                # Store computed styles
                node.computed_styles = computed

                # Process children with this node's computed styles
                for child in node.children:
                    process_node(child, computed)

            elif node.is_text:
                # Text nodes inherit all styles from parent
                node.computed_styles = parent_styles.copy()

        # Start processing from root
        process_node(tree_root, initial_styles)
        logger.debug(f"Applied style inheritance to tree")

    @classmethod
    def get_default_inherited_styles(cls) -> Dict[str, str]:
        """
        Get default values for inherited properties.

        Returns:
            Dictionary of default property values

        Note:
            Font properties (font-family, font-size) are NOT included here.
            They should be defined in HTML/CSS only, not hardcoded.
        """
        return {
            # Font properties (font-family and font-size removed - use HTML/CSS values)
            'font-style': 'normal',
            'font-weight': 'normal',
            'font-variant': 'normal',
            # Text properties
            'color': '#000000',
            'line-height': '1.2',
            'letter-spacing': 'normal',
            'word-spacing': 'normal',
            'text-align': 'left',
            'text-indent': '0',
            'text-transform': 'none',
            'white-space': 'normal',
            'direction': 'ltr',
            # List properties
            'list-style-type': 'disc',
            'list-style-position': 'outside',
            # Table properties
            'border-collapse': 'separate',
            'border-spacing': '2px',
            # Other
            'visibility': 'visible',
        }
