# Feature: <!-- TEMPLATE: Feature name -->

## Executive Contract

<!-- TEMPLATE: State what changes, for whom, the observable value, and the defining boundary in concrete terms. -->

## Evidence and Decision Status

| Topic | Status | Statement | Evidence or rationale |
|---|---|---|---|
| <!-- TEMPLATE: topic --> | <!-- TEMPLATE: Confirmed, Assumed, or Open --> | <!-- TEMPLATE: statement --> | <!-- TEMPLATE: source or rationale --> |

## Problem and Opportunity

<!-- TEMPLATE: Describe current behavior or pain, its consequences, and the desired change. Separate verified current facts from proposed behavior. -->

## Actors and Permissions

| Actor or system | Goal | Allowed actions | Forbidden or constrained actions |
|---|---|---|---|
| <!-- TEMPLATE: actor --> | <!-- TEMPLATE: goal --> | <!-- TEMPLATE: permission --> | <!-- TEMPLATE: boundary --> |

## Outcomes and Success Measures

| ID | Outcome | Measure | Target or evaluation method |
|---|---|---|---|
| OUT-001 | <!-- TEMPLATE: desired outcome --> | <!-- TEMPLATE: observable measure --> | <!-- TEMPLATE: target or method --> |

## Scope

### In Scope

<!-- TEMPLATE: List behavior required by this feature. -->

### Out of Scope

<!-- TEMPLATE: List explicit non-goals that protect the boundary. -->

### Deferred

<!-- TEMPLATE: List plausible later work that must not shape current acceptance unless stated. -->

## Requirements

| ID | Requirement | Rationale | Scenario | Acceptance |
|---|---|---|---|---|
| REQ-001 | <!-- TEMPLATE: testable observable obligation --> | <!-- TEMPLATE: why --> | <!-- TEMPLATE: SCN-NNN link --> | <!-- TEMPLATE: criterion --> |

## Invariants

| ID | Invariant | Enforcement boundary | Verification |
|---|---|---|---|
| INV-001 | <!-- TEMPLATE: rule that must always hold --> | <!-- TEMPLATE: owner --> | <!-- TEMPLATE: check --> |

## State and Lifecycle

<!-- TEMPLATE: Define relevant states, allowed transitions, triggers, guards, terminal states, cancellation, and recovery. Link the data model. -->

## Dependencies and Constraints

<!-- TEMPLATE: Define upstream/downstream systems, approved infrastructure, compatibility, operational, legal, schedule, or repository constraints. -->

## Security and Privacy

<!-- TEMPLATE: Define authentication, authorization, tenancy, trust boundaries, sensitive data, abuse cases, secrets, audit, and privacy requirements. -->

## Failure, Recovery, and Observability

<!-- TEMPLATE: Define validation and dependency failures, retries, idempotency, cancellation, rollback, degraded behavior, logs, metrics, audit events, and user-visible recovery. -->

## Acceptance Criteria

- <!-- TEMPLATE: Write an end-to-end criterion tied to REQ-NNN and SCN-NNN. -->

## Assumptions

| Assumption | Rationale | Validation method | Impact if false |
|---|---|---|---|
| <!-- TEMPLATE: reversible assumption --> | <!-- TEMPLATE: rationale --> | <!-- TEMPLATE: needed evidence --> | <!-- TEMPLATE: affected contracts --> |

## Open Questions

| Question | Impact | Owner or resolution trigger | Blocking |
|---|---|---|---|
| <!-- TEMPLATE: unresolved question --> | <!-- TEMPLATE: consequence --> | <!-- TEMPLATE: owner/evidence --> | <!-- TEMPLATE: yes/no --> |

## Traceability

Use [user scenarios](scenarios.md), [technical design](design/technical.md), [UI/UX design](design/ui-ux.md), [API contract](interfaces/api.md), [data model](data/model.md), [decisions](decisions.md), and [delivery plan](delivery/plan.md) to trace each requirement into implementation and validation.
