"""Generate wiki indexes, validate wikilinks, and update metadata.

Functions:
    build_chapter_index(chapter_dir)   — index.md for a chapter folder
    build_concepts_index(book_dir)     — alphabetical concept index across chapters
    build_book_index(book_dir)         — book-level index.md with chapter nav
    validate_wikilinks(book_dir)       — find broken [[links]]
    update_meta(book_dir, chapter_num, status, concepts)
"""

import re
from datetime import date
from pathlib import Path

import yaml


def build_chapter_index(chapter_dir):
    """Generate index.md for a chapter folder.

    Reads all .md files (except index.md) and the notebook,
    builds a chapter overview page with links.
    """
    chapter_dir = Path(chapter_dir)
    if not chapter_dir.exists():
        return None

    # Parse chapter number and title from folder name
    folder_name = chapter_dir.name
    parts = folder_name.split("-", 1)
    ch_num = parts[0] if parts[0].isdigit() else "?"
    ch_title = parts[1].replace("-", " ").title() if len(parts) > 1 else folder_name

    # Find concept articles
    articles = []
    for md_file in sorted(chapter_dir.glob("*.md")):
        if md_file.name == "index.md":
            continue
        # Read frontmatter for title
        title = _read_frontmatter_title(md_file) or md_file.stem.replace("-", " ").title()
        articles.append({"file": md_file.name, "title": title, "slug": md_file.stem})

    # Check for notebook
    has_notebook = (chapter_dir / "notebook.ipynb").exists()

    # Build index content
    lines = [
        "---",
        f"title: \"Chapter {ch_num}: {ch_title}\"",
        f"chapter: {ch_num}",
        "type: chapter-index",
        "---",
        "",
        f"# Chapter {ch_num}: {ch_title}",
        "",
    ]

    if has_notebook:
        lines.append("## Interactive Notebook")
        lines.append("")
        lines.append("- [notebook.ipynb](notebook.ipynb) — runnable code examples and exercises")
        lines.append("")

    if articles:
        lines.append("## Concepts")
        lines.append("")
        for a in articles:
            lines.append(f"- [[{a['slug']}]] — {a['title']}")
        lines.append("")

    index_path = chapter_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def build_concepts_index(book_dir):
    """Build alphabetical concept index across all chapters."""
    book_dir = Path(book_dir)
    chapters_dir = book_dir / "chapters"
    if not chapters_dir.exists():
        return None

    concepts = []  # (slug, title, chapter_folder)

    for ch_dir in sorted(chapters_dir.iterdir()):
        if not ch_dir.is_dir():
            continue
        for md_file in sorted(ch_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            title = _read_frontmatter_title(md_file) or md_file.stem.replace("-", " ").title()
            concepts.append(
                {
                    "slug": md_file.stem,
                    "title": title,
                    "chapter": ch_dir.name,
                }
            )

    # Sort alphabetically by slug
    concepts.sort(key=lambda c: c["slug"])

    lines = [
        "---",
        "title: Concept Index",
        "type: concept-index",
        "---",
        "",
        "# Concept Index",
        "",
        "Alphabetical listing of all concepts across chapters.",
        "",
    ]

    current_letter = ""
    for c in concepts:
        letter = c["slug"][0].upper()
        if letter != current_letter:
            current_letter = letter
            lines.append(f"## {letter}")
            lines.append("")
        lines.append(f"- [[{c['slug']}]] — {c['title']} _(Ch. {c['chapter'].split('-')[0]})_")

    lines.append("")

    index_path = book_dir / "concepts" / "index.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def build_book_index(book_dir):
    """Generate book-level index.md with chapter navigation."""
    book_dir = Path(book_dir)
    chapters_dir = book_dir / "chapters"

    # Read _meta.yaml for book info
    meta_path = book_dir / "_meta.yaml"
    meta = {}
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}

    title = meta.get("title", book_dir.name.replace("-", " ").title())

    # Scan chapter directories
    chapter_entries = []
    if chapters_dir.exists():
        for ch_dir in sorted(chapters_dir.iterdir()):
            if not ch_dir.is_dir():
                continue
            parts = ch_dir.name.split("-", 1)
            ch_num = parts[0]
            ch_title = parts[1].replace("-", " ").title() if len(parts) > 1 else ch_dir.name
            has_notebook = (ch_dir / "notebook.ipynb").exists()
            n_concepts = len([f for f in ch_dir.glob("*.md") if f.name != "index.md"])
            chapter_entries.append(
                {
                    "num": ch_num,
                    "title": ch_title,
                    "dir": ch_dir.name,
                    "has_notebook": has_notebook,
                    "n_concepts": n_concepts,
                }
            )

    lines = [
        "---",
        f"title: \"{title}\"",
        "type: book-index",
        "---",
        "",
        f"# {title}",
        "",
    ]

    if chapter_entries:
        lines.append("## Chapters")
        lines.append("")
        for ch in chapter_entries:
            status = "📓" if ch["has_notebook"] else "📄"
            lines.append(
                f"- {status} **Ch {ch['num']}**: [{ch['title']}](chapters/{ch['dir']}/index.md)"
                f" — {ch['n_concepts']} concepts"
            )
        lines.append("")

    lines.append(f"## [Concept Index](concepts/index.md)")
    lines.append("")

    index_path = book_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def build_library_index(library_dir):
    """Generate top-level library/index.md linking to all books."""
    library_dir = Path(library_dir)

    books = []
    for book_dir in sorted(library_dir.iterdir()):
        if not book_dir.is_dir() or book_dir.name.startswith("."):
            continue
        meta_path = book_dir / "_meta.yaml"
        if meta_path.exists():
            meta = yaml.safe_load(meta_path.read_text()) or {}
            books.append(
                {
                    "slug": book_dir.name,
                    "title": meta.get("title", book_dir.name),
                    "total_chapters": meta.get("total_chapters", "?"),
                }
            )

    lines = [
        "---",
        "title: Knowledge Library",
        "type: library-index",
        "---",
        "",
        "# Knowledge Library",
        "",
        "Distilled technical book knowledge bases.",
        "",
    ]

    for b in books:
        lines.append(f"- [{b['title']}]({b['slug']}/index.md) — {b['total_chapters']} chapters")

    lines.append("")

    index_path = library_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def validate_wikilinks(book_dir):
    """Find broken [[wikilinks]] in the book directory.

    Returns list of {"file": str, "link": str, "line": int}
    """
    book_dir = Path(book_dir)
    wikilink_pattern = re.compile(r"\[\[([^\]]+)\]\]")

    # Build set of all valid targets (markdown file stems)
    valid_targets = set()
    for md_file in book_dir.rglob("*.md"):
        valid_targets.add(md_file.stem)

    broken = []
    for md_file in book_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for line_num, line in enumerate(content.split("\n"), 1):
            for match in wikilink_pattern.finditer(line):
                link = match.group(1)
                # Handle [[link|display text]] format
                target = link.split("|")[0].strip()
                if target not in valid_targets:
                    broken.append(
                        {
                            "file": str(md_file.relative_to(book_dir)),
                            "link": target,
                            "line": line_num,
                        }
                    )

    return broken


