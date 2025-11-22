"""
Style module - Handles CSS style computation and normalization.

This module provides functionality to compute final styles for DOM nodes,
including inheritance, box model calculation, and style normalization.
"""

from html2word.style.style_resolver import StyleResolver
from html2word.style.inheritance import StyleInheritance
from html2word.style.box_model import BoxModel
from html2word.style.style_normalizer import StyleNormalizer

__all__ = ["StyleResolver", "StyleInheritance", "BoxModel", "StyleNormalizer"]
