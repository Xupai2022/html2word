#!/usr/bin/env python
"""Count all spacing values in the document."""

from docx import Document

def main():
    doc = Document('security_quarterly_report_spacing_fixed.docx')

    spacing_values = {}

    for i, para in enumerate(doc.paragraphs):
        fmt = para.paragraph_format
        space_before = fmt.space_before
        space_after = fmt.space_after

        if space_before and space_before.pt > 0:
            val = round(space_before.pt, 2)
            spacing_values[val] = spacing_values.get(val, 0) + 1

        if space_after and space_after.pt > 0:
            val = round(space_after.pt, 2)
            spacing_values[val] = spacing_values.get(val, 0) + 1

    print("All spacing values found:")
    print("-" * 60)
    for val in sorted(spacing_values.keys(), reverse=True):
        count = spacing_values[val]
        # Convert back to px
        px = round(val / 0.75, 1)
        print(f"  {val}pt ({px}px): {count} occurrences")

if __name__ == '__main__':
    main()
