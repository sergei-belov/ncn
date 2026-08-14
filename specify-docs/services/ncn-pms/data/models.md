# ncn-pms Models

## Applicability and Ownership

Applicable. PMS owns authoritative project-work domain models and their commands/DTOs. The Present frontend uses camelCase domain projections and `snake_case` wire DTOs; the Present backend has Pydantic API/DTO models. User, ProjectUser role, and authorized actor models are externally owned by `ncn-authz` and referenced through its common interface.

## Model Inventory

| ID | Model | Kind | Owner | Purpose | Interfaces | Persistence |
|---|---|---|---|---|---|---|
| MODEL-PMS-001 | Project | Domain/DTO | PMS | Project lifecycle, scope, authz permission projection, counters/version | API-PMS-001/002 | TABLE-PMS-001 plus external TABLE-AUTHZ-002 |
| MODEL-PMS-002 | WorkflowState | Domain/DTO | PMS | Ordered stage/default | API-PMS-003/004/005 | TABLE-PMS-003 |
| MODEL-PMS-003 | WorkItem | Domain/DTO/command | PMS | Trackable card and exact order | API-PMS-005/006 | TABLE-PMS-004/005 |
| MODEL-PMS-004 | Epic | Domain/DTO | PMS | Group work and derive progress | API-PMS-005/007 | TABLE-PMS-006/007 |
| MODEL-PMS-005 | BoardSnapshot/Preferences | Read/command | PMS | Aggregate board plus per-user view choices | API-PMS-005 | TABLE-PMS-001/008 plus derived joins |

## MODEL-PMS-001: Project

### Semantics

Authoritative workspace-scoped project. Active/archived lifecycle, default-stage reference, board/version and sequence counters are owner state. Returned role/permissions/counts/member previews are computed projections.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| `id`, `workspace_slug` | UUID/string | Required | Stable ID; slug 1–100 | Internal | Identity/scope |
| `name`, `identifier` | string | Required | Name 1–255; identifier uppercase 2–10 alphanumeric, unique/workspace | Internal | Display and work prefix |
| `description`, `icon`, `color`, `access` | text/JSON/string/enum | Description nullable; others defaulted | Color `#RRGGBB`; allowed access | Internal | Presentation/access setting |
| `default_state_id` | UUID | Required after bootstrap | Same project, exactly one default | Internal | New-work default |
| `archived_at` | datetime | Nullable | Set/clear by lifecycle command | Internal | Read-only state |
| `board_version`, `version` | positive int | Default 1 | Monotonic | Internal | Optimistic concurrency |
| sequence counters/timestamps/creator | int/time/UUID | Required | Monotonic/UTC | Internal | IDs and audit metadata |

### Identity and Relationships

Project identifier is unique within workspace. Project has external authz ProjectUser relations and PMS-owned stages, cards, epics and preferences. `ncn-agents` stores project/resource IDs and versions only when recording a Run/tool effect.

### State and Invariants

Archive/restore are guarded transitions. Exactly one default stage and positive versions. Project creation establishes consistent child bootstrap in one transaction.

### Serialization and Versioning

Wire is `snake_case`; frontend is mapped to camelCase. Additive fields are compatible. Permission flags are responses, never accepted as authority.

### Mappings

API Project/ListItem map to TABLE-PMS-001 plus authz ProjectUser/User projections and derived counts. Create/update/archive commands map to PMS owner transactions; creator membership uses the current common authz layer.

## MODEL-PMS-002: WorkflowState

### Semantics

Project-owned ordered stage with name/color/group/default and version. Deletion is a command that may transfer cards.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| `id`, `project_id` | UUID | Required | Same owner scope | Internal | Identity/parent |
| `name`, `color`, `group` | string/enum | Required | Name 1–50 unique CI/project; color format; allowed group | Internal | Stage presentation/semantics |
| `position`, `is_default`, `version` | int/bool/int | Required/default false/1 | Unique position/project; one default/project; version positive | Internal | Order/default/concurrency |
| `work_items_count` | int | Derived | Non-negative | Internal | UI impact summary |

### Identity and Relationships

Many stages belong to one project; cards/epics reference a stage in the same project. Position/default uniqueness is project-local.

