# Create Chapter Notebook — Generic

You are creating an interactive notebook for a chapter of a technical book. The book may cover any technical topic — DevOps, networking, databases, security, cloud infrastructure, or other subjects. The notebook should be a **structured study guide** — someone should be able to work through it in 30-60 minutes and grasp the chapter's key ideas.

## Input

You will be given:
- The raw chapter markdown
- The concept list (from extract_concepts)
- The book title, chapter number, and chapter title

## Output

Generate a sequence of notebook cells as markdown text. Use fenced code blocks for any executable content (e.g., ```python, ```bash, ```sql). If the chapter has no executable content, the notebook is still useful as a structured study guide — use only markdown cells.

## Notebook Structure

1. **Title cell** (markdown):
   ```
   # Chapter N: {Title}
   *From: {Book Title}*
   ```

2. **TL;DR cell** (markdown):
   - 3-5 bullet points summarizing what you'll learn
   - Keep each point to one sentence

3. **For each concept** (repeat — adapt the pattern to the content):

   a. **Explanation** (markdown):
      What is this concept? Why does it matter? Plain-language explanation in 2-3 paragraphs.

   b. **Visual Aid** (markdown, if appropriate):
      - Use Mermaid diagrams for architectures, workflows, or data flows:
        ```mermaid
        graph LR
          A[Component] --> B[Component]
        ```
      - Use markdown tables for comparisons or reference data
      - Use bullet lists for step-by-step procedures
      - Skip this cell if the concept does not benefit from a visual

   c. **Practical Detail** (markdown or code, depending on content):
      - If the chapter includes CLI commands: show them in a fenced code block (```bash) as a **markdown cell** (not executable unless the commands are safe and self-contained)
      - If the chapter includes configuration: show a representative example (```yaml, ```json, etc.)
      - If the chapter includes runnable code: use a Python code cell (```python — RUNNABLE)
      - If the chapter is purely conceptual: use a worked scenario or case study in markdown

   d. **Key Points** (markdown):
      2-3 bullet takeaways for this concept

4. **Comparison / Summary Table** (markdown, if applicable):
   ```
   | Approach | Strengths | Weaknesses | Best For |
   |----------|-----------|------------|----------|
   ```

5. **Key Takeaways** (markdown):
   - Numbered list, 5-7 points
   - Each takeaway is one actionable sentence

6. **See Also** (markdown):
   - Wiki links: `[[concept-slug]]` for each concept article
   - External references if highly relevant

## Rules

- **Adapt to the content** — do not force a code-heavy structure on a conceptual chapter or a purely narrative structure on a chapter with commands/configs
- **If code cells exist**, they must be self-contained and run in Python 3.11+ (stdlib only unless noted)
- **If no executable content exists**, the notebook should still be a complete, useful study guide using markdown cells
- **Mermaid diagrams** go in markdown cells for architectures and workflows
- **CLI commands and configs** go in fenced code blocks inside markdown cells (not as executable code cells) unless they are safe, self-contained Python
- Use `print()` for output in any runnable Python cells
- Prefer short, focused cells over long monolithic ones
- Never reference the PDF filename or author name in the notebook — use the book title
