# Create Chapter Notebook

You are creating an interactive Jupyter notebook for a chapter of a technical book. The notebook should be a **self-contained learning experience** — someone should be able to work through it in 30-60 minutes and grasp the chapter's key ideas.

## Input

You will be given:
- The raw chapter markdown
- The concept list (from extract_concepts)
- The book title, chapter number, and chapter title

## Output

Generate a sequence of notebook cells as markdown text, using ```python fenced code blocks for code cells. Everything outside code fences becomes markdown cells.

## Notebook Structure

1. **Title cell** (markdown):
   ```
   # Chapter N: {Title}
   *From: {Book Title}*
   ```

2. **TL;DR cell** (markdown):
   - 3-5 bullet points summarizing what you'll learn
   - Keep each point to one sentence

3. **For each concept** (repeat this pattern):
   - **Explanation** (markdown): Plain-language explanation. What is it? Why does it matter?
   - **Code example** (code): A clear, runnable demonstration. Include comments.
   - **Output discussion** (markdown): What the code shows. Any surprising behavior.
   - **Deeper dive** (code, optional): More advanced usage or edge cases.

4. **Try It Yourself** (2-3 code cells):
   - Exercises with clear instructions in comments
   - Start with `# Exercise N: description`
   - Include a `# Expected: ...` hint

5. **Key Takeaways** (markdown):
   - Numbered list, 5-7 points
   - Each takeaway is one actionable sentence

6. **See Also** (markdown):
   - Wiki links: `[[concept-slug]]` for each concept article
   - External references if highly relevant

## Rules

- **All code must be self-contained** — no imports from the book's source code
- **All code must run** in a fresh Python 3.11+ environment (stdlib only unless explicitly noted)
- Use `print()` for output — don't rely on notebook auto-display for important results
- Include type hints where they aid clarity
- Prefer short, focused code cells (5-20 lines each) over long monolithic ones
- Use real-world-ish variable names, not `x`, `y`, `foo`, `bar`
- If the book has a signature example (like FrenchDeck in Ch1), build around it
