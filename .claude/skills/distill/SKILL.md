# /distill — Technical Book Knowledge Distillation

Orchestrates the full pipeline: PDF extraction → concept identification → notebook creation → wiki articles → indexing → quality review.

## Usage

```
/distill <book-slug>                    # Process all chapters
/distill <book-slug> --chapter <N>      # Process single chapter
/distill <book-slug> --lint             # Validate wikilinks + check health
```

## Pipeline

When invoked, execute these stages in order for each chapter:

### Stage 0: RESOLVE CONFIG

Read `config.yaml` and extract the book entry for `{slug}`.

Set these variables for the rest of the pipeline:
- `content_type` = book entry's `content_type` (default: `programming`)
- `primary_language` = book entry's `primary_language` (default: `python` if programming, `null` otherwise)
- `skip_execution` = book entry's `skip_execution` (default: `false` if programming/theory, `true` if system-design/generic)
- `code_detection` = book entry's `code_detection` (default: `normal` if programming, `minimal` if system-design)

Use `content_type` to select prompt variants: `prompts/{prompt_name}_{content_type}.md`
If the variant file doesn't exist, fall back to `prompts/{prompt_name}.md`

### Stage 1: EXTRACT (if raw doesn't exist)

Check if `raw-data/{slug}/chapter-{NN}.md` exists. If not:

```bash
python3 src/extract.py init "books/{book pdf}" --slug {slug} --raw-dir raw-data
python3 src/extract.py extract "books/{book pdf}" --slug {slug} --raw-dir raw-data --chapter {N} --code-detection {code_detection} --fence-language {primary_language or "none"}
```

Also copy the PDF to the private submodule if not already there:
```bash
cp "books/{book pdf}" raw-data/{slug}/book.pdf
```

Read the extracted raw markdown to verify it looks reasonable (has headings, >1000 chars).

### Stage 2: IDENTIFY CONCEPTS

Read the raw chapter file: `raw-data/{slug}/chapter-{NN}.md`

Read the prompt template: `prompts/extract_concepts_{content_type}.md` (fallback: `prompts/extract_concepts.md`)

Following the prompt guidelines, analyze the chapter and identify 3-7 core concepts. Output as YAML and save to:
`raw-data/{slug}/chapter-{NN}-concepts.yaml`

### Stage 3: DISTILL (parallel agents)

Read: the raw chapter, the concepts YAML, and the relevant prompt templates.

Launch parallel agents:

**Agent A — Notebook Creator:**
- Read `prompts/create_notebook_{content_type}.md` (fallback: `prompts/create_notebook.md`)
- Read the raw chapter and concepts
- Generate notebook content as markdown with fenced code blocks
- For `system-design`: only ```python blocks become code cells (capacity estimation math). ```mermaid blocks stay as markdown cells.
- For `programming`/`theory`: ```python blocks become code cells as before.
- Use `src/notebook_builder.py` to create the .ipynb:
  ```python
  python3 -c "
  import sys; sys.path.insert(0, 'src')
  from notebook_builder import cells_from_markdown, build_notebook
  md = open('TEMP_NOTEBOOK.md').read()
  cells = cells_from_markdown(md)  # default: only python fences become code cells
  build_notebook('Chapter {N}: {Title}', cells, 'library/{slug}/chapters/{NN}-{ch-slug}/notebook.ipynb')
  "
  ```

**Agents B, C, D... — Wiki Article Writers (one per concept):**
- Read `prompts/create_wiki_article_{content_type}.md` (fallback: `prompts/create_wiki_article.md`)
- Read the raw chapter for context
- Write the article directly to: `library/{slug}/chapters/{NN}-{ch-slug}/{concept-slug}.md`
- Include proper YAML frontmatter, wikilinks, and content appropriate to content_type
- The `book` field in frontmatter uses the book title from config, NEVER the PDF filename or author name
- For `system-design`: include Mermaid diagrams, trade-off tables, real-world examples
- For `programming`: include runnable code examples
- For `theory`: include pseudocode, complexity tables, Python implementations

### Stage 4: BUILD INDEXES

After all distillation agents complete:

```python
python3 -c "
import sys; sys.path.insert(0, 'src')
from wiki_builder import build_chapter_index, build_concepts_index, build_book_index, build_library_index, update_meta
build_chapter_index('library/{slug}/chapters/{NN}-{ch-slug}')
build_concepts_index('library/{slug}')
build_book_index('library/{slug}')
build_library_index('library')
update_meta('library/{slug}', {N}, 'done', [{concept_slugs}])
"
```

### Stage 5: QUALITY REVIEW

**5a. Programmatic Validation:**
```bash
python3 src/wiki_builder.py validate library/{slug}
```
This runs both wikilink and Mermaid diagram validation. If errors are found, fix them before proceeding.

**5b. LLM Review Agent:**
- Read `prompts/quality_review_{content_type}.md` (fallback: `prompts/quality_review.md`)
- Read all generated files for this chapter
- For `programming`/`theory`: check code validity, notebook execution
- For `system-design`: check estimation math, trade-off balance, diagrams match text
- For all types: verify no PDF filename or author name in library/ files
- If `skip_execution` is true: skip `jupyter nbconvert --execute`, only validate notebook structure via nbformat
- Fix issues directly
- Report summary

### Stage 6: GIT COMMIT & PUSH

After all chapters are processed (or after each chapter if processing multiple):

**Push raw data to private repo:**
```bash
cd raw-data
git add .
git commit -m "Add raw extraction for {slug} chapter {N}"
git push origin main
cd ..
```

**Push distilled content to public repo:**
```bash
git add library/ raw-data
git commit -m "Add distilled content for {slug} chapter {N}"
git push origin main
```

Note: `git add raw-data` stages the submodule pointer update (not the raw content itself — that's in the private repo).

## Chapter Slug Convention

Chapter folder names: `{NN}-{kebab-case-title}`
- `01-python-data-model`
- `01-scale-from-zero-to-millions`
- `05-design-consistent-hashing`

Derive from the chapter title: lowercase, hyphens, drop articles (a/an/the) if the name gets long.

## Safety Constraints

- ONLY write to `library/` and `raw-data/` directories
- ONLY run: `python3 src/extract.py`, `python3 src/notebook_builder.py`, `python3 src/wiki_builder.py`, `python3 -c "..."` with src imports, and git commands for committing/pushing
- NEVER run `rm -rf` or destructive commands
- NEVER expose PDF filenames in public files (library/, prompts, docs)
- If extraction or distillation fails, report the error — do not retry more than once

## Lint Mode

When `--lint` is specified:
```python
python3 src/wiki_builder.py validate library/{slug}
```
Report broken wikilinks, missing indexes, chapters without notebooks.

## Multi-Chapter Processing

When no `--chapter` flag is given, process chapters in priority order from `config.yaml` (`priority_order` field, if present). Process one chapter at a time to manage context. After each chapter, report progress.
