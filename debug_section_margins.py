#!/usr/bin/env python
"""Debug section margins specifically."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.parser.html_parser import HTMLParser
from html2word.style.style_resolver import StyleResolver
from html2word.style.box_model import BoxModel

def find_all_by_class(node, class_name, results=None):
    """Find all elements with class."""
    if results is None:
        results = []

    if hasattr(node, 'get_attribute'):
        elem_class = node.get_attribute('class', '')
        if isinstance(elem_class, list) and class_name in elem_class:
            results.append(node)

    if hasattr(node, 'children'):
        for child in node.children:
            find_all_by_class(child, class_name, results)

    return results

def main():
    html_file = 'security_quarterly_report.html'

    parser = HTMLParser()
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    tree = parser.parse(html_content)

    # Apply style resolution
    resolver = StyleResolver()
    resolver.resolve_styles(tree)

    # Find all section elements
    sections = find_all_by_class(tree.root, 'section')

    print(f"Found {len(sections)} section elements\n")

    for i, section in enumerate(sections):
        print(f"Section {i+1}:")
        print(f"  margin-bottom in computed_styles: {section.computed_styles.get('margin-bottom', 'NOT SET')}")

        # Calculate box model
        box_model = BoxModel(section)
        print(f"  Box model margin-bottom: {box_model.margin.bottom}pt")
        print(f"  Box model margin-top: {box_model.margin.top}pt")

        # Check first child to see what it is
        if section.children:
            first_child = section.children[0]
            if hasattr(first_child, 'tag'):
                print(f"  First child: {first_child.tag}")
        print()

if __name__ == '__main__':
    main()
