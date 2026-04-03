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

### Stage 1: EXTRACT (if raw doesn't exist)

Check if `raw-data/{slug}/chapter-{NN}.md` exists. If not:

```bash
python3 src/extract.py init "books/{book pdf}" --slug {slug}
python3 src/extract.py extract "books/{book pdf}" --slug {slug} --chapter {N}
```

Also copy the PDF to the private submodule if not already there:
```bash
cp "books/{book pdf}" raw-data/{slug}/book.pdf
```

Read the extracted raw markdown to verify it looks reasonable (has headings, code blocks, >1000 chars).

### Stage 2: IDENTIFY CONCEPTS

Read the raw chapter file: `raw-data/{slug}/chapter-{NN}.md`

Read the prompt template: `prompts/extract_concepts.md`

Following the prompt guidelines, analyze the chapter and identify 3-7 core concepts. Output as YAML and save to:
`raw-data/{slug}/chapter-{NN}-concepts.yaml`

### Stage 3: DISTILL (parallel agents)

Read: the raw chapter, the concepts YAML, and the relevant prompt templates.

Launch parallel agents:

**Agent A — Notebook Creator:**
- Read `prompts/create_notebook.md`
- Read the raw chapter and concepts
- Generate notebook content as markdown with ```python fenced code blocks
- Use `src/notebook_builder.py` to create the .ipynb:
  ```python
  python3 -c "
  import sys; sys.path.insert(0, 'src')
  from notebook_builder import cells_from_markdown, build_notebook
  md = open('TEMP_NOTEBOOK.md').read()
  cells = cells_from_markdown(md)
  build_notebook('Chapter {N}: {Title}', cells, 'library/{slug}/chapters/{NN}-{ch-slug}/notebook.ipynb')
  "
  ```

**Agents B, C, D... — Wiki Article Writers (one per concept):**
- Read `prompts/create_wiki_article.md`
- Read the raw chapter for context
- Write the article directly to: `library/{slug}/chapters/{NN}-{ch-slug}/{concept-slug}.md`
- Include proper YAML frontmatter, wikilinks, and code examples

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

Launch a review agent:
- Read `prompts/quality_review.md`
- Read all generated files for this chapter
- Check code validity, wikilinks, notebook structure
- Web search for outdated Python patterns
- Fix issues directly
- Report summary

## Chapter Slug Convention

Chapter folder names: `{NN}-{kebab-case-title}`
- `01-python-data-model`
- `02-array-of-sequences`
- `03-dictionaries-and-sets`

Derive from the chapter title: lowercase, hyphens, drop articles (a/an/the) if the name gets long.

## Safety Constraints

- ONLY write to `library/` and `raw-data/` directories
- ONLY run: `python3 src/extract.py`, `python3 src/notebook_builder.py`, `python3 src/wiki_builder.py`, `python3 -c "..."` with src imports, and git commands for committing/pushing
- NEVER run `rm -rf` or destructive commands
- If extraction or distillation fails, report the error — do not retry more than once

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

## Lint Mode

When `--lint` is specified:
```python
python3 src/wiki_builder.py validate library/{slug}
```
Report broken wikilinks, missing indexes, chapters without notebooks.

## Multi-Chapter Processing

When no `--chapter` flag is given, process chapters in priority order from `config.yaml` (`priority_order` field). Process one chapter at a time to manage context. After each chapter, report progress.
