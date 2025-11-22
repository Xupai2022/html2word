"""
Docx module - Handles Word document generation.

This module provides functionality to generate Word documents using python-docx,
including paragraphs, tables, images, and style application.
"""

from html2word.word_builder.document_builder import DocumentBuilder
from html2word.word_builder.paragraph_builder import ParagraphBuilder
from html2word.word_builder.table_builder import TableBuilder
from html2word.word_builder.image_builder import ImageBuilder
from html2word.word_builder.style_mapper import StyleMapper

__all__ = [
    "DocumentBuilder",
    "ParagraphBuilder",
    "TableBuilder",
    "ImageBuilder",
    "StyleMapper",
]
