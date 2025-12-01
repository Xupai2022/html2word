from bs4 import BeautifulSoup
import re

# Read the HTML file
with open('oversear_monthly_report.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all divs containing "Assets Requiring Attention"
divs = soup.find_all('div')
for div in divs:
    if 'Assets Requiring Attention' in div.get_text():
        print(f"Found div with text: {div.get_text()[:50]}...")
        print(f"  Tag: {div.name}")
        print(f"  Class: {div.get('class')}")
        print(f"  Attributes: {list(div.attrs.keys())}")
        for key, value in div.attrs.items():
            print(f"    {key}: {value} (type: {type(value)})")
        break