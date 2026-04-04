# Create Wiki Article — Generic

You are writing a concept article for an Obsidian-compatible wiki. The article should help a practitioner quickly understand a technical concept from any domain — DevOps, networking, databases, security, cloud infrastructure, or other subjects.

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
tags: [{topic-tags}]
related:
  - "[[related-concept-1]]"
  - "[[related-concept-2]]"
---

# {Concept Title}

> **One-sentence summary.** This is the concept in a nutshell.

## How It Works

Explain the concept in 2-3 paragraphs. Use concrete language. If the concept involves architecture or a workflow, include a Mermaid diagram:

\```mermaid
graph LR
  A[Component A] --> B[Component B]
\```

If the concept involves commands, configuration, or code, include a representative example in the appropriate language. If it is purely conceptual, explain with clear prose and analogies.

## In Practice

When and why you'd use this in real systems. Give 1-2 practical scenarios with enough specificity to be actionable.

## Common Pitfalls

- **Pitfall 1**: What goes wrong and why
- **Pitfall 2**: Another common mistake

## See Also

- [[related-concept]] — how it connects
- [[another-concept]] — complementary idea
```

## Rules

- **Target length**: 500-1000 words (not counting diagrams, tables, or code)
- **Audience**: Has general technical literacy but may not know this specific topic
- **Wikilinks**: Use `[[slug]]` format — Obsidian resolves by filename across the vault
- **Tags**: Use 2-4 topic-relevant tags (e.g., `networking`, `load-balancing`, `dns`). Do NOT hardcode a first tag — choose tags that fit the actual content
- **No language-specific assumptions**: Do not assume the reader knows any particular programming language. If the concept involves code or commands, use whatever language or tool is natural for the topic
- **Diagrams**: Use Mermaid for architecture/flow diagrams where they add clarity, not ASCII art
- **No filler**: Every sentence should teach something. Cut "as we can see" type phrases
- **Frontmatter `related`**: Only link to concepts that actually exist in the concept list
- **Never reference the PDF filename or author name** in the article body — use the book title
