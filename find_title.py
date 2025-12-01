from bs4 import BeautifulSoup
import re

# Read the HTML file
with open('oversear_monthly_report.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all elements containing "Assets Requiring Attention"
elements = soup.find_all(text=re.compile(r'Assets Requiring Attention'))

print(f"Found {len(elements)} occurrences:")
for elem in elements:
    print(f"\nText: {elem}")
    print(f"Parent tag: {elem.parent.name}")
    print(f"Parent class: {elem.parent.get('class', 'No class')}")
    print(f"Parent style: {elem.parent.get('style', 'No style')}")

    # Go up the tree to find more context
    current = elem.parent
    for i in range(3):
        if current.parent:
            current = current.parent
            print(f"Ancestor {i+1}: {current.name}, class: {current.get('class', 'No class')}")