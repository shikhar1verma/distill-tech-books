"""PDF → raw markdown extraction pipeline.

Uses PyMuPDF for TOC parsing and page-range mapping,
pymupdf4llm for markdown conversion, and post-processing
for code block repair and cleanup.

Usage:
    python src/extract.py init "books/Fluent Python.pdf" --slug fluent-python
    python src/extract.py extract "books/Fluent Python.pdf" --slug fluent-python
    python src/extract.py extract "books/Fluent Python.pdf" --slug fluent-python --chapter 1

Raw output goes to raw-data/<slug>/ (private submodule).
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf
import pymupdf4llm
import yaml


def get_toc(doc):
    """Parse TOC into structured list: [{level, title, page}, ...]"""
    return [
        {"level": level, "title": title, "page": page}
        for level, title, page in doc.get_toc()
    ]


def find_chapters(toc):
    """Extract chapter entries with page ranges from TOC.

    Returns list of dicts: {number, title, start_page, end_page, sections}
    Pages are 1-indexed (as in PDF).
    """
    chapters = []
    chapter_pattern = re.compile(r"^(?:Chapter|CHAPTER)\s+(\d+)[.:]\s*(.+)$", re.IGNORECASE)

    # Find all chapter entries
    chapter_indices = []
    for i, entry in enumerate(toc):
        m = chapter_pattern.match(entry["title"])
        if m:
            chapter_indices.append((i, int(m.group(1)), m.group(2)))

    for idx, (toc_idx, ch_num, ch_title) in enumerate(chapter_indices):
        start_page = toc[toc_idx]["page"]

        # End page = start of next chapter (or next L1/L2 entry after all subsections)
        if idx + 1 < len(chapter_indices):
            end_page = toc[chapter_indices[idx + 1][0]]["page"] - 1
        else:
            # Last chapter — scan for next L1 entry after this chapter
            end_page = None
            for j in range(toc_idx + 1, len(toc)):
                if toc[j]["level"] <= 2 and not chapter_pattern.match(toc[j]["title"]):
                    # Check if it's a Part or non-chapter L2
                    if toc[j]["level"] == 1 or (
                        toc[j]["level"] == 2
                        and not re.match(r"(?:Chapter|CHAPTER)\s+\d+", toc[j]["title"], re.IGNORECASE)
                    ):
                        end_page = toc[j]["page"] - 1
                        break
            if end_page is None:
                end_page = start_page + 30  # fallback

        # Collect sections within this chapter
        sections = []
        for j in range(toc_idx + 1, len(toc)):
            if toc[j]["page"] > end_page:
                break
            if toc[j]["level"] >= 3:
                sections.append(
                    {
                        "level": toc[j]["level"],
                        "title": toc[j]["title"],
                        "page": toc[j]["page"],
                    }
                )

        chapters.append(
            {
                "number": ch_num,
                "title": ch_title,
                "start_page": start_page,
                "end_page": end_page,
                "sections": sections,
            }
        )

    return chapters


def detect_code_fonts(doc, sample_pages=None):
    """Detect monospace/code fonts used in the PDF by sampling pages."""
    if sample_pages is None:
        sample_pages = list(range(30, min(60, len(doc))))

    code_fonts = set()
    for pg in sample_pages:
        page = doc[pg]
        blocks = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)[
            "blocks"
        ]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font = span["font"]
                    if any(
                        mono in font.lower()
                        for mono in ["mono", "courier", "consola", "ubuntu"]
                    ):
                        code_fonts.add(font)
    return code_fonts


def extract_chapter_markdown(doc, chapter, code_fonts=None, code_detection="normal", fence_language="python"):
    """Extract a single chapter as markdown using pymupdf4llm + post-processing."""
    # 0-indexed page list
    pages = list(range(chapter["start_page"] - 1, chapter["end_page"]))

    md = pymupdf4llm.to_markdown(doc, pages=pages)

    md = postprocess_markdown(md, chapter, code_detection=code_detection, fence_language=fence_language)
    return md


def postprocess_markdown(md, chapter, code_detection="normal", fence_language="python"):
    """Clean up pymupdf4llm output."""
    # Remove page number footers like "**5**" or "**A Pythonic Card Deck | 5**"
    md = re.sub(
        r"\n\*\*(?:[A-Za-z\s:,\-–—\'\"]+\|\s*)?\d+\*\*\s*\n",
        "\n",
        md,
    )
    md = re.sub(
        r"\n\*\*\d+\s*\|\s*[A-Za-z\s:,\-–—\'\"]+\*\*\s*\n",
        "\n",
        md,
    )

    # Fix bold-code-inline patterns that should be fenced code blocks.
    # pymupdf4llm sometimes renders code as: **`keyword`** `rest of code`
    # Detect sequences of inline code on their own paragraph that look like code blocks
    md = _repair_inline_code_blocks(md, code_detection=code_detection, fence_language=fence_language)

    # Remove OCR artifacts
    md = re.sub(r"^=== Document parser messages ===.*?\n\n", "", md, flags=re.DOTALL)

    # Clean up excessive blank lines
    md = re.sub(r"\n{4,}", "\n\n\n", md)

    # Remove trailing whitespace
    md = "\n".join(line.rstrip() for line in md.split("\n"))

    return md


def _repair_inline_code_blocks(md, code_detection="normal", fence_language="python"):
    """Detect paragraphs of inline code and convert to fenced code blocks.

    pymupdf4llm sometimes renders multi-line code as a paragraph with
    **`keyword`** `code` patterns instead of fenced blocks.
    """
    fence_tag = f"```{fence_language}" if fence_language else "```"
    lines = md.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect lines that are mostly inline code with bold keywords
        # Pattern: lines consisting primarily of **`...`** `...` sequences
        if _is_inline_code_line(line) and not line.strip().startswith(("#", "-", "*")):
            # Collect consecutive inline-code lines
            code_lines = []
            while i < len(lines) and _is_inline_code_line(lines[i]):
                cleaned = _strip_inline_code_markers(lines[i])
                if cleaned.strip():
                    code_lines.append(cleaned)
                i += 1

            if len(code_lines) >= 2 or (
                len(code_lines) == 1
                and _looks_like_code_block(code_lines[0], detection_mode=code_detection)
            ):
                result.append("")
                result.append(fence_tag)
                result.extend(code_lines)
                result.append("```")
                result.append("")
            else:
                # Single short inline code, keep as-is
                for cl in code_lines:
                    result.append(f"`{cl}`")
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def _is_inline_code_line(line):
    """Check if a line is primarily composed of inline code markers."""
    stripped = line.strip()
    if not stripped:
        return False

    # Count code marker characters vs total
    without_markers = re.sub(r"\*\*`[^`]*`\*\*|`[^`]*`", "", stripped)
    # If most of the content was inside code markers, it's a code line
    if len(stripped) > 10 and len(without_markers.strip()) < len(stripped) * 0.3:
        return True

    # Also match lines that start with **`>>>  (REPL-like)
    if re.match(r'^\*\*`>>>|^`>>>', stripped):
        return True

    return False


def _looks_like_code_block(line, detection_mode="normal"):
    """Check if a single line looks like it should be a fenced code block."""
    if detection_mode == "minimal":
        # Only match REPL prompts and heavily indented blocks
        return line.strip().startswith(">>> ") or (
            len(line) - len(line.lstrip()) >= 8
        )

    keywords = [
        "import ",
        "from ",
        "class ",
        "def ",
        "return ",
        "for ",
        "while ",
        "if ",
        ">>> ",
    ]
    return any(line.strip().startswith(kw) for kw in keywords)


def _strip_inline_code_markers(line):
    """Remove inline code markdown markers, preserving the code text."""
    # Remove **`...`** → ...
    line = re.sub(r"\*\*`([^`]*)`\*\*", r"\1", line)
    # Remove `...` → ...
    line = re.sub(r"`([^`]*)`", r"\1", line)
    # Remove remaining bold markers
    line = re.sub(r"\*\*", "", line)
    # Remove _..._  italic markers (for comments like # doctest: +ELLIPSIS)
    line = re.sub(r"_([^_]+)_", r"\1", line)
    return line


def build_frontmatter(chapter):
    """Build YAML frontmatter for a chapter's raw markdown."""
    fm = {
        "title": chapter["title"],
        "chapter": chapter["number"],
        "pages": f'{chapter["start_page"]}-{chapter["end_page"]}',
        "sections": [s["title"] for s in chapter["sections"]],
    }
    return "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n\n"


