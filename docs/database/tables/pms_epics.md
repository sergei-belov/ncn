# `pms_epics`

## Purpose

Stores one ordered project epic with workflow state, priority, dates, creator, and version.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Epic and create-command ID |
| `project_id` | `uuid` | Not null, FK, indexed | — | Owning project |
| `sequence_id` | `integer` | Not null | — | Project-local sequence |
| `title` | `varchar(255)` | Not null | — | Epic title |
| `description_html` | `text` | Not null | Empty string | Sanitized rich text |
| `state_id` | `uuid` | Not null, FK, indexed | — | Current workflow state |
| `priority` | `varchar(16)` | Not null | `none` | Priority enum value |
| `start_date` | `date` | Nullable | — | Planned start |
| `due_date` | `date` | Nullable, indexed | — | Planned completion |
| `rank` | `varchar(32)` | Not null | — | Opaque epic order key |
| `created_by` | `uuid` | Not null, indexed, no FK | — | Creator user ID |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |
| `version` | `integer` | Not null | `1` | Entity version |

## Relationships

- `project_id -> pms_projects.id`: `ON DELETE CASCADE`.
- `state_id -> pms_states.id`: `ON DELETE RESTRICT`.
- Referenced by work items with `ON DELETE SET NULL`.
- Parent of epic-assignee rows with delete cascade.

## Indexes and rules

- `uq_pms_epics_project_sequence`: unique `(project_id, sequence_id)`.
- `uq_pms_epics_project_rank`: unique `(project_id, rank)`.
- `ck_pms_epics_date_order`: start must not exceed due date when both exist.
- Manager/API rules validate priority, version, scope, assignees, and HTML.

## Used by

Epic CRUD/lists, board picker data, card membership, progress aggregation, and project counts.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Epics API](../../backend/services/pms/api.md#epics)
