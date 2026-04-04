# Extract Concepts from Chapter

You are analyzing a raw chapter extraction from a technical book. The book may cover any technical topic — DevOps, networking, databases, security, cloud infrastructure, or other subjects. Your job is to identify the **3-7 core concepts** that a reader must understand from this chapter.

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
    type: "conceptual"  # or "procedural", "architectural", "comparative", "reference"
    depends_on: []  # list of other concept slugs from this chapter
    key_examples:
      - type: "diagram"  # or "table", "narrative", "code", "command", "configuration", "workflow"
        description: "brief description of the example"
```

## Guidelines

- Choose concepts that represent **distinct, teachable ideas** — not just section headings
- A concept should be something a practitioner would want to look up or reference
- Do NOT assume the chapter contains code — it may be entirely conceptual, procedural, or architectural
- Adapt to whatever the chapter actually contains: diagrams, tables, workflows, CLI commands, config files, narratives
- `slug` must be valid as a filename: lowercase, hyphens, no spaces or special chars
- `depends_on` lists concepts from this chapter that should be understood first
- Keep `summary` to one clear sentence
- 3 concepts minimum, 7 maximum — aim for the sweet spot where each concept is substantial but focused
- **Never reference the PDF filename or author name** — use the book title from config
