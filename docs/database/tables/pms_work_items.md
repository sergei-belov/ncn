# `pms_work_items`

## Purpose

Stores one ordered Kanban card with workflow, epic, dates, creator, and optimistic version.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Card and create-command ID |
| `project_id` | `uuid` | Not null, FK, indexed | — | Owning project |
| `sequence_id` | `integer` | Not null | — | Project-local sequence |
| `title` | `varchar(255)` | Not null | — | Card title |
| `description_html` | `text` | Not null | Empty string | Sanitized rich text |
| `state_id` | `uuid` | Not null, FK, indexed | — | Current workflow state |
| `priority` | `varchar(16)` | Not null | `none` | Priority enum value |
| `epic_id` | `uuid` | Nullable, FK, indexed | — | Optional owning epic |
| `start_date` | `date` | Nullable | — | Planned start |
| `due_date` | `date` | Nullable, indexed | — | Planned completion |
| `rank` | `varchar(32)` | Not null | — | Opaque manual order key |
| `created_by` | `uuid` | Not null, indexed, no FK | — | Creator user ID |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |
| `version` | `integer` | Not null | `1` | Optimistic version |

## Relationships

- `project_id -> pms_projects.id`: `ON DELETE CASCADE`.
- `state_id -> pms_states.id`: `ON DELETE RESTRICT`.
- `epic_id -> pms_epics.id`: `ON DELETE SET NULL`; alter-created FK named `fk_pms_work_items_epic`.
- Parent of assignee rows with delete cascade.

## Indexes and rules

- `uq_pms_work_items_project_sequence`: unique `(project_id, sequence_id)`.
- `uq_pms_work_items_state_rank`: unique `(project_id, state_id, rank)`.
- `ck_pms_work_items_date_order`: start must not exceed due date when both exist.
- Manager/API rules validate priority, positive version, project scope, sanitized HTML, and rank anchors.

## Used by

Board snapshots, work-item CRUD/move, epic membership/progress, state replacement, and project counts.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Work items API](../../backend/services/pms/api.md#work-items)
