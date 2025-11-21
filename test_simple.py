#!/usr/bin/env python
"""Test simple spacing scenario."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.converter import HTML2WordConverter
from docx import Document

def main():
    converter = HTML2WordConverter()

    input_file = 'test_simple_spacing.html'
    output_file = 'test_simple_spacing.docx'

    print(f"Converting {input_file}...")
    converter.convert(input_file, output_file)
    print(f"Done!\n")

    # Verify
    doc = Document(output_file)
    print("Spacing analysis:")
    print("-" * 60)

    for i, para in enumerate(doc.paragraphs):
        fmt = para.paragraph_format
        space_before = fmt.space_before
        space_after = fmt.space_after
        text = para.text.strip()[:40] if para.text.strip() else "[empty]"

        if (space_before and space_before.pt > 0) or (space_after and space_after.pt > 0):
            sb = f"{space_before.pt}pt" if space_before else "0pt"
            sa = f"{space_after.pt}pt" if space_after else "0pt"
            print(f"Para {i}: before={sb}, after={sa} | {text}")

    print("\nExpected:")
    print("  - 30pt after box1")
    print("  - 22.5pt after box2")
    print("  - Some spacing around grid")

if __name__ == '__main__':
    main()
