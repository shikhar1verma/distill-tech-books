# Create Wiki Article

You are writing a concept article for an Obsidian-compatible wiki. The article should help a developer quickly understand and apply a specific programming concept.

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
tags: [python, {topic-tags}]
related:
  - "[[related-concept-1]]"
  - "[[related-concept-2]]"
---

# {Concept Title}

> **One-sentence summary.** This is the concept in a nutshell.

## How It Works

Explain the concept in 2-3 paragraphs. Use concrete language. Reference Python internals where relevant but don't assume the reader knows them yet.

Include a key code example:

\```python
# Clear, runnable example
\```

## In Practice

When and why you'd use this in real code. Give 1-2 practical scenarios.

## Common Pitfalls

- **Pitfall 1**: What goes wrong and why
- **Pitfall 2**: Another common mistake

## See Also

- [[related-concept]] — how it connects
- [[another-concept]] — complementary idea
```

## Rules

- **Target length**: 500-1000 words (not counting code)
- **Audience**: Knows Python basics (functions, classes, loops) but not this specific concept
- **Wikilinks**: Use `[[slug]]` format — Obsidian resolves by filename across the vault
- **Code examples**: Must be runnable Python 3.11+ with stdlib only
- **Tags**: Include `python` plus 2-3 topic tags (e.g., `data-model`, `sequences`, `oop`)
- **No filler**: Every sentence should teach something. Cut "as we can see" type phrases
- **Frontmatter `related`**: Only link to concepts that actually exist in the concept list
