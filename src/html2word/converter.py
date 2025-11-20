"""
Main HTML to Word converter.

Coordinates the entire conversion pipeline from HTML to .docx.
"""

import logging
import os
from typing import Optional

from html2word.parser.html_parser import HTMLParser
from html2word.style.style_resolver import StyleResolver
from html2word.word_builder.document_builder import DocumentBuilder

logger = logging.getLogger(__name__)


class HTML2WordConverter:
    """Main converter class that orchestrates the conversion process."""

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize HTML to Word converter.

        Args:
            base_path: Base path for resolving relative paths
        """
        self.base_path = base_path or os.getcwd()

        # Initialize components
        self.html_parser = HTMLParser(base_path=self.base_path)
        self.style_resolver = StyleResolver()
        self.document_builder = DocumentBuilder(base_path=self.base_path)

    def convert(
        self,
        html_input: str,
        output_path: str,
        input_type: str = "file"
    ) -> str:
        """
        Convert HTML to Word document.

        Args:
            html_input: HTML file path or HTML string
            output_path: Output .docx file path
            input_type: Type of input - "file" or "string"

        Returns:
            Output file path

        Examples:
            converter = HTML2WordConverter()
            converter.convert("input.html", "output.docx")
            converter.convert("<html>...</html>", "output.docx", input_type="string")
        """
        logger.info(f"Starting HTML to Word conversion")
        logger.info(f"Input: {html_input if input_type == 'file' else 'HTML string'}")
        logger.info(f"Output: {output_path}")

        # Phase 1: Parse HTML
        logger.info("Phase 1: Parsing HTML")
        if input_type == "file":
            tree = self.html_parser.parse_file(html_input)
        else:
            tree = self.html_parser.parse(html_input)

        # Log statistics
        stats = tree.get_stats()
        logger.info(f"Parsed {stats['total_nodes']} nodes ({stats['element_nodes']} elements)")

        # Phase 2: Resolve styles
        logger.info("Phase 2: Resolving styles")
        self.style_resolver.resolve_styles(tree)

        # Phase 3: Build Word document
        logger.info("Phase 3: Building Word document")
        document = self.document_builder.build(tree)

        # Phase 4: Save document
        logger.info("Phase 4: Saving document")
        document.save(output_path)

        logger.info(f"Conversion complete: {output_path}")
        return output_path

    def convert_file(self, html_file: str, output_file: str) -> str:
        """
        Convert HTML file to Word document.

        Args:
            html_file: Path to HTML file
            output_file: Path to output .docx file

        Returns:
            Output file path
        """
        return self.convert(html_file, output_file, input_type="file")

    def convert_string(self, html_string: str, output_file: str) -> str:
        """
        Convert HTML string to Word document.

        Args:
            html_string: HTML content as string
            output_file: Path to output .docx file

        Returns:
            Output file path
        """
        return self.convert(html_string, output_file, input_type="string")
