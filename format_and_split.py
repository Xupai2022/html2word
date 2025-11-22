#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os

def format_and_split_html():
    """Format the HTML file and split it at the 2.2 Incidents section"""

    input_file = 'oversear_monthly_report_cut10.html'
    output_file = 'oversear_monthly_report_part1.html'

    print(f"Reading file: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"File size: {len(content)} characters")

        # Look for 2.2 Incidents & Threats section
        # Try different patterns to find the section
        patterns = [
            r'(\s+2\.2\s+Incidents\s*&\s*Threats)',
            r'(\s+2\.2\s+Incidents[^\u003c]*Threats)',
            r'(\u003c[^\u003e]*\u003e\s*2\.2\s+[^\u003c]*Incidents[^\u003c]*Threats)',
            r'(\u003c[^\u003e]*\u003e\s*2\.2\s+[^\u003c]*Incidents)',
            r'(\s+2\.2\s+[^\u003c]*Incidents)'
        ]

        split_pos = None
        found_pattern = None

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                split_pos = match.start()
                found_pattern = pattern
                print(f"Found '2.2 Incidents' section using pattern: {pattern}")
                print(f"Position: {split_pos}")
                print(f"Context: {content[max(0, split_pos-50):split_pos+150]}...")
                break

        if split_pos is None:
            print("Could not find '2.2 Incidents & Threats' section, trying to find '2.2' followed by 'Incidents' within 500 chars...")
            # Look for 2.2 followed by Incidents within 500 characters
            match_22 = re.search(r'\s+2\.2\s+', content)
            if match_22:
                pos_22 = match_22.start()
                # Look for Incidents in the next 500 characters
                incidents_match = re.search(r'Incidents', content[pos_22:pos_22+500], re.IGNORECASE)
                if incidents_match:
                    split_pos = pos_22
                    print(f"Found '2.2' at position {pos_22} with 'Incidents' nearby")

        if split_pos is None:
            print("Still could not find section, trying broader search...")
            # Look for any 2.2 section header
            match = re.search(r'(\s+2\.2\s+[<\w\s]+)', content)
            if match:
                split_pos = match.start()
                print(f"Found '2.2' section at position {split_pos}")
                print(f"Context: {content[max(0, split_pos-50):split_pos+150]}...")

        if split_pos is not None:
            # Extract content before the 2.2 section
            part1_content = content[:split_pos]

            # Make sure we have proper HTML structure
            # Add closing tags if needed
            if '\u003c/html\u003e' not in part1_content.lower():
                # Find the last closing tag before our split point
                last_tag_pos = part1_content.rfind('\u003e')
                if last_tag_pos != -1:
                    # Insert closing tags
                    part1_content = part1_content[:last_tag_pos+1]
                    # Add basic HTML closing structure
                    part1_content += '\n\n\u003c/body\u003e\n\u003c/html\u003e'

            # Write the first part
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(part1_content)

            print(f"Successfully created: {output_file}")
            print(f"Part 1 size: {len(part1_content)} characters")

            # Also create part 2 for reference
            part2_content = content[split_pos:]
            part2_file = r'c:\Users\xupai\Downloads\html2word\oversear_monthly_report_part2.html'

            # Ensure proper HTML structure for part 2
            if not part2_content.strip().lower().startswith('\u003chtml\u003e'):
                part2_content = '\u003c!DOCTYPE html\u003e\n\u003chtml\u003e\n\u003chead\u003e\n\u003cmeta charset=\"utf-8\"\u003e\n\u003c/head\u003e\n\u003cbody\u003e\n' + part2_content

            if '\u003c/html\u003e' not in part2_content.lower():
                part2_content += '\n\u003c/body\u003e\n\u003c/html\u003e'

            with open(part2_file, 'w', encoding='utf-8') as f:
                f.write(part2_content)

            print(f"Also created: {part2_file}")
            print(f"Part 2 size: {len(part2_content)} characters")

        else:
            print("ERROR: Could not find '2.2 Incidents & Threats' section in the file")
            print("Searching for any numbered section starting with 2...")

            # Show some context around where 2.2 might be
            matches = list(re.finditer(r'\s+2\.\d+\s+', content))
            if matches:
                print("Found numbered sections:")
                for match in matches[:10]:  # Show first 10
                    pos = match.start()
                    print(f"Position {pos}: {content[max(0, pos-50):pos+100]}...")

            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = format_and_split_html()
    sys.exit(0 if success else 1)