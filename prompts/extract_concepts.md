# Extract Concepts from Chapter

You are analyzing a raw chapter extraction from a technical book. Your job is to identify the **3-7 core concepts** that a reader must understand from this chapter.

## Input

You will be given:
- The raw markdown of a chapter (from `raw/chapter-NN.md`)
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
    type: "code-heavy"  # or "theory-heavy" or "mixed"
    depends_on: []  # list of other concept slugs from this chapter
    key_code_examples:
      - "brief description of main code example"
```

## Guidelines

- Choose concepts that represent **distinct, teachable ideas** — not just section headings
- A concept should be something a developer would want to look up or reference
- Prefer concepts that have runnable code examples in the chapter
- `slug` must be valid as a filename: lowercase, hyphens, no spaces or special chars
- `depends_on` lists concepts from this chapter that should be understood first
- Keep `summary` to one clear sentence
- 3 concepts minimum, 7 maximum — aim for the sweet spot where each concept is substantial but focused
