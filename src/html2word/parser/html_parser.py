"""
HTML parser using BeautifulSoup.

Parses HTML documents and builds a DOM tree with inline style information.
"""

import logging
import os
from typing import Optional, Union
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
import yaml

from html2word.parser.dom_tree import DOMNode, DOMTree, NodeType
from html2word.parser.css_parser import CSSParser
from html2word.parser.stylesheet_manager import StylesheetManager

logger = logging.getLogger(__name__)


class HTMLParser:
    """Parser for HTML documents."""

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize HTML parser.

        Args:
            base_path: Base path for resolving relative paths
        """
        self.base_path = base_path or os.getcwd()
        self.css_parser = CSSParser()
        self.stylesheet_manager = StylesheetManager()
        self.default_styles = self._load_default_styles()

    def _load_default_styles(self) -> dict:
        """Load default HTML element styles from config."""
        try:
            # Get config path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            config_path = os.path.join(project_root, "config", "default_styles.yaml")

            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"Default styles config not found: {config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading default styles: {e}")
            return {}

    def _extract_stylesheets(self, soup):
        """
        Extract and parse CSS from <style> tags.

        Args:
            soup: BeautifulSoup object
        """
        # Find all <style> tags
        style_tags = soup.find_all('style')

        for style_tag in style_tags:
            css_content = style_tag.string
            if css_content:
                self.stylesheet_manager.add_stylesheet(css_content)
                logger.debug(f"Extracted CSS from <style> tag ({len(css_content)} characters)")

        logger.debug(f"Total CSS rules extracted: {self.stylesheet_manager.get_rule_count()}")

    def parse(self, html_content: Union[str, bytes], parser: str = "lxml") -> DOMTree:
        """
        Parse HTML content and build DOM tree.

        Args:
            html_content: HTML string or bytes
            parser: BeautifulSoup parser to use ('lxml', 'html.parser', etc.)

        Returns:
            DOMTree object
        """
        try:
            soup = BeautifulSoup(html_content, parser)
        except Exception as e:
            logger.error(f"Error parsing HTML with {parser}: {e}")
            # Fallback to html.parser
            soup = BeautifulSoup(html_content, "html.parser")

        # Clear previous stylesheet rules
        self.stylesheet_manager.clear()

        # Extract and parse <style> tags first
        self._extract_stylesheets(soup)

        # Build DOM tree
        root = self._build_dom_tree(soup)
        tree = DOMTree(root)

        # Apply CSS rules to the DOM tree
        if self.stylesheet_manager.get_rule_count() > 0:
            logger.debug(f"Applying {self.stylesheet_manager.get_rule_count()} CSS rules to DOM tree")
            self.stylesheet_manager.apply_styles_to_tree(tree.root)

        logger.info(f"Parsed HTML: {tree}")
        return tree

    def parse_file(self, file_path: str, parser: str = "lxml") -> DOMTree:
        """
        Parse HTML file and build DOM tree.

        Args:
            file_path: Path to HTML file
            parser: BeautifulSoup parser to use

        Returns:
            DOMTree object
        """
        # Resolve relative paths
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.base_path, file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HTML file not found: {file_path}")

        # Update base_path to the directory of the HTML file
        self.base_path = os.path.dirname(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        return self.parse(html_content, parser)

    def _build_dom_tree(self, soup_node) -> DOMNode:
        """
        Recursively build DOM tree from BeautifulSoup node.

        Args:
            soup_node: BeautifulSoup node

        Returns:
            DOMNode
        """
        # Handle different node types
        if isinstance(soup_node, NavigableString):
            # Text node
            if isinstance(soup_node, Comment):
                # Skip comments
                return None

            text = str(soup_node)
            # Skip empty text nodes
            if not text or text.isspace():
                return None

            return DOMNode(node_type=NodeType.TEXT, text=text)

        elif isinstance(soup_node, Tag):
            # Element node
            tag_name = soup_node.name

            # Extract attributes
            attributes = dict(soup_node.attrs)

            # Create DOM node
            dom_node = DOMNode(
                node_type=NodeType.ELEMENT,
                tag=tag_name,
                attributes=attributes
            )

            # Parse inline styles
            if 'style' in attributes:
                dom_node.inline_styles = self.css_parser.parse_inline_style(attributes['style'])

            # Apply default styles for this element
            if tag_name in self.default_styles:
                default_style = self.default_styles[tag_name]
                # Merge default styles with inline styles (inline takes precedence)
                for prop, value in default_style.items():
                    if prop not in dom_node.inline_styles:
                        dom_node.inline_styles[prop] = str(value)

            # Recursively process children
            for child in soup_node.children:
                child_node = self._build_dom_tree(child)
                if child_node is not None:
                    dom_node.add_child(child_node)

            return dom_node

        else:
            # Unknown node type, skip
            return None

    def get_body_content(self, tree: DOMTree) -> Optional[DOMNode]:
        """
        Extract body content from HTML tree.

        Args:
            tree: DOM tree

        Returns:
            Body node or root if no body found
        """
        body_nodes = tree.find_by_tag('body')
        if body_nodes:
            return body_nodes[0]

        # If no body tag, return the root
        return tree.root

    def extract_title(self, tree: DOMTree) -> Optional[str]:
        """
        Extract document title from HTML tree.

        Args:
            tree: DOM tree

        Returns:
            Title text or None
        """
        title_nodes = tree.find_by_tag('title')
        if title_nodes:
            return title_nodes[0].get_text_content()
        return None
