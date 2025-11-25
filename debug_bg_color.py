
from src.html2word.converter import HTML2WordConverter
import logging

logging.basicConfig(level=logging.DEBUG)

converter = HTML2WordConverter()
converter.convert("test_bg_issue.html", "debug_bg.docx")
