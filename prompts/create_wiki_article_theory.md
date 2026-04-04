# Create Theory Wiki Article

You are writing a concept article for an Obsidian-compatible wiki. The article should help a developer or student quickly understand an algorithm, data structure, or CS theory concept.

## Input

You will be given:
- The concept name, slug, summary, and type (from the concept list)
- The raw chapter markdown for context
- The book title and chapter number

## Output

A markdown file with YAML frontmatter and the sections below.

## Article Template

```markdown
---
title: "{Concept Title}"
book: "{Book Title}"
chapter: {N}
tags: [algorithms, {topic-tags}]
related:
  - "[[related-concept-1]]"
  - "[[related-concept-2]]"
---

# {Concept Title}

> **One-sentence summary.** This is the concept in a nutshell.

## Definition

Precise definition of the algorithm, data structure, or theorem. State the problem it solves, the invariants it maintains, or the property it proves. Use LaTeX for mathematical expressions where appropriate.

## How It Works

Explain the algorithm or structure in 2-3 paragraphs. Use concrete language. Walk through the key insight that makes it work.

Include pseudocode:

\```pseudocode
ALGORITHM-NAME(input)
  1. step one
  2. step two
  3. return result
\```

## Complexity

| Case    | Time       | Space   | Notes              |
|---------|------------|---------|--------------------|
| Best    | O(...)     | O(...)  | When this happens  |
| Average | O(...)     | O(...)  | Typical case       |
| Worst   | O(...)     | O(...)  | When this happens  |

## Python Implementation

\```python
# Clear, runnable reference implementation
def algorithm_name(data):
    ...
    return result
\```

## In Practice

When and why you'd use this in real code. Give 1-2 practical scenarios where this algorithm or structure is the right choice over alternatives.

## See Also

- [[related-concept]] — how it connects
- [[another-concept]] — complementary idea
```

## Rules

- **Target length**: 500-1000 words (not counting code or tables)
- **Audience**: Knows basic programming (functions, loops, recursion) but not this specific algorithm or structure
- **Wikilinks**: Use `[[slug]]` format — Obsidian resolves by filename across the vault
- **Code examples**: Must be runnable Python 3.11+ with stdlib only
- **Tags**: Include `algorithms` plus 2-3 topic tags (e.g., `sorting`, `graphs`, `dynamic-programming`, `trees`, `complexity`)
- **No filler**: Every sentence should teach something. Cut "as we can see" type phrases
- **Frontmatter `related`**: Only link to concepts that actually exist in the concept list
- **Complexity claims must match the algorithm** — derive Big-O from the code/pseudocode, do not guess
- **Pseudocode must be consistent** with the Python implementation — same steps, same logic
- **Never reference the PDF filename or author name** in the article body — use the book title
