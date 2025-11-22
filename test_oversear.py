#!/usr/bin/env python
"""Test script for converting oversear_monthly_report.html"""

import logging
import sys
from html2word.converter import HTML2WordConverter

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

if __name__ == "__main__":
    converter = HTML2WordConverter()
    
    print("Starting conversion of oversear_monthly_report.html...")
    try:
        output_path = converter.convert_file(
            "oversear_monthly_report.html",
            "oversear_monthly_report.docx"
        )
        print(f"Conversion successful! Output: {output_path}")
    except Exception as e:
        print(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
