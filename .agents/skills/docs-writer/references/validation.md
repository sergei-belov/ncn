# Documentation Validation

Validate the changed documents, not just the skill or Markdown syntax.

## Required Checks

1. **Initial task**: Classify every initial-task matrix row and map each requested deliverable, constraint, validation request, and non-goal to the final documents; record any unmet item.
2. **Facts and state**: Compare names, behavior, fields, types, defaults, examples, and claim-ledger states with authoritative evidence at the correct layer.
3. **Implementation coverage**: Complete every applicable architecture/design, UI/UX, frontend, backend, cross-boundary, data, runtime, and operational checklist section.
4. **Frontend contract**: Verify routes, component/provider wiring, schemas, request construction, response parsing, errors, state/cache behavior, defaults, and positive mode selection in each known environment.
5. **Backend contract**: Verify composed router registration, authentication/authorization, exact request/response/error models, domain behavior, persistence effects, and transaction/version rules.
6. **Cross-boundary contract**: Complete separate contract-matrix rows for client base URL, resource path, frontend proxy/gateway prefix, backend application prefix, path-parameter type/requiredness/semantics, method, auth, headers, content type, bodies, envelopes, fields, enums, optionality/nullability, errors, status codes, and activation. Do not infer semantic mismatch from names alone.
7. **UI/UX and design**: Verify shells, navigation, visible structure, actions, states, responsive/accessibility behavior, permissions, validation, feedback, and shared design ownership.
8. **Data and runtime**: Verify declared models, browser/backend persistence scope and lifecycle, migrations/provisioning, configuration defaults, known environment selection, runtime/deployment evidence, inactive infrastructure, and layer-specific job/event/notification states.
9. **Structure**: Confirm canonical ownership, correct placement, complete indexes/inventories, updated parent scope descriptions and companion docs, and no duplicated shared facts.
10. **Writing and references**: Check terminology, language, headings, brevity, relative links, anchors, filenames, case, stale paths, and speculative or absolute wording.
11. **Commands and diff**: Run available docs checks, inspect staged/unstaged diffs, preserve user work, and confirm documentation-only scope.

## Bundled Check

Run the dependency-free checker against changed Markdown files:

```sh
python3 <skill-dir>/scripts/validate_docs.py --root <repository-root> <changed-file> [...]
```

It checks that Markdown inputs exist, fenced code blocks close, and relative local links and anchors resolve. It intentionally skips remote URLs and root-relative website routes.

Pass every changed file for a local edit. Pass the complete documentation root after moving or renaming files, changing shared anchors, or revising the documentation hierarchy. Also search the repository for old paths and names because deleted files cannot validate their former inbound links.

## Semantic Claim Audit

- Scope every claim to its exact layer; do not turn a frontend limitation or declared backend capability into a feature-wide statement.
- For optional paths, record whether each is defined, selectable, defaulted, selected in a known environment, reachable, exercised, and verified.
- Scope composed endpoint URLs to the proven client base, resource path, proxy/backend prefixes, and parameter semantics; document unknown joins as gaps.
- Publish test-source inventory, test execution, and test result separately. Never infer source absence from a missing run or result.
- Give jobs, events, notifications, and other material side effects separate classified rows, even when the result is an evidence gap or justified not-applicable; compare intended behavior, browser/mock simulation, declared contracts, backend worker/producer/consumer wiring, observed execution, and deployed operations before making a negative claim.
- Re-check every `no`, `not`, `only`, `never`, `missing`, `unavailable`, and `unimplemented` statement against the claim ledger.

## Type-Specific Checks

- **Full feature**: Verify published current/declaration/target, contract-compatibility, and persistence-boundary matrices or canonical equivalents; every required row must contain evidence, an explicit gap, or a justified not-applicable result.
- **Page**: Verify route, shell, audience, primary behavior, visible structure, important states, permissions, navigation, responsive variants, and referenced APIs.
- **Table**: Verify column names and order, types, nullability, defaults, keys, constraints, indexes, relationships, and delete behavior.
- **Current-state audit**: Verify source scope, registration and wiring, interface boundaries, mode/configuration selection, known environment activation, test source/execution/result, deployment evidence, negative-claim scope, and documented gaps.
- **Restructure**: Verify the ownership map, root and folder indexes, moved-file history where practical, old-path searches, inbound and outbound links, and the complete documentation tree.

Re-read the final files or inspect the diff after automated checks. Report commands run and any validation that could not be performed.
