# Create Theory Chapter Notebook

You are creating an interactive notebook for a chapter of an algorithms or CS theory book. The notebook should be a **self-contained learning experience** — someone should be able to work through it in 30-60 minutes and deeply understand the algorithms, data structures, or theoretical results.

## Input

You will be given:
- The raw chapter markdown
- The concept list (from extract_concepts)
- The book title, chapter number, and chapter title

## Output

Generate a sequence of notebook cells as markdown text. Use ```python fenced code blocks for runnable implementation and demonstration cells. Use ```pseudocode for algorithm pseudocode (these stay as markdown cells). Everything else is markdown.

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

   a. **Definition** (markdown):
      Formal or semi-formal definition. State the problem, structure, or theorem precisely. Use LaTeX notation for mathematical expressions where appropriate (e.g., `$O(n \log n)$`).

   b. **Pseudocode** (markdown with ```pseudocode fence — stays as markdown cell):
      ```pseudocode
      ALGORITHM-NAME(input)
        1. step one
        2. step two
        3. if condition
        4.     then action
        5. return result
      ```

   c. **Python Implementation** (code cell — RUNNABLE):
      ```python
      def algorithm_name(data: list[int]) -> list[int]:
          """Reference implementation with clear comments."""
          # Step 1: explanation
          ...
          return result

      # Demonstrate with a concrete input
      sample = [5, 2, 8, 1, 9, 3]
      result = algorithm_name(sample)
      print(f"Input:  {sample}")
      print(f"Output: {result}")
      ```

   d. **Complexity** (markdown table):
      ```
      | Case    | Time         | Space   | Notes                    |
      |---------|--------------|---------|--------------------------|
      | Best    | O(n)         | O(1)    | Already sorted input     |
      | Average | O(n log n)   | O(n)    | Random input             |
      | Worst   | O(n^2)       | O(1)    | Reverse-sorted input     |
      ```

   e. **Worked Example** (markdown + optional code cell):
      Step-by-step trace with a concrete input. Show the state at each iteration or recursive call. Optionally include a runnable code cell that prints the trace.

4. **Practice Problems** (markdown + code scaffolds):
   - 2-3 exercises with clear instructions in comments
   - Start with `# Exercise N: description`
   - Include a `# Expected: ...` hint
   - Provide function stubs for the student to fill in

5. **Key Takeaways** (markdown):
   - Numbered list, 5-7 points
   - Each takeaway is one actionable sentence

6. **See Also** (markdown):
   - Wiki links: `[[concept-slug]]` for each concept article
   - External references if highly relevant

## Rules

- **All Python code must be self-contained** — no imports from the book's source code
- **All Python code must run** in a fresh Python 3.11+ environment (stdlib only unless explicitly noted)
- Use `print()` for output — don't rely on notebook auto-display for important results
- Include type hints where they aid clarity
- Prefer short, focused code cells (5-20 lines each) over long monolithic ones
- Use descriptive variable names, not `x`, `y`, `foo`, `bar`
- Pseudocode fences stay as markdown cells — only Python fences become code cells
- Complexity tables must match the actual algorithm — do not guess Big-O, derive it from the code
- Never reference the PDF filename or author name in the notebook — use the book title
