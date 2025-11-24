"""
Extract the problematic section and convert it separately.
"""
from bs4 import BeautifulSoup
import re

# Read HTML
with open('oversear_monthly_report_part1.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Find the section
text_node = soup.find(string=re.compile('Security devices are the first line of defense'))
if not text_node:
    print("Text not found")
    exit(1)

parent = text_node.parent
while parent and parent.name != 'section':
    parent = parent.parent

if not parent:
    print("Section not found")
    exit(1)

# Get all style tags
style_tags = soup.find_all('style')
styles_content = '\n'.join([str(tag) for tag in style_tags])

# Create standalone HTML
standalone_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    {styles_content}
</head>
<body>
    {parent}
</body>
</html>
"""

# Save to file
with open('problem_section.html', 'w', encoding='utf-8') as f:
    f.write(standalone_html)

print("Extracted section saved to problem_section.html")

# Also save a simplified version for debugging
tables = parent.find_all('table')
simple_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .el-table__header {{ }}
        .el-table__body {{ }}
    </style>
</head>
<body>
    <p>Security devices are the first line of defense against attacks, so ensuring their effectiveness is crucial. During this period, we checked 2 devices and found 7 with risky policy configurations.</p>
    {tables[0] if len(tables) > 0 else ''}
    {tables[1] if len(tables) > 1 else ''}
</body>
</html>
"""

with open('simple_section.html', 'w', encoding='utf-8') as f:
    f.write(simple_html)

print("Simplified section saved to simple_section.html")