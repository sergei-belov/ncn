# Documentation Validation

Validate the changed documents, not just the skill or Markdown syntax.

## Required Checks

1. **Facts**: Compare names, behavior, routes, commands, fields, types, constraints, defaults, and examples with authoritative sources.
2. **State**: Confirm that requested, declared, implemented, configured, verified, integrated, deployed, and gap language matches its evidence. Check both sides and the activation path of cross-boundary claims.
3. **Structure**: Confirm every document has the right owner and canonical location, folder indexes are complete, and shared facts are not duplicated across leaf documents.
4. **Consistency**: Check terminology, language, heading hierarchy, formatting, and cross-document claims against neighboring docs.
5. **Completeness**: Confirm the requested behavior is covered and affected indexes, navigation, diagrams, or companion docs are updated.
6. **Brevity**: Remove repetition, placeholders, empty sections, and implementation detail that does not help the audience.
7. **References**: Verify relative links, anchors, filenames, and case. Confirm renamed or removed documents have no stale references or unindexed replacements.
8. **Commands**: Run the project's existing docs lint, link, spell, or build commands when available. Do not install a new tool unless asked.

## Bundled Check

Run the dependency-free checker against changed Markdown files:

```sh
python3 <skill-dir>/scripts/validate_docs.py --root <repository-root> <changed-file> [...]
```

It checks that Markdown inputs exist, fenced code blocks close, and relative local links and anchors resolve. It intentionally skips remote URLs and root-relative website routes.

Pass every changed file for a local edit. Pass the complete documentation root after moving or renaming files, changing shared anchors, or revising the documentation hierarchy. Also search the repository for old paths and names because deleted files cannot validate their former inbound links.

## Type-Specific Checks

- **Page**: Verify route, shell, audience, primary behavior, visible structure, important states, permissions, navigation, responsive variants, and referenced APIs.
- **Table**: Verify column names and order, types, nullability, defaults, keys, constraints, indexes, relationships, and delete behavior.
- **Current-state audit**: Verify source scope, registration and wiring, interface boundaries, mode/configuration selection, activation preconditions, executed checks, deployment evidence, negative-claim scope, and documented gaps.
- **Restructure**: Verify the ownership map, root and folder indexes, moved-file history where practical, old-path searches, inbound and outbound links, and the complete documentation tree.

Re-read the final files or inspect the diff after automated checks. Report commands run and any validation that could not be performed.