def extract_images(doc, chapter, output_dir):
    """Extract images from chapter pages and save to output_dir."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    images_saved = []
    for pg_num in range(chapter["start_page"] - 1, chapter["end_page"]):
        page = doc[pg_num]
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            image_bytes = base_image["image"]
            ext = base_image["ext"]

            # Skip tiny images (likely decorative)
            if len(image_bytes) < 1000:
                continue

            fname = f"ch{chapter['number']:02d}-p{pg_num + 1}-{img_idx}.{ext}"
            out_path = output_dir / fname
            out_path.write_bytes(image_bytes)
            images_saved.append(fname)

    return images_saved


# --- CLI commands ---


def cmd_init(pdf_path, slug, library_dir="library", raw_dir="raw-data"):
    """Initialize book structure: parse TOC, create _meta.yaml."""
    doc = pymupdf.open(pdf_path)
    toc = get_toc(doc)
    chapters = find_chapters(toc)

    book_dir = Path(library_dir) / slug
    book_dir.mkdir(parents=True, exist_ok=True)
    (book_dir / "images").mkdir(exist_ok=True)
    (book_dir / "chapters").mkdir(exist_ok=True)
    (book_dir / "concepts").mkdir(exist_ok=True)

    # Raw output goes to private submodule
    raw_book_dir = Path(raw_dir) / slug
    raw_book_dir.mkdir(parents=True, exist_ok=True)

    # Save chapter map
    chapter_map = {}
    for ch in chapters:
        chapter_map[ch["number"]] = {
            "title": ch["title"],
            "pages": f'{ch["start_page"]}-{ch["end_page"]}',
            "sections": [s["title"] for s in ch["sections"]],
        }

    meta = {
        "book": slug,
        "title": doc.metadata.get("title", slug),
        "total_chapters": len(chapters),
        "chapters": chapter_map,
    }

    meta_path = book_dir / "_meta.yaml"
    meta_path.write_text(
        yaml.dump(meta, default_flow_style=False, allow_unicode=True, sort_keys=False)
    )

    print(f"Initialized {slug}: {len(chapters)} chapters found")
    for ch in chapters:
        print(f"  Ch {ch['number']:2d}: p{ch['start_page']:4d}-{ch['end_page']:4d}  {ch['title']}")

    doc.close()
    return chapters


def cmd_extract(pdf_path, slug, library_dir="library", raw_dir="raw-data", chapter_num=None,
                code_detection="normal", fence_language="python"):
    """Extract chapters to raw markdown.

    Raw markdown goes to raw-data/<slug>/ (private submodule).
    Images go to library/<slug>/images/ (public).
    """
    doc = pymupdf.open(pdf_path)
    toc = get_toc(doc)
    chapters = find_chapters(toc)

    book_dir = Path(library_dir) / slug
    raw_book_dir = Path(raw_dir) / slug
    raw_book_dir.mkdir(parents=True, exist_ok=True)
    images_dir = book_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    if chapter_num:
        chapters = [ch for ch in chapters if ch["number"] == chapter_num]
        if not chapters:
            print(f"Chapter {chapter_num} not found")
            sys.exit(1)

    code_fonts = detect_code_fonts(doc)
    print(f"Detected code fonts: {code_fonts}")
    print(f"Code detection: {code_detection}, fence language: {fence_language}")

    for ch in chapters:
        print(f"Extracting Chapter {ch['number']}: {ch['title']}...")

        # Extract markdown
        md = extract_chapter_markdown(doc, ch, code_fonts,
                                      code_detection=code_detection,
                                      fence_language=fence_language)
        frontmatter = build_frontmatter(ch)

        out_path = raw_book_dir / f"chapter-{ch['number']:02d}.md"
        out_path.write_text(frontmatter + md, encoding="utf-8")
        print(f"  → {out_path} ({len(md)} chars)")

        # Extract images
        images = extract_images(doc, ch, images_dir)
        if images:
            print(f"  → {len(images)} images saved to {images_dir}")

    doc.close()
    print(f"\nDone. Extracted {len(chapters)} chapter(s).")


def main():
    parser = argparse.ArgumentParser(description="PDF extraction pipeline")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize book structure from PDF TOC")
    p_init.add_argument("pdf", help="Path to PDF file")
    p_init.add_argument("--slug", required=True, help="Book slug (e.g., fluent-python)")
    p_init.add_argument("--library-dir", default="library")
    p_init.add_argument("--raw-dir", default="raw-data", help="Raw output directory (private submodule)")

    p_extract = sub.add_parser("extract", help="Extract chapters to raw markdown")
    p_extract.add_argument("pdf", help="Path to PDF file")
    p_extract.add_argument("--slug", required=True, help="Book slug")
    p_extract.add_argument("--chapter", type=int, help="Extract only this chapter number")
    p_extract.add_argument("--library-dir", default="library")
    p_extract.add_argument("--raw-dir", default="raw-data", help="Raw output directory (private submodule)")
    p_extract.add_argument("--code-detection", choices=["normal", "minimal"], default="normal",
                           help="Code block detection mode (minimal for non-code books)")
    p_extract.add_argument("--fence-language", default="python",
                           help="Language tag for fenced code blocks (use 'none' for no tag)")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args.pdf, args.slug, args.library_dir, args.raw_dir)
    elif args.command == "extract":
        fence_lang = args.fence_language if args.fence_language != "none" else None
        cmd_extract(args.pdf, args.slug, args.library_dir, args.raw_dir, args.chapter,
                    code_detection=args.code_detection, fence_language=fence_lang)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
