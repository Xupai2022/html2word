from bs4 import BeautifulSoup
import re

# Read the HTML file
with open('oversear_monthly_report.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the Assets Requiring Attention title
title = soup.find('div', string=re.compile(r'Assets Requiring Attention'))
if title:
    print(f"Found title: {title.get_text()}")
    print(f"Tag: {title.name}")
    print(f"Class attribute: {title.get('class')}")
    print(f"Class type: {type(title.get('class'))}")

    # Check if class is a list
    classes = title.get('class', [])
    if isinstance(classes, list):
        print(f"Classes: {classes}")
    else:
        print(f"Class: {classes}")