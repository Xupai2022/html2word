#!/usr/bin/env python
"""Simple debug to print tree structure."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.parser.html_parser import HTMLParser

def print_tree(node, depth=0, max_depth=5):
    """Print tree structure."""
    if depth > max_depth:
        return

    indent = "  " * depth
    tag = node.tag if hasattr(node, 'tag') else '?'
    elem_class = node.get_attribute('class', '') if hasattr(node, 'get_attribute') else ''
    class_str = f" class='{elem_class}'" if elem_class else ''

    print(f"{indent}{tag}{class_str}")

    if hasattr(node, 'children'):
        for i, child in enumerate(node.children):
            if i > 10 and depth > 2:  # Limit output
                print(f"{indent}  ... ({len(node.children) - i} more children)")
                break
            print_tree(child, depth + 1, max_depth)

def main():
    parser = HTMLParser()
    with open('security_quarterly_report.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    tree = parser.parse(html_content)

    print("Tree structure:")
    print_tree(tree.root, max_depth=4)

if __name__ == '__main__':
    main()
