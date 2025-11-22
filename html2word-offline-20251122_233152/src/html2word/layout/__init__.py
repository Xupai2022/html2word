"""
Layout module - Handles layout computation for DOM elements.

This module provides functionality to compute layout for HTML elements,
including flow layout, block layout, and inline layout.
"""

from html2word.layout.flow_layout import FlowLayout
from html2word.layout.block_layout import BlockLayout
from html2word.layout.inline_layout import InlineLayout
from html2word.layout.position_calculator import PositionCalculator

__all__ = ["FlowLayout", "BlockLayout", "InlineLayout", "PositionCalculator"]
