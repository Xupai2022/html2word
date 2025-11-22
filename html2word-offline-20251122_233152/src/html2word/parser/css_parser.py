"""
CSS parser for inline styles and stylesheet rules.

Parses CSS from style attributes, <style> tags, and extracts style properties.
"""

import re
import logging
from typing import Dict, Optional, List, Tuple
import tinycss2

logger = logging.getLogger(__name__)


class CSSParser:
    """Parser for inline CSS styles."""

    # CSS property name pattern
    PROPERTY_PATTERN = re.compile(r'^[a-z-]+$')

    @classmethod
    def parse_inline_style(cls, style_string: str) -> Dict[str, str]:
        """
        Parse inline CSS from style attribute.

        Args:
            style_string: CSS string from style attribute

        Returns:
            Dictionary of property: value pairs

        Examples:
            parse_inline_style("color: red; font-size: 12px")
            -> {"color": "red", "font-size": "12px"}
        """
        if not style_string:
            return {}

        styles = {}

        try:
            # Parse using tinycss2
            declarations = tinycss2.parse_declaration_list(style_string)

            for item in declarations:
                if isinstance(item, tinycss2.ast.Declaration):
                    prop_name = item.name.lower()
                    prop_value = cls._serialize_value(item.value)

                    if prop_value:
                        styles[prop_name] = prop_value

        except Exception as e:
            logger.warning(f"Error parsing CSS with tinycss2: {e}, falling back to simple parser")
            # Fallback to simple parsing
            styles = cls._parse_simple(style_string)

        # Expand shorthand properties
        styles = cls._expand_shorthands(styles)

        return styles

    @classmethod
    def _serialize_value(cls, tokens) -> str:
        """
        Serialize CSS token list to string value.

        Args:
            tokens: List of CSS tokens

        Returns:
            Serialized value string
        """
        parts = []
        for token in tokens:
            if isinstance(token, tinycss2.ast.WhitespaceToken):
                # Skip leading/trailing whitespace, but preserve internal spaces
                if parts:
                    parts.append(" ")
            elif isinstance(token, tinycss2.ast.IdentToken):
                parts.append(token.value)
            elif isinstance(token, tinycss2.ast.NumberToken):
                parts.append(str(token.value))
            elif isinstance(token, tinycss2.ast.PercentageToken):
                parts.append(f"{token.value}%")
            elif isinstance(token, tinycss2.ast.DimensionToken):
                parts.append(f"{token.value}{token.unit}")
            elif isinstance(token, tinycss2.ast.HashToken):
                parts.append(f"#{token.value}")
            elif isinstance(token, tinycss2.ast.StringToken):
                parts.append(token.value)
            elif isinstance(token, tinycss2.ast.URLToken):
                parts.append(f"url({token.value})")
            elif isinstance(token, tinycss2.ast.FunctionBlock):
                # Handle function blocks like rgb(), rgba()
                func_content = cls._serialize_value(token.arguments)
                parts.append(f"{token.name}({func_content})")
            else:
                # Fallback: serialize the token
                parts.append(tinycss2.serialize([token]))

        # Clean up multiple spaces
        result = "".join(parts).strip()
        result = re.sub(r'\s+', ' ', result)
        return result

    @classmethod
    def _parse_simple(cls, style_string: str) -> Dict[str, str]:
        """
        Simple fallback CSS parser.

        Args:
            style_string: CSS string

        Returns:
            Dictionary of property: value pairs
        """
        styles = {}

        # Split by semicolon
        declarations = style_string.split(';')

        for decl in declarations:
            decl = decl.strip()
            if not decl:
                continue

            # Split by first colon
            parts = decl.split(':', 1)
            if len(parts) != 2:
                continue

            prop_name = parts[0].strip().lower()
            prop_value = parts[1].strip()

            if prop_name and prop_value:
                styles[prop_name] = prop_value

        return styles

    @classmethod
    def parse_border(cls, border_string: str) -> Dict[str, str]:
        """
        Parse CSS border shorthand property.

        Args:
            border_string: Border value (e.g., "1px solid red")

        Returns:
            Dictionary with border-width, border-style, border-color

        Examples:
            parse_border("1px solid red")
            -> {"border-width": "1px", "border-style": "solid", "border-color": "red"}
        """
        result = {
            'border-width': '',
            'border-style': '',
            'border-color': ''
        }

        if not border_string:
            return result

        parts = border_string.strip().split()

        border_styles = ['none', 'hidden', 'dotted', 'dashed', 'solid', 'double', 'groove', 'ridge', 'inset', 'outset']
        border_widths = ['thin', 'medium', 'thick']

        for part in parts:
            part_lower = part.lower()

            # Check if it's a style
            if part_lower in border_styles:
                result['border-style'] = part_lower
            # Check if it's a width keyword
            elif part_lower in border_widths:
                result['border-width'] = part_lower
            # Check if it's a width with unit
            elif re.match(r'^[\d.]+[a-z]+$', part_lower):
                result['border-width'] = part_lower
            # Otherwise assume it's a color
            else:
                result['border-color'] = part

        return result

    @classmethod
    def parse_font(cls, font_string: str) -> Dict[str, str]:
        """
        Parse CSS font shorthand property.

        Args:
            font_string: Font value (e.g., "bold 12px Arial, sans-serif")

        Returns:
            Dictionary with font properties

        Note: This is a simplified parser for basic font declarations
        """
        result = {}

        if not font_string:
            return result

        parts = font_string.strip().split()

        font_styles = ['normal', 'italic', 'oblique']
        font_weights = ['normal', 'bold', 'bolder', 'lighter'] + [str(i) for i in range(100, 1000, 100)]

        i = 0
        while i < len(parts):
            part = parts[i]
            part_lower = part.lower()

            # Check font-style
            if part_lower in font_styles:
                result['font-style'] = part_lower
            # Check font-weight
            elif part_lower in font_weights:
                result['font-weight'] = part_lower
            # Check font-size
            elif re.match(r'^[\d.]+[a-z%]+$', part_lower):
                result['font-size'] = part_lower
            # Remaining parts are font-family
            else:
                # Join remaining parts as font-family
                result['font-family'] = ' '.join(parts[i:])
                break

            i += 1

        return result

    @classmethod
    def _expand_shorthands(cls, styles: Dict[str, str]) -> Dict[str, str]:
        """
        Expand CSS shorthand properties.

        Args:
            styles: Dictionary of CSS properties

        Returns:
            Dictionary with expanded properties
        """
        expanded = styles.copy()

        # Expand border shorthand
        if 'border' in styles:
            border_parts = cls.parse_border(styles['border'])
            if border_parts.get('border-width'):
                expanded['border-width'] = border_parts['border-width']
                expanded['border-top-width'] = border_parts['border-width']
                expanded['border-right-width'] = border_parts['border-width']
                expanded['border-bottom-width'] = border_parts['border-width']
                expanded['border-left-width'] = border_parts['border-width']
            if border_parts.get('border-style'):
                expanded['border-style'] = border_parts['border-style']
                expanded['border-top-style'] = border_parts['border-style']
                expanded['border-right-style'] = border_parts['border-style']
                expanded['border-bottom-style'] = border_parts['border-style']
                expanded['border-left-style'] = border_parts['border-style']
            if border_parts.get('border-color'):
                expanded['border-color'] = border_parts['border-color']
                expanded['border-top-color'] = border_parts['border-color']
                expanded['border-right-color'] = border_parts['border-color']
                expanded['border-bottom-color'] = border_parts['border-color']
                expanded['border-left-color'] = border_parts['border-color']

        # Expand border-top, border-right, border-bottom, border-left
        for side in ['top', 'right', 'bottom', 'left']:
            prop_name = f'border-{side}'
            if prop_name in styles:
                border_parts = cls.parse_border(styles[prop_name])
                if border_parts.get('border-width'):
                    expanded[f'border-{side}-width'] = border_parts['border-width']
                if border_parts.get('border-style'):
                    expanded[f'border-{side}-style'] = border_parts['border-style']
                if border_parts.get('border-color'):
                    expanded[f'border-{side}-color'] = border_parts['border-color']

        # Handle background property with gradients
        if 'background' in styles and 'background-color' not in styles:
            bg_color = cls._extract_background_color(styles['background'])
            if bg_color:
                expanded['background-color'] = bg_color

        # Expand gap shorthand (for grid/flex layouts)
        # gap can be: "20px" (both) or "20px 15px" (row column)
        if 'gap' in styles:
            gap_value = styles['gap'].strip()
            parts = gap_value.split()

            if len(parts) == 1:
                # Single value: applies to both row-gap and column-gap
                expanded['row-gap'] = parts[0]
                expanded['column-gap'] = parts[0]
            elif len(parts) >= 2:
                # Two values: row-gap column-gap
                expanded['row-gap'] = parts[0]
                expanded['column-gap'] = parts[1]

        return expanded

    @classmethod
    def _extract_background_color(cls, background_value: str) -> Optional[str]:
        """
        Extract a solid color from background property.

        Handles linear-gradient by extracting and blending colors for better visual approximation.

        Args:
            background_value: Background property value

        Returns:
            Extracted color or None
        """
        bg_lower = background_value.strip().lower()

        # Check for linear-gradient
        if 'linear-gradient' in bg_lower:
            # Extract colors from gradient
            # Pattern: linear-gradient(direction, color1, color2, ...)
            gradient_match = re.search(r'linear-gradient\s*\([^)]+\)', bg_lower, re.IGNORECASE)
            if gradient_match:
                gradient_content = gradient_match.group(0)
                # Extract colors (hex, rgb, rgba, or named colors)
                color_patterns = [
                    r'#[0-9a-f]{6}',  # hex colors
                    r'#[0-9a-f]{3}',  # short hex colors
                    r'rgba?\s*\([^)]+\)',  # rgb/rgba colors
                    r'\b(?:red|blue|green|white|black|yellow|gray|grey|cyan|magenta|orange|purple|pink|brown|[a-z]+)\b'  # named colors
                ]

                extracted_colors = []
                for pattern in color_patterns:
                    colors = re.findall(pattern, gradient_content)
                    for color in colors:
                        # Skip direction keywords
                        if color not in ('to', 'top', 'bottom', 'left', 'right', 'deg'):
                            extracted_colors.append(color)

                if extracted_colors:
                    # For better visual approximation, prefer the first substantial color
                    # This gives a better representation than always using the first color
                    return extracted_colors[0]

        # Check for radial-gradient
        elif 'radial-gradient' in bg_lower:
            gradient_match = re.search(r'radial-gradient\s*\([^)]+\)', bg_lower, re.IGNORECASE)
            if gradient_match:
                gradient_content = gradient_match.group(0)
                color_patterns = [
                    r'#[0-9a-f]{6}',
                    r'#[0-9a-f]{3}',
                    r'rgba?\s*\([^)]+\)',
                ]

                for pattern in color_patterns:
                    colors = re.findall(pattern, gradient_content)
                    if colors:
                        return colors[0]

        # Check if it's just a color value (not a gradient)
        else:
            # Try to detect if it's a color (hex, rgb, or named color)
            color_test = re.match(r'^(#[0-9a-f]{3,6}|rgba?\s*\([^)]+\)|[a-z]+)$', bg_lower)
            if color_test:
                return bg_lower

        return None

    @classmethod
    def normalize_property_name(cls, prop_name: str) -> str:
        """
        Normalize CSS property name.

        Args:
            prop_name: Property name (can be camelCase or kebab-case)

        Returns:
            Normalized property name in kebab-case

        Examples:
            normalize_property_name("fontSize") -> "font-size"
            normalize_property_name("font-size") -> "font-size"
        """
        # Convert camelCase to kebab-case
        result = re.sub(r'([a-z])([A-Z])', r'\1-\2', prop_name)
        return result.lower()

    @classmethod
    def parse_stylesheet(cls, css_string: str) -> List[Tuple[str, Dict[str, str]]]:
        """
        Parse CSS stylesheet and extract rules.

        Args:
            css_string: CSS stylesheet content

        Returns:
            List of (selector, styles_dict) tuples

        Examples:
            parse_stylesheet(".foo { color: red; } #bar { font-size: 12px; }")
            -> [(".foo", {"color": "red"}), ("#bar", {"font-size": "12px"})]
        """
        if not css_string:
            return []

        rules = []

        try:
            # Parse stylesheet using tinycss2
            parsed_rules = tinycss2.parse_stylesheet(css_string)

            logger.debug(f"Parsing {len(parsed_rules)} CSS rules...")

            for idx, rule in enumerate(parsed_rules):
                # Log progress for large stylesheets
                if idx > 0 and idx % 1000 == 0:
                    logger.info(f"Parsed {idx}/{len(parsed_rules)} CSS rules...")

                if isinstance(rule, tinycss2.ast.QualifiedRule):
                    # Extract selector
                    selector_tokens = rule.prelude
                    selector = cls._serialize_value(selector_tokens).strip()

                    # Skip pseudo-element selectors that don't affect Word conversion
                    # These include ::before, ::after, :hover, :focus, etc.
                    if any(pseudo in selector for pseudo in ['::before', '::after', ':before', ':after',
                                                              ':hover', ':focus', ':active', ':visited',
                                                              ':link', ':enabled', ':disabled']):
                        continue

                    # Extract declarations
                    content = rule.content
                    if content:
                        declarations = tinycss2.parse_declaration_list(content)
                        styles = {}

                        for item in declarations:
                            if isinstance(item, tinycss2.ast.Declaration):
                                prop_name = item.name.lower()
                                prop_value = cls._serialize_value(item.value)

                                if prop_value:
                                    styles[prop_name] = prop_value

                        # Expand shorthand properties
                        styles = cls._expand_shorthands(styles)

                        if selector and styles:
                            rules.append((selector, styles))

                # Skip @-rules that are not relevant for Word conversion
                # This includes @font-face, @keyframes, @media, etc.
                elif isinstance(rule, tinycss2.ast.AtRule):
                    # Skip all @-rules as they don't directly affect Word conversion
                    continue

        except Exception as e:
            logger.warning(f"Error parsing CSS stylesheet with tinycss2: {e}, falling back to simple parser")
            # Fallback to simple parsing
            rules = cls._parse_stylesheet_simple(css_string)

        logger.debug(f"Extracted {len(rules)} CSS rules (filtered from original)")
        return rules

    @classmethod
    def _parse_stylesheet_simple(cls, css_string: str) -> List[Tuple[str, Dict[str, str]]]:
        """
        Simple fallback CSS stylesheet parser.

        Args:
            css_string: CSS stylesheet content

        Returns:
            List of (selector, styles_dict) tuples
        """
        rules = []

        # Remove comments
        css_string = re.sub(r'/\*.*?\*/', '', css_string, flags=re.DOTALL)

        # Remove @-rules (like @font-face, @keyframes, @media)
        # These are not relevant for Word conversion
        css_string = re.sub(r'@[^{]+\{[^}]*\}', '', css_string, flags=re.DOTALL)
        # Handle nested @-rules like @media
        css_string = re.sub(r'@[^{]+\{(?:[^{}]|\{[^}]*\})*\}', '', css_string, flags=re.DOTALL)

        # Match CSS rules: selector { declarations }
        rule_pattern = re.compile(r'([^{]+)\{([^}]+)\}', re.DOTALL)

        matches = list(rule_pattern.finditer(css_string))
        logger.debug(f"Found {len(matches)} CSS rule matches in simple parser")

        for idx, match in enumerate(matches):
            # Log progress for large stylesheets
            if idx > 0 and idx % 1000 == 0:
                logger.info(f"Parsed {idx}/{len(matches)} CSS rules (simple parser)...")

            selector = match.group(1).strip()
            declarations = match.group(2).strip()

            # Skip pseudo-element selectors
            if any(pseudo in selector for pseudo in ['::before', '::after', ':before', ':after',
                                                      ':hover', ':focus', ':active', ':visited',
                                                      ':link', ':enabled', ':disabled']):
                continue

            # Parse declarations
            styles = cls._parse_simple(declarations)

            # Expand shorthand properties
            styles = cls._expand_shorthands(styles)

            if selector and styles:
                rules.append((selector, styles))

        logger.debug(f"Extracted {len(rules)} CSS rules from simple parser")
        return rules
