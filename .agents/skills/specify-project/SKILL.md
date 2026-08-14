---
name: specify-project
description: Create, validate, and maintain a living, service-oriented project specification in `docs/**`. Use when Codex needs to establish or revise the project contract, add a service such as `management-service` or `agent-service`, specify a new feature inside its owning service, propagate cross-service changes, or audit documentation consistency. Each service receives a complete specification folder covering behavior, scenarios, technical design, UI/UX, APIs, events, models, database tables, and decisions. This skill writes specifications only, not development plans or implementation, and reads `frontend/**`, `backend/**`, or other implementation trees only when the user explicitly requests verification of docs against implementation.
---

# Specify Project

## Core Contract

Maintain an authoritative project specification organized around service ownership:

```text
docs/
├── spec.md
├── architecture/system.md
├── services/
│   ├── README.md
│   └── <service-slug>/
│       ├── README.md
│       ├── spec.md
│       ├── scenarios.md
│       ├── features/
│       ├── design/
│       ├── interfaces/
│       ├── data/
│       └── decisions.md
└── project-map.md
```

Treat service folders as living specifications, not implementation plans. Incorporate each feature into the contracts of its owning and affected services.

Operate in specification mode:

- Write only documentation under the selected docs root.
- Do not implement code, create migrations, install dependencies, or modify runtime configuration.
- Do not create delivery plans, work breakdowns, sprint plans, or frontend/backend phase plans unless the user separately requests them outside this skill.
- Preserve service ownership and keep one authoritative location for each rule.
- Mark statements as **Confirmed**, **Assumed**, or **Open** and paths as **Present**, **Planned**, **External**, or **Unknown**.
- Keep every service's UI/UX and persistence applicability explicit; use a reasoned `Not applicable` contract rather than omitting files.

## Evidence Boundary

Use, in order:

1. the user's current request and supplied artifacts;
2. applicable `AGENTS.md` files;
3. existing specifications, contracts, service docs, and decisions;
4. other documentation explicitly named by the user;
5. labeled assumptions.

Do not inspect source code, tests, runtime configuration, `frontend/**`, or `backend/**` to enrich the spec. Inspect the narrowest relevant implementation surfaces only when the user explicitly asks to verify documentation against implementation. Remain read-only outside documentation and record the evidence used. Never infer implemented tables, models, endpoints, commands, or paths from plans.

## Load the Resources

Before writing, read:

1. [references/project-system.md](references/project-system.md) for project-level authority and structure.
2. [references/service-system.md](references/service-system.md) for the complete service contract and feature-update rules.
3. [references/navigation-context.md](references/navigation-context.md) when paths, ownership, services, entry points, or document inventory change.

Initialize a new docs baseline with:

```bash
python3 <skill-directory>/scripts/init_project.py <project-root>/docs
```

Initialize a new service with:

```bash
python3 <skill-directory>/scripts/init_service.py "<service name or slug>" --docs-root <project-root>/docs
```

Initialize a feature inside its owning service with:

```bash
python3 <skill-directory>/scripts/init_feature.py "<feature name or slug>" --service <service-slug> --docs-root <project-root>/docs
```

Initializers refuse to overwrite existing content. Reconcile an existing project or service manually.

## Select the Work Mode

- **Bootstrap project**: establish project-wide scope, architecture, ownership, and navigation.
- **Add service**: create a complete `docs/services/<service-slug>/` contract and register it.
- **Add feature**: add the feature contract under its owning service and revise every affected service contract.
- **Revise or support**: incorporate decisions, changed behavior, renamed ownership, status, or explicit implementation-verification evidence.
- **Validate**: audit structure, links, registries, completeness, applicability, traceability, and contradictions.

## Workflow

### 1. Discover documentation context

1. Resolve the project root, docs root, applicable instructions, and existing service catalog.
2. Read the request and only evidence allowed by the Evidence Boundary.
3. Identify project-wide rules, service owners, affected services, and the feature owner when relevant.
4. Preserve existing authored content and surface contradictions instead of silently replacing them.

