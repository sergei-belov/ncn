# API and Interface Contract

## Applicability

<!-- TEMPLATE: State which machine-facing interfaces change. If none apply, provide evidence, reason, delivery consequence, and traceability. -->

## Ownership and Consumers

| Interface family | Owner | Consumer | Trust boundary | Status |
|---|---|---|---|---|
| <!-- TEMPLATE: HTTP/event/job/webhook/CLI/file --> | <!-- TEMPLATE: owner --> | <!-- TEMPLATE: consumer --> | <!-- TEMPLATE: boundary --> | <!-- TEMPLATE: present/planned --> |

## Interface Inventory

| ID | Kind | Entry point | Purpose | Requirement |
|---|---|---|---|---|
| API-001 | <!-- TEMPLATE: HTTP/event/job/etc. --> | <!-- TEMPLATE: route/topic/trigger --> | <!-- TEMPLATE: purpose --> | <!-- TEMPLATE: REQ-NNN --> |

## Authentication and Authorization

<!-- TEMPLATE: Define identity, credentials, role/scope checks, tenancy, policy owner, audit, and denial behavior. -->

## Operations

### API-001: <!-- TEMPLATE: Operation name -->

#### Contract

<!-- TEMPLATE: Define method/protocol, entry point, owner, consumer, preconditions, and side effects. -->

#### Request

<!-- TEMPLATE: Define fields, types, required/optional/null/default semantics, validation, size limits, and example when useful. -->

#### Response

<!-- TEMPLATE: Define success shape, status, ordering, pagination/streaming, headers/metadata, and example when useful. -->

#### Errors and Recovery

| Condition | Stable error | Retry or recovery |
|---|---|---|
| <!-- TEMPLATE: condition --> | <!-- TEMPLATE: status/code/body --> | <!-- TEMPLATE: caller behavior --> |

#### Idempotency and Concurrency

<!-- TEMPLATE: Define idempotency keys, duplicate handling, optimistic concurrency, ordering, atomicity, and timeouts. -->

## Compatibility and Versioning

<!-- TEMPLATE: Define additive/breaking changes, schema evolution, deprecation, consumer rollout, and compatibility window. -->

## Limits and Performance

<!-- TEMPLATE: Define rate, size, pagination, timeout, latency, throughput, and backpressure requirements. -->

## Observability

<!-- TEMPLATE: Define correlation IDs, logs, metrics, audit events, dashboards, and alerts without exposing sensitive payloads. -->

## Traceability

<!-- TEMPLATE: Map API-NNN to REQ-NNN, SCN-NNN, DATA-NNN, errors handled by UX-NNN, tests, and SLICE-NNN. -->
