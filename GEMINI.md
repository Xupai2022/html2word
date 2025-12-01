# html2word Project Context

## Project Overview
`html2word` is a Python library and command-line tool designed to convert HTML content into Microsoft Word (`.docx`) documents. Its primary differentiator is its focus on accurately preserving CSS styles during the conversion process, bridging the gap between web rendering and document formatting.

## Key Technologies & Dependencies
*   **Language:** Python 3.8+
*   **Core Libraries:**
    *   `python-docx`: For generating `.docx` files.
    *   `beautifulsoup4`: For parsing HTML.
    *   `lxml`: High-performance XML/HTML processing backend.
    *   `tinycss2`: For robust CSS parsing.
    *   `Pillow` (PIL): For image manipulation.
    *   `requests`: For fetching remote resources.

## Architecture
The project follows a pipeline architecture:
1.  **Parsing (`html2word.parser`):** Converts raw HTML into a DOM-like tree structure (`dom_tree.py`) and extracts CSS.
2.  **Style Resolution (`html2word.style`):** Resolves CSS rules against the DOM nodes, calculating computed styles (inheritance, specificity).
3.  **Layout (`html2word.layout`):** (Inferred) handles block/inline layout logic to map HTML flows to Word's paragraph/run structure.
4.  **Building (`html2word.word_builder`):** Maps the styled DOM tree to `python-docx` objects (`DocumentBuilder`).

## Development & Usage

### Installation
```bash
pip install .
# For development dependencies:
pip install .[dev]
```

### Command Line Interface
The main entry point is `html2word`.
```bash
# Basic usage
html2word input.html -o output.docx

# With options
html2word input.html -o output.docx --base-path ./assets --log-level DEBUG
```

### Python API
```python
from html2word.converter import HTML2WordConverter

converter = HTML2WordConverter()
# Convert file
converter.convert_file("input.html", "output.docx")
# Convert string
converter.convert_string("<h1>Hello World</h1>", "output.docx")
```

### Development Workflow
*   **Testing:** `pytest` is used for the test suite.
*   **Formatting:** `black` is used for code formatting.
*   **Linting:** `flake8` and `mypy` are used for linting and type checking.
*   **Windows Setup:** `run_setup.bat` is provided, likely to handle specific library dependencies (references `setup_cairo_windows.py`).

## Key Files
*   `src/html2word/converter.py`: The orchestrator class `HTML2WordConverter`.
*   `src/html2word/cli.py`: CLI implementation.
*   `src/html2word/parser/html_parser.py`: HTML parsing logic.
*   `src/html2word/style/style_resolver.py`: Logic for applying CSS to nodes.
*   `CLAUDE.md`: Contains operational rules and persona definitions for AI assistants working on this project.

## AI Assistant Persona (from CLAUDE.md)
*   **Role:** Senior Technical Writer & Architect.
*   **Style:** Factual, rigorous (no guessing), uses Markdown & Mermaid.
*   **Workflows:** Follows specific command patterns (`INDEX`, `WIKI_PLAN`, `FULL_WIKI`) for documentation tasks.