### 2. Maintain the project contract

Keep project-wide truth in:

- `docs/spec.md`: purpose, actors, outcomes, scope, capabilities, invariants, service inventory, and project acceptance;
- `docs/architecture/system.md`: system context, service boundaries, ownership, cross-service flows, infrastructure, security, failure isolation, and operations;
- `docs/services/README.md`: service registry and authority links;
- `docs/features/README.md`: feature registry, one owning service per feature, and affected services;
- `docs/interfaces/README.md`: cross-service API/event conventions and interaction map;
- `docs/data/README.md`: system-of-record and data-ownership map;
- `docs/decisions/README.md`: project-level decisions only;
- `docs/project-map.md`: durable navigation and present/planned status.

Keep product audience and canonical language in `docs/product/`. Populate `docs/README.md` and `docs/AGENTS.md` as the entry point and handoff.

### 3. Maintain each service contract

Every service folder must contain:

```text
docs/services/<service-slug>/
├── README.md
├── spec.md
├── scenarios.md
├── features/
│   └── README.md
├── design/
│   ├── technical.md
│   └── ui-ux.md
├── interfaces/
│   ├── api.md
│   └── events.md
├── data/
│   ├── models.md
│   └── tables.md
└── decisions.md
```

Use [assets/service-template](assets/service-template) as the required baseline. Add detail files only when a single baseline document becomes hard to navigate; link every addition from the service README or its area owner.

### 4. Add or revise a feature

1. Select exactly one owning service; stop and mark the ownership decision **Open** if no safe owner exists.
2. Initialize or revise `services/<owner>/features/<feature-slug>.md` with feature scope, actors, requirements, invariants, scenarios, permissions, failures, acceptance, and traceability.
3. Update the owner's `spec.md` and `scenarios.md`.
4. Update technical design, UI/UX, API, events, models, tables, and decisions wherever the feature changes their contract.
5. For each consuming or collaborating service, update its own interface, data, scenario, and design contracts rather than copying the feature.
6. Register the feature in the owner service's `features/README.md` and project `docs/features/README.md`.
7. Update project architecture, interface map, data ownership, project spec, decisions, and project map only where cross-service truth changes.

Trace applicable behavior as:

```text
project capability
  -> owning service
  -> feature requirement
  -> scenario
  -> UI/UX and/or API/event
  -> model and table effect
  -> failure/recovery/observability
  -> acceptance criterion
```

### 5. Validate and reconcile

Run:

```bash
python3 <skill-directory>/scripts/validate_spec.py <project-root>/docs
```

Fix missing service files/headings, unresolved template markers, broken links, orphan docs, invalid service names, unregistered services/features, and missing stable IDs. Then manually review contradictions, ownership, applicability, permissions, security, interface compatibility, model/table consistency, transaction rules, UI states, failure recovery, observability, and acceptance coverage.

## Quality Bar

- Make requirements observable and acceptance criteria testable.
- Make service responsibility and data ownership exclusive and explicit.
- Define API/event schemas, validation, errors, authorization, idempotency, ordering, compatibility, and limits when applicable.
- Define models, fields, relationships, lifecycle, tables, keys, constraints, indexes, transactions, consistency, migration implications, retention, deletion, audit, backup, and restore when persistence applies.
- Define information architecture, flows, screen/interaction inventory, loading, empty, success, validation, error, disabled, permission-denied, degraded, accessible, and responsive behavior when UI applies.
- Cover happy, alternate, boundary, permission, duplicate, concurrent, stale, partial-failure, cancellation, and recovery scenarios when applicable.
- Never leave `<!-- TEMPLATE: ... -->` markers in active specification documents.

## Completion Report

Report the docs entry point, services and features created or revised, ownership and cross-service effects, decisions and assumptions, open questions, implementation evidence if explicitly requested, validation results, and the next specification gap. Do not turn the report into an implementation plan.
