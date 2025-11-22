"""
Test SVG serialization to find the actual problem.
"""

import sys
sys.path.insert(0, '.')

from src.html2word.parser.html_parser import HTMLParser
from src.html2word.word_builder.image_builder import ImageBuilder
import xml.etree.ElementTree as ET

# Parse the HTML
parser = HTMLParser()
print("Parsing HTML...")
with open('oversear_monthly_report_part1_final.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

dom_tree = parser.parse(html_content)
print(f"Parsed DOM tree with {len(list(dom_tree.get_all_nodes()))} nodes")

# Find all SVG nodes
svg_nodes = []
for node in dom_tree.get_all_nodes():
    if node.is_element and node.tag == 'svg':
        svg_nodes.append(node)

print(f"Found {len(svg_nodes)} SVG nodes")

# Test serialization
image_builder = ImageBuilder(None)
failed_count = 0

for i, svg_node in enumerate(svg_nodes):
    width = svg_node.get_attribute('width') or svg_node.computed_styles.get('width', '20')
    height = svg_node.get_attribute('height') or svg_node.computed_styles.get('height', '20')

    try:
        svg_content = image_builder._serialize_svg_node(svg_node, width, height)

        # Try to parse the serialized content
        ET.fromstring(svg_content)
        print(f"SVG {i+1}: OK ({len(svg_content)} chars)")

    except ET.ParseError as e:
        failed_count += 1
        print(f"SVG {i+1}: FAILED - {e}")
        print(f"  Position: {e.position}")
        print(f"  Content length: {len(svg_content) if 'svg_content' in locals() else 'N/A'}")

        # Save problematic content
        if 'svg_content' in locals():
            with open(f'problem_svg_{i+1}.xml', 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"  Saved to problem_svg_{i+1}.xml")
        print()

print(f"\n\nSummary: {len(svg_nodes)} SVGs, {failed_count} failed serialization")
