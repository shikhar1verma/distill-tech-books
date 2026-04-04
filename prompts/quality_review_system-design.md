# Quality Review — System Design

You are reviewing the distilled output for a single chapter of a system design book. Your job is to find and fix issues — then report what you changed.

## Input

You will be given:
- All generated files for one chapter:
  - `chapters/NN-slug/index.md` — chapter index
  - `chapters/NN-slug/notebook.ipynb` — interactive notebook
  - `chapters/NN-slug/*.md` — wiki concept articles
- The raw chapter source for reference

## Checks

### 1. Diagram Validity
- All Mermaid blocks have valid syntax (balanced brackets, valid node/edge definitions)
- Diagrams match the text descriptions (components mentioned in text appear in diagrams)
- No orphan nodes in diagrams

### 2. Estimation Accuracy
- Capacity estimation Python cells are syntactically valid and execute
- Numbers are realistic (not off by orders of magnitude)
- All print() statements produce readable output

### 3. Trade-off Balance
- Trade-off tables are not one-sided (each approach has real pros AND cons)
- Alternatives are genuinely different approaches, not strawmen

### 4. Wikilinks
- Every `[[slug]]` in articles and notebook resolves to an existing .md file
- No orphan articles (every concept is linked from chapter index)
- Cross-references between articles are bidirectional where appropriate

### 5. Content Accuracy
- Explanations match what the book actually says
- No hallucinated services or APIs
- Scale numbers match the chapter's stated requirements

### 6. Privacy
- No PDF filename or author name appears in any library/ file
- Book title is used consistently

## Output

Fix issues directly in the files. Then report:

```
## Review Summary

### Fixed
- [file]: description of fix

### Warnings
- [file]: potential issue that needs human review

### Stats
- Mermaid diagrams checked: N
- Estimation cells checked: N
- Wikilinks checked: N
- Issues fixed: N
- Warnings: N
```
