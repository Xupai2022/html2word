from bs4 import BeautifulSoup
import re

# Read the HTML file
with open('oversear_monthly_report.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all divs with square-title class
square_divs = soup.find_all('div', class_='square-title')
print(f"Found {len(square_divs)} divs with square-title class")

for div in square_divs:
    print(f"\nText: {div.get_text()}")
    print(f"Class: {div.get('class')}")

# Also search for the specific text
import re
pattern = re.compile(r'Assets Requiring Attention')
matches = soup.find_all(string=pattern)
print(f"\nFound {len(matches)} text matches for 'Assets Requiring Attention'")
for match in matches:
    print(f"Text: '{match}'")
    parent = match.parent
    print(f"Parent: {parent.name}, class: {parent.get('class')}")