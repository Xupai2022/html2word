"""
Flow layout computation.

For HTML to Word conversion, we preserve the flow layout structure
and analyze element positioning within the document flow.
"""

import logging
from typing import List
from html2word.parser.dom_tree import DOMNode

logger = logging.getLogger(__name__)


class FlowLayout:
    """Handles flow layout computation and analysis."""

    @classmethod
    def is_block_container(cls, node: DOMNode) -> bool:
        """Check if node is a block container."""
        return node.display in ('block', 'list-item', 'table', 'table-row', 'table-cell')

    @classmethod
    def is_inline_container(cls, node: DOMNode) -> bool:
        """Check if node is an inline container."""
        return node.display == 'inline'

    @classmethod
    def contains_block_children(cls, node: DOMNode) -> bool:
        """Check if node contains any block-level children."""
        for child in node.children:
            if child.is_element and child.is_block_level:
                return True
        return False

    @classmethod
    def get_block_children(cls, node: DOMNode) -> List[DOMNode]:
        """Get all block-level children of a node."""
        return [child for child in node.children if child.is_element and child.is_block_level]

    @classmethod
    def get_inline_children(cls, node: DOMNode) -> List[DOMNode]:
        """Get all inline-level children of a node."""
        return [child for child in node.children if child.is_text or (child.is_element and child.is_inline)]

    @classmethod
    def get_flow_context(cls, node: DOMNode) -> str:
        """Determine the flow context type for a node."""
        if node.display == 'table':
            return 'table'
        elif node.display in ('table-row', 'table-cell'):
            return 'table'
        elif node.is_block_level:
            return 'block'
        else:
            return 'inline'
