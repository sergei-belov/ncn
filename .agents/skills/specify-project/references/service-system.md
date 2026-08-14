# Service Specification System

## Contents

- [Required structure](#required-structure)
- [Document authority](#document-authority)
- [Service behavior](#service-behavior)
- [Technical and UI/UX design](#technical-and-uiux-design)
- [Interfaces](#interfaces)
- [Models and tables](#models-and-tables)
- [Features and scenarios](#features-and-scenarios)
- [Decisions and maintenance](#decisions-and-maintenance)

## Required structure

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

Use lowercase ASCII kebab-case for service and feature filenames. Keep the baseline even when UI, events, or tables are not applicable; state evidence, reason, consequence, and traceability.

## Document authority

| Concern | Authority |
|---|---|
| Navigation, purpose, status, reading routes | `README.md` |
| Responsibility, actors, behavior, requirements, invariants, acceptance | `spec.md` |
| Happy paths, alternatives, edge cases, failures, recovery | `scenarios.md` |
| Feature inventory and behavior contracts | `features/` |
| Components, flows, dependencies, security, operations | `design/technical.md` |
| Service-owned UI surfaces and user interaction | `design/ui-ux.md` |
| HTTP/RPC/CLI/job/file interfaces | `interfaces/api.md` |
| Published/consumed events and stream contracts | `interfaces/events.md` |
| Domain, DTO, command, event, and read models | `data/models.md` |
| Schemas, tables, columns, constraints, indexes, transactions | `data/tables.md` |
| Service-local consequential decisions | `decisions.md` |

## Service behavior

Make `spec.md` define service purpose and boundary, owned capabilities, actors/systems and permissions, upstream/downstream dependencies, requirements, invariants, lifecycle/state machines, security/privacy, failure/recovery, observability/operations, quality attributes, assumptions, open questions, and service acceptance.

Separate observable obligations from design choices. Explicitly state forbidden ownership and direct-access boundaries.

## Technical and UI/UX design

Make `design/technical.md` define context, confirmed versus proposed state, components, responsibility map, synchronous and asynchronous flows, state ownership, dependencies, trust boundaries, failure isolation, retries/idempotency/cancellation/reconciliation, observability, scale, deployment/runtime shape, compatibility, and alternatives.

Make `design/ui-ux.md` define applicability, experience goals, information architecture, flows, screens/interactions, entry points, permissions, loading/empty/populated/validation/error/disabled/denied/degraded/success states, content and feedback, accessibility, responsive/platform behavior, localization, and success signals.

A backend-only service still keeps `ui-ux.md` with `Not applicable`, evidence, non-UI consumers, user-visible consequences delivered elsewhere, and traceability.

## Interfaces

Use stable `API-NNN` and `EVT-NNN` identifiers where cross-references help.

For API and other request/response operations define owner, consumer, protocol, entry point, authentication, authorization, tenancy, request and response fields, types, optional/null/default semantics, validation, stable errors, side effects, transaction boundary, idempotency, concurrency, ordering, pagination/streaming, timeouts, limits, compatibility, audit, and examples when useful.

For events define producer, consumers, topic/stream, trigger, schema, key/partitioning, ordering, delivery semantics, correlation/causation, deduplication, compatibility, retention, replay, privacy, failure/dead-letter/recovery, and observability.

Consumers link to the owner contract and specify only their handling behavior.

## Models and tables

Use stable `MODEL-NNN` and `TABLE-NNN` identifiers.

Define models with purpose, owner, kind (domain/DTO/command/event/read model), fields, types, required/null/default semantics, validation, invariants, relationships, serialization, versioning, sensitivity, and interface/table mappings.

Define tables with database/schema status, table purpose, columns/types/null/defaults, primary/foreign/unique/check constraints, relationships, indexes and query patterns, expected volume, lifecycle, retention/deletion, encryption, audit, transaction/isolation/locking rules, concurrency, outbox/reconciliation, migration/backfill/rollback implications, backup/restore, and data-quality checks.

Keep conceptual ownership in models and physical persistence in tables. Do not treat an ORM model as the table contract. Never claim a model/table/migration exists without explicitly authorized implementation evidence.

## Features and scenarios

Keep `features/README.md` as the service feature registry. Store each feature at `features/<feature-slug>.md` with:

- status and ownership;
- problem, actors, scope, non-goals, and dependencies;
- `REQ-NNN` requirements and `INV-NNN` invariants scoped to the service;
- linked `SCN-NNN`, `UX-NNN`, `API-NNN`, `EVT-NNN`, `MODEL-NNN`, and `TABLE-NNN` contracts where applicable;
- permissions, failure/recovery, observability, acceptance criteria, assumptions, and open questions.

Keep full scenario behavior in `scenarios.md`: preconditions, trigger, ordered happy path, alternatives, boundary/duplicate/concurrent/stale/partial cases, permission behavior, failures, retries/cancellation/recovery, accessibility when applicable, observable result, and traceability.

One service owns the feature. Affected services update their consumer contracts and link to the owner rather than copying the feature definition.

## Decisions and maintenance

Give service-local choices `DEC-NNN` and include status, context, drivers, decision, alternatives, consequences, reversal conditions, and affected contracts. Escalate cross-service ownership or infrastructure choices to project decisions.

When any feature changes, inspect every service document for impact. Update the service README and registries when files, status, ownership, or reading routes change. Keep active truth current; decisions preserve rationale, not stale behavior.
