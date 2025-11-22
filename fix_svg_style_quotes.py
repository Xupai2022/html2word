"""
Fix SVG style attribute quotes in HTML files.

The issue: SVG style attributes contain unescaped quotes like:
  style="font: 12px "Microsoft YaHei";"

This should be:
  style="font: 12px &quot;Microsoft YaHei&quot;;"
"""

import re
import sys


def fix_svg_style_quotes(html_content):
    """
    Fix SVG style attributes with quotes in the values.

    Args:
        html_content: HTML string content

    Returns:
        Fixed HTML string
    """
    # Simple and effective approach:
    # Replace " inside font specifications with &quot;
    # Pattern matches: font: 12px "FontName" or font: bold 12px "FontName"

    # Handle font specs with quotes
    # Before: font: 12px "Microsoft YaHei"
    # After:  font: 12px &quot;Microsoft YaHei&quot;
    html_content = re.sub(
        r'font:\s*([^;"]*?)\s*"([^"]*)"\s*;',
        r'font: \1 &quot;\2&quot;;',
        html_content
    )

    # Handle quotes in other style properties if any
    # This is a more general pattern for any style property values with quotes
    html_content = re.sub(
        r'([a-zA-Z-]+):\s*([^;"]*?)"([^"]*)"([^;]*);',
        r'\1: \2&quot;\3&quot;\4;',
        html_content
    )

    return html_content


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_svg_style_quotes.py <input_html_file> [output_html_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.html', '_svg_fixed.html')

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Fixing SVG style attribute quotes...")
    fixed_content = fix_svg_style_quotes(html_content)

    # Count fixes
    quot_entities = len(re.findall(r'&quot;', fixed_content))

    print(f"Found {quot_entities} font specifications with &quot; entities")
    if quot_entities > 0:
        print("Sample fix detected!")

    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print("Done!")


if __name__ == '__main__':
    main()
