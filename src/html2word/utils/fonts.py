"""
Font mapping utilities.

Handles mapping of web fonts to Word-supported fonts using a configuration file.
"""

import os
import yaml
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class FontMapper:
    """Maps web fonts to Word-supported fonts."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize font mapper.

        Args:
            config_path: Path to font mapping YAML file
        """
        self.font_map: Dict[str, str] = {}
        self.default_font = "Calibri"

        if config_path is None:
            # Use default config from package
            config_path = self._get_default_config_path()

        self._load_config(config_path)

    def _get_default_config_path(self) -> str:
        """Get the default font mapping config path."""
        # Get the config directory relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        config_path = os.path.join(project_root, "config", "font_mapping.yaml")
        return config_path

    def _load_config(self, config_path: str):
        """
        Load font mapping from YAML config file.

        Args:
            config_path: Path to YAML config file
        """
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if config:
                        self.font_map = config
                        self.default_font = config.get("default", "Calibri")
                        logger.debug(f"Loaded font mapping from {config_path}")
            else:
                logger.warning(f"Font mapping config not found: {config_path}")
                self._use_fallback_mapping()
        except Exception as e:
            logger.error(f"Error loading font mapping config: {e}")
            self._use_fallback_mapping()

    def _use_fallback_mapping(self):
        """Use fallback font mapping if config cannot be loaded."""
        self.font_map = {
            # Sans-serif
            "Arial": "Arial",
            "Helvetica": "Arial",
            "Verdana": "Verdana",
            "Calibri": "Calibri",
            # Serif
            "Times New Roman": "Times New Roman",
            "Georgia": "Georgia",
            # Monospace
            "Courier New": "Courier New",
            "Consolas": "Consolas",
            # Generic families
            "sans-serif": "Arial",
            "serif": "Times New Roman",
            "monospace": "Courier New",
        }
        self.default_font = "Calibri"

    def map_font(self, font_family: str) -> str:
        """
        Map a web font to a Word-supported font.

        Args:
            font_family: Font family from CSS (can be comma-separated list)

        Returns:
            Word-supported font name

        Examples:
            map_font("Arial") -> "Arial"
            map_font("Helvetica, Arial, sans-serif") -> "Arial"
            map_font("Unknown Font") -> "Calibri" (default)
        """
        if not font_family:
            return self.default_font

        # CSS font-family can be a comma-separated list
        fonts = [f.strip().strip('"').strip("'") for f in font_family.split(",")]

        # Try each font in order
        for font in fonts:
            if font in self.font_map:
                return self.font_map[font]

        # No match found, use default
        logger.debug(f"Font '{font_family}' not found in mapping, using default: {self.default_font}")
        return self.default_font

    def add_mapping(self, web_font: str, word_font: str):
        """
        Add a custom font mapping.

        Args:
            web_font: Web font name
            word_font: Word font name
        """
        self.font_map[web_font] = word_font

    def get_available_fonts(self) -> list[str]:
        """
        Get list of available Word fonts.

        Returns:
            List of Word font names
        """
        return sorted(set(self.font_map.values()))
