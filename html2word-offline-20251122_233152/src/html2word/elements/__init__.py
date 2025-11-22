"""
Elements module - Handles conversion of HTML elements to Word elements.

This module provides converters for different types of HTML elements
(text, lists, tables, images, etc.) to their Word equivalents.
"""

from html2word.elements.base import BaseConverter
from html2word.elements.text_converter import TextConverter
from html2word.elements.list_converter import ListConverter
from html2word.elements.table_converter import TableConverter
from html2word.elements.image_converter import ImageConverter
from html2word.elements.link_converter import LinkConverter

__all__ = [
    "BaseConverter",
    "TextConverter",
    "ListConverter",
    "TableConverter",
    "ImageConverter",
    "LinkConverter",
]
