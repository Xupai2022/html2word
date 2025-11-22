#!/usr/bin/env python
"""Test script for converting cut HTML"""

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
    
    print("="*70)
    print("Converting oversear_monthly_report_cut.html")
    print("(39 sections, up to the 91-row table)")
    print("="*70)
    
    start_time = time.time()
    try:
        output_path = converter.convert_file(
            "oversear_monthly_report_cut.html",
            "oversear_monthly_report_cut.docx"
        )
        elapsed = time.time() - start_time
        print("="*70)
        print(f"SUCCESS! Conversion completed in {elapsed:.2f} seconds")
        print(f"Output: {output_path}")
        print("="*70)
    except Exception as e:
        elapsed = time.time() - start_time
        print("="*70)
        print(f"FAILED after {elapsed:.2f} seconds: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
