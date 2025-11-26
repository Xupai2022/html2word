#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify text position fix in background image compositing
"""

import os
import sys
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('src')

from html2word import HTML2WordConverter

def test_text_position():
    """Test the text position fix with oversear_monthly_report_part1.html"""

    # Check if the HTML file exists
    html_file = "oversear_monthly_report_part1.html"
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return False

    print(f"Testing text position fix with {html_file}...")
    print("-" * 60)

    # Convert HTML to Word
    converter = HTML2WordConverter()

    try:
        # Convert HTML file to Word document
        import time
        output_file = f"test_text_position_output_{int(time.time())}.docx"
        converter.convert_file(html_file, output_file)

        print(f"✓ Conversion successful! Output saved to: {output_file}")
        print("\nPlease check the output document to verify:")
        print("1. Background images are rendered correctly")
        print("2. Text overlays (like '2K+ logs') are positioned accurately")
        print("3. No text is shifted down or to the right")
        print("\nLook especially at the section after:")
        print('"The security rating is calculated based on..."')

        return True

    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_fix_applied():
    """Verify that our fixes are in place"""
    import importlib.util

    # Check if the fix is applied in document_builder.py
    doc_builder_path = "src/html2word/word_builder/document_builder.py"

    with open(doc_builder_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fixes_applied = []
    fixes_missing = []

    # Check for removal of hardcoded offset
    if 'left_px - 40' not in content:
        fixes_applied.append("✓ Hardcoded offset removed")
    else:
        fixes_missing.append("✗ Hardcoded offset still present")

    # Check for direct pixel conversion without scaling
    if 'CSS positions are relative to the container' in content:
        fixes_applied.append("✓ Direct pixel conversion without scaling")
    else:
        fixes_missing.append("✗ Direct pixel conversion missing")

    # Check that scaling is NOT applied to text position
    if '* scale_y' not in content or '* scale_x' not in content:
        fixes_applied.append("✓ Scaling removed from text position calculation")
    else:
        fixes_missing.append("✗ Scaling still applied to text position")

    # Check for debug logging
    if 'Text positioning for' in content:
        fixes_applied.append("✓ Debug logging added")
    else:
        fixes_missing.append("✗ Debug logging missing")

    print("\nFix Verification:")
    print("-" * 60)
    for fix in fixes_applied:
        print(fix)
    for fix in fixes_missing:
        print(fix)

    return len(fixes_missing) == 0

if __name__ == "__main__":
    print("Text Position Fix Verification")
    print("=" * 60)

    # First check if fixes are applied
    if check_fix_applied():
        print("\n✓ All fixes have been applied successfully!")
    else:
        print("\n⚠ Some fixes are missing. Please review the code.")

    print("\n")

    # Run the test
    if test_text_position():
        print("\n✓ Test completed successfully!")
        print("\nNext steps:")
        print("1. Open 'test_text_position_output.docx' in Microsoft Word")
        print("2. Navigate to the security rating section")
        print("3. Verify that text overlays are correctly positioned on background images")
    else:
        print("\n✗ Test failed. Please check the error messages above.")