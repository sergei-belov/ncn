---
name: docs-writer
description: Create, restructure, revise, and validate evidence-backed Markdown project documentation in any repository. Use when Codex needs to document a feature or current implementation across requirements, architecture, design, UI/UX, frontend and backend contracts, APIs, data, runtime behavior, READMEs, guides, pages, and database tables while preserving local structure and validating task coverage, facts, state, navigation, and links.
---

# Docs Writer

## Workflow

1. Read the applicable `AGENTS.md` files. Discover documentation roots, guides, templates, indexes, and validation commands; do not assume fixed paths.
2. Inspect the target documentation's working state. In a Git repository, check status and staged and unstaged diffs for affected files so pre-existing edits remain intact.
3. Classify the task with `references/task-map.md` and instantiate the applicable items and required matrices from `references/checklist.md` in working notes. Do not add them to product documentation unless project rules or the user require it.
4. Define the audience, requested deliverables, non-goals, ownership boundary, and state being documented. Unless the user names a release or commit, treat “current” as the current working tree and do not imply that uncommitted code is released or deployed.
5. Build a scoped claim ledger for material capabilities: subject or layer, state, evidence, activation, and unknowns. Separate decisions, frontend behavior, declared backend contracts, registered backend behavior, data provisioning, selected environments, test source, test execution/results, and deployment evidence.
6. Identify authoritative evidence using `references/docs-guide.md`. For cross-boundary claims such as client/server compatibility, declared/runtime schema, or configured/observed behavior, verify both sides and the complete path that activates or connects them.
7. For a documentation set, restructure, or current-state audit, read `references/structure-and-state.md`; read page and table templates only for those document types. Choose the document map before writing and preserve an established hierarchy unless the requested scope cannot fit it.
8. Write the smallest complete documentation. For full-feature work, publish or link the compact current/target, contract-compatibility, and persistence-boundary matrices required by `references/task-map.md`. Use evidence-matched state language and record material gaps instead of inventing details.
9. Update navigation, indexes, and companion documents when the inventory, ownership, or public contract changes.
10. Classify every checklist and matrix row as complete, not applicable with a reason, or a documented gap. Validate the affected set with `references/validation.md`, the bundled checker, and project-provided checks; fix failures and inspect the final diff before finishing.

## Rules

- Follow project-local instructions over this generic guidance.
- Modify documentation files only unless the user explicitly expands the task. Read source files when needed and permitted to verify documentation.
- Treat existing staged, unstaged, and untracked changes as user-owned. Do not overwrite or normalize them incidentally.
- Preserve established language, tone, terminology, heading hierarchy, and formatting.
- Preserve the established documentation hierarchy unless the task calls for structural change. Do not reorganize unrelated documents while making a local edit.
- Keep page and table descriptions compact. Prefer short paragraphs, bullets, and tables; avoid repeating the same fact in several sections.
- Distinguish optional fields (`field?: Type`) from nullable values (`null | Type`) when documenting typed contracts.
- Distinguish requested, declared, implemented, configured, verified, integrated, and deployed states. Source presence alone does not prove runtime, deployment, or end-to-end compatibility.
- Scope every state claim to its layer. Do not collapse intended behavior, frontend support, declared contracts, registered runtime behavior, selected configuration, verified tests, or deployment into one feature-wide claim.
- Distinguish test source existence, test execution, and test result. Missing execution evidence proves only that a check was not run or recorded.
- Record an explicit documentation gap when a material fact cannot be verified.
- Keep internal links relative when that matches the project convention.

## References

- Read `references/checklist.md` for every task and use all applicable implementation and validation gates.
- Read `references/docs-guide.md` for source precedence and writing principles.
- Read `references/structure-and-state.md` for evidence language and documentation hierarchy decisions when documenting current state or changing a documentation set.
- Read `references/task-map.md` to choose task-specific inputs and companion files.
- Read `references/page-template.md` only for UI page or screen documentation.
- Read `references/table-template.md` only for database table documentation.
- Read `references/validation.md` before completing any documentation change.
