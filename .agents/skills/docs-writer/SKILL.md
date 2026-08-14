---
name: docs-writer
description: Create, restructure, revise, and validate evidence-backed Markdown project documentation in any repository. Use when Codex needs to document the current implementation state, organize documentation by product area, service, or domain, or update READMEs, guides, specifications, API and architecture docs, UI page descriptions, and database table descriptions while preserving local conventions and verifying facts, structure, navigation, and links.
---

# Docs Writer

## Workflow

1. Read the applicable `AGENTS.md` files. Discover documentation roots, guides, templates, indexes, and validation commands; do not assume fixed paths.
2. Inspect the target documentation's working state. In a Git repository, check status and staged and unstaged diffs for affected files so pre-existing edits remain intact.
3. Classify the task with `references/task-map.md`. For a documentation set, restructure, or current-state audit, also read `references/structure-and-state.md`; read page and table templates only for those document types.
4. Define the audience, scope, ownership boundary, and state being documented. Unless the user names a release or commit, treat “current” as the current working tree and do not imply that uncommitted code is released or deployed.
5. Identify authoritative evidence for each material claim using `references/docs-guide.md`. For cross-boundary claims such as client/server compatibility, declared/runtime schema, or configured/observed behavior, verify both sides and the path that activates or connects them.
6. Choose the document map before writing. Preserve an established hierarchy unless the user requests a restructure or it cannot represent the requested scope; for a new or explicitly restructured set, assign one canonical home per subject and identify affected indexes, shared references, and leaf documents.
7. Write the smallest complete documentation. Use concrete names and evidence-matched state language; record material gaps or conflicts instead of inventing details.
8. Update navigation, indexes, and companion documents when the inventory, ownership, or public contract changes.
9. Validate the complete affected set with `references/validation.md`, the bundled checker, and project-provided documentation checks. Fix failures and inspect the final diff before finishing.

## Rules

- Follow project-local instructions over this generic guidance.
- Modify documentation files only unless the user explicitly expands the task. Read source files when needed and permitted to verify documentation.
- Treat existing staged, unstaged, and untracked changes as user-owned. Do not overwrite or normalize them incidentally.
- Preserve established language, tone, terminology, heading hierarchy, and formatting.
- Preserve the established documentation hierarchy unless the task calls for structural change. Do not reorganize unrelated documents while making a local edit.
- Keep page and table descriptions compact. Prefer short paragraphs, bullets, and tables; avoid repeating the same fact in several sections.
- Distinguish optional fields (`field?: Type`) from nullable values (`null | Type`) when documenting typed contracts.
- Distinguish requested, declared, implemented, configured, verified, integrated, and deployed states. Source presence alone does not prove runtime, deployment, or end-to-end compatibility.
- Record an explicit documentation gap when a material fact cannot be verified.
- Keep internal links relative when that matches the project convention.

## References

- Read `references/docs-guide.md` for source precedence and writing principles.
- Read `references/structure-and-state.md` for evidence language and documentation hierarchy decisions when documenting current state or changing a documentation set.
- Read `references/task-map.md` to choose task-specific inputs and companion files.
- Read `references/page-template.md` only for UI page or screen documentation.
- Read `references/table-template.md` only for database table documentation.
- Read `references/validation.md` before completing any documentation change.
