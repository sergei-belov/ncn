# Architecture

## Existing constraints

<!-- TEMPLATE: Link the canonical architecture and affected docs. Summarize verified ownership, dependency direction, reusable patterns, and current limitations. -->

## Proposed design

<!-- TEMPLATE: Describe the smallest repository-native change that satisfies the target behavior. Name boundaries, owners, dependencies, and important tradeoffs. -->

```text
<!-- TEMPLATE: Replace with a compact component or request/data-flow sketch. -->
```

## Boundaries and flow

| Boundary or step | Responsibility | Inputs and outputs | Expected location |
| --- | --- | --- | --- |
| <!-- TEMPLATE: component or flow step --> | <!-- TEMPLATE: owned behavior --> | <!-- TEMPLATE: typed contract or state transition --> | <!-- TEMPLATE: verified path or planned child of a verified module --> |

<!-- TEMPLATE: Describe ordering, transactions, concurrency, retries, partial failure, and user-visible completion only where material. -->

## Implementation patterns

### <!-- TEMPLATE: Pattern name and destination path -->

<!-- TEMPLATE: Link the neighboring repository example and explain the intended delta. Replace this block with a focused example in the repository language. -->

```text
<!-- TEMPLATE: Typed signature, DTO, route, component composition, query, or configuration fragment. -->
```

## Contracts and data

<!-- TEMPLATE: Summarize changed interfaces, schemas, persistence, state ownership, compatibility, and migrations. Link optional docs-shaped detail rather than duplicating it. -->

## Security, failure handling, and observability

<!-- TEMPLATE: Specify applicable trust/permission boundaries, validation, fail-safe behavior, recovery, logs, metrics, audit, and sensitive-data handling. -->

## Rollout and rollback

<!-- TEMPLATE: Define compatibility order, flags or staged enablement, migrations/backfill, monitoring/stop conditions, rollback, and cleanup when applicable. -->

## Validation approach

- <!-- TEMPLATE: Unit or static validation tied to a concrete boundary. -->
- <!-- TEMPLATE: Integration or end-to-end scenario, including an important failure case. -->
- <!-- TEMPLATE: Security, accessibility, migration, performance, or operational check when applicable. -->
