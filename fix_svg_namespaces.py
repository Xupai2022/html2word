"""
Fix SVG namespace issues in HTML files.

This script fixes SVG elements that use xlink:href but don't declare
the xlink namespace, which causes XML parsing errors.
"""

import re
import sys

def fix_svg_namespaces(html_content):
    """
    Fix SVG namespace issues in HTML content.

    Args:
        html_content: HTML string content

    Returns:
        Fixed HTML string with proper SVG namespaces
    """
    # Pattern to match SVG start tags that have xlink:href attributes
    # but don't have xmlns:xlink declaration

    # First, handle simple <use> tags within SVG
    # Replace xlink:href with href (modern SVG supports this)
    # This is simpler than adding namespace declarations

    # Pattern 1: Replace xlink:href="..." with href="..."
    html_content = re.sub(
        r'(<svg[^>]*>[^<]*<use[^>]*)xlink:href=',
        r'\1href=',
        html_content,
        flags=re.IGNORECASE
    )

    # Pattern 2: For nested SVGs or more complex cases
    html_content = re.sub(
        r'(<use[^>]*)xlink:href=',
        r'\1href=',
        html_content,
        flags=re.IGNORECASE
    )

    return html_content

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_svg_namespaces.py <input_html_file> [output_html_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.html', '_fixed.html')

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Fixing SVG namespace issues...")
    fixed_content = fix_svg_namespaces(html_content)

    # Count how many fixes were made
    original_use_count = len(re.findall(r'xlink:href=', html_content, re.IGNORECASE))
    fixed_use_count = len(re.findall(r'xlink:href=', fixed_content, re.IGNORECASE))
    fixes_made = original_use_count - fixed_use_count

    print(f"Fixed {fixes_made} SVG namespace issues")
    print(f"Writing to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print("Done!")

if __name__ == '__main__':
    main()
