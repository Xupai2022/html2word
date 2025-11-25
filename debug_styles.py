#!/usr/bin/env python
"""Debug computed styles for level-svg image"""

from src.html2word.parser.html_parser import HTMLParser
from src.html2word.style.style_resolver import StyleResolver

def debug_level_svg_styles():
    html_file = "oversear_monthly_report_part1.html"

    print("Parsing HTML...")
    parser = HTMLParser()
    dom_tree = parser.parse_file(html_file)

    print("Resolving styles...")
    resolver = StyleResolver()
    resolver.resolve_styles(dom_tree)

    # Find the level-svg div and its img
    def find_level_svg(node, depth=0):
        if node.is_element:
            classes = node.get_attribute('class', '')
            if 'level-svg' in classes:
                print(f"\nFound level-svg div at depth {depth}:")
                print(f"  Tag: {node.tag}")
                print(f"  Classes: {classes}")
                print(f"  Computed styles:")
                for key, value in node.computed_styles.items():
                    if 'margin' in key or 'align' in key or 'display' in key:
                        print(f"    {key}: {value}")

                # Find img child
                for child in node.children:
                    if child.is_element and child.tag == 'img':
                        print(f"\n  Found img child:")
                        print(f"    Tag: {child.tag}")
                        print(f"    Computed styles:")
                        for key, value in child.computed_styles.items():
                            if 'margin' in key or 'align' in key or 'display' in key:
                                print(f"      {key}: {value}")
                        return True

        for child in node.children:
            if find_level_svg(child, depth+1):
                return True
        return False

    find_level_svg(dom_tree.root)

if __name__ == "__main__":
    debug_level_svg_styles()
