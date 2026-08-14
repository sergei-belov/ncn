---
name: docs-writer
description: Write, revise, and validate concise project documentation in any repository. Use when Codex needs to create or update Markdown documentation such as READMEs, guides, specifications, API or architecture docs, UI page descriptions, and database table descriptions while following local project conventions and checking facts, structure, and links.
---

# Docs Writer

## Workflow

1. Read the applicable `AGENTS.md` files and discover the project's documentation roots, guides, templates, indexes, and validation commands. Do not assume fixed paths.
2. Identify the target files and authoritative sources. Prefer, in order: the user request, project specifications or contracts, implementation when local rules allow it, and neighboring documentation.
3. Read only the relevant sources and nearest documents needed to match terminology, language, structure, and link style.
4. Select the relevant guidance from `references/task-map.md`. Read a page or table template only for that document type.
5. Write the smallest complete document. Use concrete names and verified facts; omit irrelevant sections and do not invent missing details.
6. Update navigation, indexes, or companion docs when the documentation inventory or public contract changes.
7. Validate every changed document with `references/validation.md`, the bundled checker, and any project-provided documentation checks. Fix failures before finishing.

## Rules

- Follow project-local instructions over this generic guidance.
- Modify documentation files only unless the user explicitly expands the task. Read source files when needed and permitted to verify documentation.
- Preserve established language, tone, terminology, heading hierarchy, and formatting.
- Keep page and table descriptions compact. Prefer short paragraphs, bullets, and tables; avoid repeating the same fact in several sections.
- Distinguish optional fields (`field?: Type`) from nullable values (`null | Type`) when documenting typed contracts.
- Record an explicit documentation gap when a material fact cannot be verified.
- Keep internal links relative when that matches the project convention.

## References

- Read `references/docs-guide.md` for source precedence and writing principles.
- Read `references/task-map.md` to choose task-specific inputs and companion files.
- Read `references/page-template.md` only for UI page or screen documentation.
- Read `references/table-template.md` only for database table documentation.
- Read `references/validation.md` before completing any documentation change.
