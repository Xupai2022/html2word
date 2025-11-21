#!/usr/bin/env python3
"""Compare old vs final version."""

from docx import Document


def count_spacers(docx_file):
    """Count spacer paragraphs."""
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


def analyze_consecutive(spacers):
    consecutive = []
    for i in range(len(spacers) - 1):
        if spacers[i+1]['index'] == spacers[i]['index'] + 1:
            consecutive.append((spacers[i], spacers[i+1]))
    return consecutive


print("=" * 80)
print("FINAL COMPARISON")
print("=" * 80)

old_file = "security_quarterly_report_spacing_fixed.docx"
final_file = "security_quarterly_report_FINAL.docx"

print(f"\nOLD VERSION: {old_file}")
old_spacers = count_spacers(old_file)
old_consecutive = analyze_consecutive(old_spacers)
print(f"  Total spacers: {len(old_spacers)}")
print(f"  Consecutive pairs: {len(old_consecutive)}")
if old_spacers:
    avg = sum(s['total'] for s in old_spacers) / len(old_spacers)
    print(f"  Average spacing: {avg:.1f}pt")

print(f"\nFINAL VERSION: {final_file}")
final_spacers = count_spacers(final_file)
final_consecutive = analyze_consecutive(final_spacers)
print(f"  Total spacers: {len(final_spacers)}")
print(f"  Consecutive pairs: {len(final_consecutive)}")
if final_spacers:
    avg = sum(s['total'] for s in final_spacers) / len(final_spacers)
    print(f"  Average spacing: {avg:.1f}pt")

print(f"\n{'='*80}")
print("IMPROVEMENTS")
print(f"{'='*80}")

reduction_spacers = len(old_spacers) - len(final_spacers)
reduction_percent = (reduction_spacers / len(old_spacers) * 100) if old_spacers else 0
print(f"Spacers reduced: {len(old_spacers)} → {len(final_spacers)}")
print(f"  ({reduction_spacers} fewer, {reduction_percent:.1f}% reduction)")

reduction_pairs = len(old_consecutive) - len(final_consecutive)
reduction_percent_pairs = (reduction_pairs / len(old_consecutive) * 100) if old_consecutive else 0
print(f"\nConsecutive pairs reduced: {len(old_consecutive)} → {len(final_consecutive)}")
print(f"  ({reduction_pairs} fewer, {reduction_percent_pairs:.1f}% reduction)")

if len(final_consecutive) == 0:
    print("\n✅ SUCCESS: ALL consecutive spacer pairs eliminated!")

print("\n" + "=" * 80)
