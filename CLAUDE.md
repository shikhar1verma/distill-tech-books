# Distill Tech Books — Project Guide

## What This Project Does

Automated pipeline: PDF tech books → distilled knowledge base (Jupyter notebooks + Obsidian wiki).
User drops a PDF in `books/`, runs `/distill <slug>`, pipeline handles everything including git push.

## Repository Structure

**Two repos:**
- `distill-tech-books` (public) — pipeline code + distilled output in `library/`
- `distill-tech-books-raw` (private) — source PDFs + raw extractions, linked as git submodule at `raw-data/`

**Key paths:**
- `books/` — local PDF drop zone (gitignored, user puts PDFs here)
- `raw-data/<slug>/` — git submodule (private repo), stores `book.pdf` + `chapter-NN.md` + `chapter-NN-concepts.yaml`
- `library/<slug>/chapters/` — distilled output (public), one folder per chapter with `notebook.ipynb` + wiki `.md` files
- `library/<slug>/concepts/index.md` — alphabetical cross-chapter concept index
- `src/` — extraction and build scripts
- `prompts/` — LLM prompt templates for distillation
- `.claude/skills/distill/SKILL.md` — the `/distill` orchestrator skill

## Adding a New Book (End-to-End)

1. User drops PDF into `books/`
2. User adds entry to `config.yaml`:
   ```yaml
   books:
     new-book-slug:
       title: "Book Title"
       author: "Author Name"
       edition: "1st"
       pdf: "books/Book Title.pdf"
       slug: new-book-slug
       total_chapters: N
   ```
3. User runs `/distill new-book-slug` (or in YOLO mode: `claude -p "/distill new-book-slug" --dangerously-skip-permissions`)
4. Pipeline does:
   - Copies PDF to `raw-data/new-book-slug/book.pdf`
   - Runs `src/extract.py` → raw markdown to `raw-data/new-book-slug/`
   - Identifies concepts → `raw-data/new-book-slug/chapter-NN-concepts.yaml`
   - Creates `library/new-book-slug/chapters/NN-slug/` with notebook + wiki articles
   - Builds indexes
   - Quality review
   - Commits + pushes `raw-data/` to private repo
   - Commits + pushes public repo

## Git Workflow

**Raw data (private):**
```bash
cd raw-data
git add .
git commit -m "Add raw extraction for <slug> chapter N"
git push origin main
cd ..
```

**Public content:**
```bash
git add library/ raw-data .gitmodules
git commit -m "Add distilled content for <slug> chapter N"
git push origin main
```

`git add raw-data` stages the submodule pointer (commit hash), not the actual raw files.

## Conventions

- **Chapter folders**: `NN-kebab-case-title` (e.g., `01-python-data-model`)
- **Wiki articles**: `kebab-case-concept.md` with YAML frontmatter
- **Wikilinks**: Use `[[concept-name]]` (Obsidian resolves by filename across vault)
- **Notebooks**: One per chapter at `chapters/NN-slug/notebook.ipynb`, all code self-contained (stdlib only)
- **Frontmatter**: Every `.md` article has `title`, `book`, `chapter`, `tags`, `related` fields
- **Raw output path**: Always `raw-data/<slug>/`, never `library/<slug>/raw/`

## Scripts

| Script | Purpose |
|--------|---------|
| `src/extract.py init <pdf> --slug <s>` | Parse TOC, create directory structure |
| `src/extract.py extract <pdf> --slug <s>` | Extract all chapters to raw markdown |
| `src/notebook_builder.py` | Convert structured cells to valid `.ipynb` |
| `src/wiki_builder.py book-index <dir>` | Rebuild book-level index |
| `src/wiki_builder.py concepts-index <dir>` | Rebuild alphabetical concept index |
| `src/wiki_builder.py validate <dir>` | Check wikilinks + Mermaid diagrams |
| `src/wiki_builder.py validate-mermaid <dir>` | Check Mermaid diagrams only (requires Node.js) |

## Git Commits

- **Never add `Co-Authored-By` trailers** to commit messages. The repo owner is the sole author of all commits.

## Safety

- Never `rm -rf`, `sudo`, `git push --force`, `git reset --hard`
- Only write to `library/` and `raw-data/`
- Only run Python scripts from `src/` and git commands
- `books/*.pdf` is gitignored — PDFs stay local, copies go to private `raw-data/`
