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

    def __init__(self, document, document_builder=None):
        """
        Initialize paragraph builder.

        Args:
            document: python-docx Document object
            document_builder: Reference to parent DocumentBuilder (optional, for context tracking)
        """
        self.document = document
        self.document_builder = document_builder
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

        # Check if we're in a table cell (to avoid redundant white backgrounds)
        in_table_cell = getattr(self.document_builder, 'in_table_cell', False) if self.document_builder else False

        # Convert left-aligned text to justified for better readability
        # Create a copy of computed_styles if we need to modify it
        styles = node.computed_styles
        text_align = styles.get('text-align') if styles else None

        # Convert left-aligned or default (no text-align) to justified
        # This ensures better readability for body text
        # Keep explicit center/right/justify alignments as-is
        if text_align in ('left', 'start', None):
            styles = dict(styles) if styles else {}  # Create a copy
            styles['text-align'] = 'justify'

        self.style_mapper.apply_paragraph_style(
            paragraph,
            styles,
            box_model,
            prev_margin_bottom=self.last_margin_bottom,  # Pass for margin collapse
            in_table_cell=in_table_cell  # Pass table cell context
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
            elif child.tag == 'img':
                # FIXED: Handle inline images
                self._add_inline_image(child, paragraph)
            elif child.tag == 'svg':
                # FIXED: Handle inline SVG
                self._add_inline_svg(child, paragraph)
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

    def _add_inline_image(self, img_node: DOMNode, paragraph):
        """
        Add inline image to paragraph run.

        Args:
            img_node: Image DOM node
            paragraph: python-docx Paragraph object
        """
        try:
            # Import image builder utilities
            from html2word.word_builder.image_builder import ImageBuilder
            from html2word.utils.image_utils import ImageProcessor
            from docx.shared import Inches

            # Get image source
            image_builder = ImageBuilder(self.document)
            src = image_builder._get_best_image_src(img_node)
            if not src:
                return

            # Get CSS dimensions
            css_width = img_node.computed_styles.get('width')
            css_height = img_node.computed_styles.get('height')
            transform = img_node.computed_styles.get('transform')
            filter_value = img_node.computed_styles.get('filter')

            # Process image
            image_processor = ImageProcessor()
            result = image_processor.process_image(src, transform=transform, filter_css=filter_value)
            if not result:
                return

            image_stream, image_size = result

            # Calculate size (smaller for inline images)
            max_width_inches = 1.0  # Default max for inline images
            max_height_inches = 0.5

            if css_width:
                from html2word.utils.units import UnitConverter
                width_pt = UnitConverter.to_pt(css_width)
                max_width_inches = width_pt / 72

            if css_height:
                from html2word.utils.units import UnitConverter
                height_pt = UnitConverter.to_pt(css_height)
                max_height_inches = height_pt / 72

            display_width, display_height = image_processor.calculate_display_size(
                image_size, css_width, css_height, max_width_inches, max_height_inches
            )

            # Add inline image to paragraph run
            run = paragraph.add_run()
            run.add_picture(image_stream, width=Inches(display_width), height=Inches(display_height))

            logger.debug(f"Added inline image: {src} ({display_width:.2f}x{display_height:.2f} in)")

        except Exception as e:
            logger.warning(f"Failed to add inline image: {e}")

    def _add_inline_svg(self, svg_node: DOMNode, paragraph):
        """
        Add inline SVG to paragraph run (converted to image).

        Args:
            svg_node: SVG DOM node
            paragraph: python-docx Paragraph object
        """
        try:
            from html2word.word_builder.image_builder import ImageBuilder

            # Use ImageBuilder's SVG conversion, but add to existing paragraph
            width = svg_node.get_attribute('width') or svg_node.computed_styles.get('width', '20')
            height = svg_node.get_attribute('height') or svg_node.computed_styles.get('height', '20')

            # Get SVG content by serializing
            image_builder = ImageBuilder(self.document)
            svg_content = image_builder._serialize_svg_node(svg_node, width, height)

            if not svg_content:
                return

            # Try to convert SVG to PNG
            try:
                import cairosvg
                import io
                from docx.shared import Inches

                png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
                image_stream = io.BytesIO(png_data)

                # Parse dimensions (use small sizes for inline SVGs)
                width_pt = image_builder._parse_dimension(width)
                height_pt = image_builder._parse_dimension(height)

                # Add inline SVG as image in paragraph run
                run = paragraph.add_run()
                run.add_picture(
                    image_stream,
                    width=Inches(width_pt / 72),
                    height=Inches(height_pt / 72)
                )

                logger.debug(f"Added inline SVG as image ({width}x{height})")

            except ImportError:
                logger.warning("cairosvg not available, inline SVG skipped")

        except Exception as e:
            logger.warning(f"Failed to add inline SVG: {e}")
