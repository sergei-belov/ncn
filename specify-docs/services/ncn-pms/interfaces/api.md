# ncn-pms API and Request/Response Interfaces

## Applicability

Applicable. The resource-oriented FastAPI `/api/v1/workspaces/{workspace_slug}/projects` family is **Present**. This contract groups related operations; exact Present DTO validation is defined by verified Pydantic models and must remain compatible during backend evolution.

## Ownership and Consumers

| Interface family | Owner | Consumer | Trust boundary | Status |
|---|---|---|---|---|
| PMS HTTP resources | `ncn-pms` | Current Vue adapters; future `ncn-agents` tools | Common `ncn-authz` actor/decision into domain owner | Present |
| PMS API/MCP tools | `ncn-pms` | `ncn-agents` | Agent tool policy plus owner API | Planned |

## Shared Conventions

Base path is `/api/v1/workspaces/{workspace_slug}/projects`. Protected requests require the common persisted actor; project routes require the current authz ProjectUser role/action, and agent calls also carry their Run/tool domain context. JSON uses `snake_case`; timestamps are UTC ISO 8601; dates are `YYYY-MM-DD`; IDs are UUID. Create requests use client-generated IDs where defined. Guarded mutations carry expected entity/board versions in JSON. No custom synchronous tracking, duplicate-control, or concurrency headers are accepted. List endpoints use cursor/limit (1–100); board uses `per_column` (1–50). Unknown query parameters and invalid/null fields are rejected.

Success envelopes expose `data` and optional `meta`. Stable error envelope is `{error:{code,message,field_errors?}}`. Required codes include authentication required, forbidden, validation, not found, archived/read-only, version/board conflict, duplicate identifier/name/rank, default/sole-stage deletion, invalid replacement, and rate/dependency errors.

## Operation Inventory

| ID | Kind/entry point | Purpose | Consumer | Requirement/feature |
|---|---|---|---|---|
| API-PMS-001 | `GET/POST /` | List/search/create projects | Frontend | PMS-REQ-001 |
| API-PMS-002 | `GET/PATCH /{project_id}`; `POST .../archive|restore` | Read/update/lifecycle project | Frontend | PMS-REQ-001/005 |
| API-PMS-003 | `GET/POST /{project_id}/states`; `PATCH /.../{state_id}` | Read/create/update stage | Frontend | PMS-REQ-004/005 |
| API-PMS-004 | `POST /.../states/reorder`; `DELETE /.../states/{state_id}` | Reorder/delete with transfer | Frontend | PMS-REQ-004/005 |
| API-PMS-005 | `GET /{project_id}/board`; `GET/PATCH .../board-preferences` | Board snapshot/preferences | Frontend | PMS-REQ-002 |
| API-PMS-006 | `GET/POST/PATCH/DELETE .../work-items`; `POST .../{id}/move` | Work-item lifecycle/order | Frontend/agent tools | PMS-REQ-002/003/005 |
| API-PMS-007 | `GET/POST/PATCH/DELETE .../epics`; membership operations | Epic lifecycle/membership | Frontend/agent tools | PMS-REQ-003/005 |

## API-PMS-001: Projects Collection

### Contract

`GET` filters by `search`, active/archive status, ownership/mine, sort, cursor, and limit. `POST` atomically creates a project, creator membership, one usable default workflow (current product expects four initial stages), counters/version, and any required coordinator bootstrap through a separately owned contract.

### Authentication and Authorization

A persisted workspace actor is required. `GET` returns only projects with a ProjectUser relation for that actor. Any persisted actor may currently create a project; creation establishes only that actor's admin relation in the new project and grants no authority elsewhere.

### Request

Create: client UUID `id`, trimmed `name` 1–255, uppercase `identifier` matching 2–10 `[A-Z0-9]`, nullable description up to 2000, optional icon, `#RRGGBB` color, access enum. Explicit null is allowed only where defined.

### Response

`201` returns full Project with permissions, member summary/IDs, default state, archive/timestamps, and version. List returns project items plus cursor metadata and workspace-level permissions.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Invalid/duplicate identifier | `422 validation` or `409 duplicate_identifier` | Correct field; do not blind retry |
| Authentication or scope failure | `401 AUTH_REQUIRED` or `403 FORBIDDEN` | Reauthenticate/provision or correct scope |
| Duplicate client ID | Original project for the same creator/scope or `409 PROJECT_ID_TAKEN` | GET by ID; never create another ID automatically |

### State, Idempotency, and Concurrency

Client-generated project ID is the create replay identity. Creation is one current shared transaction across PMS project/bootstrap and authz creator membership. Present project patch/archive/restore do not accept a client expected version; their returned version remains canonical, and stronger project-update concurrency is an Open compatibility gap rather than a header contract.

## API-PMS-002: Project Resource and Lifecycle

### Contract

Read returns full project. Patch accepts only changed project fields and returns full representation. Archive requires confirmation name; restore accepts an empty command body.

### Authentication and Authorization

Read requires API-AUTHZ-003 project access; update/archive/restore require the admin-level PMS action and PMS recheck. Archive changes all effective shared-domain mutations to denied.

### Request

