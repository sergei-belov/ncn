# Documentation Guide

## Discover the Project Convention

- Read applicable repository instructions before editing.
- Locate documentation with `rg --files` and inspect the nearest relevant files.
- Reuse project-provided templates and commands when present.
- Do not assume documentation lives in `docs/`, uses English, or has a central specification.

## Source Precedence

Use the first applicable authoritative source:

1. User requirements and accepted decisions
2. Project specifications, contracts, schemas, or generated API definitions
3. Current implementation and configuration, when reading them is allowed
4. Existing canonical documentation
5. Neighboring documents for style only

Report unresolved conflicts or missing material facts instead of guessing.

## Writing Principles

- Write for the document's audience and purpose.
- Lead with behavior and outcomes; include implementation detail only when useful.
- Use exact routes, commands, identifiers, fields, constraints, and relationships when verified.
- Define unfamiliar terms once and use them consistently.
- Prefer one canonical explanation and link to it instead of duplicating content.
- Keep paragraphs short and remove sections that add no information.

## Contracts and Examples

- Prefer typed models for stable API or data contracts; use examples to clarify, not replace, the contract.
- Use the project's type notation. If none exists, use consistent forms such as `str`, `int`, `bool`, `uuid`, `datetime`, `null | Type`, `Type[]`, and `enum(a, b)`.
- Mark a field optional only when it may be omitted; mark it nullable only when `null` is a valid value.
- Never turn an illustrative value into a claimed default or allowed enum member.
