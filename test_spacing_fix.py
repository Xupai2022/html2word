#!/usr/bin/env python
"""Test script to verify spacing fixes."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.converter import HTML2WordConverter

def main():
    converter = HTML2WordConverter()

    input_file = 'security_quarterly_report.html'
    output_file = 'security_quarterly_report_spacing_fixed.docx'

    print(f"Converting {input_file} to {output_file}...")
    converter.convert(input_file, output_file)
    print(f"Done! Output saved to {output_file}")

if __name__ == '__main__':
    main()
