#!/usr/bin/env python
"""Debug margin calculations."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.parser.html_parser import HTMLParser
from html2word.style.box_model import BoxModel

def analyze_element(node, name=""):
    """Analyze an element's margins."""
    if not node.is_element:
        return

    elem_class = node.get_attribute('class', '')
    if elem_class:
        box_model = BoxModel(node)
        print(f"\n{name or node.tag} (class='{elem_class}'):")
        print(f"  margin-top: {box_model.margin.top}pt")
        print(f"  margin-bottom: {box_model.margin.bottom}pt")
        print(f"  CSS margin-bottom: {node.computed_styles.get('margin-bottom', 'not set')}")
        print(f"  CSS margin-top: {node.computed_styles.get('margin-top', 'not set')}")
        print(f"  display: {node.computed_styles.get('display', 'block')}")

def find_by_class(node, class_name, depth=0):
    """Find first element with class."""
    if not hasattr(node, 'is_element'):
        return None

    elem_class = node.get_attribute('class', '') if hasattr(node, 'get_attribute') else ''
    # Check if class_name is exactly in the class list
    if isinstance(elem_class, list):
        classes = elem_class
    elif isinstance(elem_class, str):
        classes = elem_class.split() if elem_class else []
    else:
        classes = []

    if class_name in classes:
        print(f"  Found at depth {depth}: {node.tag}.{classes}")
        return node

    # Recurse into children
    if hasattr(node, 'children'):
        for child in node.children:
            result = find_by_class(child, class_name, depth + 1)
            if result:
                return result
    return None

def main():
    html_file = 'security_quarterly_report.html'

    print("="*80)
    print("Margin Analysis from HTML")
    print("="*80)

    parser = HTMLParser()
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    tree = parser.parse(html_content)
    body = tree.root  # Use root instead

    print(f"\nRoot node: tag={body.tag}, is_element={body.is_element}, children={len(body.children)}")

    # Expected: 30px = 22.5pt (30 * 0.75)
    print("\n1px = 0.75pt in CSS-to-Word conversion")
    print("30px should be 22.5pt")
    print("20px should be 15pt")
    print("40px should be 30pt")

    elements = [
        ('executive-summary', 'Executive Summary'),
        ('risk-overview', 'Risk Overview'),
        ('metric-grid', 'Metric Grid'),
        ('section', 'Section'),
    ]

    for class_name, display_name in elements:
        elem = find_by_class(body, class_name)
        if elem:
            analyze_element(elem, display_name)
        else:
            print(f"\n{display_name}: NOT FOUND")

if __name__ == '__main__':
    main()
