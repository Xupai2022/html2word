"""
Image builder for Word documents.

Inserts images into Word documents with proper sizing.
"""

import logging
from typing import Optional
from docx.shared import Inches

from html2word.parser.dom_tree import DOMNode
from html2word.utils.image_utils import ImageProcessor

logger = logging.getLogger(__name__)


class ImageBuilder:
    """Builds image insertions for Word documents."""

    def __init__(self, document, base_path: Optional[str] = None):
        """
        Initialize image builder.

        Args:
            document: python-docx Document object
            base_path: Base path for resolving relative image paths
        """
        self.document = document
        self.image_processor = ImageProcessor(base_path)

    def build_image(self, img_node: DOMNode) -> Optional[object]:
        """
        Insert image from img node.

        Args:
            img_node: Image DOM node

        Returns:
            python-docx InlineShape object or None
        """
        if img_node.tag != 'img':
            return None

        # Get image source
        src = img_node.get_attribute('src')
        if not src:
            logger.warning("Image node has no src attribute")
            return None

        # Get CSS dimensions
        css_width = img_node.computed_styles.get('width')
        css_height = img_node.computed_styles.get('height')
        max_width = img_node.computed_styles.get('max-width')
        max_height = img_node.computed_styles.get('max-height')

        # Process image
        result = self.image_processor.process_image(src)
        if result is None:
            logger.error(f"Failed to process image: {src}")
            return None

        image_stream, image_size = result

        # Calculate display size in inches
        max_width_inches = 6.0  # Default max width (for letter size page)
        max_height_inches = 9.0  # Default max height

        if max_width:
            from html2word.utils.units import UnitConverter
            max_width_pt = UnitConverter.to_pt(max_width)
            max_width_inches = max_width_pt / 72

        if max_height:
            from html2word.utils.units import UnitConverter
            max_height_pt = UnitConverter.to_pt(max_height)
            max_height_inches = max_height_pt / 72

        display_width, display_height = self.image_processor.calculate_display_size(
            image_size,
            css_width,
            css_height,
            max_width_inches,
            max_height_inches
        )

        # Insert image
        try:
            # Create paragraph for image
            paragraph = self.document.add_paragraph()
            run = paragraph.add_run()

            # Add picture
            picture = run.add_picture(
                image_stream,
                width=Inches(display_width),
                height=Inches(display_height)
            )

            logger.debug(f"Inserted image: {src} ({display_width:.2f}x{display_height:.2f} in)")
            return picture

        except Exception as e:
            logger.error(f"Error inserting image {src}: {e}")
            return None
