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
