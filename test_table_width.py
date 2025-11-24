"""
Test script to verify table column widths in generated Word document.
"""
from docx import Document
import sys

def analyze_table_widths(docx_path):
    """Analyze table column widths in Word document."""
    doc = Document(docx_path)

    print(f"Analyzing document: {docx_path}")
    print("=" * 80)

    # Find all tables
    for i, table in enumerate(doc.tables):
        print(f"\nTable {i+1}:")
        print(f"  Rows: {len(table.rows)}")
        print(f"  Columns: {len(table.columns)}")

        # Check column widths
        print(f"  Column widths:")
        total_width = 0
        widths = []

        for j, col in enumerate(table.columns):
            try:
                # Get width in twips (twentieths of a point)
                width_obj = col.width
                if width_obj:
                    # Convert to inches
                    width_inches = width_obj.inches if hasattr(width_obj, 'inches') else width_obj / 914400
                    width_pt = width_inches * 72
                    widths.append(width_pt)
                    total_width += width_pt
                    print(f"    Column {j+1}: {width_pt:.1f}pt ({width_inches:.2f} inches)")
                else:
                    print(f"    Column {j+1}: Auto")
            except Exception as e:
                print(f"    Column {j+1}: Error - {e}")

        # Calculate proportions
        if widths and total_width > 0:
            print(f"  Column proportions:")
            for j, width in enumerate(widths):
                proportion = (width / total_width) * 100
                print(f"    Column {j+1}: {proportion:.1f}%")

            print(f"  Total width: {total_width:.1f}pt ({total_width/72:.2f} inches)")

        # Check if table fits in standard page width (6.5 inches = 468pt)
        if total_width > 468:
            print(f"  WARNING: Table exceeds standard page width!")
        else:
            print(f"  OK: Table fits within page width")

        # Display first row content for context
        if len(table.rows) > 0:
            print(f"  First row content:")
            for j, cell in enumerate(table.rows[0].cells[:5]):  # Show max 5 columns
                text = cell.text[:50] if cell.text else "(empty)"
                print(f"    Cell {j+1}: {text}...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = "oversear_monthly_report_part1_test.docx"

    analyze_table_widths(docx_path)