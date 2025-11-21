"""
Paragraph builder for Word documents.

Builds Word paragraphs from HTML elements with styles.
"""

import logging
from typing import Optional, List
from docx.shared import Pt

from html2word.parser.dom_tree import DOMNode
from html2word.word_builder.style_mapper import StyleMapper
from html2word.style.style_normalizer import StyleNormalizer

logger = logging.getLogger(__name__)


class ParagraphBuilder:
    """Builds Word paragraphs from HTML nodes."""

    def __init__(self, document):
        """
        Initialize paragraph builder.

        Args:
            document: python-docx Document object
        """
        self.document = document
        self.style_mapper = StyleMapper()
        # Track previous element's margin-bottom for true margin collapse
        self.last_margin_bottom = 0.0

    def build_paragraph(self, node: DOMNode) -> Optional[object]:
        """
        Build a Word paragraph from HTML node with proper margin collapse.

        Args:
            node: DOM node (typically p, h1-h6, div, etc.)

        Returns:
            python-docx Paragraph object or None
        """
        if not node.is_element:
            return None

        # Create paragraph
        paragraph = self.document.add_paragraph()

        # Apply paragraph-level styles with margin collapse
        box_model = node.layout_info.get('box_model')
        self.style_mapper.apply_paragraph_style(
            paragraph,
            node.computed_styles,
            box_model,
            prev_margin_bottom=self.last_margin_bottom  # Pass for margin collapse
        )

        # Update last_margin_bottom for next element
        if box_model:
            self.last_margin_bottom = box_model.margin.bottom
        else:
            self.last_margin_bottom = 0.0

        # Process content (text and inline elements)
        self._process_content(node, paragraph)

        return paragraph

    def _process_content(self, node: DOMNode, paragraph):
        """
        Process node content and add runs to paragraph.

        Args:
            node: DOM node
            paragraph: python-docx Paragraph object
        """
        for child in node.children:
            if child.is_text:
                # Add text run
                self._add_text_run(child, paragraph)
            elif child.is_inline:
                # Process inline element
                self._process_inline_element(child, paragraph)
            else:
                # Block element inside paragraph - this shouldn't happen
                # but handle it by adding text content
                text = child.get_text_content()
                if text.strip():
                    run = paragraph.add_run(text)

    def _add_text_run(self, text_node: DOMNode, paragraph):
        """
        Add text run to paragraph.

        Args:
            text_node: Text DOM node
            paragraph: python-docx Paragraph object
        """
        text = text_node.text or ""
        if not text:
            return

        # Check if whitespace should be preserved
        from html2word.layout.inline_layout import InlineLayout
        preserve_whitespace = InlineLayout.should_preserve_whitespace(text_node)

        # Normalize whitespace unless it should be preserved
        if not preserve_whitespace:
            text = InlineLayout.normalize_whitespace(text, preserve=False)

        # Skip if text is only whitespace after normalization
        if not text.strip():
            return

        # Apply text-transform if needed
        if text_node.computed_styles.get('text-transform'):
            text = StyleNormalizer.apply_text_transform(
                text,
                text_node.computed_styles['text-transform']
            )

        run = paragraph.add_run(text)

        # Apply run styles from computed styles
        self.style_mapper.apply_run_style(run, text_node.computed_styles)

    def _process_inline_element(self, node: DOMNode, paragraph):
        """
        Process inline element (span, strong, em, etc.).

        Args:
            node: Inline element node
            paragraph: python-docx Paragraph object
        """
        # Get text content
        for child in node.children:
            if child.is_text:
                text = child.text or ""
                if not text:
                    continue

                # Normalize whitespace
                from html2word.layout.inline_layout import InlineLayout
                preserve = InlineLayout.should_preserve_whitespace(child)
                text = InlineLayout.normalize_whitespace(text, preserve=preserve)

                # Skip pure whitespace
                if not text.strip():
                    continue

                # Apply text-transform if needed
                if node.computed_styles.get('text-transform'):
                    text = StyleNormalizer.apply_text_transform(
                        text,
                        node.computed_styles['text-transform']
                    )

                run = paragraph.add_run(text)
                # Apply styles from parent inline element
                self.style_mapper.apply_run_style(run, node.computed_styles)
            elif child.is_inline:
                # Nested inline element
                self._process_inline_element(child, paragraph)
            else:
                # Unexpected block element
                text = child.get_text_content()
                if text.strip():
                    run = paragraph.add_run(text)

    def build_heading(self, node: DOMNode, level: int = 1) -> Optional[object]:
        """
        Build a Word heading from HTML heading node.

        Args:
            node: Heading node (h1-h6)
            level: Heading level (1-6)

        Returns:
            python-docx Paragraph object
        """
        paragraph = self.build_paragraph(node)

        if paragraph:
            # Apply heading style if available
            try:
                paragraph.style = f'Heading {level}'
            except:
                # Heading style not available, keep as normal paragraph
                # Make it bold and larger
                for run in paragraph.runs:
                    run.font.bold = True
                    if run.font.size:
                        run.font.size = Pt(run.font.size.pt * 1.2)

        return paragraph
