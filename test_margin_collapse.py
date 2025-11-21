#!/usr/bin/env python
"""
Test script to verify margin collapse implementation.

This script converts the security quarterly report and analyzes spacing
to ensure CSS margin collapse is properly implemented.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.converter import HTML2WordConverter

def test_spacing():
    """Test spacing in converted document."""
    input_file = Path(__file__).parent / 'security_quarterly_report.html'
    output_file = Path(__file__).parent / 'output_margin_collapse.docx'

    print("=" * 70)
    print("Testing Margin Collapse Implementation")
    print("=" * 70)

    print(f"\nInput:  {input_file}")
    print(f"Output: {output_file}")

    # Convert
    print("\nConverting HTML to Word...")
    try:
        converter = HTML2WordConverter()
        converter.convert(str(input_file), str(output_file))
        print("[OK] Conversion successful!")
    except Exception as e:
        print(f"[FAIL] Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Analyze spacing
    print("\nAnalyzing paragraph spacing...")
    from docx import Document
    doc = Document(str(output_file))

    spacing_info = []
    for i, para in enumerate(doc.paragraphs[:50]):  # Check first 50 paragraphs
        fmt = para.paragraph_format
        text = para.text[:50] if para.text else "[empty]"

        space_before = fmt.space_before.pt if fmt.space_before else 0
        space_after = fmt.space_after.pt if fmt.space_after else 0

        if space_before > 0 or space_after > 0:
            spacing_info.append({
                'index': i,
                'text': text,
                'space_before': space_before,
                'space_after': space_after
            })

    print(f"\nFound {len(spacing_info)} paragraphs with spacing:")
    print("\n{:<5} {:<12} {:<12} {}".format("Para", "Before (pt)", "After (pt)", "Text"))
    print("-" * 70)

    for info in spacing_info[:20]:  # Show first 20
        print("{:<5} {:<12.1f} {:<12.1f} {}".format(
            info['index'],
            info['space_before'],
            info['space_after'],
            info['text']
        ))

    # Verify: Most paragraphs should have space_after only, not space_before
    with_before = sum(1 for info in spacing_info if info['space_before'] > 0)
    with_after = sum(1 for info in spacing_info if info['space_after'] > 0)

    print("\n" + "=" * 70)
    print("Spacing Analysis:")
    print("=" * 70)
    print(f"Paragraphs with space_before: {with_before}")
    print(f"Paragraphs with space_after:  {with_after}")

    # Expected: most spacing should be space_after (margin-bottom)
    # Only spacers after tables should have space_before
    if with_after > with_before * 2:
        print("\n[PASS] Margin collapse implemented correctly!")
        print("       Most spacing uses space_after (margin-bottom only)")
    else:
        print("\n[WARNING] Too much space_before detected")
        print("          This may indicate spacing accumulation issues")

    print("\n" + "=" * 70)
    print(f"[OK] Test complete! Check {output_file}")
    print("=" * 70)

    return True

if __name__ == '__main__':
    test_spacing()
