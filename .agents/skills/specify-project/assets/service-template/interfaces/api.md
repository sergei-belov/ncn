# API and Request/Response Interfaces

## Applicability

<!-- TEMPLATE: State applicable HTTP/RPC/CLI/job/file interfaces, or N/A with evidence, consequence, and traceability. -->

## Ownership and Consumers

| Interface family | Owner | Consumer | Trust boundary | Status |
|---|---|---|---|---|
| <!-- TEMPLATE: family --> | <!-- TEMPLATE: owner --> | <!-- TEMPLATE: consumer --> | <!-- TEMPLATE: boundary --> | <!-- TEMPLATE: present/planned/unknown --> |

## Shared Conventions

<!-- TEMPLATE: Define authn/authz, tenancy, IDs, null/default semantics, time, errors, idempotency, correlation, pagination, compatibility, and limits. -->

## Operation Inventory

| ID | Kind/entry point | Purpose | Consumer | Requirement/feature |
|---|---|---|---|---|
| API-001 | <!-- TEMPLATE: method/route or trigger --> | <!-- TEMPLATE: purpose --> | <!-- TEMPLATE: consumer --> | <!-- TEMPLATE: IDs --> |

## API-001: <!-- TEMPLATE: Operation name -->

### Contract

<!-- TEMPLATE: Define protocol, entry point, preconditions, owner, consumer, and side effects. -->

### Authentication and Authorization

<!-- TEMPLATE: Define identity, scopes/roles/policies, tenancy, denial, and audit. -->

### Request

<!-- TEMPLATE: Define fields, types, required/optional/null/default, validation, limits, and example if useful. -->

### Response

<!-- TEMPLATE: Define success status/shape, ordering, pagination/streaming, metadata, and example if useful. -->

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| <!-- TEMPLATE: condition --> | <!-- TEMPLATE: status/code/schema --> | <!-- TEMPLATE: behavior --> |

### State, Idempotency, and Concurrency

<!-- TEMPLATE: Define transactions, side effects, keys, duplicates, optimistic concurrency, ordering, atomicity, and timeouts. -->

## Compatibility and Versioning

<!-- TEMPLATE: Define additive/breaking change, deprecation, schema evolution, consumer compatibility, and version window. -->

## Limits and Performance

<!-- TEMPLATE: Define rate, size, pagination, timeout, latency, throughput, and backpressure. -->

## Observability

<!-- TEMPLATE: Define correlation, logs, metrics, audit, dashboards, and alerts without exposing sensitive payloads. -->

## Traceability

<!-- TEMPLATE: Map API-NNN to feature/REQ/SCN/UX/MODEL/TABLE/tests/acceptance. -->
