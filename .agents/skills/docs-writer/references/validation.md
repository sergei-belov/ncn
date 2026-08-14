# Documentation Validation

Validate the changed documents, not just the skill or Markdown syntax.

## Required Checks

1. **Facts**: Compare names, behavior, routes, commands, fields, types, constraints, defaults, and examples with authoritative sources.
2. **Consistency**: Check terminology, language, heading hierarchy, formatting, and cross-document claims against neighboring docs.
3. **Completeness**: Confirm the requested behavior is covered and affected indexes, navigation, diagrams, or companion docs are updated.
4. **Brevity**: Remove repetition, placeholders, empty sections, and implementation detail that does not help the audience.
5. **References**: Verify relative links, anchors, filenames, and case. Confirm renamed or removed documents have no stale references.
6. **Commands**: Run the project's existing docs lint, link, spell, or build commands when available. Do not install a new tool unless asked.

## Bundled Check

Run the dependency-free checker against changed Markdown files:

```sh
python3 <skill-dir>/scripts/validate_docs.py --root <repository-root> <changed-file> [...]
```

It checks that Markdown inputs exist, fenced code blocks close, and relative local links and anchors resolve. It intentionally skips remote URLs and root-relative website routes.

## Type-Specific Checks

- **Page**: Verify route, audience, primary behavior, important states, permissions, navigation, and referenced APIs.
- **Table**: Verify column names and order, types, nullability, defaults, keys, constraints, indexes, relationships, and delete behavior.

Re-read the final files or inspect the diff after automated checks. Report commands run and any validation that could not be performed.
