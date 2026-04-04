# Quality Review — Theory

You are reviewing the distilled output for a single chapter of an algorithms or CS theory book. Your job is to find and fix issues — then report what you changed.

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
- Implementations produce correct output for the demonstrated inputs

### 2. Complexity Correctness
- Complexity claims in tables match the actual algorithm
- Big-O notation is correct for the code as written (e.g., a nested loop over n elements is O(n^2), not O(n log n))
- Best/average/worst cases are correctly identified
- Space complexity accounts for auxiliary data structures, not just input

### 3. Pseudocode Consistency
- Pseudocode matches the Python implementation in logic and structure
- No steps in pseudocode that are missing from the Python code (or vice versa)
- Edge cases handled consistently between pseudocode and code

### 4. Wikilinks
- Every `[[slug]]` in articles and notebook resolves to an existing .md file
- No orphan articles (every concept is linked from chapter index)
- Cross-references between articles are bidirectional where appropriate

### 5. Notebook Quality
- Cells are in logical learning order: Definition -> Pseudocode -> Implementation -> Complexity -> Worked Example
- Markdown cells provide context before code cells
- Worked examples trace through a concrete input step by step
- Practice problems are solvable from information given
- No duplicate explanations between notebook and articles

### 6. Content Accuracy
- Explanations match what the book actually says
- No hallucinated algorithms, theorems, or properties
- Definitions are precise and correct

### 7. Privacy
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
- Code blocks checked: N
- Complexity claims checked: N
- Wikilinks checked: N
- Issues fixed: N
- Warnings: N
```
