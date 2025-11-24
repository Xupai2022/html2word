"""
Debug script to check table conversion process.
"""
from bs4 import BeautifulSoup
import re

# Read HTML
with open('oversear_monthly_report_part1.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find tables near the target text
text_element = soup.find(string=re.compile('Security devices are the first line of defense'))
if text_element:
    # Go up to find containing section
    parent = text_element.parent
    while parent and parent.name not in ['section', 'div', 'body']:
        parent = parent.parent

    if parent:
        # Find all table elements and their classes
        tables = parent.find_all('table')
        print(f'Found {len(tables)} tables in section')

        for i, table in enumerate(tables):
            print(f'\nTable {i+1}:')

            # Get class attribute
            classes = table.get('class', [])
            print(f'  Classes: {classes}')

            # Check parent class
            if table.parent:
                parent_classes = table.parent.get('class', [])
                print(f'  Parent classes: {parent_classes}')

            # Check for thead/tbody
            has_thead = table.find('thead') is not None
            has_tbody = table.find('tbody') is not None
            print(f'  Has thead: {has_thead}, Has tbody: {has_tbody}')

            # Check colgroup
            colgroup = table.find('colgroup')
            if colgroup:
                cols = colgroup.find_all('col')
                print(f'  Colgroup with {len(cols)} columns')

            # Count rows
            rows = table.find_all('tr')
            print(f'  Total rows: {len(rows)}')

            # Check if next sibling is another table
            next_sibling = table.find_next_sibling('table')
            if next_sibling:
                next_classes = next_sibling.get('class', [])
                print(f'  Next table classes: {next_classes}')