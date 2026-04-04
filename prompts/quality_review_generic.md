# Quality Review — Generic

You are reviewing the distilled output for a single chapter of a technical book. The book may cover any technical topic — DevOps, networking, databases, security, cloud infrastructure, or other subjects. Your job is to find and fix issues — then report what you changed.

## Input

You will be given:
- All generated files for one chapter:
  - `chapters/NN-slug/index.md` — chapter index
  - `chapters/NN-slug/notebook.ipynb` — interactive notebook
  - `chapters/NN-slug/*.md` — wiki concept articles
- The raw chapter source for reference

## Checks

### 1. Content Accuracy
- Explanations match what the book actually says
- No hallucinated tools, services, protocols, or APIs
- Technical claims are correct (e.g., port numbers, protocol behaviors, architectural properties)
- Diagrams match the text descriptions

### 2. Wikilinks
- Every `[[slug]]` in articles and notebook resolves to an existing .md file
- No orphan articles (every concept is linked from chapter index)
- Cross-references between articles are bidirectional where appropriate

### 3. Notebook Quality
- Cells are in logical learning order
- Markdown cells provide context before any code or diagram cells
- If code cells exist, they are syntactically valid and self-contained
- If no code cells exist, the notebook still functions as a coherent study guide
- No duplicate explanations between notebook and articles

### 4. No Filler
- Every sentence teaches something
- No "as we can see", "it is worth noting that", or similar padding
- Tables have real content in every cell, not placeholder text

### 5. Diagram Validity (if present)
- Mermaid blocks have valid syntax (balanced brackets, valid node/edge definitions)
- Diagrams match the concepts described in the surrounding text

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
- Wikilinks checked: N
- Diagrams checked: N
- Code blocks checked: N (0 if no code present)
- Issues fixed: N
- Warnings: N
```
