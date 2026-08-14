# Database Tables

## Applicability and Database Status

<!-- TEMPLATE: State persistence applicability, database/schema technology and evidence status. If N/A/external, define owner, access contract, consequence, and traceability. -->

## Table Inventory

| ID | Schema.table | Purpose | Authoritative/derived | Lifecycle | Models |
|---|---|---|---|---|---|
| TABLE-001 | <!-- TEMPLATE: schema.table --> | <!-- TEMPLATE: purpose --> | <!-- TEMPLATE: role --> | <!-- TEMPLATE: create-retain-delete --> | <!-- TEMPLATE: MODEL IDs --> |

## TABLE-001: <!-- TEMPLATE: Table name -->

### Ownership and Purpose

<!-- TEMPLATE: Define owning service, database/schema status, authority, and writer/readers. -->

### Columns

| Column | Database type | Null/default | Key/constraint | Sensitivity | Meaning |
|---|---|---|---|---|---|
| <!-- TEMPLATE: column --> | <!-- TEMPLATE: type --> | <!-- TEMPLATE: semantics --> | <!-- TEMPLATE: PK/FK/unique/check --> | <!-- TEMPLATE: class --> | <!-- TEMPLATE: meaning --> |

### Relationships and Constraints

<!-- TEMPLATE: Define PK/FK, uniqueness, checks, cardinality, tenancy, ownership, delete/update behavior, and invariant enforcement. -->

### Access Patterns and Indexes

| Query/access pattern | Filter/order | Expected volume | Index/partition | Verification |
|---|---|---|---|---|
| <!-- TEMPLATE: use --> | <!-- TEMPLATE: shape --> | <!-- TEMPLATE: scale --> | <!-- TEMPLATE: index --> | <!-- TEMPLATE: method --> |

### Transactions and Concurrency

<!-- TEMPLATE: Define atomic units, isolation, locking, optimistic concurrency, idempotency, outbox, consistency, and reconciliation. -->

### Lifecycle, Retention, and Privacy

<!-- TEMPLATE: Define creation/update/archive, retention, deletion, legal hold, encryption, masking, audit, and orphan handling. -->

### Schema Evolution

<!-- TEMPLATE: Define migration implications, compatibility, backfill, verification, rollback, and cleanup. Mark all unverified migrations planned. -->

### Backup, Restore, and Data Quality

<!-- TEMPLATE: Define backup/restore expectations, recovery objectives, integrity checks, reconciliation, and alerts. -->

## Cross-Table Rules

<!-- TEMPLATE: Define shared IDs, timestamps, tenancy, audit, transaction, naming, and constraint conventions. -->

## Traceability

<!-- TEMPLATE: Map TABLE-NNN to MODEL/feature/REQ/SCN/API/EVT/DEC/acceptance. -->
