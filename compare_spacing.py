#!/usr/bin/env python3
"""
Compare spacing between two DOCX files.
"""

from docx import Document


def count_spacers(docx_file):
    """Count spacer paragraphs and their total spacing."""
    doc = Document(docx_file)
    spacers = []

    for i, para in enumerate(doc.paragraphs):
        space_before = para.paragraph_format.space_before
        space_after = para.paragraph_format.space_after

        before_pt = space_before.pt if space_before else 0
        after_pt = space_after.pt if space_after else 0

        text = para.text.strip()

        if (before_pt > 0 or after_pt > 0) and not text:
            spacers.append({
                'index': i,
                'before': before_pt,
                'after': after_pt,
                'total': before_pt + after_pt
            })

    return spacers


def analyze_consecutive_spacers(spacers):
    """Find consecutive spacer paragraphs."""
    consecutive = []
    for i in range(len(spacers) - 1):
        if spacers[i+1]['index'] == spacers[i]['index'] + 1:
            consecutive.append((spacers[i], spacers[i+1]))
    return consecutive


def main():
    print("=" * 80)
    print("SPACING COMPARISON")
    print("=" * 80)

    old_file = "security_quarterly_report_spacing_fixed.docx"
    new_file = "security_quarterly_report_v2.docx"

    print(f"\nOLD FILE: {old_file}")
    old_spacers = count_spacers(old_file)
    old_consecutive = analyze_consecutive_spacers(old_spacers)

    print(f"Total spacers: {len(old_spacers)}")
    print(f"Consecutive spacer pairs: {len(old_consecutive)}")
    if old_spacers:
        avg = sum(s['total'] for s in old_spacers) / len(old_spacers)
        max_s = max(s['total'] for s in old_spacers)
        print(f"Average spacing: {avg:.1f}pt")
        print(f"Max spacing: {max_s:.1f}pt")

    print(f"\nNEW FILE: {new_file}")
    new_spacers = count_spacers(new_file)
    new_consecutive = analyze_consecutive_spacers(new_spacers)

    print(f"Total spacers: {len(new_spacers)}")
    print(f"Consecutive spacer pairs: {len(new_consecutive)}")
    if new_spacers:
        avg = sum(s['total'] for s in new_spacers) / len(new_spacers)
        max_s = max(s['total'] for s in new_spacers)
        print(f"Average spacing: {avg:.1f}pt")
        print(f"Max spacing: {max_s:.1f}pt")

    print(f"\nIMPROVEMENT:")
    print(f"Spacers reduced: {len(old_spacers)} → {len(new_spacers)} ({len(old_spacers) - len(new_spacers)} fewer)")
    print(f"Consecutive pairs reduced: {len(old_consecutive)} → {len(new_consecutive)} ({len(old_consecutive) - len(new_consecutive)} fewer)")

    if len(old_consecutive) > 0 and len(new_consecutive) == 0:
        print("\n✅ SUCCESS: All consecutive spacer pairs eliminated!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
