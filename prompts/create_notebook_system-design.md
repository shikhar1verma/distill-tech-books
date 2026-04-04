# Create System Design Chapter Notebook

You are creating an interactive notebook for a chapter of a system design book. The notebook should be a **structured study guide** — someone should be able to work through it in 30-60 minutes and understand the complete system design.

## Input

You will be given:
- The raw chapter markdown
- The concept list (from extract_concepts)
- The book title, chapter number, and chapter title

## Output

Generate a sequence of notebook cells as markdown text. Use ```python fenced code blocks ONLY for capacity estimation calculations. Use ```mermaid for architecture diagrams (these stay as markdown cells). Everything else is markdown.

## Notebook Structure

1. **Title cell** (markdown):
   ```
   # Chapter N: Design a {System}
   *From: {Book Title}*
   ```

2. **TL;DR cell** (markdown):
   - 3-5 bullet points: what this system does, key scale numbers, main architectural decisions

3. **Requirements** (markdown):
   - **Functional Requirements**: bullet list of what the system must do
   - **Non-Functional Requirements**: scalability, availability, latency targets

4. **Back-of-Envelope Estimation** (Python code cell — RUNNABLE):
   ```python
   # Capacity Estimation
   dau = 100_000_000  # daily active users
   writes_per_day = dau * 0.1
   write_qps = writes_per_day / 86400
   print(f"Write QPS: {write_qps:,.0f}")
   print(f"Peak Write QPS (2x): {write_qps * 2:,.0f}")
   # Storage, bandwidth, etc.
   ```

5. **High-Level Design** (markdown with Mermaid):
   ```mermaid
   graph LR
     Client --> LB[Load Balancer]
     LB --> API[API Servers]
     API --> Cache[Redis Cache]
     API --> DB[(Database)]
   ```

6. **Deep Dive** sections (markdown + Mermaid per component):
   - One section per major concept/component
   - Detailed data flow diagrams
   - Explain the design choices

7. **Trade-offs and Alternatives** (markdown table):
   ```
   | Approach | Pros | Cons | When to Use |
   |----------|------|------|-------------|
   ```

8. **Key Takeaways** (markdown):
   - Numbered list, 5-7 points

9. **See Also** (markdown):
   - Wiki links: `[[concept-slug]]` for each concept article

## Rules

- **Only capacity estimation cells are Python code** — all math must be runnable Python 3.11+
- **Architecture diagrams use Mermaid** in markdown cells (NOT images)
- **Trade-off tables use standard markdown tables**
- Use realistic numbers from the chapter for estimations
- Never reference the PDF filename or author name in the notebook
- Use the book title from the concept YAML or chapter frontmatter
