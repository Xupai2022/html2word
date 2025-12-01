from bs4 import BeautifulSoup
import re

# Read the HTML file
with open('oversear_monthly_report.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all divs with square-title class
title_divs = soup.find_all('div', class_='square-title')

print(f"Found {len(title_divs)} square-title divs:")
for div in title_divs:
    text = div.get_text(strip=True)
    print(f"\nText: '{text}'")
    print(f"Tag: {div.name}")
    print(f"Class: {div.get('class', [])}")
    print(f"Style: {div.get('style', 'No style')}")

    # Check next sibling to see what follows
    next_elem = div.find_next_sibling()
    if next_elem:
        print(f"Next sibling: {next_elem.name}, class: {next_elem.get('class', 'No class')}")
        # Check if it's a table
        table = next_elem.find('table') if next_elem else None
        if table or next_elem.name == 'table':
            print("*** This title is followed by a table! ***")