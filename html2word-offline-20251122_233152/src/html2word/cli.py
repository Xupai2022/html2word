"""
Command-line interface for html2word.

Provides a CLI for converting HTML files to Word documents.
"""

import argparse
import logging
import sys
import os

from html2word.converter import HTML2WordConverter


def setup_logging(log_level: str = "INFO"):
    """
    Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Convert HTML files to Word (.docx) documents with CSS style preservation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert HTML file to Word
  html2word input.html -o output.docx

  # Convert with debug logging
  html2word input.html -o output.docx --log-level DEBUG

  # Specify base path for relative resources
  html2word input.html -o output.docx --base-path /path/to/resources
        """
    )

    parser.add_argument(
        'input',
        help='Input HTML file path'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output Word (.docx) file path'
    )

    parser.add_argument(
        '--base-path',
        help='Base path for resolving relative paths (images, etc.)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='html2word 0.1.0'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Convert input path to absolute path
        input_path = os.path.abspath(args.input)

        # Validate input file
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            sys.exit(1)

        # Determine base path
        base_path = args.base_path
        if base_path is None:
            # Use input file directory as base path
            base_path = os.path.dirname(input_path)

        # Create converter
        converter = HTML2WordConverter(base_path=base_path)

        # Convert
        output_path = converter.convert_file(input_path, args.output)

        logger.info(f"Success! Document saved to: {output_path}")
        print(f"\nConversion successful!")
        print(f"Output: {output_path}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Error during conversion: {e}")
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
