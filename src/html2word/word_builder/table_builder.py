"""
Table builder for Word documents.

Builds Word tables from HTML table elements with proper cell merging.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from docx.shared import Inches

from html2word.parser.dom_tree import DOMNode
from html2word.word_builder.style_mapper import StyleMapper
from html2word.word_builder.paragraph_builder import ParagraphBuilder

logger = logging.getLogger(__name__)


class TableBuilder:
    """Builds Word tables from HTML table nodes."""

    def __init__(self, document):
        """
        Initialize table builder.

        Args:
            document: python-docx Document object
        """
        self.document = document
        self.style_mapper = StyleMapper()
        self.paragraph_builder = ParagraphBuilder(document)

    def build_table(self, table_node: DOMNode) -> Optional[object]:
        """
        Build a Word table from HTML table node.

        Args:
            table_node: Table DOM node

        Returns:
            python-docx Table object or None
        """
        if table_node.tag != 'table':
            return None

        # Extract table structure
        rows = self._extract_rows(table_node)
        if not rows:
            return None

        # Calculate dimensions
        num_rows = len(rows)
        num_cols = self._calculate_columns(rows)

        if num_rows == 0 or num_cols == 0:
            return None

        # Create table
        table = self.document.add_table(rows=num_rows, cols=num_cols)

        # Fill table cells
        self._fill_table(table, rows)

        # Apply table-level styles
        self._apply_table_style(table, table_node)

        return table

    def _extract_rows(self, table_node: DOMNode) -> List[DOMNode]:
        """
        Extract row nodes from table.

        Args:
            table_node: Table DOM node

        Returns:
            List of row nodes (tr)
        """
        rows = []

        # Process children to find rows
        for child in table_node.children:
            if child.tag == 'tr':
                rows.append(child)
            elif child.tag in ('thead', 'tbody', 'tfoot'):
                # Process section
                for section_child in child.children:
                    if section_child.tag == 'tr':
                        rows.append(section_child)

        return rows

    def _calculate_columns(self, rows: List[DOMNode]) -> int:
        """
        Calculate number of columns in table.

        Args:
            rows: List of row nodes

        Returns:
            Number of columns
        """
        max_cols = 0

        for row in rows:
            col_count = 0
            for cell in row.children:
                if cell.tag in ('td', 'th'):
                    colspan = int(cell.get_attribute('colspan', '1'))
                    col_count += colspan
            max_cols = max(max_cols, col_count)

        return max_cols

    def _fill_table(self, table, rows: List[DOMNode]):
        """
        Fill table with content and handle cell merging.

        Args:
            table: python-docx Table object
            rows: List of row nodes
        """
        # Build cell matrix to track merged cells
        matrix = self._build_cell_matrix(rows)

        # Fill cells
        for row_idx, row_node in enumerate(rows):
            word_row = table.rows[row_idx]

            # Set row height based on CSS height property
            self._apply_row_height(word_row, row_node)

            col_idx = 0

            for cell_node in row_node.children:
                if cell_node.tag not in ('td', 'th'):
                    continue

                # Skip cells that are occupied by a previous rowspan/colspan
                # (matrix[row_idx][col_idx] points to a different cell_node)
                while col_idx < len(matrix[row_idx]) and matrix[row_idx][col_idx] != cell_node:
                    col_idx += 1

                if col_idx >= len(word_row.cells):
                    break

                word_cell = word_row.cells[col_idx]

                # Get colspan and rowspan
                colspan = int(cell_node.get_attribute('colspan', '1'))
                rowspan = int(cell_node.get_attribute('rowspan', '1'))

                # Prepare cell styles - merge row styles with cell styles
                cell_styles = self._get_merged_cell_styles(row_node, cell_node)
                box_model = cell_node.layout_info.get('box_model')

                # Handle cell merging
                if colspan > 1 or rowspan > 1:
                    # CRITICAL: Apply borders to ALL cells BEFORE merging
                    # This ensures consistent border appearance across merged cells
                    self._apply_borders_before_merge(table, row_idx, col_idx, rowspan, colspan, box_model)
                    # Now perform the merge
                    self._merge_cells(table, row_idx, col_idx, rowspan, colspan)

                # Apply cell-level styles (background, borders, alignment)
                # For merged cells, this re-applies to ensure consistency
                self.style_mapper.apply_table_cell_style(
                    word_cell,
                    cell_styles,
                    box_model
                )

                # Fill cell content with merged styles
                self._fill_cell(word_cell, cell_node, cell_styles)

                col_idx += colspan

    def _get_merged_cell_styles(self, row_node: DOMNode, cell_node: DOMNode) -> Dict[str, Any]:
        """
        Merge row styles with cell styles.

        Args:
            row_node: Row DOM node
            cell_node: Cell DOM node

        Returns:
            Merged styles dictionary
        """
        merged_styles = {}

        # Start with row styles
        if row_node.computed_styles:
            merged_styles.update(row_node.computed_styles)

        # Override with cell styles
        if cell_node.computed_styles:
            merged_styles.update(cell_node.computed_styles)

        return merged_styles

    def _build_cell_matrix(self, rows: List[DOMNode]) -> List[List[Optional[DOMNode]]]:
        """
        Build matrix to track cell positions including merged cells.

        Args:
            rows: List of row nodes

        Returns:
            Matrix where None indicates a merged cell
        """
        if not rows:
            return []

        num_rows = len(rows)
        num_cols = self._calculate_columns(rows)
        matrix = [[None for _ in range(num_cols)] for _ in range(num_rows)]

        for row_idx, row_node in enumerate(rows):
            col_idx = 0

            for cell_node in row_node.children:
                if cell_node.tag not in ('td', 'th'):
                    continue

                # Find next available column
                while col_idx < num_cols and matrix[row_idx][col_idx] is not None:
                    col_idx += 1

                if col_idx >= num_cols:
                    break

                # Get span values
                colspan = int(cell_node.get_attribute('colspan', '1'))
                rowspan = int(cell_node.get_attribute('rowspan', '1'))

                # Mark cells as occupied
                for r in range(row_idx, min(row_idx + rowspan, num_rows)):
                    for c in range(col_idx, min(col_idx + colspan, num_cols)):
                        matrix[r][c] = cell_node

                col_idx += colspan

        return matrix

    def _merge_cells(self, table, row_idx: int, col_idx: int, rowspan: int, colspan: int):
        """
        Merge table cells.

        Args:
            table: python-docx Table object
            row_idx: Starting row index
            col_idx: Starting column index
            rowspan: Number of rows to span
            colspan: Number of columns to span
        """
        try:
            # Get starting cell
            start_cell = table.rows[row_idx].cells[col_idx]

            # Get ending cell
            end_row_idx = min(row_idx + rowspan - 1, len(table.rows) - 1)
            end_col_idx = min(col_idx + colspan - 1, len(table.rows[0].cells) - 1)
            end_cell = table.rows[end_row_idx].cells[end_col_idx]

            # Merge
            if start_cell != end_cell:
                start_cell.merge(end_cell)
        except Exception as e:
            logger.warning(f"Error merging cells: {e}")

    def _apply_borders_before_merge(self, table, row_idx: int, col_idx: int,
                                      rowspan: int, colspan: int, box_model):
        """
        Apply border styles to all cells BEFORE merging.

        This is critical for preventing border color inconsistencies in merged cells.
        When cells are merged in Word, each cell in the merged range retains its own
        border settings. If these borders differ, you'll see inconsistent colors/styles.

        Solution: Apply the same border to ALL cells in the range BEFORE merging.

        Args:
            table: python-docx Table object
            row_idx: Starting row index
            col_idx: Starting column index
            rowspan: Number of rows to span
            colspan: Number of columns to span
            box_model: BoxModel object with border information
        """
        if not box_model or not box_model.border.has_border():
            return

        try:
            # Calculate the range of cells to be merged
            end_row_idx = min(row_idx + rowspan, len(table.rows))

            # Apply the same border to ALL cells in the merge range
            for r in range(row_idx, end_row_idx):
                # Get the number of cells in this row
                num_cells = len(table.rows[r].cells)
                end_col_idx = min(col_idx + colspan, num_cells)

                for c in range(col_idx, end_col_idx):
                    try:
                        cell = table.rows[r].cells[c]
                        # Apply the source cell's borders to this cell
                        self.style_mapper._apply_cell_borders(cell, box_model.border)
                        logger.debug(f"Applied border to cell [{r},{c}] before merge")
                    except Exception as e:
                        logger.debug(f"Could not apply border to cell [{r},{c}]: {e}")
                        continue

        except Exception as e:
            logger.warning(f"Error applying borders before merge: {e}")

    def _fill_cell(self, word_cell, cell_node: DOMNode, cell_styles: Dict[str, Any]):
        """
        Fill cell with content.

        Args:
            word_cell: python-docx Cell object
            cell_node: Cell DOM node
            cell_styles: Merged styles (row + cell)
        """
        # Get or create first paragraph
        if word_cell.paragraphs:
            paragraph = word_cell.paragraphs[0]
            # Clear default content
            paragraph.clear()
        else:
            paragraph = word_cell.add_paragraph()

        # Apply paragraph-level styles to the first paragraph
        box_model = cell_node.layout_info.get('box_model')
        self.style_mapper.apply_paragraph_style(paragraph, cell_styles, box_model)

        # Check if we've added any content
        has_content = False

        # Process all children
        for child in cell_node.children:
            if child.is_text:
                text = child.text or ""
                # Normalize whitespace
                text = ' '.join(text.split())
                if text:
                    # Add text with merged styles
                    run = paragraph.add_run(text)
                    self.style_mapper.apply_run_style(run, cell_styles)
                    has_content = True

            elif child.is_element:
                if child.tag == 'br':
                    # Line break - add new paragraph
                    paragraph = word_cell.add_paragraph()
                    # Apply paragraph-level styles
                    self.style_mapper.apply_paragraph_style(paragraph, cell_styles, box_model)
                    has_content = True

                elif child.tag == 'img':
                    # FIXED: Handle images in table cells
                    self._add_cell_image(paragraph, child)
                    has_content = True

                elif child.tag == 'svg':
                    # FIXED: Handle SVG in table cells
                    self._add_cell_svg(paragraph, child)
                    has_content = True

                elif child.tag in ('p', 'div'):
                    # Block element
                    if has_content:
                        # Create new paragraph for block element
                        paragraph = word_cell.add_paragraph()
                    self._add_cell_block_content(paragraph, child, cell_styles)
                    has_content = True

                elif child.tag in ('strong', 'b', 'em', 'i', 'u', 'span', 'a'):
                    # Inline formatting
                    self._add_cell_inline_content(paragraph, child, cell_styles)
                    has_content = True

                elif child.tag == 'table':
                    # Nested table - Word supports tables within table cells
                    nested_table = self._build_nested_table(word_cell, child)
                    if nested_table:
                        has_content = True

                else:
                    # Other elements - extract text content
                    text = child.get_text_content()
                    text = ' '.join(text.split())
                    if text:
                        run = paragraph.add_run(text)
                        # Merge styles
                        element_styles = cell_styles.copy()
                        element_styles.update(child.computed_styles)
                        self.style_mapper.apply_run_style(run, element_styles)
                        has_content = True

    def _add_cell_block_content(self, paragraph, node: DOMNode, base_styles: Dict[str, Any]):
        """
        Add content from a block element to paragraph.

        Args:
            paragraph: Word paragraph
            node: Block element node
            base_styles: Base styles from cell/row
        """
        # Merge styles - node styles override base
        merged_styles = base_styles.copy()
        merged_styles.update(node.computed_styles)

        # Apply paragraph-level styles
        box_model = node.layout_info.get('box_model')
        self.style_mapper.apply_paragraph_style(paragraph, merged_styles, box_model)

        # Process children
        for child in node.children:
            if child.is_text:
                text = child.text or ""
                text = ' '.join(text.split())
                if text:
                    run = paragraph.add_run(text)
                    self.style_mapper.apply_run_style(run, merged_styles)

            elif child.is_inline:
                self._add_cell_inline_content(paragraph, child, merged_styles)

            else:
                # Nested block - just extract text
                text = child.get_text_content()
                text = ' '.join(text.split())
                if text:
                    run = paragraph.add_run(text)
                    self.style_mapper.apply_run_style(run, merged_styles)

    def _add_cell_inline_content(self, paragraph, node: DOMNode, base_styles: Dict[str, Any]):
        """
        Add inline element content to paragraph.

        Args:
            paragraph: Word paragraph
            node: Inline element node
            base_styles: Base styles from parent
        """
        # Merge styles
        merged_styles = base_styles.copy()
        merged_styles.update(node.computed_styles)

        for child in node.children:
            if child.is_text:
                text = child.text or ""
                text = ' '.join(text.split())
                if text:
                    run = paragraph.add_run(text)
                    self.style_mapper.apply_run_style(run, merged_styles)

            elif child.is_inline:
                # Nested inline
                self._add_cell_inline_content(paragraph, child, merged_styles)

            else:
                # Block inside inline - extract text
                text = child.get_text_content()
                text = ' '.join(text.split())
                if text:
                    run = paragraph.add_run(text)
                    self.style_mapper.apply_run_style(run, merged_styles)

    def _build_nested_table(self, word_cell, table_node: DOMNode) -> Optional[object]:
        """
        Build a nested table within a table cell.

        Args:
            word_cell: python-docx Cell object (parent cell)
            table_node: Table DOM node (nested table)

        Returns:
            python-docx Table object or None
        """
        try:
            # Extract table structure
            rows = self._extract_rows(table_node)
            if not rows:
                return None

            # Calculate dimensions
            num_rows = len(rows)
            num_cols = self._calculate_columns(rows)

            if num_rows == 0 or num_cols == 0:
                return None

            # Create nested table in the cell
            # Note: We need to clear the default paragraph first
            if word_cell.paragraphs:
                # Clear the first paragraph but keep it
                word_cell.paragraphs[0].clear()

            # Add table to cell
            nested_table = word_cell.add_table(rows=num_rows, cols=num_cols)

            # Fill nested table cells
            self._fill_table(nested_table, rows)

            # Apply table-level styles
            self._apply_table_style(nested_table, table_node)

            logger.debug(f"Built nested table: {num_rows}x{num_cols}")
            return nested_table

        except Exception as e:
            logger.warning(f"Error building nested table: {e}")
            # Fallback: just extract text content
            text = table_node.get_text_content()
            text = ' '.join(text.split())
            if text and word_cell.paragraphs:
                para = word_cell.paragraphs[0]
                para.add_run(text)
            return None

    def _add_cell_image(self, paragraph, img_node: DOMNode):
        """
        Add image to table cell paragraph.

        Args:
            paragraph: Word paragraph
            img_node: Image DOM node
        """
        try:
            from html2word.word_builder.image_builder import ImageBuilder
            from html2word.utils.image_utils import ImageProcessor
            from docx.shared import Inches

            image_builder = ImageBuilder(self.document)
            src = image_builder._get_best_image_src(img_node)
            if not src:
                return

            # Get CSS dimensions
            css_width = img_node.computed_styles.get('width')
            css_height = img_node.computed_styles.get('height')
            transform = img_node.computed_styles.get('transform')
            filter_value = img_node.computed_styles.get('filter')

            # Process image
            image_processor = ImageProcessor()
            result = image_processor.process_image(src, transform=transform, filter_css=filter_value)
            if not result:
                return

            image_stream, image_size = result

            # Calculate size
            max_width_inches = 2.0  # Default max for table images
            max_height_inches = 2.0

            if css_width:
                from html2word.utils.units import UnitConverter
                width_pt = UnitConverter.to_pt(css_width)
                max_width_inches = width_pt / 72

            if css_height:
                from html2word.utils.units import UnitConverter
                height_pt = UnitConverter.to_pt(css_height)
                max_height_inches = height_pt / 72

            display_width, display_height = image_processor.calculate_display_size(
                image_size, css_width, css_height, max_width_inches, max_height_inches
            )

            # Add image to paragraph run
            run = paragraph.add_run()
            run.add_picture(image_stream, width=Inches(display_width), height=Inches(display_height))

            logger.debug(f"Added image to table cell: {src}")

        except Exception as e:
            logger.warning(f"Failed to add image to table cell: {e}")

    def _add_cell_svg(self, paragraph, svg_node: DOMNode):
        """
        Add SVG to table cell paragraph (converted to image).

        Args:
            paragraph: Word paragraph
            svg_node: SVG DOM node
        """
        try:
            from html2word.word_builder.image_builder import ImageBuilder
            import io
            from docx.shared import Inches

            image_builder = ImageBuilder(self.document)
            width = svg_node.get_attribute('width') or svg_node.computed_styles.get('width', '100')
            height = svg_node.get_attribute('height') or svg_node.computed_styles.get('height', '100')

            svg_content = image_builder._serialize_svg_node(svg_node, width, height)
            if not svg_content:
                return

            try:
                import cairosvg
                png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
                image_stream = io.BytesIO(png_data)

                width_pt = image_builder._parse_dimension(width)
                height_pt = image_builder._parse_dimension(height)

                run = paragraph.add_run()
                run.add_picture(
                    image_stream,
                    width=Inches(width_pt / 72),
                    height=Inches(height_pt / 72)
                )

                logger.debug(f"Added SVG to table cell ({width}x{height})")

            except ImportError:
                logger.warning("cairosvg not available, SVG in table cell skipped")

        except Exception as e:
            logger.warning(f"Failed to add SVG to table cell: {e}")

    def _apply_table_style(self, table, table_node: DOMNode):
        """
        Apply table-level styles.

        Args:
            table: python-docx Table object
            table_node: Table DOM node
        """
        # Set table width if specified
        box_model = table_node.layout_info.get('box_model')
        if box_model and box_model.width:
            try:
                table.width = Inches(box_model.width / 72)  # pt to inches
            except:
                pass

        # Apply column widths
        self._apply_column_widths(table, table_node)

        # Apply table style
        try:
            table.style = 'Table Grid'
        except:
            pass

    def _apply_column_widths(self, table, table_node: DOMNode):
        """
        Extract and apply column widths from HTML table.

        Args:
            table: python-docx Table object
            table_node: Table DOM node
        """
        from html2word.utils.units import UnitConverter

        # Try to extract column widths from <col> tags or first row cells
        col_widths = self._extract_column_widths(table_node)

        if not col_widths:
            return  # No width information, use default

        # Get total table width
        box_model = table_node.layout_info.get('box_model')
        table_width_pt = box_model.width if box_model and box_model.width else 468  # Default: 6.5 inches * 72

        try:
            # Apply widths to columns
            for col_idx, width_info in enumerate(col_widths):
                if col_idx >= len(table.columns):
                    break

                if width_info:
                    width_pt = None

                    # Parse width (can be px, %, pt, or just a number)
                    if isinstance(width_info, str):
                        if '%' in width_info:
                            # Percentage width
                            percent = float(width_info.rstrip('%'))
                            width_pt = table_width_pt * (percent / 100.0)
                        else:
                            # Absolute width (px, pt, etc.)
                            width_pt = UnitConverter.to_pt(width_info)
                    elif isinstance(width_info, (int, float)):
                        # Numeric width, assume pixels
                        width_pt = width_info * 0.75  # px to pt

                    if width_pt:
                        table.columns[col_idx].width = Inches(width_pt / 72)
                        logger.debug(f"Set column {col_idx} width to {width_pt}pt")

        except Exception as e:
            logger.warning(f"Error applying column widths: {e}")

    def _extract_column_widths(self, table_node: DOMNode) -> List[Optional[str]]:
        """
        Extract column widths from <col> tags or first row cells.

        Args:
            table_node: Table DOM node

        Returns:
            List of width values (can be None for auto-width columns)
        """
        widths = []

        # First, try to find <col> or <colgroup> tags
        for child in table_node.children:
            if child.tag == 'colgroup':
                for col in child.children:
                    if col.tag == 'col':
                        width = col.get_attribute('width') or col.computed_styles.get('width')
                        widths.append(width)
            elif child.tag == 'col':
                width = child.get_attribute('width') or child.computed_styles.get('width')
                widths.append(width)

        # If we found column definitions, return them
        if widths:
            return widths

        # Otherwise, extract from first row cells
        rows = self._extract_rows(table_node)
        if not rows:
            return []

        first_row = rows[0]
        for cell in first_row.children:
            if cell.tag in ('td', 'th'):
                width = cell.get_attribute('width') or cell.computed_styles.get('width')
                widths.append(width)

        return widths

    def _apply_row_height(self, word_row, row_node: DOMNode):
        """
        Apply row height from CSS styles.

        Args:
            word_row: python-docx Row object
            row_node: Row DOM node
        """
        from docx.shared import Pt
        from docx.oxml import parse_xml
        from docx.oxml.ns import nsdecls

        # Get height from CSS
        height_str = row_node.computed_styles.get('height')
        if not height_str:
            # Also check cells for height
            for cell in row_node.children:
                if cell.tag in ('td', 'th'):
                    height_str = cell.computed_styles.get('height')
                    if height_str:
                        break

        if height_str and height_str != 'auto':
            try:
                # Parse height value
                from html2word.utils.units import UnitConverter
                height_pt = UnitConverter.to_pt(height_str)

                if height_pt > 0:
                    # Set row height with 'atLeast' rule
                    # This allows content to expand if needed but sets a minimum
                    trPr = word_row._element.get_or_add_trPr()

                    # Remove existing height if present
                    for trHeight in trPr.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}trHeight'):
                        trPr.remove(trHeight)

                    # Add new height with atLeast rule
                    trHeight = parse_xml(f'<w:trHeight {nsdecls("w")} w:val="{int(height_pt * 20)}" w:hRule="atLeast"/>')
                    trPr.append(trHeight)

                    logger.debug(f"Applied row height: {height_pt}pt (atLeast)")
            except Exception as e:
                logger.warning(f"Failed to apply row height: {e}")