Patch fields match create except `id`; only `description` may be cleared with null. Archive includes `confirmation_name` equal to current name. Restore uses an empty JSON object. Current project lifecycle requests carry no expected-version field; clients use the canonical returned version for display/refetch.

### Response

Current canonical Project and incremented version/updated time.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Wrong archive confirmation | `422 confirmation_mismatch` | Re-enter current name |
| Already archived/restored | Stable no-op or `409 invalid_transition` | GET canonical project |

### State, Idempotency, and Concurrency

Archive/restore is atomic. Concurrent project update protection beyond database transaction order is Open in the Present contract; clients refetch canonical state after completion/conflict.

## API-PMS-003/004: Stage Workflow

### Contract

List/create/patch stages; reorder all IDs; delete a stage with `replacement_state_id` when needed. Only stages in the same project participate.

### Authentication and Authorization

Read requires common project access. Every mutation requires the admin stage-management action plus PMS active-project/domain checks.

### Request

Stage create: client UUID, trimmed unique name 1–50, color, group, optional `after_state_id`, `is_default`. Patch rejects nulls. Reorder requires a complete non-empty ordered ID list and `expected_board_version >= 1`. Delete uses valid replacement and expected board version.

### Response

Stage representation includes id/project/name/color/group/position/default/work-item count/version. Reorder/delete returns canonical stages and board version.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Duplicate name/position | `409 state_conflict` | Reload and choose name/order |
| Default/sole delete | `409 protected_state` | Select another default/retain stage |
| Invalid replacement/stale board | `422 invalid_replacement` / `409 board_conflict` | Reload and confirm again |

### State, Idempotency, and Concurrency

Default switch, reorder, and delete/transfer are atomic under project/board concurrency control. Duplicate create uses client ID.

## API-PMS-005: Board and Preferences

### Contract

Board read returns project, permissions, `board_version`, ordered column snapshots with paged cards, members, epic pickers, and per-user preferences. Queries filter search, priority, assignee, epic, due status, mine, and per-column size. Preferences patch display booleans and/or collapsed stage IDs.

### Authentication and Authorization

Common project read access is required; preference changes belong to current persisted actor/project and do not mutate shared board truth. All roles may change personal preferences under the current policy.

### Request

Filters are optional and validated. Preferences reject explicit null and cross-project/unknown state IDs.

### Response

Canonical board snapshot or preferences with version. Ordering is deterministic by stage position and card rank.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Invalid cursor/filter | `422 validation` | Reset filter/cursor |
| Stale preference version | `409 version_conflict` | Reload preferences |
| Partial backend dependency | `503 unavailable` | Retry bounded read; keep last clearly stale view |

### State, Idempotency, and Concurrency

Reads are side-effect free. Preference patch uses versioned actor/project row. Board result is a snapshot, not a multi-resource write surface.

## API-PMS-006/007: Work Items and Epics

### Contract

Both resources support list/create/read/patch/delete. Work items support exact move. Epics support list/add/remove work-item membership and derived progress.

### Authentication and Authorization

Common project read or role-appropriate work-management action is required by operation. PMS rechecks referenced states, authz project users, epics, and work items within the same project.

### Request

Work item: UUID, title 1–255, HTML description, state, priority, up to 10 assignees, optional epic/dates, optional one before/after anchor. Move: target state, mutually exclusive anchor, expected item/board versions, client mutation UUID. Epic has equivalent title/description/state/priority/assignees/dates; membership batch contains 1–100 IDs and explicit `move_from_other_epics`.

### Response

Full resource/detail or cursor page. Move returns card, board version, echoed mutation ID, and canonical neighbors. Epic membership returns updated epic and cards; progress is derived.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Invalid date/reference/anchor | `422 validation` | Correct request |
| Stale entity/board | `409 version_conflict` / `board_conflict` | Roll back UI, reload, reapply intent |
| Cross-project or forbidden | `404 not_found` or `403 forbidden` per disclosure policy | Do not retry |
| Unknown move outcome | `409/503 outcome_unknown` if applicable | GET board and locate mutation/result; do not blind repeat |

### State, Idempotency, and Concurrency

Create is idempotent by client ID. Move is atomic across old/new ordering and board version, deduped by client mutation ID. Epic relink and derived counts/progress are one transaction. Deletes preserve relationship invariants.

## Compatibility and Versioning

Maintain `/api/v1` through backend/service evolution. Additive response fields are allowed; field removal/meaning change requires `/v2` or a negotiated version and migration window. Stable error codes and enum semantics are part of compatibility.

## Limits and Performance

Current list limit is 1–100; board per column 1–50; assignees 10; epic membership batch 100. Production rate, payload, timeout, p95, and project-size limits remain Open.

## Observability

Record persisted `user.id`, scope/role, operation, safe resource IDs/versions, status/error code, latency, DB time, conflicts, duplicate outcome, and safe audit outcome. Agent-owned Run/tool IDs may accompany agent calls. Do not log bearer data, rich descriptions, or member-sensitive bodies.

## Traceability

API-PMS-001..007 consume API-AUTHZ-003 → PMS-REQ-001..008 → SCN-001..003 → UX-PMS-001..004 → MODEL/TABLE-PMS plus MODEL/TABLE-AUTHZ references → FEAT-001/004 acceptance.
