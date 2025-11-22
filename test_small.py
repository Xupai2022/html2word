#!/usr/bin/env python
"""Test script for converting small HTML"""

import logging
import sys
import time
from html2word.converter import HTML2WordConverter

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

if __name__ == "__main__":
    converter = HTML2WordConverter()
    
    print("="*60)
    print("Converting oversear_monthly_report_1section.html (1 section only)")
    print("="*60)
    
    start_time = time.time()
    try:
        output_path = converter.convert_file(
            "oversear_monthly_report_1section.html",
            "oversear_monthly_report_1section.docx"
        )
        elapsed = time.time() - start_time
        print("="*60)
        print(f"SUCCESS! Conversion completed in {elapsed:.2f} seconds")
        print(f"Output: {output_path}")
        print("="*60)
    except Exception as e:
        elapsed = time.time() - start_time
        print("="*60)
        print(f"FAILED after {elapsed:.2f} seconds: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
