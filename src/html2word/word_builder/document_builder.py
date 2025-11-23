"""
Document builder for Word documents.

Main coordinator for building Word documents from DOM trees.
"""

import logging
import math
import re
from typing import Optional
from docx import Document

from html2word.parser.dom_tree import DOMNode, DOMTree
from html2word.word_builder.paragraph_builder import ParagraphBuilder
from html2word.word_builder.table_builder import TableBuilder
from html2word.word_builder.image_builder import ImageBuilder

logger = logging.getLogger(__name__)


class DocumentBuilder:
    """Builds complete Word documents from DOM trees."""

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize document builder.

        Args:
            base_path: Base path for resolving relative paths
        """
        self.base_path = base_path
        self.document = Document()
        self.paragraph_builder = ParagraphBuilder(self.document)
        self.table_builder = TableBuilder(self.document)
        self.image_builder = ImageBuilder(self.document, base_path)
        self.in_table_cell = False  # Track if we're processing content inside a table cell

    def build(self, tree: DOMTree) -> Document:
        """
        Build Word document from DOM tree.

        Args:
            tree: DOM tree

        Returns:
            python-docx Document object
        """
        logger.info("Building Word document")

        # Get body content
        from html2word.parser.html_parser import HTMLParser
        parser = HTMLParser()
        body = parser.get_body_content(tree)

        if body:
            # Process body children
            self._process_children(body)
        else:
            # No body found, process root
            self._process_children(tree.root)

        logger.info("Document built successfully")
        return self.document

    def _process_children(self, node: DOMNode):
        """
        Process child nodes recursively.

        Args:
            node: Parent DOM node
        """
        for child in node.children:
            self._process_node(child)

    def _process_node(self, node: DOMNode):
        """
        Process a single DOM node.

        Args:
            node: DOM node
        """
        if node.is_text:
            # Skip standalone text nodes (they should be inside elements)
            return

        if not node.is_element:
            return

        # Skip elements with position: absolute or position: fixed
        # UNLESS they contain important content (cover pages, titles, tables, etc.)
        position = node.computed_styles.get('position', '')
        if position in ('absolute', 'fixed'):
            # Check if this is a cover page or contains important structural content
            if self._contains_important_content(node):
                logger.debug(f"Processing {node.tag} with position: {position} because it contains important content")
                # Process children directly, ignoring the positioning wrapper
                self._process_children(node)
                return
            else:
                logger.debug(f"Skipping {node.tag} with position: {position}")
                return

        # Route to appropriate builder based on tag
        tag = node.tag

        # Headings
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.paragraph_builder.build_heading(node, level)

        # Paragraphs
        elif tag in ('p', 'blockquote', 'pre'):
            logger.debug(f"Building paragraph for <{tag}>, text: {node.get_text_content()[:50] if hasattr(node, 'get_text_content') else 'N/A'}")
            self.paragraph_builder.build_paragraph(node)

        # Divs - intelligent handling based on layout and styles
        elif tag == 'div':
            # FIXED: display:grid now works correctly after removing default styles
            if self._should_convert_to_grid_table(node):
                # Grid/flex layout - convert to table with horizontal layout
                self._convert_grid_to_table_smart(node)
            elif self._should_wrap_in_styled_table(node):
                # Has background/border - wrap in table to preserve styling
                # But skip if it's a root layout container (like .container)
                if self._is_root_layout_container(node):
                    # Skip wrapping for root layout containers
                    self._process_children(node)
                else:
                    self._wrap_div_in_styled_table(node)
            elif self._should_treat_div_as_paragraph(node):
                # Only inline content - treat as paragraph
                self.paragraph_builder.build_paragraph(node)
            else:
                # Plain container - process children directly
                # NO spacing needed: child elements handle their own margins via space_after
                # This implements CSS margin collapse behavior
                self._process_children(node)

        # Lists
        elif tag in ('ul', 'ol'):
            self._process_list(node)

        # List items (shouldn't appear standalone, but handle it)
        elif tag == 'li':
            self.paragraph_builder.build_paragraph(node)

        # Tables
        elif tag == 'table':
            self.table_builder.build_table(node)

        # Images
        elif tag == 'img':
            self.image_builder.build_image(node)

        # SVG elements
        elif tag == 'svg':
            self._process_svg(node)

        # Line break
        elif tag == 'br':
            self.document.add_paragraph()

        # Horizontal rule
        elif tag == 'hr':
            self._add_horizontal_rule()

        # Container elements - process children directly
        elif tag in ('body', 'html', 'main', 'article', 'section', 'header', 'footer', 'nav', 'aside'):
            # NO spacing needed: child elements handle their own margins via space_after
            # This implements CSS margin collapse behavior naturally
            self._process_children(node)

        # Inline elements - skip (should be handled by paragraph builder)
        elif node.is_inline:
            # Create a paragraph for standalone inline elements
            para = self.document.add_paragraph()
            text = node.get_text_content()
            if text.strip():
                run = para.add_run(text)

        # Unknown elements - process children
        else:
            logger.debug(f"Unknown element: {tag}, processing children")
            self._process_children(node)

    def _process_list(self, list_node: DOMNode):
        """
        Process list (ul/ol) and its items.

        Args:
            list_node: List DOM node
        """
        is_ordered = list_node.tag == 'ol'

        # Get list style
        list_style = list_node.computed_styles.get('list-style-type', 'disc' if not is_ordered else 'decimal')

        for child in list_node.children:
            if child.tag == 'li':
                self._process_list_item(child, is_ordered, list_style)
            elif child.tag in ('ul', 'ol'):
                # Nested list
                self._process_list(child)

    def _process_list_item(self, li_node: DOMNode, is_ordered: bool, list_style: str):
        """
        Process list item.

        Args:
            li_node: List item DOM node
            is_ordered: Whether it's an ordered list
            list_style: List style type
        """
        paragraph = self.paragraph_builder.build_paragraph(li_node)

        if paragraph:
            # Apply list formatting
            if is_ordered:
                paragraph.style = 'List Number'
            else:
                paragraph.style = 'List Bullet'

    def _add_horizontal_rule(self):
        """Add a horizontal rule."""
        # Create a paragraph with bottom border
        paragraph = self.document.add_paragraph()
        fmt = paragraph.paragraph_format
        from docx.shared import Pt
        fmt.space_before = Pt(6)
        fmt.space_after = Pt(6)

        # Add bottom border (simplified)
        paragraph.add_run()

    def _should_treat_div_as_paragraph(self, node: DOMNode) -> bool:
        """
        Determine if a div should be treated as a paragraph or a container.

        Args:
            node: DOM node

        Returns:
            True if should treat as paragraph, False if should treat as container
        """
        # Check if div has any block-level children
        for child in node.children:
            if child.is_element and not child.is_inline:
                # Has block-level children - treat as container
                return False

        # Only has text and inline elements - treat as paragraph
        # But only if it has actual content
        text_content = node.get_text_content().strip()
        if text_content:
            return True

        # Empty or only whitespace - treat as container (will be skipped)
        return False

    def _contains_important_content(self, node: DOMNode) -> bool:
        """
        Check if a node contains important structural content that should be preserved
        even if the node itself has position: absolute/fixed.

        This is used to preserve cover pages, titles, and tables that use absolute
        positioning for layout purposes.

        Args:
            node: DOM node to check

        Returns:
            True if node contains important content
        """
        # Check if node has classes that indicate it's a cover page or important container
        class_attr = node.attributes.get('class', '')
        if isinstance(class_attr, list):
            node_classes = class_attr
        else:
            node_classes = class_attr.split() if class_attr else []
        important_classes = [
            'cover-info--wrapper',  # Cover page wrapper
            'cover-info--title',    # Cover title
            'cover-info-table',     # Cover table
            'export-report__cover', # Export report cover
        ]

        if any(cls in node_classes for cls in important_classes):
            return True

        # Recursively check if any descendant contains important tags
        def has_important_descendants(n: DOMNode) -> bool:
            # Important tags that indicate real content
            important_tags = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'ul', 'ol', 'pre', 'blockquote'}

            if n.tag in important_tags:
                # Check if it has actual text content (not just whitespace)
                text_content = self._get_text_content(n).strip()
                if text_content:
                    return True

            # Check children
            for child in n.children:
                if child.is_element and has_important_descendants(child):
                    return True

            return False

        return has_important_descendants(node)

    def _get_text_content(self, node: DOMNode) -> str:
        """
        Get all text content from a node and its descendants.

        Args:
            node: DOM node

        Returns:
            Concatenated text content
        """
        if node.is_text:
            return node.text

        text_parts = []
        for child in node.children:
            if child.is_text:
                text_parts.append(child.text)
            elif child.is_element:
                text_parts.append(self._get_text_content(child))

        return ''.join(text_parts)

    def _should_convert_to_grid_table(self, node: DOMNode) -> bool:
        """
        Check if div uses grid/flex layout and should be converted to table.

        Args:
            node: DOM node

        Returns:
            True if should convert to table
        """
        if not node.computed_styles:
            return False

        display = node.computed_styles.get('display', '')

        # Check for grid or flex with multiple children
        if 'grid' in display or 'flex' in display:
            # FIXED: Count ALL element children, not just block-level
            # In flex/grid layouts, img and svg are inline but should be treated as flex/grid items
            child_elements = [c for c in node.children if c.is_element]
            # Only convert if has 2+ children (grid/flex items)
            if len(child_elements) >= 2:
                logger.debug(f"Detected {display} layout with {len(child_elements)} children, converting to table")
                return True

        return False

    def _should_wrap_in_styled_table(self, node: DOMNode) -> bool:
        """
        Check if div has significant styling that requires table wrapper.

        Args:
            node: DOM node

        Returns:
            True if needs table wrapper for styling
        """
        # CRITICAL: If already inside a table cell, do NOT wrap in another table
        # This prevents nested table creation and eliminates duplicate spacing
        if self.in_table_cell:
            logger.debug(f"Skipping table wrap for {node.tag} (already in cell)")
            return False

        if not node.computed_styles:
            return False

        # Check for important visual styles FIRST
        styles = node.computed_styles

        # Check background property first (for gradients)
        has_non_white_bg = False
        bg_prop = styles.get('background', '')
        if bg_prop and bg_prop not in ('', 'none', 'transparent'):
            bg_lower = bg_prop.lower()
            # Gradient always counts as meaningful background
            if 'gradient' in bg_lower:
                has_non_white_bg = True

        # Check background-color
        bg_color = styles.get('background-color', '')
        if bg_color and bg_color not in ('', 'transparent', 'rgba(0, 0, 0, 0)', 'rgba(0,0,0,0)'):
            bg_lower = bg_color.lower()
            # Check if it's white/very light (likely just layout container)
            is_white = (
                bg_lower in ('#fff', '#ffffff', 'white', 'rgb(255,255,255)', 'rgb(255, 255, 255)') or
                bg_lower.startswith('#fff') or
                'rgb(255,255,255)' in bg_lower.replace(' ', '')
            )

            if not is_white:
                has_non_white_bg = True
                logger.debug(f"Has non-white background: {bg_color}")
            else:
                logger.debug(f"Ignoring white background: {bg_color}")

        # Borders - only count if it's a full border with non-white color
        has_border = False
        border_count = 0
        for side in ['top', 'right', 'bottom', 'left']:
            width_key = f'border-{side}-width'
            color_key = f'border-{side}-color'

            # Check if border exists (non-zero width)
            if width_key in styles and styles.get(width_key, '0') not in ('0', '0px', 'none'):
                # Check if border color is not white/transparent
                border_color = styles.get(color_key, '').lower()
                is_white_border = (
                    border_color in ('', 'transparent', '#fff', '#ffffff', 'white',
                                   'rgb(255,255,255)', 'rgb(255, 255, 255)') or
                    border_color.startswith('#fff') or
                    'rgb(255,255,255)' in border_color.replace(' ', '')
                )

                # Only count non-white borders
                if not is_white_border:
                    border_count += 1

        # Only consider it styled if it has 3+ sides bordered (like a box)
        if border_count >= 3:
            has_border = True

        # Box shadow
        has_shadow = 'box-shadow' in styles and styles['box-shadow'] not in ('none', '')

        # Check if has meaningful visual styling
        has_visual_styling = has_non_white_bg or has_border or has_shadow

        # If has visual styling, always wrap (even for simple content)
        if has_visual_styling:
            return True

        # No visual styling - only wrap if has block-level children
        has_block_children = any(
            c.is_element and not c.is_inline
            for c in node.children
        )

        return has_block_children

    def _convert_grid_to_table(self, grid_node: DOMNode):
        """
        Convert a grid/flex container to a Word table.

        Args:
            grid_node: DOM node with grid/flex layout
        """
        try:
            # Get grid properties
            display = grid_node.computed_styles.get('display', '')
            grid_template_cols = grid_node.computed_styles.get('grid-template-columns', '')

            # Collect direct children (grid items)
            child_elements = [child for child in grid_node.children if child.is_element]

            if not child_elements:
                # No children, render as paragraph
                self.paragraph_builder.build_paragraph(grid_node)
                return

            # Determine number of columns
            num_cols = self._determine_grid_columns(grid_template_cols, len(child_elements))

            # Calculate number of rows
            num_rows = (len(child_elements) + num_cols - 1) // num_cols

            logger.debug(f"Creating table from grid: {num_rows} rows × {num_cols} columns")

            # Create table
            table = self.document.add_table(rows=num_rows, cols=num_cols)

            # Fill table with grid items
            cell_index = 0
            for row_idx in range(num_rows):
                for col_idx in range(num_cols):
                    if cell_index < len(child_elements):
                        child = child_elements[cell_index]
                        cell = table.rows[row_idx].cells[col_idx]

                        # Add child content to cell
                        # Get text content and add as paragraph
                        text_content = child.get_text_content()
                        if text_content.strip():
                            paragraph = cell.paragraphs[0]
                            paragraph.text = text_content.strip()

                            # Apply styles from child to cell
                            if child.computed_styles:
                                from html2word.word_builder.style_mapper import StyleMapper
                                mapper = StyleMapper()
                                mapper.apply_table_cell_style(cell, child.computed_styles, child.box_model)

                        cell_index += 1

            # Apply grid container styles to table
            if grid_node.computed_styles:
                # Apply background color if present
                bg_color = grid_node.computed_styles.get('background-color')
                if bg_color:
                    # Apply to all cells
                    for row in table.rows:
                        for cell in row.cells:
                            if cell.paragraphs:
                                from html2word.word_builder.style_mapper import StyleMapper
                                mapper = StyleMapper()
                                # Create temporary style dict for background
                                temp_styles = {'background-color': bg_color}
                                mapper.apply_table_cell_style(cell, temp_styles)

        except Exception as e:
            logger.warning(f"Error converting grid to table: {e}, falling back to paragraph")
            # Fallback: render as paragraph
            self.paragraph_builder.build_paragraph(grid_node)

    def _convert_grid_to_table_smart(self, grid_node: DOMNode):
        """
        Intelligently convert grid/flex layout to table, preserving nested structure.

        Args:
            grid_node: DOM node with grid/flex layout
        """
        try:
            grid_template_cols = grid_node.computed_styles.get('grid-template-columns', '')
            flex_wrap = grid_node.computed_styles.get('flex-wrap', 'nowrap')
            display = grid_node.computed_styles.get('display', '')

            # FIXED: Count ALL element children (including inline like img, svg)
            child_elements = [c for c in grid_node.children if c.is_element]

            if not child_elements:
                self._process_children(grid_node)
                return

            # Determine columns based on layout type
            if 'flex' in display:
                # For flex layouts, determine columns based on flex-wrap
                num_cols = self._determine_flex_columns(flex_wrap, len(child_elements))
            else:
                # For grid layouts, use grid-template-columns
                num_cols = self._determine_grid_columns(grid_template_cols, len(child_elements))

            num_rows = (len(child_elements) + num_cols - 1) // num_cols

            logger.debug(f"Creating smart grid table: {num_rows}×{num_cols}")

            # Create table (no spacing before - previous element's space_after handles that)
            table = self.document.add_table(rows=num_rows, cols=num_cols)

            # Apply gap as table cell spacing (read from HTML, not hardcoded)
            self._apply_grid_gap_to_table(table, grid_node.computed_styles)

            # Fill cells with grid items
            cell_index = 0
            for row_idx in range(num_rows):
                for col_idx in range(num_cols):
                    if cell_index < len(child_elements):
                        child = child_elements[cell_index]
                        cell = table.rows[row_idx].cells[col_idx]

                        # Apply cell styles from child (including background, border, padding)
                        if child.computed_styles:
                            from html2word.word_builder.style_mapper import StyleMapper
                            from html2word.style.box_model import BoxModel
                            mapper = StyleMapper()
                            # Calculate box model from child element to get padding, borders
                            box_model = BoxModel(child)
                            mapper.apply_table_cell_style(cell, child.computed_styles, box_model)

                        # Recursively process child content in cell context
                        # Save current document temporarily
                        original_doc = self.document

                        # Create a temporary processor for cell content
                        # We need to clear the first paragraph if it's empty
                        if len(cell.paragraphs) == 1 and not cell.paragraphs[0].text:
                            # Remove empty paragraph
                            p = cell.paragraphs[0]._element
                            p.getparent().remove(p)

                        # Process child's children in the cell
                        for grandchild in child.children:
                            self._process_node_in_cell(grandchild, cell, original_doc)

                        # Restore document
                        self.document = original_doc
                        cell_index += 1

            # Apply spacing after table (from grid container's margin-bottom)
            self._apply_spacing_after_table(grid_node)

        except Exception as e:
            logger.warning(f"Error in smart grid conversion: {e}, falling back")
            self._process_children(grid_node)

    def _apply_grid_gap_to_table(self, table, computed_styles: dict):
        """
        Apply grid/flex gap as Word table cell spacing.
        Reads gap values from HTML/CSS (not hardcoded).

        Args:
            table: Word table object
            computed_styles: Computed CSS styles containing gap properties
        """
        if not computed_styles:
            return

        # Read gap values from HTML/CSS (row-gap and column-gap were expanded from gap by CSS parser)
        gap_value = computed_styles.get('gap') or computed_styles.get('row-gap') or computed_styles.get('column-gap')

        if not gap_value:
            return

        try:
            from html2word.utils.units import UnitConverter

            # Convert gap to points
            gap_pt = UnitConverter.to_pt(gap_value)

            if gap_pt <= 0:
                return

            # Convert points to twips (Word's internal unit: 1 pt = 20 twips)
            gap_twips = int(gap_pt * 20)

            logger.debug(f"Applying grid gap: {gap_value} → {gap_pt}pt → {gap_twips} twips")

            # Apply cell spacing to table using OpenXML
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls

            tbl = table._element
            tblPr = tbl.tblPr

            # Ensure tblPr exists
            if tblPr is None:
                tblPr = parse_xml(f'<w:tblPr {nsdecls("w")}/>')
                tbl.insert(0, tblPr)

            # Add or update tblCellSpacing element
            # Remove existing cellSpacing if present
            for child in list(tblPr):
                if child.tag.endswith('tblCellSpacing'):
                    tblPr.remove(child)

            # Add new cellSpacing (applies to all sides)
            cellSpacing = parse_xml(
                f'<w:tblCellSpacing {nsdecls("w")} w:w="{gap_twips}" w:type="dxa"/>'
            )
            tblPr.append(cellSpacing)

        except Exception as e:
            logger.warning(f"Failed to apply grid gap: {e}")

    def _process_node_in_cell(self, node: DOMNode, cell, original_doc):
        """Process a node within a table cell context."""
        # Create a wrapper that redirects document operations to cell
        class CellDocumentWrapper:
            def __init__(self, cell_obj, original):
                self._cell = cell_obj
                self._original = original

            def add_paragraph(self, *args, **kwargs):
                return self._cell.add_paragraph(*args, **kwargs)

            def add_table(self, *args, **kwargs):
                # FIXED: Add table to cell, not to original document
                return self._cell.add_table(*args, **kwargs)

        old_doc = self.paragraph_builder.document
        old_table_doc = self.table_builder.document
        old_image_doc = self.image_builder.document  # Save image builder document
        old_self_doc = self.document
        old_in_cell = self.in_table_cell  # Save previous state
        old_margin_bottom = self.paragraph_builder.last_margin_bottom  # Save margin state

        wrapper = CellDocumentWrapper(cell, original_doc)
        self.paragraph_builder.document = wrapper
        self.table_builder.document = wrapper
        self.image_builder.document = wrapper  # CRITICAL: Also update image_builder to use cell context
        self.document = wrapper  # CRITICAL: Also replace self.document for grid conversion
        self.in_table_cell = True  # Mark that we're inside a cell
        self.paragraph_builder.last_margin_bottom = 0.0  # Reset margin collapse in new context

        try:
            self._process_node(node)
        finally:
            self.paragraph_builder.document = old_doc
            self.table_builder.document = old_table_doc
            self.image_builder.document = old_image_doc  # Restore image builder document
            self.document = old_self_doc
            self.in_table_cell = old_in_cell  # Restore previous state
            self.paragraph_builder.last_margin_bottom = old_margin_bottom  # Restore margin state

    def _wrap_div_in_styled_table(self, node: DOMNode):
        """
        Wrap a styled div in a single-cell table to preserve background/borders.

        Args:
            node: DOM node with styling
        """
        try:
            logger.debug("Wrapping styled div in table")

            # Create 1x1 table (no spacing before - previous element's space_after handles that)
            table = self.document.add_table(rows=1, cols=1)
            cell = table.rows[0].cells[0]

            # Apply div styles to cell
            if node.computed_styles:
                from html2word.word_builder.style_mapper import StyleMapper
                mapper = StyleMapper()
                box_model = node.layout_info.get('box_model') if hasattr(node, 'layout_info') else None
                mapper.apply_table_cell_style(cell, node.computed_styles, box_model)

            # Clear default empty paragraph if present
            if len(cell.paragraphs) == 1 and not cell.paragraphs[0].text:
                p = cell.paragraphs[0]._element
                p.getparent().remove(p)

            # Process children within the cell
            original_doc = self.document
            for child in node.children:
                self._process_node_in_cell(child, cell, original_doc)
            self.document = original_doc

            # Apply spacing after table (from div's margin-bottom)
            self._apply_spacing_after_table(node)

        except Exception as e:
            logger.warning(f"Error wrapping div in table: {e}, falling back")
            self._process_children(node)

    def _apply_spacing_before_table(self, node: DOMNode):
        """
        DEPRECATED: No longer used. Previous element's space_after handles spacing.

        Kept for compatibility but does nothing.
        This implements CSS margin collapse: we don't add spacing before elements,
        only after (via space_after on paragraphs or spacer after tables).
        """
        pass  # Intentionally do nothing

    def _apply_spacing_after_table(self, node: DOMNode):
        """
        Apply spacing after a table based on the source element's margin-bottom.

        Since tables don't support paragraph_format.space_after, we add a spacer paragraph
        with space_before set to the table's margin-bottom. This implements the "only space_after"
        principle (or in this case, space_before on the spacer represents the table's bottom margin).

        Args:
            node: Source DOM node (div/grid container/table wrapper)
        """
        try:
            # Calculate box model to get margin
            from html2word.style.box_model import BoxModel
            box_model = BoxModel(node)

            # Apply margin-bottom as space_before on a spacer paragraph
            # This represents the table's margin-bottom and will be the spacing
            # between this table and the next element
            if box_model.margin.bottom > 0:
                from docx.shared import Pt
                spacer = self.document.add_paragraph()
                spacer.paragraph_format.space_before = Pt(box_model.margin.bottom)
                logger.debug(f"Applied {box_model.margin.bottom}pt spacing after table (from margin-bottom)")
        except Exception as e:
            logger.debug(f"Could not apply spacing after table: {e}")

    def _apply_container_spacing_before(self, node: DOMNode):
        """
        DEPRECATED: No longer used. Implements CSS margin collapse behavior.

        In CSS, vertical margins collapse. To mimic this in Word, we only apply
        space_after on elements, never space_before. This method is kept for
        compatibility but does nothing.
        """
        pass  # Intentionally do nothing - implements margin collapse

    def _apply_container_spacing_after(self, node: DOMNode):
        """
        DEPRECATED: No longer used. Implements CSS margin collapse behavior.

        Container elements (section, article, etc.) don't need explicit spacing.
        Their child elements handle spacing via their own margin-bottom (space_after).
        This method is kept for compatibility but does nothing.
        """
        pass  # Intentionally do nothing - child elements handle their own spacing

    def _determine_flex_columns(self, flex_wrap: str, num_items: int) -> int:
        """
        Determine number of columns for flex layout based on flex-wrap.

        Args:
            flex_wrap: CSS flex-wrap value (nowrap, wrap, wrap-reverse)
            num_items: Number of flex items

        Returns:
            Number of columns
        """
        if flex_wrap in ('wrap', 'wrap-reverse'):
            # For wrapping flex, estimate columns based on square-ish layout
            # This is a heuristic - in reality it depends on item widths
            # Use a reasonable default that works well for most cases
            if num_items <= 3:
                return num_items  # Single row
            elif num_items <= 6:
                return 3  # 2 rows of 3
            else:
                return 4  # Multiple rows of 4
        else:
            # For nowrap (default), all items in one row
            # Limit to 6 columns for readability
            return min(num_items, 6)

    def _determine_grid_columns(self, grid_template_cols: str, num_items: int) -> int:
        """
        Determine number of columns from grid-template-columns or auto-fit/auto-fill.

        Args:
            grid_template_cols: CSS grid-template-columns value
            num_items: Number of grid items

        Returns:
            Number of columns
        """
        if not grid_template_cols:
            # Default: try to make a square-ish grid
            return max(1, int(math.sqrt(num_items)))

        # Count explicit column definitions
        # Handle: "repeat(3, 1fr)", "200px 200px 200px", "repeat(auto-fit, minmax(250px, 1fr))"
        if 'repeat' in grid_template_cols.lower():
            # Try to extract repeat count
            import re
            match = re.search(r'repeat\s*\(\s*(\d+|auto-fit|auto-fill)', grid_template_cols)
            if match:
                count_str = match.group(1)
                if count_str.isdigit():
                    return int(count_str)
                else:
                    # auto-fit/auto-fill: use actual item count for single-row layout
                    # In Word output (print), we want all items in one row
                    # Limit to reasonable max (e.g., 6 columns)
                    return min(6, num_items)

        # Count space-separated values
        parts = grid_template_cols.strip().split()
        if len(parts) > 0:
            return len(parts)

        # Default
        return min(3, num_items)

    def _is_root_layout_container(self, node: DOMNode) -> bool:
        """
        Check if node is a root layout container (like .container) that should not be wrapped.

        Args:
            node: DOM node

        Returns:
            True if it's a root layout container
        """
        # Check if parent is body or a direct child of a major container
        is_child_of_body = node.parent and node.parent.tag == 'body'

        # Check styles:
        # - Has white/transparent background
        # - Has box-shadow (likely for visual separation, not content styling)
        # - Likely has max-width, margin: 0 auto (centered layout)
        if not node.computed_styles:
            return False

        styles = node.computed_styles

        # Check if it has white/transparent background
        bg_color = styles.get('background-color', '')
        bg_prop = styles.get('background', '')

        has_white_bg = False
        if bg_color:
            bg_lower = bg_color.lower()
            has_white_bg = bg_lower in ('#fff', '#ffffff', 'white', 'rgb(255,255,255)', 'rgb(255, 255, 255)')
        elif bg_prop:
            bg_lower = bg_prop.lower()
            has_white_bg = bg_lower in ('white', '#fff', '#ffffff')

        # If not white background, it's not a layout container
        if not has_white_bg:
            return False

        # Check if has box-shadow (layout visual effect)
        has_shadow = 'box-shadow' in styles and styles['box-shadow'] not in ('none', '')

        # Check if has max-width (typical of layout containers)
        has_max_width = 'max-width' in styles

        # It's a root layout container if:
        # 1. Direct child of body (or very close to root)
        # 2. Has white background
        # 3. Has box-shadow (for visual separation)
        # 4. Probably has max-width for centering
        return is_child_of_body and has_shadow and (has_max_width or True)

    def _process_svg(self, svg_node: DOMNode):
        """
        Process SVG element and convert to image.

        Args:
            svg_node: SVG DOM node
        """
        try:
            # Get SVG dimensions from attributes or CSS
            width = svg_node.get_attribute('width') or svg_node.computed_styles.get('width', '100')
            height = svg_node.get_attribute('height') or svg_node.computed_styles.get('height', '100')

            # Convert SVG to image using ImageBuilder's SVG support
            self.image_builder.build_svg(svg_node, width, height)

        except Exception as e:
            logger.warning(f"Failed to process SVG element: {e}")
            # Fallback: skip the SVG element
            pass

    def save(self, output_path: str):
        """
        Save document to file.

        Args:
            output_path: Output file path
        """
        self.document.save(output_path)
        logger.info(f"Document saved to: {output_path}")
