# Extract Concepts from System Design Chapter

You are analyzing a raw chapter extraction from a system design book. Your job is to identify the **3-7 core concepts** that a reader must understand from this chapter.

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
    type: "pattern"  # or "comparison", "estimation", "case-study"
    depends_on: []  # list of other concept slugs from this chapter
    key_artifacts:
      - type: "diagram"  # or "comparison-table", "estimation", "trade-off"
        description: "brief description of the artifact"
```

## Guidelines

- Each chapter in a system design book typically IS a standalone design problem
- Concepts should be the **subsystem components and key design decisions** discussed
  - e.g., for "Design a URL Shortener": hash function, read-heavy optimization, cache layer, analytics pipeline
- Look for: system components, data flows, scaling strategies, trade-offs, bottleneck analyses
- `slug` must be valid as a filename: lowercase, hyphens, no spaces or special chars
- `depends_on` lists concepts from this chapter that should be understood first
- Keep `summary` to one clear sentence
- 3 concepts minimum, 7 maximum
- **Never reference the PDF filename or author name** — use the book title from config
