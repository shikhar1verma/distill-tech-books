# Create System Design Wiki Article

You are writing a concept article for an Obsidian-compatible wiki. The article should help a developer quickly understand a system design concept, pattern, or component.

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
tags: [system-design, {topic-tags}]
related:
  - "[[related-concept-1]]"
  - "[[related-concept-2]]"
---

# {Concept Title}

> **One-sentence summary.** This is the concept in a nutshell.

## How It Works

Explain the architecture, component, or pattern in 2-3 paragraphs. Include a Mermaid diagram showing the data flow or component relationships:

\```mermaid
graph LR
  A[Component A] --> B[Component B]
  B --> C[(Storage)]
\```

## When to Use

Concrete scenarios where this pattern/component/approach applies. Give 2-3 practical situations.

## Trade-offs

| Aspect | Advantage | Disadvantage |
|--------|-----------|--------------|
| ... | ... | ... |

## Real-World Examples

- **System X**: Uses this because...
- **System Y**: A different approach because...

## Common Pitfalls

- **Pitfall 1**: What goes wrong and why
- **Pitfall 2**: Another common mistake

## See Also

- [[related-concept]] — how it connects
- [[another-concept]] — complementary idea
```

## Rules

- **Target length**: 500-1000 words (not counting diagrams/tables)
- **Audience**: Knows basic web architecture (clients, servers, databases, caches) but not this specific design pattern
- **Wikilinks**: Use `[[slug]]` format — Obsidian resolves by filename across the vault
- **Diagrams**: Use Mermaid for architecture/flow diagrams, not ASCII art
- **Tags**: Include `system-design` plus 2-3 topic tags (e.g., `caching`, `databases`, `load-balancing`)
- **No filler**: Every sentence should teach something
- **Frontmatter `related`**: Only link to concepts that actually exist in the concept list
- **Never reference the PDF filename or author name** in the article body — use the book title
