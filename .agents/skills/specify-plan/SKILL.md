---
name: specify-plan
description: Create or revise a docs-first, implementation-ready feature planning package in a validated `feat-{name}` folder. Use when Codex needs to turn a feature request, product change, enhancement, epic, or rough brief into a coherent feature contract covering requirements, user scenarios, technical design, API and other interfaces, UI/UX, data and state, decisions, delivery slices, validation, rollout, and persistent agent navigation before implementation.
---

# Specify Plan

## Core Contract

Turn one feature request into an authoritative planning package at `<plan-root>/feat-{feature-slug}/`. Default `<plan-root>` to the repository root unless the user or repository conventions name another location. Normalize `{feature-slug}` to lowercase kebab-case.

Operate in specification mode:

- Write only planning and documentation artifacts inside the feature folder.
- Do not implement source code, install dependencies, create migrations, or change runtime configuration.
- Ground the plan in the user's request, applicable instructions, existing specifications, and verified repository behavior.
- Mark consequential statements as **Confirmed**, **Assumed**, or **Open**.
- Preserve existing user-authored content and surface conflicts instead of silently replacing it.
- Keep required documents even when an area is not applicable; state `Not applicable`, the reason, and the consequence for delivery.

If implementation is also requested, complete and validate the feature package first, then hand implementation to the applicable development workflow.

## Load the Resources

Before writing:

1. Read [references/feature-plan-system.md](references/feature-plan-system.md) completely for document ownership, required coverage, traceability, and consistency rules.
2. Initialize a new package from [assets/feature-template](assets/feature-template) with:

```bash
python3 <skill-directory>/scripts/init_feature.py "<ASCII feature name or slug>" --path <plan-root>
```

3. Adapt every generated template to the feature instead of copying placeholders literally. If the target folder already exists, reconcile it manually; the initializer deliberately refuses to overwrite it.

After writing, run:

```bash
python3 <skill-directory>/scripts/validate_feature.py <plan-root>/feat-{feature-slug}
```

Read [scripts/validate_feature.py](scripts/validate_feature.py) only when its validation behavior must change.

## Workflow

### 1. Discover the working context

1. Resolve the repository root, the plan root, and all applicable `AGENTS.md` files.
2. Read the complete request and explicitly supplied artifacts.
3. Inspect existing project specifications, contracts, affected implementation surfaces, tests, and established UI patterns only as needed to ground the plan.
4. Distinguish current behavior from proposed behavior and verified paths from planned paths.
5. Select a concise ASCII feature slug and create or reconcile exactly one `feat-{feature-slug}` folder. Use `scripts/init_feature.py` for a new package.

### 2. Establish the navigation spine

Create and populate these files first:

- `README.md`: entry point, reading routes, status, and document map;
- `feature.md`: authoritative product and behavior contract;
- `AGENTS.md`: persistent instructions and reading order for later agents.

Then create every remaining document from the template skeleton. Make all detail documents reachable from `README.md`.

### 3. Write from observable behavior to implementation slices

Use this order:

1. Define the problem, outcomes, actors, scope, requirements, invariants, permissions, and acceptance criteria in `feature.md`.
2. Specify happy paths, alternatives, edge cases, failures, recovery, and accessibility in `scenarios.md`.
3. Describe current context, proposed components, flows, ownership, security, failure isolation, and operations in `design/technical.md`.
4. Specify information architecture, screens, interactions, states, content, accessibility, and responsive behavior in `design/ui-ux.md`.
5. Define applicable API or other machine-facing contracts in `interfaces/api.md`, including authorization, schemas, validation, errors, idempotency, compatibility, and limits.
6. Define persistent and transient state, ownership, lifecycle, consistency, retention, migration, and audit rules in `data/model.md`.
7. Record consequential choices, alternatives, consequences, and reversal conditions in `decisions.md`.
8. Split work into dependency-ordered, end-to-end slices in `delivery/plan.md`; include implementation surfaces, validation, rollout, rollback, and documentation updates.

### 4. Reconcile the feature contract

Trace each in-scope requirement through the applicable layers:

```text
user outcome
  -> REQ-NNN
  -> SCN-NNN
  -> UX behavior and/or API operation
  -> technical owner
  -> data effect
  -> failure and recovery behavior
  -> acceptance criterion
  -> SLICE-NNN
```

Use links and stable IDs rather than duplicating full contracts. Ensure names, actors, states, permissions, identifiers, payloads, paths, and lifecycle rules have the same meaning everywhere.

### 5. Validate and finish

1. Run `scripts/validate_feature.py` against the feature folder.
2. Fix structural errors, unresolved template markers, broken or escaping links, missing README routes, orphan documents, and missing stable IDs.
3. Search for accidental terminology or technology copied from unrelated examples.
4. Manually review assumptions, open questions, accessibility, security, failure recovery, observability, compatibility, rollout, and acceptance coverage.
5. Re-run validation until it passes.

## Quality Bar

- Keep each section as compact as the contract allows; add rows or scenarios only for distinct behavior, risk, or traceability.
- Make requirements testable and implementation surfaces concrete without inventing unverified code symbols.
- Prefer vertical delivery slices that produce observable value and leave the system coherent.
- Include primary, alternate, empty, boundary, concurrent, stale, partial-failure, permission, and recovery scenarios when applicable.
- Define loading, empty, success, validation, error, disabled, and degraded UI states when a UI applies.
- Define stable error behavior and compatibility rules when an API or machine interface applies.
- Never present an assumption as verified fact or mark a path `present` without inspecting it.
- Never leave `<!-- TEMPLATE: ... -->` markers in a generated feature package.

## Completion Report

Report:

- the feature folder and `README.md` entry point;
- the selected slug and scope boundary;
- major decisions and assumptions;
- blocking and non-blocking open questions;
- validation results;
- the first safe delivery slice or applicable implementation workflow.