### State and Invariants

Default/sole deletion is forbidden. Default switch and reorder are atomic. Delete transfers cards before removing the stage.

### Serialization and Versioning

Stage group enum changes are additive/versioned. Reorder command carries all ordered IDs plus expected board version.

### Mappings

API-PMS-003/004/005; TABLE-PMS-003; Project.default_state_id and WorkItem/Epic.state_id.

## MODEL-PMS-003: WorkItem

### Semantics

Authoritative card with project sequence identifier, rich description, stage, priority, assignees, optional epic/dates, rank, audit timestamps, and version.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| identity/project/sequence | UUID/UUID/int | Required | Sequence unique/project | Internal | Stable and human ID |
| `title`, `description_html` | string | Required/default empty | Title 1–255; HTML untrusted | Potentially confidential | Content |
| `state_id`, `priority`, `rank` | UUID/enum/string | Required | Same project; rank unique within project/state | Internal | Workflow/order |
| `assignee_ids` | UUID list | Default empty, max 10 | Members in same project | Personal/internal | Ownership |
| `epic_id` | UUID | Nullable | Same project; at most one | Internal | Grouping |
| `start_date`, `due_date` | date | Nullable | Start <= due | Internal | Schedule |
| creator/timestamps/version | UUID/time/int | Required | UTC; version positive | Internal | Audit/concurrency |

### Identity and Relationships

One Project and State; zero/one Epic; many assignees. `identifier` is derived from project identifier and sequence.

### State and Invariants

Move validates target/anchors and expected item/board versions, then atomically updates ranks and board version. Epic delete clears link. State delete transfers.

### Serialization and Versioning

Detail and card-summary forms share stable identity/version. Unknown additive fields are tolerated by compatible clients after schema updates.

### Mappings

API-PMS-005/006; TABLE-PMS-004/005.

## MODEL-PMS-004: Epic

### Semantics

Project-owned higher-level work grouping with card membership and derived progress.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| identity/project/sequence | UUID/UUID/int | Required | Sequence unique/project | Internal | Identity |
| title/description/state/priority/rank | mixed | Required | Same core validation as work item | Potentially confidential | Definition/order |
| assignees/dates | UUID list/dates | Optional | Max 10; start <= due | Personal/internal | Responsibility/schedule |
| counts/progress | ints | Derived | 0–100 percent | Internal | Completion summary |
| timestamps/version | time/int | Required | UTC/positive | Internal | Audit/concurrency |

### Identity and Relationships

One project/stage, many assignees, many work items where each card has at most one epic.

### State and Invariants

Progress derives from current linked-card states. Delete clears card links. Membership command explicitly decides whether to move cards from other epics.

### Serialization and Versioning

List/detail/picker models are compatible projections of the same aggregate.

### Mappings

API-PMS-005/007; TABLE-PMS-006/007 and WorkItem.epic_id.

## MODEL-PMS-005: BoardSnapshot and Preferences

### Semantics

BoardSnapshot is a transient consistent read model; Preferences are authoritative only for a user's display choices, not work truth.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| project/permissions/version | aggregate | Required | Single scope/snapshot | Internal | Board context |
| columns/included | lists | Required | Ordered/paged; same project | Internal/personal | Stages/cards/members/epics |
| display flags | booleans | Defaults true | Known keys | Internal | Visible card properties |
| collapsed_state_ids | UUID list | Default empty | Same project states | Internal | User column collapse |
| preference version | int | Default 1 | Positive | Internal | Concurrency |

### Identity and Relationships

One preference per project/user. Snapshot composes owner models without becoming a writable aggregate.

### State and Invariants

Filters affect returned view only. Preference edits never change shared order or card state.

### Serialization and Versioning

Board additions are additive; clients must not reconstruct mutation commands from omitted paged items.

### Mappings

API-PMS-005; TABLE-PMS-008 plus joins to TABLE-PMS-001..007.

## Traceability

MODEL-PMS-001..005 → PMS-REQ-001..008 → SCN-001..003 → API-PMS-001..007 plus API-AUTHZ-003 → PMS-owned tables and TABLE-AUTHZ-001/002 → FEAT-001 acceptance.
