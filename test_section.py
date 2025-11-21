#!/usr/bin/env python
"""Test section spacing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.converter import HTML2WordConverter
from docx import Document

def main():
    converter = HTML2WordConverter()

    input_file = 'test_section_spacing.html'
    output_file = 'test_section_spacing.docx'

    print(f"Converting {input_file}...")
    converter.convert(input_file, output_file)
    print(f"Done!\n")

    # Verify
    doc = Document(output_file)
    print("Document structure:")
    print("-" * 80)

    for i, para in enumerate(doc.paragraphs):
        fmt = para.paragraph_format
        space_before = fmt.space_before
        space_after = fmt.space_after
        text = para.text.strip()[:60] if para.text.strip() else "[empty]"

        sb = f"{space_before.pt:.1f}pt" if space_before else "---"
        sa = f"{space_after.pt:.1f}pt" if space_after else "---"
        print(f"Para {i:2d}: before={sb:8s} after={sa:8s} | {text}")

    print("\n" + "="*80)
    print("EXPECTED: Each section should have 30pt (40px) spacing after it")
    print("="*80)

if __name__ == '__main__':
    main()
