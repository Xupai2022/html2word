"""
Comprehensive SVG fix for HTML files.

This script fixes all SVG issues that cause XML parsing errors:
1. Replaces xlink:href with href (namespace issues)
2. XML-escapes attribute values
3. Handles special characters in SVG attributes
"""

import re
import sys
import html


def xml_escape(value):
    """Escape XML special characters in attribute values."""
    if not value:
        return value
    # Escape XML special characters
    # Escape & first to avoid double-escaping
    value = value.replace('&', '&amp;')
    value = value.replace('<', '&lt;')
    value = value.replace('>', '&gt;')
    value = value.replace('\"', '&quot;')
    value = value.replace("'", '&apos;')
    return value


def fix_svg_attributes(html_content):
    """
    Fix all SVG attribute values by XML-escaping them.

    Args:
        html_content: HTML string content

    Returns:
        Fixed HTML string
    """
    # Pattern to match SVG elements and their attributes
    # This is complex because we need to parse attributes properly

    def fix_svg_tag(match):
        """Fix a single SVG tag."""
        full_tag = match.group(0)

        # Replace xlink:href with href first
        full_tag = re.sub(r'xlink:href=', 'href=', full_tag, flags=re.IGNORECASE)

        # Fix attributes with proper XML escaping
        # Pattern to match attribute="value" pairs
        attr_pattern = r'([a-zA-Z0-9:_-]+)\s*=\s*\"([^\"]*)\"'

        def fix_attr(attr_match):
            attr_name = attr_match.group(1)
            attr_value = attr_match.group(2)
            # Escape the value
            escaped_value = xml_escape(attr_value)
            return f'{attr_name}="{escaped_value}"'

        fixed_tag = re.sub(attr_pattern, fix_attr, full_tag)
        return fixed_tag

    # Find all SVG tags (including use, path, etc. within SVG)
    # Process the entire document

    # First, fix SVG start tags
    svg_start_pattern = r'<svg[^>]*>'
    html_content = re.sub(svg_start_pattern, fix_svg_tag, html_content, flags=re.IGNORECASE)

    # Then fix use tags
    use_pattern = r'<use[^>]*/>'
    html_content = re.sub(use_pattern, fix_svg_tag, html_content, flags=re.IGNORECASE)

    use_pattern2 = r'<use[^>]*></use>'
    html_content = re.sub(use_pattern2, fix_svg_tag, html_content, flags=re.IGNORECASE)

    # Fix path tags
    path_pattern = r'<path[^>]*/>'
    html_content = re.sub(path_pattern, fix_svg_tag, html_content, flags=re.IGNORECASE)

    return html_content


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_svg_complete.py <input_html_file> [output_html_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.html', '_fixed_complete.html')

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Fixing SVG namespace and escaping issues...")
    fixed_content = fix_svg_attributes(html_content)

    # Find SVG count before and after
    original_svg_count = len(re.findall(r'<svg', html_content, re.IGNORECASE))
    fixed_svg_count = len(re.findall(r'<svg', fixed_content, re.IGNORECASE))

    print(f"Found {original_svg_count} SVG elements")

    # Count xlink replacements
    xlink_count_before = len(re.findall(r'xlink:href=', html_content, re.IGNORECASE))
    xlink_count_after = len(re.findall(r'xlink:href=', fixed_content, re.IGNORECASE))
    xlink_fixed = xlink_count_before - xlink_count_after

    print(f"Fixed {xlink_fixed} xlink:href attributes")

    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print("Done!")


if __name__ == '__main__':
    main()
