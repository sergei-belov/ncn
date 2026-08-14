# Feature: Agent Configuration

## Status

Owning service: `ncn-agents`. Status: Active/partial. Owner: Agent platform. Reviewed 2026-08-13. List/create/read/update/enable/disable/archive UI/API and a transitional SQL table are Present; configuration publication/version snapshots and ownership extraction are Planned.

## Problem and Goal

Each project needs one coordinator and reusable specialist workers whose behavior and allowed capabilities can be governed. The goal is to let admins authorized by the common `ncn-authz` project-role policy manage configuration without changing in-flight Runs or weakening coordinator/domain invariants.

## Actors and Permissions

| Actor/system | Goal | Allowed | Forbidden/constrained |
|---|---|---|---|
| Project admin | Create/configure workers and coordinator settings | Authorized edits and worker status commands | Cannot disable/archive coordinator; cannot edit active snapshot |
| Member/viewer | Understand available agents | Authorized read-only view | No configuration/status mutation |
| Run creator | Execute with a stable configuration | Reference published/eligible agents | Cannot mutate config through Run input |

## Scope

### In Scope

Agent list/detail; worker create; name/description/instructions/model/memory policy/max steps/approval mode; active/disabled/archived status; coordinator protection; expected-version mutation; read-only archive/permission states; immutable Run snapshot boundary.

### Out of Scope

Model registry administration, execution orchestration, memory implementation, tool connection lifecycle, policy ownership, and arbitrary worker-to-worker delegation.

## Requirements and Invariants

| ID | Requirement/invariant | Rationale | Acceptance |
|---|---|---|---|
| AGT-CFG-001 | One and only one active coordinator exists per project. | Stable orchestration root. | Concurrent create/status tests cannot violate it |
| AGT-CFG-002 | Users create only workers; coordinator cannot be disabled/archived. | Prevent unusable project agent team. | UI/API/DB all reject transition |
| AGT-CFG-003 | Config updates require the common authz actor/action, validate fields/scope, and compare `expected_version` from JSON. | Prevent invalid/lost edits. | Stale/cross-project/denied tests fail atomically |
| AGT-CFG-004 | Run start records immutable effective configuration and policy/tool/memory constraints. | Reproducibility. | Later edit does not alter active Run |

## Scenarios and Contract Effects

| Scenario | UI/UX | API/events | Models/tables | Affected services |
|---|---|---|---|---|
| SCN-001 configure an agent team | UX-AGT-001/002 | API-AGT-001/002 plus API-AUTHZ-003 | MODEL-AGT-001/002; TABLE-AGT-001/002 | `ncn-authz`, frontend, PMS project reference/migration |
| SCN-002 start Run with snapshot | UX-AGT-003 | API-AGT-003 | MODEL-AGT-002/004; TABLE-AGT-002/005 | Frontend, PMS tool boundary |

## Failure, Recovery, and Observability

Validation and stale-version errors preserve user input and current owner state. Authz denial/archive violations are not retried. Duplicate worker names or coordinator creation fail under project-scoped uniqueness. Migration from `pms_agents` must preserve IDs/versions and block dual writes. Audit persisted actor UUID, scope, changed field names (not secret/instruction bodies), old/new version, status transition, and outcome; monitor conflicts and protected-transition attempts.

## Acceptance Criteria

- Authorized admin can create and configure a worker and toggle active/disabled/archive with expected version.
- Coordinator remains active under UI, API, concurrent, and direct constraint tests.
- Unauthorized, archived-project, stale, and cross-project mutation is rejected without partial state.
- A Run snapshot is immutable after creation.

## Assumptions and Open Questions

Current fields are retained initially. Open: publish/draft lifecycle, model/tool registry selection UI, which service bootstraps coordinator during project creation, and extraction/migration from `pms_agents`.

## Traceability

[Service spec](../spec.md), [SCN-001/002](../scenarios.md), [UI/UX](../design/ui-ux.md), [API](../interfaces/api.md), [models](../data/models.md), [tables](../data/tables.md), project FEAT-002/REQ-002.
