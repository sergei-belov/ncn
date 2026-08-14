# Data and State Model

## Applicability

<!-- TEMPLATE: State whether persistent or transient state changes. If none apply, provide evidence, reason, delivery consequence, and traceability. -->

## Ownership

<!-- TEMPLATE: Name systems of record, write authority, read models, derived state, and bounded-context ownership. -->

## Entity Inventory

| ID | Entity or state | Owner | Purpose | Classification |
|---|---|---|---|---|
| DATA-001 | <!-- TEMPLATE: entity/state --> | <!-- TEMPLATE: owner --> | <!-- TEMPLATE: purpose --> | <!-- TEMPLATE: public/internal/sensitive/restricted --> |

## Entities and Fields

### DATA-001: <!-- TEMPLATE: Entity or state name -->

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| <!-- TEMPLATE: field --> | <!-- TEMPLATE: type --> | <!-- TEMPLATE: semantics --> | <!-- TEMPLATE: validation/uniqueness --> | <!-- TEMPLATE: definition --> |

## Relationships and Constraints

<!-- TEMPLATE: Define identifiers, references, cardinality, uniqueness, ownership boundaries, and invariant enforcement. -->

## State Transitions

| From | Trigger | Guard | To | Side effects |
|---|---|---|---|---|
| <!-- TEMPLATE: state --> | <!-- TEMPLATE: action/event --> | <!-- TEMPLATE: precondition --> | <!-- TEMPLATE: state --> | <!-- TEMPLATE: effects --> |

## Consistency and Transactions

<!-- TEMPLATE: Define transaction boundaries, concurrency, isolation, idempotency, eventual consistency, outbox/events, and reconciliation. -->

## Retention, Deletion, and Privacy

<!-- TEMPLATE: Define sensitivity, encryption expectations, retention, archival, export, deletion, legal hold, anonymization, and audit. -->

## Access Patterns and Indexing

<!-- TEMPLATE: Define reads/writes, filters, sort order, expected volume, indexes, cache behavior, and projection rebuild rules. -->

## Migration and Backfill

<!-- TEMPLATE: Define planned schema/data migration, compatibility, backfill, verification, rollback, and cleanup. Mark uncreated migrations as planned. -->

## Audit and Observability

<!-- TEMPLATE: Define audit records, change history, metrics, data-quality signals, reconciliation alerts, and sensitive-data redaction. -->

## Traceability

<!-- TEMPLATE: Map DATA-NNN to REQ-NNN, INV-NNN, SCN-NNN, API-NNN, DEC-NNN, and SLICE-NNN. -->
