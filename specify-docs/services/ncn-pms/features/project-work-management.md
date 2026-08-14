# Feature: Project Work Management

## Status

Owning service: `ncn-pms`. Status: Active core slice, draft expanded scope. Owner: PMS team. Last reviewed: 2026-08-13. Evidence: legacy docs plus authorized Vue/FastAPI/model verification.

## Problem and Goal

Teams need a consistent project workspace for ordered work, not disconnected lists. PMS owns this feature because projects, stages, cards, epics and ordering form one transactional domain. The goal is for an authorized user or tool to read and change work without orphaning relationships or overwriting concurrent updates.

## Actors and Permissions

| Actor/system | Goal | Allowed | Forbidden/constrained |
|---|---|---|---|
| Admin | Configure project and workflow | Project/stage/card/epic actions granted by policy | No mutation when archived |
| Member | Manage daily work | Authorized card and epic actions | No project/stage administration by default |
| Viewer | Read status | Read authorized project data | No mutations |
| Agent/frontend | Act for a common `ncn-authz` persisted principal | Owner API/MCP or current resource operations with scope and policy | No direct tables, token grants, or client-derived permission |

## Scope

### In Scope

Project list/search/create/update/archive/restore; initial stages; board load/filters/display/collapse; work-item quick/full CRUD, assignees, epic, dates, priority and exact movement; epic CRUD/membership/progress; stage create/edit/default/reorder/delete-with-transfer; read-only archive; responsive route-aware details; stable API errors and JSON version fields for guarded mutations.

### Out of Scope

Agent execution, agent memory/artifacts, and future external integrations. No not-yet-developed PMS expansion is included.

## Requirements and Invariants

| ID | Requirement/invariant | Rationale | Acceptance |
|---|---|---|---|
| PMS-FR-001 | New project creation establishes a usable workflow with one default stage. | No project may start unusable. | Create then board read returns ordered stages/default |
| PMS-FR-002 | Card movement specifies target plus at most one before/after anchor and expected card/board versions. | Exact order and concurrent safety. | Canonical response persists after reload; stale request conflicts |
| PMS-FR-003 | Deleting a populated stage atomically transfers cards to a valid replacement. | Prevent orphaned work. | All cards survive and default invariant remains |
| PMS-FR-004 | Epic membership is at most one per card; deleting an epic only clears links. | Cards are independent work truth. | Card count unchanged after epic delete |
| PMS-FR-005 | UI and API deny mutation for archived or unauthorized projects. | Defense in depth. | Controls absent/disabled and API rejects direct request |

## Scenarios and Contract Effects

| Scenario | UI/UX | API/events | Models/tables | Affected services |
|---|---|---|---|---|
| SCN-001 manage project work | UX-PMS-001..004 | API-PMS-001..006 plus API-AUTHZ-003 | MODEL-PMS-001..005; PMS tables plus TABLE-AUTHZ-001/002 | Frontend, authz, agents |
| SCN-002 change workflow safely | UX-PMS-004 | API-PMS-003/004 | Project/State/WorkItem; project/state/item tables | Frontend, agents |

## Failure, Recovery, and Observability

Field validation remains local and server-enforced. Version conflicts and permission/archive failures do not mutate state. Optimistic UI changes snapshot every affected board query, roll back all snapshots on error, and refetch. Create/move duplicates are deduplicated by client identifier/mutation ID. Agent tool uncertainty is resolved by reading canonical PMS state. Observe API latency/errors, conflict frequency, rollback/refetch, board-version anomalies and scope denials.

## Acceptance Criteria

- An admin can create, edit, archive, restore, and configure workflow without breaking the default-stage invariant.
- A member can create, filter, edit, and exactly move cards; order survives reload and failed optimistic updates roll back.
- Epics link cards and derive progress; deletion leaves cards intact.
- Viewer and archived-project mutations are denied in UI and API.
- Concurrent stale guarded card/stage/board updates fail without partial state; stronger project-update concurrency remains Open.

## Assumptions and Open Questions

Initial four-stage names and groups remain implementation/product configuration, not an immutable architecture rule. Exact defect/gate/history behavior, domain event schemas, ProjectUser administration (owner is authz), and retention are Open.

## Traceability

[Service spec](../spec.md), [scenarios](../scenarios.md), [technical design](../design/technical.md), [UI/UX](../design/ui-ux.md), [API](../interfaces/api.md), [events](../interfaces/events.md), [models](../data/models.md), [tables](../data/tables.md), [decisions](../decisions.md), project FEAT-001/004 and REQ-001/004/005.
