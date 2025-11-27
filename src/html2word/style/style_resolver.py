"""
Style resolver - main style computation engine.

Coordinates style inheritance, normalization, and final computation.
"""

import logging
from typing import Dict, Any, Optional
from html2word.parser.dom_tree import DOMNode, DOMTree
from html2word.style.inheritance import StyleInheritance
from html2word.style.style_normalizer import StyleNormalizer
from html2word.style.box_model import BoxModel

logger = logging.getLogger(__name__)


class StyleResolver:
    """Resolves and computes final styles for DOM nodes."""

    def __init__(self):
        """Initialize style resolver."""
        self.inheritance = StyleInheritance()
        self.normalizer = StyleNormalizer()

    def resolve_styles(self, tree: DOMTree):
        """
        Resolve styles for entire DOM tree.

        This is the main entry point that orchestrates:
        1. Style inheritance
        2. Style normalization
        3. Box model calculation

        Args:
            tree: DOM tree
        """
        logger.info("Starting style resolution")

        # Get initial styles from body or root
        initial_styles = self._get_initial_styles(tree)

        # Step 1: Apply inheritance
        self.inheritance.apply_inheritance(tree.root, initial_styles)
        logger.debug("Applied style inheritance")

        # Step 2: Normalize styles
        self._normalize_tree_styles(tree.root)
        logger.debug("Normalized styles")

        # Step 2.5: Fix table border specificity issues
        self._fix_table_borders(tree.root)
        logger.debug("Fixed table border styles")

        # Step 3: Calculate box models
        self._calculate_box_models(tree.root)
        logger.debug("Calculated box models")

        logger.info("Style resolution complete")

    def _get_initial_styles(self, tree: DOMTree) -> Dict[str, str]:
        """
        Get initial styles for the root element.

        Args:
            tree: DOM tree

        Returns:
            Dictionary of initial styles
        """
        # Start with default inherited styles
        initial = self.inheritance.get_default_inherited_styles()

        # Check for body element styles
        body_nodes = tree.find_by_tag('body')
        if body_nodes:
            body_node = body_nodes[0]
            # Merge body inline styles
            initial.update(body_node.inline_styles)

        return initial

    def _normalize_tree_styles(self, node: DOMNode, parent_context: Optional[Dict[str, Any]] = None):
        """
        Normalize styles for entire tree.

        Args:
            node: Current node
            parent_context: Context from parent node
        """
        if not node.is_element:
            return

        # Build context for this node
        context = self._build_context(node, parent_context)

        # Normalize computed styles
        if node.computed_styles:
            normalized = self.normalizer.normalize_styles(node.computed_styles, context)
            node.computed_styles.update(normalized)

        # Process children
        for child in node.children:
            self._normalize_tree_styles(child, context)

    def _build_context(
        self,
        node: DOMNode,
        parent_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build context for style computation.

        Args:
            node: DOM node
            parent_context: Context from parent

        Returns:
            Context dictionary
        """
        context = parent_context.copy() if parent_context else {}

        # Update font size for em/rem calculations
        if 'font-size' in node.computed_styles:
            font_size_str = node.computed_styles['font-size']
            try:
                # Get numeric value
                from html2word.utils.units import UnitConverter
                font_size_pt = UnitConverter.to_pt(font_size_str, parent_context)
                context['parent_font_size'] = font_size_pt
            except:
                pass

        # Set root font size if this is the root element
        if node.parent is None and 'parent_font_size' in context:
            context['root_font_size'] = context['parent_font_size']

        return context

    def _fix_table_borders(self, node: DOMNode):
        """
        Fix table border styles to prevent incorrect inheritance.

        Specifically fixes the issue where 3px border-left styles from
        .common-left-border or .detail-content__name are incorrectly
        applied to table cells.

        Args:
            node: DOM node to process
        """
        if not node.is_element:
            return

        # Check if this is a table cell (td or th)
        # Use node.tag for element name
        node_tag = getattr(node, 'tag', '')
        if node_tag in ['td', 'th']:
            # Check for incorrectly applied 3px borders
            if node.computed_styles:
                # Log current border values for debugging
                border_left = node.computed_styles.get('border-left-width', '')
                border_width = node.computed_styles.get('border-width', '')
                if border_left or border_width:
                    logger.debug(f"Checking {node_tag} borders: border-left-width={border_left}, border-width={border_width}")
                # Fix border-left if it's 3px (should be 1px for table cells)
                if 'border-left-width' in node.computed_styles:
                    value = str(node.computed_styles.get('border-left-width', '')).strip()
                    # If it's 3px or 3.0px, it's likely incorrectly inherited
                    if value in ['3px', '3.0px']:
                        # Reset to default table border (1px)
                        node.computed_styles['border-left-width'] = '1px'
                        logger.debug(f"Fixed table cell border-left from {value} to 1px")

                # Also check the general border-width property
                if 'border-width' in node.computed_styles:
                    value = str(node.computed_styles.get('border-width', '')).strip()
                    # If any part is 3px, fix it
                    if '3px' in value or '3.0px' in value:
                        # Replace 3px with 1px
                        fixed_value = value.replace('3.0px', '1px').replace('3px', '1px')
                        node.computed_styles['border-width'] = fixed_value
                        logger.debug(f"Fixed table cell border-width from {value} to {fixed_value}")

        # Recursively process children
        for child in node.children:
            self._fix_table_borders(child)

    def _calculate_box_models(self, node: DOMNode):
        """
        Calculate box models for entire tree.

        Args:
            node: Current node
        """
        if not node.is_element:
            return

        # Calculate box model for this node
        try:
            box_model = BoxModel(node)
            node.layout_info['box_model'] = box_model
        except Exception as e:
            logger.warning(f"Error calculating box model for {node.tag}: {e}")

        # Process children
        for child in node.children:
            self._calculate_box_models(child)

    def get_computed_style(
        self,
        node: DOMNode,
        property_name: str,
        default: Any = None
    ) -> Any:
        """
        Get a computed style value for a node.

        Args:
            node: DOM node
            property_name: CSS property name
            default: Default value if property not found

        Returns:
            Computed property value
        """
        return node.computed_styles.get(property_name, default)

    def get_box_model(self, node: DOMNode) -> Optional[BoxModel]:
        """
        Get box model for a node.

        Args:
            node: DOM node

        Returns:
            BoxModel object or None
        """
        return node.layout_info.get('box_model')
