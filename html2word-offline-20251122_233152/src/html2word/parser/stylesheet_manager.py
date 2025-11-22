"""
Stylesheet manager for CSS rules.

Manages CSS rules and applies them to DOM nodes with proper cascading and specificity.
"""

import logging
from typing import Dict, List, Tuple
from html2word.parser.dom_tree import DOMNode
from html2word.parser.css_parser import CSSParser
from html2word.parser.css_selector import CSSSelector

logger = logging.getLogger(__name__)


class StylesheetManager:
    """Manages CSS rules and applies them to DOM nodes."""

    def __init__(self):
        """Initialize stylesheet manager."""
        self.rules: List[Tuple[str, Dict[str, str], Tuple[int, int, int]]] = []
        self.css_parser = CSSParser()
        self.css_selector = CSSSelector()

    def add_stylesheet(self, css_content: str):
        """
        Add CSS rules from a stylesheet.

        Args:
            css_content: CSS stylesheet content
        """
        parsed_rules = self.css_parser.parse_stylesheet(css_content)

        for selector, styles in parsed_rules:
            specificity = self.css_selector.calculate_specificity(selector)
            self.rules.append((selector, styles, specificity))

        logger.debug(f"Added {len(parsed_rules)} CSS rules from stylesheet")

    def apply_styles_to_node(self, node: DOMNode):
        """
        Apply matching CSS rules to a DOM node.

        This respects CSS cascading and specificity rules:
        - Styles are applied in order of specificity (low to high)
        - Inline styles have highest priority
        - Later rules with same specificity override earlier ones

        Args:
            node: DOM node to apply styles to
        """
        if not node.is_element:
            return

        # Collect matching rules with their specificity
        matching_rules: List[Tuple[Dict[str, str], Tuple[int, int, int]]] = []

        for selector, styles, specificity in self.rules:
            if self.css_selector.matches(selector, node):
                matching_rules.append((styles, specificity))

        if not matching_rules:
            return

        # Sort by specificity (low to high)
        matching_rules.sort(key=lambda x: x[1])

        # Apply styles in order of specificity
        # Start with an empty dict for CSS rule styles
        css_styles = {}

        for styles, specificity in matching_rules:
            # Later rules with same/higher specificity override earlier ones
            css_styles.update(styles)

        # Merge CSS styles into node's inline styles
        # Inline styles have precedence, so only add CSS styles that aren't already set
        for prop, value in css_styles.items():
            if prop not in node.inline_styles:
                node.inline_styles[prop] = value

        logger.debug(f"Applied {len(matching_rules)} CSS rules to {node.tag}")

    def apply_styles_to_tree(self, node: DOMNode, _depth: int = 0, _node_count: int = 0):
        """
        Recursively apply CSS rules to entire DOM tree.

        Args:
            node: Root node of tree
            _depth: Internal - current recursion depth
            _node_count: Internal - current node count for progress logging
        """
        # Log progress for large trees
        if _depth == 0:
            logger.info("Applying CSS rules to DOM tree...")
            _node_count = [0]  # Use list to make it mutable in nested calls

        if isinstance(_node_count, list):
            _node_count[0] += 1
            if _node_count[0] % 500 == 0:
                logger.info(f"Applied styles to {_node_count[0]} DOM nodes...")

        self.apply_styles_to_node(node)

        # Recursively process children
        for child in node.children:
            self.apply_styles_to_tree(child, _depth + 1, _node_count)

        if _depth == 0 and isinstance(_node_count, list):
            logger.info(f"Completed applying styles to {_node_count[0]} DOM nodes")

    def clear(self):
        """Clear all CSS rules."""
        self.rules.clear()

    def get_rule_count(self) -> int:
        """
        Get the number of CSS rules.

        Returns:
            Number of rules
        """
        return len(self.rules)
