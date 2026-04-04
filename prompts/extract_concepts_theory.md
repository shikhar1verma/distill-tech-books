# Extract Concepts from Theory Chapter

You are analyzing a raw chapter extraction from an algorithms or CS theory book. Your job is to identify the **3-7 core concepts** that a reader must understand from this chapter.

## Input

You will be given:
- The raw markdown of a chapter (from `raw-data/<slug>/chapter-NN.md`)
- The book title and chapter number

## Output

Return a YAML document with this structure:

```yaml
chapter: {number}
title: "{chapter title}"
concepts:
  - slug: "concept-name-in-kebab-case"
    title: "Human Readable Title"
    summary: "One sentence explaining what this concept is."
    type: "algorithm"  # or "proof", "complexity-analysis", "data-structure"
    depends_on: []  # list of other concept slugs from this chapter
    key_examples:
      - type: "algorithm"  # or "proof", "complexity-analysis", "data-structure"
        description: "brief description of the example"
```

## Guidelines

- Choose concepts that represent **distinct, teachable ideas** — not just section headings
- A concept should be something a student or developer would want to look up or reference
- Prefer concepts with clear algorithmic steps, formal definitions, or provable properties
- Look for: algorithms, data structures, mathematical proofs, complexity classes, recurrences, invariants
- `slug` must be valid as a filename: lowercase, hyphens, no spaces or special chars
- `depends_on` lists concepts from this chapter that should be understood first
- Keep `summary` to one clear sentence
- 3 concepts minimum, 7 maximum — aim for the sweet spot where each concept is substantial but focused
- **Never reference the PDF filename or author name** — use the book title from config
