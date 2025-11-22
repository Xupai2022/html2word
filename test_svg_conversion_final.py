#!/usr/bin/env python3
"""
Final comprehensive test for SVG conversion fix.

This script tests the conversion of oversear_monthly_report_part1.html
and verifies that all real SVG charts are successfully converted to images
in the generated Word document.
"""

import logging
import sys
from pathlib import Path
from docx import Document
import zipfile
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


def count_svgs_in_html(html_file):
    """Count SVG elements in HTML file, separating icons from real charts."""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    
    real_svgs = 0
    icon_svgs = 0
    
    for svg in soup.find_all('svg'):
        use = svg.find('use')
        if use:
            xlink_href = use.get('xlink:href') or use.get('href')
            if xlink_href and xlink_href.startswith('#icon-'):
                icon_svgs += 1
            else:
                real_svgs += 1
        else:
            real_svgs += 1
    
    return real_svgs, icon_svgs


def count_images_in_docx(docx_file):
    """Count images in Word document."""
    if not Path(docx_file).exists():
        return 0, []
    
    doc = Document(docx_file)
    
    # Count images via relationships
    image_count = 0
    for rel_id, rel in doc.part.rels.items():
        if "image" in rel.target_ref:
            image_count += 1
    
    # Get media file details
    media_files = []
    with zipfile.ZipFile(docx_file, 'r') as zip_ref:
        for f in zip_ref.namelist():
            if 'media/' in f:
                info = zip_ref.getinfo(f)
                media_files.append((f, info.file_size))
    
    return image_count, media_files


def main():
    """Run comprehensive SVG conversion test."""
    print("=" * 80)
    print("SVG CONVERSION FINAL VERIFICATION TEST")
    print("=" * 80)
    print()
    
    html_file = "oversear_monthly_report_part1.html"
    output_file = "oversear_monthly_report_part1_final.docx"
    
    # Step 1: Count SVGs in HTML
    logger.info("Step 1: Analyzing HTML source file...")
    real_svgs, icon_svgs = count_svgs_in_html(html_file)
    total_svgs = real_svgs + icon_svgs
    
    print(f"HTML Analysis:")
    print(f"  Total SVG elements: {total_svgs}")
    print(f"  Real chart SVGs: {real_svgs}")
    print(f"  Icon reference SVGs (should be skipped): {icon_svgs}")
    print()
    
    # Step 2: Convert HTML to Word
    logger.info("Step 2: Converting HTML to Word...")
    from html2word.converter import HTML2WordConverter
    
    converter = HTML2WordConverter()
    try:
        result_path = converter.convert_file(html_file, output_file)
        logger.info(f"Conversion completed: {result_path}")
    except Exception as e:
        logger.error(f"Conversion failed: {e}", exc_info=True)
        return 1
    
    print()
    
    # Step 3: Verify Word document
    logger.info("Step 3: Verifying generated Word document...")
    image_count, media_files = count_images_in_docx(output_file)
    
    print(f"Word Document Analysis:")
    print(f"  Total images: {image_count}")
    print(f"  Media files:")
    for filename, size in sorted(media_files):
        print(f"    {filename}: {size:,} bytes")
    print()
    
    # Step 4: Final verification
    print("=" * 80)
    print("VERIFICATION RESULTS")
    print("=" * 80)
    
    success = True
    
    # Check 1: All real SVGs converted
    if image_count >= real_svgs:
        print(f"✓ PASS: All {real_svgs} real SVG charts converted to images")
    else:
        print(f"✗ FAIL: Only {image_count} images found, expected at least {real_svgs}")
        success = False
    
    # Check 2: Icon SVGs were skipped
    if image_count < total_svgs:
        skipped = total_svgs - image_count
        print(f"✓ PASS: Icon SVGs correctly skipped ({skipped} skipped)")
    else:
        print(f"⚠ WARNING: Expected some SVGs to be skipped, but all were converted")
    
    # Check 3: Image file sizes are reasonable
    small_images = [f for f, s in media_files if s < 500]
    if small_images:
        print(f"✓ INFO: {len(small_images)} small placeholder/icon images found")
    
    large_images = [f for f, s in media_files if s > 1000]
    if large_images:
        print(f"✓ INFO: {len(large_images)} chart images found (size > 1KB)")
    
    print()
    
    if success:
        print("=" * 80)
        print("🎉 ALL TESTS PASSED! SVG conversion is working correctly!")
        print("=" * 80)
        return 0
    else:
        print("=" * 80)
        print("❌ TESTS FAILED! Please review the issues above.")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
