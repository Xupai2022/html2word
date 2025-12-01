"""
CSS selector matcher.

Matches CSS selectors against DOM nodes and calculates specificity.
"""

import re
import logging
from typing import Optional, Tuple
from html2word.parser.dom_tree import DOMNode

logger = logging.getLogger(__name__)


class CSSSelector:
    """CSS selector matcher with specificity calculation."""

    # 预编译正则表达式 (类级别，只编译一次)
    _TAG_PATTERN = re.compile(r'^([a-zA-Z0-9-]*)')
    _ID_PATTERN = re.compile(r'#([a-zA-Z0-9_-]+)')
    _CLASS_PATTERN = re.compile(r'\.([a-zA-Z0-9_-]+)')
    _ATTR_PATTERN = re.compile(r'\[([a-zA-Z0-9_-]+)(?:([~|^$*]?=)["\']?([^"\'\]]+)["\']?)?\]')
    _PSEUDO_PATTERN = re.compile(r':([a-zA-Z0-9_-]+)(?:\(([^)]+)\))?')

    # 用于specificity计算的正则
    _SPECIFICITY_ID_PATTERN = re.compile(r'#[a-zA-Z0-9_-]+')
    _SPECIFICITY_CLASS_PATTERN = re.compile(r'\.[a-zA-Z0-9_-]+')
    _SPECIFICITY_ATTR_PATTERN = re.compile(r'\[[^\]]+\]')
    _SPECIFICITY_PSEUDO_PATTERN = re.compile(r':[a-zA-Z0-9_-]+(?:\([^)]+\))?')
    _SPECIFICITY_TAG_PATTERN = re.compile(r'\b[a-zA-Z][a-zA-Z0-9-]*\b')
    _COMBINATOR_PATTERN = re.compile(r'\s*[>+~]\s*')

    @classmethod
    def matches(cls, selector: str, node: DOMNode) -> bool:
        """
        Check if a CSS selector matches a DOM node.

        Args:
            selector: CSS selector string
            node: DOM node to match against

        Returns:
            True if selector matches node

        Examples:
            matches(".foo", node_with_class_foo) -> True
            matches("#bar", node_with_id_bar) -> True
            matches("div", div_node) -> True
            matches("table.basic-table", table_node_with_class) -> True
        """
        if not node.is_element:
            return False

        # Handle multiple selectors separated by comma
        if ',' in selector:
            selectors = [s.strip() for s in selector.split(',')]
            return any(cls.matches(s, node) for s in selectors)

        # Normalize selector
        selector = selector.strip()

        # Handle descendant selectors (space)
        if ' ' in selector:
            return cls._matches_descendant(selector, node)

        # Handle child selectors (>)
        if '>' in selector:
            return cls._matches_child(selector, node)

        # Handle adjacent sibling selectors (+)
        if '+' in selector:
            return cls._matches_adjacent(selector, node)

        # Handle general sibling selectors (~)
        if '~' in selector:
            return cls._matches_sibling(selector, node)

        # Simple selector matching
        return cls._matches_simple(selector, node)

    @classmethod
    def _matches_simple(cls, selector: str, node: DOMNode) -> bool:
        """
        Match a simple selector (tag, class, id, or combination).

        Args:
            selector: Simple CSS selector
            node: DOM node

        Returns:
            True if matches
        """
        # Universal selector
        if selector == '*':
            return True

        # Parse selector into components using pre-compiled patterns
        # Format: tag#id.class1.class2[attr=value]:pseudo

        # Extract tag
        tag_match = cls._TAG_PATTERN.match(selector)
        if tag_match:
            required_tag = tag_match.group(1)
            if required_tag and node.tag != required_tag:
                return False

        # Extract and check ID
        id_matches = cls._ID_PATTERN.findall(selector)
        if id_matches:
            node_id = node.attributes.get('id', '')
            if node_id not in id_matches:
                return False

        # Extract and check classes
        class_matches = cls._CLASS_PATTERN.findall(selector)
        if class_matches:
            node_classes = node.attributes.get('class', '')
            if isinstance(node_classes, list):
                node_classes = ' '.join(node_classes)
            node_class_list = node_classes.split() if node_classes else []

            for required_class in class_matches:
                if required_class not in node_class_list:
                    return False

        # Extract and check attributes
        attr_matches = cls._ATTR_PATTERN.findall(selector)
        for attr_match in attr_matches:
            attr_name = attr_match[0]
            operator = attr_match[1] if len(attr_match) > 1 else None
            attr_value = attr_match[2] if len(attr_match) > 2 else None

            if attr_name not in node.attributes:
                return False

            if operator and attr_value:
                node_attr_value = str(node.attributes[attr_name])

                if operator == '=':
                    if node_attr_value != attr_value:
                        return False
                elif operator == '~=':  # Word match
                    if attr_value not in node_attr_value.split():
                        return False
                elif operator == '|=':  # Prefix match with hyphen
                    if not (node_attr_value == attr_value or node_attr_value.startswith(attr_value + '-')):
                        return False
                elif operator == '^=':  # Starts with
                    if not node_attr_value.startswith(attr_value):
                        return False
                elif operator == '$=':  # Ends with
                    if not node_attr_value.endswith(attr_value):
                        return False
                elif operator == '*=':  # Contains
                    if attr_value not in node_attr_value:
                        return False

        # Handle pseudo-classes (simplified support)
        pseudo_matches = cls._PSEUDO_PATTERN.findall(selector)
        for pseudo_match in pseudo_matches:
            pseudo_class = pseudo_match[0]

            if pseudo_class in ('first-child',):
                if node.parent and node.parent.children:
                    # For LightweightNode in parallel mode, compare paths instead of objects
                    if hasattr(node, 'path') and hasattr(node.parent.children[0], 'path'):
                        if node.parent.children[0].path != node.path:
                            return False
                    else:
                        if node.parent.children[0] != node:
                            return False
            elif pseudo_class in ('last-child',):
                if node.parent and node.parent.children:
                    # For LightweightNode in parallel mode, compare paths instead of objects
                    if hasattr(node, 'path') and hasattr(node.parent.children[-1], 'path'):
                        if node.parent.children[-1].path != node.path:
                            return False
                    else:
                        if node.parent.children[-1] != node:
                            return False
            elif pseudo_class in ('nth-child',):
                # Simplified nth-child support
                formula = pseudo_match[1] if len(pseudo_match) > 1 else None
                if formula:
                    if formula == 'even':
                        if node.parent:
                            index = node.parent.children.index(node)
                            if (index + 1) % 2 != 0:
                                return False
                    elif formula == 'odd':
                        if node.parent:
                            index = node.parent.children.index(node)
                            if (index + 1) % 2 == 0:
                                return False

        return True

    @classmethod
    def _matches_descendant(cls, selector: str, node: DOMNode) -> bool:
        """
        Match descendant selector (space).

        Args:
            selector: Descendant selector (e.g., "div p")
            node: DOM node

        Returns:
            True if matches
        """
        # Split into parts
        parts = selector.split()
        if len(parts) < 2:
            return False

        # The rightmost part must match the current node
        rightmost = parts[-1]
        if not cls._matches_simple(rightmost, node):
            return False

        # Check if any ancestor matches the rest
        remaining = ' '.join(parts[:-1])
        current = node.parent

        while current is not None:
            if cls.matches(remaining, current):
                return True
            current = current.parent

        return False

    @classmethod
    def _matches_child(cls, selector: str, node: DOMNode) -> bool:
        """
        Match child selector (>).

        Args:
            selector: Child selector (e.g., "div > p")
            node: DOM node

        Returns:
            True if matches
        """
        parts = selector.split('>')
        if len(parts) < 2:
            return False

        # The rightmost part must match the current node
        rightmost = parts[-1].strip()
        if not cls._matches_simple(rightmost, node):
            return False

        # The parent must match the rest
        if node.parent is None:
            return False

        remaining = '>'.join(parts[:-1]).strip()
        return cls.matches(remaining, node.parent)

    @classmethod
    def _matches_adjacent(cls, selector: str, node: DOMNode) -> bool:
        """
        Match adjacent sibling selector (+).

        Args:
            selector: Adjacent selector (e.g., "h1 + p")
            node: DOM node

        Returns:
            True if matches
        """
        parts = selector.split('+')
        if len(parts) < 2:
            return False

        # The rightmost part must match the current node
        rightmost = parts[-1].strip()
        if not cls._matches_simple(rightmost, node):
            return False

        # Find previous sibling
        if node.parent is None:
            return False

        siblings = node.parent.children
        try:
            index = siblings.index(node)
            if index > 0:
                prev_sibling = siblings[index - 1]
                remaining = '+'.join(parts[:-1]).strip()
                return cls.matches(remaining, prev_sibling)
        except (ValueError, IndexError):
            pass

        return False

    @classmethod
    def _matches_sibling(cls, selector: str, node: DOMNode) -> bool:
        """
        Match general sibling selector (~).

        Args:
            selector: Sibling selector (e.g., "h1 ~ p")
            node: DOM node

        Returns:
            True if matches
        """
        parts = selector.split('~')
        if len(parts) < 2:
            return False

        # The rightmost part must match the current node
        rightmost = parts[-1].strip()
        if not cls._matches_simple(rightmost, node):
            return False

        # Find any previous sibling that matches
        if node.parent is None:
            return False

        siblings = node.parent.children
        try:
            index = siblings.index(node)
            for i in range(index):
                sibling = siblings[i]
                remaining = '~'.join(parts[:-1]).strip()
                if cls.matches(remaining, sibling):
                    return True
        except ValueError:
            pass

        return False

    @classmethod
    def calculate_specificity(cls, selector: str) -> Tuple[int, int, int]:
        """
        Calculate CSS specificity of a selector.

        Returns a tuple of (a, b, c) where:
        - a: number of ID selectors
        - b: number of class selectors, attribute selectors, and pseudo-classes
        - c: number of type selectors and pseudo-elements

        Args:
            selector: CSS selector string

        Returns:
            Tuple of (id_count, class_count, tag_count)

        Examples:
            calculate_specificity("div") -> (0, 0, 1)
            calculate_specificity(".foo") -> (0, 1, 0)
            calculate_specificity("#bar") -> (1, 0, 0)
            calculate_specificity("div.foo#bar") -> (1, 1, 1)
        """
        # Handle multiple selectors (use the highest specificity)
        if ',' in selector:
            selectors = [s.strip() for s in selector.split(',')]
            specificities = [cls.calculate_specificity(s) for s in selectors]
            return max(specificities)

        # For complex selectors, calculate based on all components
        # Remove combinators but keep the components
        selector_clean = cls._COMBINATOR_PATTERN.sub(' ', selector)

        id_count = len(cls._SPECIFICITY_ID_PATTERN.findall(selector_clean))
        class_count = len(cls._SPECIFICITY_CLASS_PATTERN.findall(selector_clean))
        attr_count = len(cls._SPECIFICITY_ATTR_PATTERN.findall(selector_clean))
        pseudo_class_count = len(cls._SPECIFICITY_PSEUDO_PATTERN.findall(selector_clean))

        # Count type selectors (tags)
        # Remove IDs, classes, attributes, and pseudo-classes first
        tag_selector = selector_clean
        tag_selector = cls._SPECIFICITY_ID_PATTERN.sub('', tag_selector)
        tag_selector = cls._SPECIFICITY_CLASS_PATTERN.sub('', tag_selector)
        tag_selector = cls._SPECIFICITY_ATTR_PATTERN.sub('', tag_selector)
        tag_selector = cls._SPECIFICITY_PSEUDO_PATTERN.sub('', tag_selector)

        # Count remaining tag names
        tags = cls._SPECIFICITY_TAG_PATTERN.findall(tag_selector)
        tag_count = len(tags)

        # b = class + attribute + pseudo-class
        b_count = class_count + attr_count + pseudo_class_count

        return (id_count, b_count, tag_count)

    @classmethod
    def compare_specificity(cls, spec1: Tuple[int, int, int], spec2: Tuple[int, int, int]) -> int:
        """
        Compare two specificities.

        Args:
            spec1: First specificity tuple
            spec2: Second specificity tuple

        Returns:
            1 if spec1 > spec2, -1 if spec1 < spec2, 0 if equal
        """
        if spec1[0] > spec2[0]:
            return 1
        elif spec1[0] < spec2[0]:
            return -1

        if spec1[1] > spec2[1]:
            return 1
        elif spec1[1] < spec2[1]:
            return -1

        if spec1[2] > spec2[2]:
            return 1
        elif spec1[2] < spec2[2]:
            return -1

        return 0