def update_meta(book_dir, chapter_num, status="done", concepts=None):
    """Update _meta.yaml with chapter processing status."""
    book_dir = Path(book_dir)
    meta_path = book_dir / "_meta.yaml"

    meta = {}
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}

    if "chapters" not in meta:
        meta["chapters"] = {}

    meta["chapters"][chapter_num] = {
        "status": status,
        "distilled_at": str(date.today()),
    }
    if concepts:
        meta["chapters"][chapter_num]["concepts"] = concepts

    meta_path.write_text(
        yaml.dump(meta, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return meta_path


def _read_frontmatter_title(md_path):
    """Extract title from YAML frontmatter if present."""
    try:
        text = Path(md_path).read_text(encoding="utf-8")
    except Exception:
        return None

    if not text.startswith("---"):
        return None

    end = text.find("---", 3)
    if end == -1:
        return None

    try:
        fm = yaml.safe_load(text[3:end])
        return fm.get("title") if isinstance(fm, dict) else None
    except Exception:
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python wiki_builder.py <command> <book_dir>")
        print("Commands: chapter-index <chapter_dir>, concepts-index, book-index, library-index <library_dir>, validate")
        sys.exit(1)

    cmd = sys.argv[1]
    path = sys.argv[2]

    if cmd == "chapter-index":
        result = build_chapter_index(path)
        print(f"Built: {result}")
    elif cmd == "concepts-index":
        result = build_concepts_index(path)
        print(f"Built: {result}")
    elif cmd == "book-index":
        result = build_book_index(path)
        print(f"Built: {result}")
    elif cmd == "library-index":
        result = build_library_index(path)
        print(f"Built: {result}")
    elif cmd == "validate":
        broken = validate_wikilinks(path)
        if broken:
            print(f"Found {len(broken)} broken wikilinks:")
            for b in broken:
                print(f"  {b['file']}:{b['line']} → [[{b['link']}]]")
        else:
            print("All wikilinks valid.")
    else:
        print(f"Unknown command: {cmd}")
