"""
Document builder for Word documents.

Main coordinator for building Word documents from DOM trees.
"""

import logging
from typing import Optional
from docx import Document

from html2word.parser.dom_tree import DOMNode, DOMTree
from html2word.word_builder.paragraph_builder import ParagraphBuilder
from html2word.word_builder.table_builder import TableBuilder
from html2word.word_builder.image_builder import ImageBuilder

logger = logging.getLogger(__name__)


class DocumentBuilder:
    """Builds complete Word documents from DOM trees."""

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize document builder.

        Args:
            base_path: Base path for resolving relative paths
        """
        self.base_path = base_path
        self.document = Document()
        self.paragraph_builder = ParagraphBuilder(self.document)
        self.table_builder = TableBuilder(self.document)
        self.image_builder = ImageBuilder(self.document, base_path)

    def build(self, tree: DOMTree) -> Document:
        """
        Build Word document from DOM tree.

        Args:
            tree: DOM tree

        Returns:
            python-docx Document object
        """
        logger.info("Building Word document")

        # Get body content
        from html2word.parser.html_parser import HTMLParser
        parser = HTMLParser()
        body = parser.get_body_content(tree)

        if body:
            # Process body children
            self._process_children(body)
        else:
            # No body found, process root
            self._process_children(tree.root)

        logger.info("Document built successfully")
        return self.document

    def _process_children(self, node: DOMNode):
        """
        Process child nodes recursively.

        Args:
            node: Parent DOM node
        """
        for child in node.children:
            self._process_node(child)

    def _process_node(self, node: DOMNode):
        """
        Process a single DOM node.

        Args:
            node: DOM node
        """
        if node.is_text:
            # Skip standalone text nodes (they should be inside elements)
            return

        if not node.is_element:
            return

        # Route to appropriate builder based on tag
        tag = node.tag

        # Headings
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.paragraph_builder.build_heading(node, level)

        # Paragraphs and divs
        elif tag in ('p', 'div', 'blockquote', 'pre'):
            self.paragraph_builder.build_paragraph(node)

        # Lists
        elif tag in ('ul', 'ol'):
            self._process_list(node)

        # List items (shouldn't appear standalone, but handle it)
        elif tag == 'li':
            self.paragraph_builder.build_paragraph(node)

        # Tables
        elif tag == 'table':
            self.table_builder.build_table(node)

        # Images
        elif tag == 'img':
            self.image_builder.build_image(node)

        # Line break
        elif tag == 'br':
            self.document.add_paragraph()

        # Horizontal rule
        elif tag == 'hr':
            self._add_horizontal_rule()

        # Container elements - process children
        elif tag in ('body', 'html', 'main', 'article', 'section', 'header', 'footer', 'nav', 'aside'):
            self._process_children(node)

        # Inline elements - skip (should be handled by paragraph builder)
        elif node.is_inline:
            # Create a paragraph for standalone inline elements
            para = self.document.add_paragraph()
            text = node.get_text_content()
            if text.strip():
                run = para.add_run(text)

        # Unknown elements - process children
        else:
            logger.debug(f"Unknown element: {tag}, processing children")
            self._process_children(node)

    def _process_list(self, list_node: DOMNode):
        """
        Process list (ul/ol) and its items.

        Args:
            list_node: List DOM node
        """
        is_ordered = list_node.tag == 'ol'

        # Get list style
        list_style = list_node.computed_styles.get('list-style-type', 'disc' if not is_ordered else 'decimal')

        for child in list_node.children:
            if child.tag == 'li':
                self._process_list_item(child, is_ordered, list_style)
            elif child.tag in ('ul', 'ol'):
                # Nested list
                self._process_list(child)

    def _process_list_item(self, li_node: DOMNode, is_ordered: bool, list_style: str):
        """
        Process list item.

        Args:
            li_node: List item DOM node
            is_ordered: Whether it's an ordered list
            list_style: List style type
        """
        paragraph = self.paragraph_builder.build_paragraph(li_node)

        if paragraph:
            # Apply list formatting
            if is_ordered:
                paragraph.style = 'List Number'
            else:
                paragraph.style = 'List Bullet'

    def _add_horizontal_rule(self):
        """Add a horizontal rule."""
        # Create a paragraph with bottom border
        paragraph = self.document.add_paragraph()
        fmt = paragraph.paragraph_format
        from docx.shared import Pt
        fmt.space_before = Pt(6)
        fmt.space_after = Pt(6)

        # Add bottom border (simplified)
        paragraph.add_run()

    def save(self, output_path: str):
        """
        Save document to file.

        Args:
            output_path: Output file path
        """
        self.document.save(output_path)
        logger.info(f"Document saved to: {output_path}")
