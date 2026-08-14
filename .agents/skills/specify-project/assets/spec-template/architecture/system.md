# System Architecture

## Context

<!-- TEMPLATE: Define system boundary, actors, external systems, trust zones, and architecture drivers. -->

## Service Boundaries

| Service | Responsibility | Owns | Exposes | Depends on | Status |
|---|---|---|---|---|---|
| <!-- TEMPLATE: service --> | <!-- TEMPLATE: responsibility --> | <!-- TEMPLATE: capabilities/data --> | <!-- TEMPLATE: APIs/events --> | <!-- TEMPLATE: dependencies --> | <!-- TEMPLATE: status --> |

## Cross-Service Flows

| Flow | Trigger | Ordered participants | State/authority changes | Failure/recovery | Observability |
|---|---|---|---|---|---|
| <!-- TEMPLATE: flow --> | <!-- TEMPLATE: trigger --> | <!-- TEMPLATE: services --> | <!-- TEMPLATE: changes --> | <!-- TEMPLATE: behavior --> | <!-- TEMPLATE: signals --> |

## Data and Consistency Boundaries

<!-- TEMPLATE: Define systems of record, owner-only writes, projections, consistency, transactions, events, and reconciliation. -->

## Shared Infrastructure and Integrations

<!-- TEMPLATE: Define approved shared infrastructure, external dependencies, protocols, and ownership. -->

## Security and Trust Boundaries

<!-- TEMPLATE: Define identity, authorization, tenancy, secrets, untrusted inputs, sensitive flows, and audit points. -->

## Failure Isolation and Recovery

<!-- TEMPLATE: Define timeouts, retry, idempotency, cancellation, backpressure, degraded operation, backup/restore, and disaster recovery. -->

## Observability and Operations

<!-- TEMPLATE: Define logs, metrics, audit, health, alerts, runbooks, configuration, and owners. -->

## Runtime and Deployment Shape

<!-- TEMPLATE: Define environments, deployment units, ingress, scaling, availability, compatibility, and rollout constraints without inventing present implementation. -->

## Architecture Decisions

Use [project decisions](../decisions/README.md) for cross-service choices and service decision files for local choices.
