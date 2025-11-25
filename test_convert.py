"""
Test conversion of section elements
"""

from src.html2word.converter import HTML2WordConverter
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Convert test HTML
converter = HTML2WordConverter()
converter.convert_file('test_section_merge.html', 'test_section_merge_output.docx')

print("Conversion completed! Check test_section_merge_output.docx")