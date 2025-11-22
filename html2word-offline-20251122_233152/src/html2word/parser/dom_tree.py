"""
DOM tree data structures.

Defines the DOM node and tree structures for representing parsed HTML.
"""

from typing import Optional, List, Dict, Any
from enum import Enum


class NodeType(Enum):
    """Type of DOM node."""
    ELEMENT = "element"
    TEXT = "text"
    COMMENT = "comment"


class DOMNode:
    """Represents a node in the DOM tree."""

    def __init__(
        self,
        node_type: NodeType,
        tag: Optional[str] = None,
        text: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
        parent: Optional['DOMNode'] = None
    ):
        """
        Initialize a DOM node.

        Args:
            node_type: Type of node
            tag: HTML tag name (for element nodes)
            text: Text content (for text nodes)
            attributes: HTML attributes
            parent: Parent node
        """
        self.node_type = node_type
        self.tag = tag.lower() if tag else None
        self.text = text
        self.attributes = attributes or {}
        self.parent = parent
        self.children: List[DOMNode] = []

        # Computed properties
        self.inline_styles: Dict[str, str] = {}  # Parsed from style attribute
        self.computed_styles: Dict[str, Any] = {}  # Final computed styles
        self.layout_info: Dict[str, Any] = {}  # Layout information

    @property
    def is_element(self) -> bool:
        """Check if this is an element node."""
        return self.node_type == NodeType.ELEMENT

    @property
    def is_text(self) -> bool:
        """Check if this is a text node."""
        return self.node_type == NodeType.TEXT

    @property
    def is_block_level(self) -> bool:
        """Check if this is a block-level element."""
        block_elements = {
            'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'table', 'tr', 'td', 'th',
            'blockquote', 'pre', 'hr', 'form', 'fieldset',
            'address', 'article', 'aside', 'footer', 'header',
            'main', 'nav', 'section'
        }
        return self.tag in block_elements if self.tag else False

    @property
    def is_inline(self) -> bool:
        """Check if this is an inline element."""
        return not self.is_block_level and self.is_element

    @property
    def display(self) -> str:
        """Get the display type of the element."""
        if self.is_text:
            return 'inline'

        # Check computed styles first
        if 'display' in self.computed_styles:
            return self.computed_styles['display']

        # Default display based on element type
        if self.tag == 'table':
            return 'table'
        elif self.tag == 'tr':
            return 'table-row'
        elif self.tag in ('td', 'th'):
            return 'table-cell'
        elif self.tag in ('ul', 'ol'):
            return 'list'
        elif self.tag == 'li':
            return 'list-item'
        elif self.is_block_level:
            return 'block'
        else:
            return 'inline'

    def add_child(self, child: 'DOMNode'):
        """Add a child node."""
        child.parent = self
        self.children.append(child)

    def get_attribute(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get an HTML attribute value."""
        return self.attributes.get(name, default)

    def has_children(self) -> bool:
        """Check if node has children."""
        return len(self.children) > 0

    def get_descendants(self) -> List['DOMNode']:
        """Get all descendant nodes (depth-first)."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_text_content(self) -> str:
        """Get all text content recursively."""
        if self.is_text:
            return self.text or ""

        text_parts = []
        for child in self.children:
            text_parts.append(child.get_text_content())
        return "".join(text_parts)

    def __repr__(self) -> str:
        """String representation of the node."""
        if self.is_text:
            text_preview = self.text[:30] + "..." if self.text and len(self.text) > 30 else self.text
            return f"DOMNode(TEXT: {text_preview!r})"
        else:
            attrs = ", ".join([f"{k}={v!r}" for k, v in list(self.attributes.items())[:2]])
            return f"DOMNode({self.tag}, {len(self.children)} children, {attrs})"


class DOMTree:
    """Represents the complete DOM tree."""

    def __init__(self, root: DOMNode):
        """
        Initialize DOM tree.

        Args:
            root: Root node of the tree
        """
        self.root = root

    def traverse(self, callback, node: Optional[DOMNode] = None):
        """
        Traverse the tree depth-first and call callback on each node.

        Args:
            callback: Function to call on each node
            node: Starting node (defaults to root)
        """
        if node is None:
            node = self.root

        callback(node)
        for child in node.children:
            self.traverse(callback, child)

    def find_by_tag(self, tag: str, node: Optional[DOMNode] = None) -> List[DOMNode]:
        """
        Find all nodes with a specific tag.

        Args:
            tag: HTML tag name
            node: Starting node (defaults to root)

        Returns:
            List of matching nodes
        """
        if node is None:
            node = self.root

        results = []
        if node.tag == tag.lower():
            results.append(node)

        for child in node.children:
            results.extend(self.find_by_tag(tag, child))

        return results

    def find_by_attribute(
        self,
        attr_name: str,
        attr_value: Optional[str] = None,
        node: Optional[DOMNode] = None
    ) -> List[DOMNode]:
        """
        Find all nodes with a specific attribute.

        Args:
            attr_name: Attribute name
            attr_value: Attribute value (optional, matches any value if None)
            node: Starting node (defaults to root)

        Returns:
            List of matching nodes
        """
        if node is None:
            node = self.root

        results = []
        if attr_name in node.attributes:
            if attr_value is None or node.attributes[attr_name] == attr_value:
                results.append(node)

        for child in node.children:
            results.extend(self.find_by_attribute(attr_name, attr_value, child))

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the tree.

        Returns:
            Dict with statistics
        """
        total_nodes = 0
        element_nodes = 0
        text_nodes = 0
        tag_counts: Dict[str, int] = {}

        def count_node(node: DOMNode):
            nonlocal total_nodes, element_nodes, text_nodes
            total_nodes += 1

            if node.is_element:
                element_nodes += 1
                if node.tag:
                    tag_counts[node.tag] = tag_counts.get(node.tag, 0) + 1
            elif node.is_text:
                text_nodes += 1

        self.traverse(count_node)

        return {
            'total_nodes': total_nodes,
            'element_nodes': element_nodes,
            'text_nodes': text_nodes,
            'tag_counts': tag_counts
        }

    def __repr__(self) -> str:
        """String representation of the tree."""
        stats = self.get_stats()
        return f"DOMTree({stats['total_nodes']} nodes, root: {self.root.tag})"
