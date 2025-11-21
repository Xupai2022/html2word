#!/usr/bin/env python
"""Debug CSS parsing and application."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html2word.parser.html_parser import HTMLParser

def main():
    html_file = 'security_quarterly_report.html'

    parser = HTMLParser()
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Parsing HTML...")
    tree = parser.parse(html_content)

    print(f"CSS rules parsed: {parser.stylesheet_manager.get_rule_count()}")

    # Find executive-summary
    def find_elem(node, class_name):
        if hasattr(node, 'get_attribute'):
            elem_class = node.get_attribute('class', '')
            if isinstance(elem_class, list) and class_name in elem_class:
                return node
        if hasattr(node, 'children'):
            for child in node.children:
                result = find_elem(child, class_name)
                if result:
                    return result
        return None

    exec_summary = find_elem(tree.root, 'executive-summary')
    if exec_summary:
        print(f"\nExecutive Summary found (BEFORE style resolution):")
        print(f"  inline_styles keys: {list(exec_summary.inline_styles.keys())}")
        print(f"  computed_styles keys: {list(exec_summary.computed_styles.keys())}")
        print(f"  margin-bottom in inline_styles: {'margin-bottom' in exec_summary.inline_styles}")
        print(f"  margin-bottom in computed_styles: {'margin-bottom' in exec_summary.computed_styles}")

        # Now apply style resolution
        from html2word.style.style_resolver import StyleResolver
        resolver = StyleResolver()
        print(f"\nApplying style resolution...")
        resolver.resolve_styles(tree)

        print(f"\nExecutive Summary (AFTER style resolution):")
        print(f"  inline_styles keys: {list(exec_summary.inline_styles.keys())}")
        print(f"  computed_styles keys: {list(exec_summary.computed_styles.keys())}")
        print(f"  margin-bottom in inline_styles: {'margin-bottom' in exec_summary.inline_styles}")
        print(f"  margin-bottom in computed_styles: {'margin-bottom' in exec_summary.computed_styles}")
        if 'margin-bottom' in exec_summary.computed_styles:
            print(f"  margin-bottom value: {exec_summary.computed_styles['margin-bottom']}")

        # Check all margin/padding styles
        if exec_summary.computed_styles:
            print(f"\n  All margin/padding styles:")
            for key, value in sorted(exec_summary.computed_styles.items()):
                if 'margin' in key or 'padding' in key:
                    print(f"    {key}: {value}")

if __name__ == '__main__':
    main()
