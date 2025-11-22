"""
Inline layout computation.

Handles layout calculations for inline-level elements.
"""

import logging
from typing import List
from html2word.parser.dom_tree import DOMNode

logger = logging.getLogger(__name__)


class InlineLayout:
    """Handles inline layout computation."""

    @classmethod
    def is_replaced_element(cls, node: DOMNode) -> bool:
        """
        Check if element is a replaced element (img, input, etc.).

        Args:
            node: DOM node

        Returns:
            True if element is replaced
        """
        return node.tag in ('img', 'input', 'textarea', 'select', 'video', 'canvas', 'iframe')

    @classmethod
    def compute_baseline_alignment(cls, node: DOMNode) -> str:
        """
        Compute baseline alignment for inline element.

        Args:
            node: Inline element node

        Returns:
            Alignment value: 'baseline', 'top', 'middle', 'bottom', etc.
        """
        return node.computed_styles.get('vertical-align', 'baseline')

    @classmethod
    def get_inline_runs(cls, parent: DOMNode) -> List[List[DOMNode]]:
        """
        Group inline children into runs for text layout.

        A run is a sequence of inline/text nodes that should be laid out together.

        Args:
            parent: Parent node

        Returns:
            List of runs, where each run is a list of nodes
        """
        runs = []
        current_run = []

        for child in parent.children:
            if child.is_text or child.is_inline:
                current_run.append(child)
            else:
                # Block element breaks the run
                if current_run:
                    runs.append(current_run)
                    current_run = []

        # Add final run
        if current_run:
            runs.append(current_run)

        return runs

    @classmethod
    def should_preserve_whitespace(cls, node: DOMNode) -> bool:
        """
        Check if whitespace should be preserved.

        Args:
            node: DOM node

        Returns:
            True if white-space property preserves spaces
        """
        white_space = node.computed_styles.get('white-space', 'normal')
        return white_space in ('pre', 'pre-wrap', 'pre-line')

    @classmethod
    def normalize_whitespace(cls, text: str, preserve: bool = False) -> str:
        """
        Normalize whitespace in text according to CSS rules.

        Args:
            text: Input text
            preserve: Whether to preserve whitespace

        Returns:
            Normalized text
        """
        if preserve:
            return text

        # Collapse whitespace
        import re
        # Replace multiple spaces/tabs/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        return text
