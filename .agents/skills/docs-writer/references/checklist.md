# Documentation Checklist

Use this checklist for every documentation task. Mark each item `[x]` complete, `[!]` a documented gap, or `[-]` not applicable with a reason; do not finish with unclassified `[ ]` items. Keep the checklist in working notes unless project rules or the user require publication.

For full-feature, current-state, or cross-boundary work, also complete these working matrices before drafting:

- `initial requirement | target document/section | evidence | status`
- `subject/layer | state | evidence | activation | unknowns`
- `contract concern | frontend | backend | activation | compatibility/gap`

Every material `[!]` matrix row must be visible in the canonical documentation, not only in working notes.

## Initial Task and Scope

- [ ] Restate the requested outcome, audience, deliverables, and definition of done.
- [ ] Record explicit non-goals and confirm documentation-only scope unless expanded by the user.
- [ ] Select the state baseline: working tree, commit, release, or deployed environment.
- [ ] Identify applicable instructions, documentation roots, canonical sources, target files, and validation commands.
- [ ] Map every initial-task requirement to a target document or section; record omissions as gaps.

## Current State and Evidence

- [ ] Build a claim ledger with `subject/layer | state | evidence | activation | unknowns`.
- [ ] Separate requested, declared, implemented, configured, activated, verified, integrated, deployed, and unknown states.
- [ ] Separate frontend behavior, backend declarations, registered backend behavior, data provisioning, known environment selection, and end-to-end behavior.
- [ ] Trace definitions through registration, wiring, call sites, configuration, guards, transport, response handling, and runtime selection.
- [ ] Publish test-source inventory status, executed commands/scenarios, and results as three separate states; do not infer one from another.
- [ ] Scope negative and absolute claims such as `no`, `not`, `only`, `never`, `missing`, `unavailable`, and `unimplemented` to the inspected evidence.

## Product and Behavior

- [ ] Document actors, goals, primary scenarios, outcomes, and ownership.
- [ ] Document permissions, business rules, validation, lifecycle, transitions, side effects, and limits.
- [ ] Document success, loading, empty, partial, error, disabled, offline, conflict, retry, and recovery behavior when applicable.
- [ ] Separate current behavior, interface-specific behavior, compatibility gaps, accepted decisions/delivery phases, and future work.

## Architecture and Design

- [ ] Document system boundaries, service/domain/component ownership, dependency direction, and shared responsibilities.
- [ ] Document important control flow, data flow, state flow, and integration sequence.
- [ ] Document applicable security, authorization, concurrency, idempotency, events, jobs, caching, storage, observability, and failure handling; classify intended, mock-simulated, declared, implemented/wired, executed, and operational states separately.
- [ ] Document configuration modes, defaults, feature flags, environment selection, deployment topology, and inactive infrastructure.
- [ ] Record material design decisions, constraints, alternatives, and known limitations when they belong in the requested documentation.

## UI and UX

- [ ] Verify routes, redirects, route registration, shared shells/layouts, navigation, and page ownership.
- [ ] Document information hierarchy, visible page structure, primary actions, forms, dialogs, sheets, tables, and feedback.
- [ ] Document responsive behavior, accessibility, keyboard/screen-reader behavior, localization, theme, and offline behavior when material.
- [ ] Verify UI permissions, hidden/disabled controls, validation, loading/empty/error states, optimistic behavior, and recovery paths.
- [ ] Link shared design or shell behavior canonically instead of duplicating it in every page.

## Frontend Contract

- [ ] Verify registered routes, reachable components, provider wiring, defaults, and the selected mode in every known environment.
- [ ] Verify types and schemas, including optionality, nullability, defaults, enums, field mapping, and parsing.
- [ ] Verify request methods, paths, route/query parameters, headers, authentication, bodies, responses, errors, and status handling.
- [ ] Verify query/cache keys, mutations, invalidation, optimistic updates, rollback, persistence, and client-side state where relevant.
- [ ] Record frontend test source separately from commands actually run and their results.

## Backend Contract

- [ ] Verify router registration, prefixes, methods, paths, dependencies, authentication, authorization, and scope checks.
- [ ] Verify request, response, error, pagination, filtering, sorting, versioning, and concurrency models exactly.
- [ ] Verify manager/service behavior, repository/storage effects, transaction boundaries, idempotency, events, and side effects.
- [ ] Distinguish declared schemas or handlers from routes reachable through the composed application.
- [ ] Record backend test source separately from commands actually run and their results.

## Cross-Boundary Contract

- [ ] Compare frontend and backend method, path, parameter schema/requiredness/meaning, authentication, headers, content type, request, response, errors, versions, and identifiers.
- [ ] Verify field-name, enum, optionality/nullability, envelope, pagination, and status-code compatibility; different placeholder names alone prove neither matching nor incompatible semantics.
- [ ] Give configured client base URL, resource path, frontend proxy/gateway prefix, backend application prefix, and path-parameter semantics separate classified rows; do not combine missing segments or present their concatenation as unconditional.
- [ ] Trace the complete activation path: defined, selectable, defaulted, positively selected in each known environment, reachable, exercised, and verified.
- [ ] Classify differences as static contract differences, dormant-path gaps, active runtime gaps, or verified incompatibilities; publish every material unknown in a compatibility matrix or canonical equivalent.

## Data and Persistence

- [ ] Verify models, tables, fields, types, nullability, defaults, keys, constraints, indexes, relationships, and delete/update behavior.
- [ ] Distinguish application models, declared schema, checked-in migrations, provisioned database state, and deployed data.
- [ ] For browser and backend persistence, publish or link ownership/scoping, retention, cleanup/eviction, privacy/security, migration/provisioning, transaction/side-effect, and application-invariant facts or gaps.
- [ ] Give jobs, events, notifications, and each other material side-effect category its own classified row, including an explicit gap or justified not-applicable result; for each, separate browser/mock behavior, declared identifiers or schemas, backend implementation/worker/producer/consumer wiring, observed execution, and deployment/operations.

## Documentation Structure and Writing

- [ ] Preserve the established hierarchy or justify structural change from the requested scope.
- [ ] Give every subject one canonical owner and location; keep shared facts at the nearest common parent.
- [ ] Update root maps, folder indexes and scope descriptions, route/service/table inventories, related docs, diagrams, and inbound/outbound links whenever inventory or child-document scope changes.
- [ ] Match local language, terminology, heading hierarchy, link style, and detail level.
- [ ] Remove duplication, placeholders, empty sections, speculation, and details that do not help the audience.

## Validation Gates

- [ ] Validate the final output against every initial-task matrix row, not only against edited files.
- [ ] Validate architecture/design, UI/UX, frontend, backend, cross-boundary, data, runtime, and operational claims that are in scope.
- [ ] Re-audit every claim-ledger and contract-matrix row plus every negative or absolute statement against its exact evidence and layer.
- [ ] Validate document placement, canonical ownership, complete indexes, stale paths, relative links, anchors, filenames, and case.
- [ ] Run the bundled checker and project-provided docs checks; record commands, results, and checks not run.
- [ ] Inspect staged and unstaged diffs, preserve user-owned changes, confirm documentation-only scope, and re-read every final file.
