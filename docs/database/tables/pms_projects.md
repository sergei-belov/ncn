# `pms_projects`

## Purpose

Stores project identity, visibility, archive state, default workflow state, sequence counters, and board/entity versions.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Project and create-command ID |
| `workspace_slug` | `varchar(100)` | Not null, indexed | — | External owning workspace |
| `name` | `varchar(255)` | Not null | — | Project name |
| `identifier` | `varchar(10)` | Not null | — | Prefix for card/epic identifiers |
| `description` | `text` | Nullable | — | Project description |
| `icon` | `jsonb` | Not null | `{"type":"initial","value":"P"}` | Emoji/initial icon object |
| `color` | `varchar(7)` | Not null | `#5E6AD2` | Hex presentation color |
| `access` | `varchar(16)` | Not null | `private` | `private` or `workspace` visibility |
| `default_state_id` | `uuid` | Nullable, no FK | — | Current default workflow state |
| `archived_at` | `timestamptz` | Nullable, indexed | — | Archive timestamp |
| `board_version` | `integer` | Not null, positive | `1` | Structural board version |
| `next_work_item_sequence` | `integer` | Not null | `1` | Next card sequence |
| `next_epic_sequence` | `integer` | Not null | `1` | Next epic sequence |
| `created_by` | `uuid` | Not null, indexed, no FK | — | Creator user ID |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |
| `version` | `integer` | Not null, positive | `1` | Project entity version |

## Relationships

- Parent of agents, states, work items, epics, and board preferences; their declared FKs delete-cascade.
- `default_state_id` and `created_by` are logical references without FKs.
- `project_users.project_id` is also a logical, non-FK relation.

## Indexes and rules

- `uq_pms_projects_workspace_identifier`: unique `(workspace_slug, identifier)`.
- `ck_pms_projects_version_positive` and `ck_pms_projects_board_version_positive`.
- Single-column indexes on workspace, archive timestamp, and creator.
- API/manager validation, not database checks, enforces identifier, color, access, and sequence semantics.

## Used by

Every project-scoped API, sequence allocation, archive enforcement, permission context, and board concurrency.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Projects API](../../backend/services/pms/api.md#projects)
