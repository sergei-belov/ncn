---
name: specify-plan
description: Create or revise a concise, docs-linked implementation plan in a validated `feat-{name}` folder. Use when Codex needs to turn a feature request, product change, enhancement, epic, or rough brief into concrete target behavior, repository-native architecture patterns with focused code examples, affected documentation contracts, and a dependency-ordered Markdown implementation checklist before coding.
---

# Specify Plan

## Contract

Create one planning package at `<plan-root>/feat-{feature-slug}/`. Default `<plan-root>` to the repository root and normalize the slug to lowercase ASCII kebab-case.

Write planning artifacts only. Do not implement source code, install dependencies, create migrations, or change runtime configuration. If implementation is also requested, finish and validate the package before handing work to the applicable development workflow.

Keep the package compact and shaped like the repository documentation:

```text
feat-{feature-slug}/
├── README.md          # feature contract and navigation
├── architecture.md    # repository-specific design and code patterns
└── implementation.md  # dependency-ordered checkbox plan
```

Create additional Markdown only when a substantial affected contract does not fit clearly in those files. Mirror the canonical documentation path without its `docs/` prefix; for example, extend `docs/backend/services/authz/api.md` at `backend/services/authz/api.md`. Do not create empty files or directories for symmetry.

## Required Resources

Before writing:

1. Read [references/plan-format.md](references/plan-format.md) completely.
2. For a new package, run:

```bash
python3 <skill-directory>/scripts/init_feature.py "<ASCII feature name or slug>" --path <plan-root>
```

3. If the package exists, reconcile it without overwriting user-authored content.

When revising a legacy multi-document package, consolidate unique behavior into `README.md`, implementation design into `architecture.md` or justified docs-shaped detail, and incomplete work into `implementation.md`. Preserve completed work state and remove obsolete files only after their unique content and inbound links have a canonical replacement.

After writing, run:

```bash
python3 <skill-directory>/scripts/validate_feature.py <plan-root>/feat-{feature-slug}
```

Read the validator source only when its validation behavior must change.

## Workflow

### 1. Ground the plan

1. Read applicable `AGENTS.md` files and inspect the working-tree status and relevant diffs.
2. Discover the documentation root and read its root map, architecture page, affected area indexes, and nearest comparable leaf documents.
3. Inspect only the implementation, tests, schemas, and configuration needed to verify current behavior and repository-native patterns.
4. Treat the user's request as target behavior, not proof of current behavior. Record unresolved conflicts or missing evidence as concise open questions.
5. Choose the feature slug and initialize or reconcile exactly one package.

### 2. Choose the document map

Use the three baseline files for most features. Add a docs-shaped detail file only when at least one condition holds:

- a public API or data contract needs several concrete schemas or examples;
- a frontend page or shared interaction needs behavior that would overwhelm the overview;
- a service or cross-service flow has several independently reviewable cases;
- the canonical `docs/**` hierarchy already separates that concern and the plan proposes a material change to it.

List every plan document in `README.md`. Link existing canonical documentation directly with repository-relative Markdown links. Cite source paths for verified implementation facts. Do not copy an existing contract into the plan; describe only the relevant current constraint and intended delta.

### 3. Write the feature contract

Use `README.md` to state:

- the user or system goal in one short paragraph;
- verified current behavior with evidence links;
- concrete target behavior and scope boundaries;
- a small set of primary, permission, failure, and recovery scenarios;
- testable requirements and end-to-end acceptance criteria;
- the plan map, canonical docs that will change, decisions, and blocking questions.

Use direct heading or file links instead of synthetic cross-document identifiers such as `REQ-001`, `UX-002`, or `SLICE-003`. Do not add status vocabulary, traceability matrices, or `Not applicable` sections merely to satisfy a template.

### 4. Specify architecture concretely

Use `architecture.md` to explain the current constraints, proposed component boundaries, dependency direction, control/data flow, contracts, persistence, security, failure handling, observability, and rollout that materially affect implementation.

For every non-trivial new or changed boundary, include a focused repository-native example showing the intended shape. Prefer types, function signatures, DTOs, routes, component composition, queries, or configuration fragments over broad pseudocode. Each example must:

- name the destination path or module;
- reuse neighboring repository conventions;
- show the architectural pattern and important types or calls;
- omit routine boilerplate and avoid pretending the code already exists.

Keep detailed UI, API, or table contracts in an optional docs-shaped file only when they need independent review. Link that file from the architecture and overview.

### 5. Write the implementation checklist

Use `implementation.md` as an executable checklist, not a prose delivery document. Write dependency-ordered `- [ ]` tasks grouped into small coherent phases. Preserve existing `[x]` state when revising a plan.

Each task must name:

- the concrete outcome;
- expected files, modules, or documentation paths;
- the key architecture or contract constraint;
- the validation that proves completion.

Place blocking discovery or decisions before dependent code tasks. Prefer end-to-end increments over isolated “backend”, “frontend”, or “test everything” phases. Finish with integration, failure-path, security/accessibility when applicable, and canonical `docs/**` update tasks.

### 6. Validate and compact

1. Run the feature validator and fix errors.
2. Treat size and legacy-ID warnings as issues to fix unless the user explicitly needs the extra material.
3. Check every user requirement against the feature contract and at least one checklist item.
4. Verify links, paths, symbols, commands, types, examples, and current-state claims against evidence.
5. Remove duplicated facts, empty sections, speculative symbols, generic advice, and checklist items without a completion test.
6. Inspect the final diff and re-read every changed file.

## Quality Bar

- Prefer direct links and exact paths over cross-reference codes.
- Keep one canonical explanation for each fact.
- Match the detail and tone of neighboring `docs/**`; add precision through implementation patterns and examples, not repeated prose.
- Target at most 150 lines for `README.md`, 250 for `architecture.md`, 150 for `implementation.md`, and 800 total unless the feature genuinely requires split detail.
- Distinguish requested, verified current, planned, and open states in plain language.
- Never claim a path, symbol, test result, integration, migration, or deployment exists without the matching evidence.
- Never leave `<!-- TEMPLATE: ... -->` markers in a completed package.

## Completion Report

Report the feature folder and `README.md`, scope boundary, principal architecture choice, blocking questions, checklist size, validation command/result, and the first unchecked implementation task.
