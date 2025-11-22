"""
Test fixing SVG style attribute quotes on sample files.
"""

import re
import sys


def fix_svg_style_quotes_simple(html_content):
    """
    Simple fix: replace font: ... "Font" with font: ... &quot;Font&quot;
    """
    # Find font specs with quotes and escape them
    # Pattern: font: 12px "Microsoft YaHei";
    html_content = re.sub(
        r'font:\s*([^;"]*?)\s*"([^"]*)"',
        r'font: \1 &quot;\2&quot;',
        html_content
    )

    return html_content


def fix_svg_style_quotes_comprehensive(html_content):
    """
    Comprehensive fix: parse the entire style attribute and fix nested quotes.
    """
    def fix_style_attr(match):
        full_match = match.group(0)

        # Count double quotes
        quote_count = full_match.count('"')

        # If more than 2 quotes (outer + inner), we have nested quotes
        if quote_count > 2:
            # Find the style value
            # Look for patterns like: style="font: 12px \"Microsoft YaHei\";"

            # Method: Parse the attribute manually
            # Find style="
            start = full_match.find('style="')
            if start == -1:
                return full_match

            # Find the end quote
            # Need to handle nested quotes
            pos = start + 7  # after style="
            value = ""
            in_escape = False

            while pos < len(full_match):
                char = full_match[pos]

                if in_escape:
                    # Next char is escaped
                    value += char
                    in_escape = False
                elif char == '\\':
                    in_escape = True
                    value += char
                elif char == '"':
                    # Quote - if we've already seen one, this is the end
                    break
                else:
                    value += char

                pos += 1

            # Now value contains the style content
            # Replace any " in the value with &quot;
            value_escaped = value.replace('"', '&quot;')

            # Rebuild the attribute
            before_value = full_match[:start + 7]
            after_value = full_match[start + 7 + len(value):]

            return f'{before_value}{value_escaped}{after_value}'

        return full_match

    # Match style="..." with variable content
    # Use re.DOTALL to allow across lines
    pattern = r'style="[^"]*(?:"[^"]*)*"'
    html_content = re.sub(pattern, fix_style_attr, html_content)

    return html_content


def main():
    test_files = [
        'problem_svg_10.xml',
        'problem_svg_11.xml',
        'problem_svg_12.xml'
    ]

    for filename in test_files:
        print(f"\n=== Testing {filename} ===")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        print("Original quotes:", content.count('"'))

        # Test the simple fix
        fixed_simple = fix_svg_style_quotes_simple(content)
        print("After simple fix quotes:", fixed_simple.count('"'))

        # Write fixed version
        output_file = filename.replace('.xml', '_fixed_simple.xml')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_simple)
        print(f"Wrote simple fix to {output_file}")

        # Check if &quot; was added
        quot_count = fixed_simple.count('&quot;')
        print(f"Found {quot_count} &quot; entities")

        if quot_count > 0:
            # Extract a sample
            lines = fixed_simple.split('\n')
            for i, line in enumerate(lines[:10]):
                if '&quot;' in line:
                    print(f"Line {i}: {line[:150]}...")
                    break


if __name__ == '__main__':
    main()
