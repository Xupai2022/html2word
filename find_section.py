#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def find_section_boundary():
    """Find the line number where "2.2 Incidents & Threats" section starts"""

    with open('c:\\Users\\xupai\\Downloads\\html2word\\oversear_monthly_report_cut10.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Look for patterns like "2.2", "2.2 Incidents", etc.
    patterns = [
        r'2\.2\s+Incidents\s*&\s*Threats',
        r'2\.2\s+Incidents',
        r'2\.2\s+.*Incidents',
        r'<[^>]*>\s*2\.2\s+Incidents',
        r'<[^>]*>\s*2\.2\s*<[^>]*>.*Incidents'
    ]

    for i, line in enumerate(lines):
        line_num = i + 1
        line_stripped = line.strip()

        # Check each pattern
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                print(f"Found '2.2 Incidents & Threats' at line {line_num}")
                print(f"Line content: {line_stripped[:150]}...")
                return line_num

        # Also check if "Incidents" and "Threats" appear close together near "2.2"
        if '2.2' in line:
            # Look ahead a few lines for Incidents/Threats
            for j in range(max(0, i-2), min(len(lines), i+3)):
                if j != i and 'Incidents' in lines[j] and 'Threats' in lines[j]:
                    print(f"Found '2.2' at line {line_num}, with 'Incidents & Threats' at line {j+1}")
                    print(f"2.2 line: {line_stripped[:150]}...")
                    print(f"Incidents line: {lines[j].strip()[:150]}...")
                    return line_num

    print("Could not find '2.2 Incidents & Threats' section")
    return None

if __name__ == "__main__":
    find_section_boundary()