"""
Test script to reproduce section merging issue
"""

from bs4 import BeautifulSoup
import re

# Read HTML file
with open('oversear_monthly_report_part1.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the sections and text between them
endpoint_text = soup.find(string=re.compile('Endpoint-Side Log Trend'))
security_text = soup.find(string=re.compile('Security Alert Trend.*Unit.*Thousand'))
based_text = soup.find(string=re.compile('Based on the analysis of all logs'))

if endpoint_text and security_text and based_text:
    # Find parent sections
    endpoint_section = endpoint_text.find_parent('section')
    security_section = security_text.find_parent('section')

    # Find the structure around the middle text
    based_element = based_text.parent if based_text else None

    print("=== STRUCTURE ANALYSIS ===")
    print(f"1. Endpoint section found: {endpoint_section is not None}")
    print(f"   - Section class: {endpoint_section.get('class') if endpoint_section else 'N/A'}")

    print(f"\n2. Middle text found: {based_text[:50] if based_text else 'N/A'}")
    if based_element:
        print(f"   - Parent tag: {based_element.name}")
        print(f"   - Parent class: {based_element.get('class')}")
        # Check siblings
        prev_sibling = based_element.find_previous_sibling()
        next_sibling = based_element.find_next_sibling()
        print(f"   - Previous sibling: {prev_sibling.name if prev_sibling else 'None'} (class: {prev_sibling.get('class') if prev_sibling else 'N/A'})")
        print(f"   - Next sibling: {next_sibling.name if next_sibling else 'None'} (class: {next_sibling.get('class') if next_sibling else 'N/A'})")

    print(f"\n3. Security section found: {security_section is not None}")
    print(f"   - Section class: {security_section.get('class') if security_section else 'N/A'}")

    # Check if sections are siblings
    if endpoint_section and security_section:
        # Find common parent
        endpoint_parent = endpoint_section.parent
        security_parent = security_section.parent

        if endpoint_parent == security_parent:
            print(f"\n4. Both sections are siblings in parent: {endpoint_parent.name}")

            # Get all children between the two sections
            all_siblings = list(endpoint_parent.children)
            endpoint_idx = all_siblings.index(endpoint_section)
            security_idx = all_siblings.index(security_section)

            elements_between = all_siblings[endpoint_idx + 1:security_idx]

            print(f"   - Elements between sections: {len(elements_between)}")
            for elem in elements_between:
                if hasattr(elem, 'name'):
                    print(f"     * {elem.name}: {elem.get_text()[:100].strip() if elem.get_text() else 'empty'}")
                elif elem.strip():
                    print(f"     * Text node: {elem.strip()[:100]}")
else:
    print("Could not find all required elements")

# Now let's create a simple test case to reproduce the issue
test_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        .chart-panel-wrap {
            border: 1px solid #e0e0e0;
            padding: 16px;
            margin: 20px 0;
            background: #f5f5f5;
        }
        p {
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <section class="chart-panel-wrap">
        <h3>Endpoint-Side Log Trend</h3>
        <table>
            <tr><td>Table 1 content</td></tr>
        </table>
    </section>

    <p>Based on the analysis of all logs using multiple engines, 17464 alerts were generated.</p>

    <section class="chart-panel-wrap">
        <h3>Security Alert Trend (Unit: Thousand)</h3>
        <table>
            <tr><td>Table 2 content</td></tr>
        </table>
    </section>
</body>
</html>
"""

# Save test HTML
with open('test_section_merge.html', 'w', encoding='utf-8') as f:
    f.write(test_html)

print("\n=== TEST HTML CREATED ===")
print("Saved as test_section_merge.html")
print("This simulates the structure causing the issue")