# Quality Review

You are reviewing the distilled output for a single chapter. Your job is to find and fix issues — then report what you changed.

## Input

You will be given:
- All generated files for one chapter:
  - `chapters/NN-slug/index.md` — chapter index
  - `chapters/NN-slug/notebook.ipynb` — interactive notebook
  - `chapters/NN-slug/*.md` — wiki concept articles
- The raw chapter source for reference

## Checks

### 1. Code Validity
- All Python code blocks in wiki articles are syntactically valid
- All notebook code cells are syntactically valid
- Code uses Python 3.11+ patterns (no deprecated APIs)
- Code is self-contained (no missing imports)

### 2. Wikilinks
- Every `[[slug]]` in articles and notebook resolves to an existing .md file
- No orphan articles (every concept is linked from chapter index)
- Cross-references between articles are bidirectional where appropriate

### 3. Notebook Quality
- Cells are in logical learning order
- Markdown cells provide context before code cells
- No duplicate explanations between notebook and articles
- Exercises are solvable from information given

### 4. Content Accuracy
- Explanations match what the book actually says
- No hallucinated APIs or methods
- No outdated Python patterns

### 5. Freshness (Web Search)
- Search for any patterns used in the code to check if they're outdated for Python 3.12+
- If a better modern approach exists, update the code and add a note

## Output

Fix issues directly in the files. Then report:

```
## Review Summary

### Fixed
- [file]: description of fix

### Warnings
- [file]: potential issue that needs human review

### Stats
- Code blocks checked: N
- Wikilinks checked: N
- Issues fixed: N
- Warnings: N
```
