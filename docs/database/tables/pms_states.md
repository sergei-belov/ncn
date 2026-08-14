# `pms_states`

## Purpose

Stores one ordered workflow state and the single default marker within a project.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | State and create-command ID |
| `project_id` | `uuid` | Not null, FK, indexed | — | Owning project |
| `name` | `varchar(50)` | Not null | — | Display name |
| `color` | `varchar(7)` | Not null | — | Hex color |
| `group` | `varchar(16)` | Not null | — | Semantic state group |
| `position` | `integer` | Not null | — | Zero-based board order |
| `is_default` | `boolean` | Not null | `false` | Project creation fallback |
| `version` | `integer` | Not null | `1` | Entity version |

## Relationships

- `project_id -> pms_projects.id`: many-to-one, `ON DELETE CASCADE`.
- Referenced by work items and epics with `ON DELETE RESTRICT`.
- Project `default_state_id` points here logically without a foreign key.

## Indexes and rules

- `uq_pms_states_project_position`: unique `(project_id, position)`.
- `uq_pms_states_project_name_ci`: unique `(project_id, lower(name))`.
- `uq_pms_states_project_default`: unique `project_id` where `is_default=true`.
- State-group, color, position bounds, and positive version are API/manager rules rather than table checks.

## Used by

Kanban columns, default card/epic state, board structure, completion progress, and state administration.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [States API](../../backend/services/pms/api.md#states)
