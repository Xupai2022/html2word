#!/usr/bin/env python
"""Test margin centering detection logic"""

from src.html2word.parser.html_parser import HTMLParser
from src.html2word.style.style_resolver import StyleResolver

def test_margin_detection():
    html_file = "oversear_monthly_report_part1.html"

    print("Parsing HTML...")
    parser = HTMLParser()
    dom_tree = parser.parse_file(html_file)

    print("Resolving styles...")
    resolver = StyleResolver()
    resolver.resolve_styles(dom_tree)

    # Find level-svg img
    def find_and_test(node):
        if node.is_element:
            classes = node.get_attribute('class', '')
            if 'level-svg' in classes:
                print(f"\nFound level-svg div:")
                print(f"  margin: {node.computed_styles.get('margin', 'none')}")
                print(f"  margin-left: {node.computed_styles.get('margin-left', 'none')}")
                print(f"  margin-right: {node.computed_styles.get('margin-right', 'none')}")

                # Find img child
                for child in node.children:
                    if child.is_element and child.tag == 'img':
                        print(f"\nFound img in level-svg:")
                        print(f"  img margin: {child.computed_styles.get('margin', 'none')}")
                        print(f"  img margin-left: {child.computed_styles.get('margin-left', 'none')}")
                        print(f"  img margin-right: {child.computed_styles.get('margin-right', 'none')}")

                        # Test the logic
                        parent_margin = node.computed_styles.get('margin', '')
                        print(f"\nTesting detection logic:")
                        print(f"  parent_margin = '{parent_margin}'")
                        if parent_margin:
                            parts = str(parent_margin).split()
                            print(f"  parts = {parts}")
                            print(f"  'auto' in parts = {'auto' in parts}")
                            print(f"  len(parts) = {len(parts)}")
                            if 'auto' in parts and len(parts) == 3:
                                print(f"  parts[1] = '{parts[1]}'")
                                print(f"  Should be centered: {parts[1] == 'auto'}")
                        return True

        for child in node.children:
            if find_and_test(child):
                return True
        return False

    find_and_test(dom_tree.root)

if __name__ == "__main__":
    test_margin_detection()
