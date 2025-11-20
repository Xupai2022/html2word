"""
Parser module - Handles HTML and CSS parsing.

This module provides functionality to parse HTML documents and extract
inline CSS styles, building an enhanced DOM tree with style information.
"""

from html2word.parser.html_parser import HTMLParser
from html2word.parser.css_parser import CSSParser
from html2word.parser.dom_tree import DOMNode, DOMTree

__all__ = ["HTMLParser", "CSSParser", "DOMNode", "DOMTree"]
