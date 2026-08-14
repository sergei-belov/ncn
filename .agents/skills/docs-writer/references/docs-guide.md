# Documentation Guide

## Discover the Project Convention

- Read applicable repository instructions before editing.
- Locate documentation with `rg --files` and inspect the nearest relevant files.
- Reuse project-provided templates and commands when present.
- Do not assume documentation lives in `docs/`, uses English, or has a central specification.

## Select Sources by Claim

- Use user requirements and accepted decisions for requested or intended behavior.
- Use accepted specifications, schemas, and generated definitions for declared contracts.
- Use the current implementation, configuration, registration, and wiring for implemented behavior when reading them is allowed.
- Use executed checks or runtime evidence for claims that something passes, runs, integrates, or is deployed.
- Use existing canonical documentation when it is the project's designated source of truth and verify it when the task is a current-state audit.
- Use neighboring documents for language, format, and terminology, not as sole proof of a technical fact.

Report unresolved conflicts or missing material facts instead of guessing. A user request for new behavior is not evidence that the behavior already exists, and a specification does not prove that its implementation is current.

For a cross-boundary claim, trace the selected path as well as both endpoint definitions: mode selection, configuration defaults, call sites, guards, transport topology, registration, and response handling. A static difference is evidence of a contract difference; it becomes an active integration or runtime failure only when the connecting path and its preconditions are established.

## Writing Principles

- Write for the document's audience and purpose.
- Lead with behavior and outcomes; include implementation detail only when useful.
- Use exact routes, commands, identifiers, fields, constraints, and relationships when verified.
- Define unfamiliar terms once and use them consistently.
- Prefer one canonical explanation and link to it instead of duplicating content.
- Keep paragraphs short and remove sections that add no information.
- Keep current behavior, interface-specific behavior, known gaps, and future work visibly distinct.
- Describe verification scope precisely: source inspection, a specific command, an end-to-end scenario, or deployed runtime evidence.

## Contracts and Examples

- Prefer typed models for stable API or data contracts; use examples to clarify, not replace, the contract.
- Use the project's type notation. If none exists, use consistent forms such as `str`, `int`, `bool`, `uuid`, `datetime`, `null | Type`, `Type[]`, and `enum(a, b)`.
- Mark a field optional only when it may be omitted; mark it nullable only when `null` is a valid value.
- Never turn an illustrative value into a claimed default or allowed enum member.
