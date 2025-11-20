"""
Base converter for HTML elements.

Provides common functionality for element converters.
"""

import logging
from typing import Optional
from html2word.parser.dom_tree import DOMNode

logger = logging.getLogger(__name__)


class BaseConverter:
    """Base class for element converters."""

    def __init__(self, document):
        """
        Initialize base converter.

        Args:
            document: python-docx Document object
        """
        self.document = document

    def convert_node(self, node: DOMNode) -> Optional[object]:
        """
        Convert a DOM node to Word element.

        Args:
            node: DOM node

        Returns:
            Word element or None
        """
        if node.is_text:
            return None

        # This is a placeholder - actual conversion is handled
        # by the DocumentBuilder which routes to specific builders
        return None
