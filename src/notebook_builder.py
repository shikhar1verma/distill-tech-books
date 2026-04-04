"""Build valid .ipynb notebooks from structured cell lists.

Usage:
    from notebook_builder import build_notebook, validate_notebook

    cells = [
        {"type": "markdown", "content": "# Chapter 1\\nThe Python Data Model"},
        {"type": "code", "content": "print('hello')"},
    ]
    build_notebook("Chapter 1: The Python Data Model", cells, "output/notebook.ipynb")
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def build_notebook(title, cells, output_path):
    """Create a valid .ipynb from a list of cell dicts.

    Args:
        title: Notebook title (used in metadata)
        cells: List of {"type": "markdown"|"code", "content": str}
        output_path: Where to write the .ipynb
    """
    nb = new_notebook()

    nb.metadata.update(
        {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0",
                "mimetype": "text/x-python",
                "file_extension": ".py",
            },
            "title": title,
        }
    )

    for cell in cells:
        cell_type = cell.get("type", "markdown")
        content = cell.get("content", "")

        if cell_type == "code":
            nb.cells.append(new_code_cell(source=content))
        else:
            nb.cells.append(new_markdown_cell(source=content))

    # Validate structure
    nbformat.validate(nb)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    return output_path


def validate_notebook(path, skip_execution=False):
    """Validate and optionally execute a notebook.

    If skip_execution is True, only validate notebook structure via nbformat.
    Returns (success: bool, error_msg: str|None)
    """
    path = Path(path)
    if not path.exists():
        return False, f"Notebook not found: {path}"

    if skip_execution:
        try:
            nb = nbformat.read(str(path), as_version=4)
            nbformat.validate(nb)
            return True, None
        except Exception as e:
            return False, str(e)

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--ExecutePreprocessor.timeout=120",
                "--output", "/tmp/_nb_validate_output.ipynb",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Notebook execution timed out (180s)"
    except FileNotFoundError:
        return False, "jupyter nbconvert not found — install jupyterlab"


_FENCE_RE = re.compile(r"^```(\w*)\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)


def cells_from_markdown(md_text, code_languages=None):
    """Parse markdown with fenced code blocks into notebook cells.

    Args:
        md_text: Markdown text with fenced code blocks.
        code_languages: Set of languages to treat as executable code cells.
                       Default: {"python"}. All other fences stay as markdown.
    """
    if code_languages is None:
        code_languages = {"python"}

    cells = []
    last_end = 0

    for match in _FENCE_RE.finditer(md_text):
        # Text before this fence = markdown cell
        before = md_text[last_end : match.start()].strip()
        if before:
            cells.append({"type": "markdown", "content": before})

        lang = match.group(1).lower()
        code = match.group(2).strip()

        if lang in code_languages and code:
            # Executable code cell (strip fence markers)
            cells.append({"type": "code", "content": code})
        elif code:
            # Non-executable fence — keep as markdown with fence markers
            cells.append(
                {"type": "markdown", "content": f"```{match.group(1)}\n{code}\n```"}
            )

        last_end = match.end()

    # Trailing text after last fence
    trailing = md_text[last_end:].strip()
    if trailing:
        cells.append({"type": "markdown", "content": trailing})

    return cells


if __name__ == "__main__":
    # Quick test
    test_cells = [
        {"type": "markdown", "content": "# Test Notebook\nThis is a test."},
        {"type": "code", "content": "print('Hello from notebook!')"},
        {"type": "markdown", "content": "## Section 2\nMore content."},
        {"type": "code", "content": "x = [i**2 for i in range(10)]\nprint(x)"},
    ]
    out = build_notebook("Test", test_cells, "/tmp/test_notebook.ipynb")
    print(f"Created: {out}")
    ok, err = validate_notebook(out)
    print(f"Valid: {ok}" + (f" — {err}" if err else ""))
