# `pms_board_preferences`

## Purpose

Stores one user's presentation preferences for one project board.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Preference ID |
| `project_id` | `uuid` | Not null, FK, indexed | — | Project |
| `user_id` | `uuid` | Not null, indexed, no FK | — | Preference owner |
| `display` | `jsonb` | Not null | All four flags `true` | Priority, assignee, due-date, and epic visibility |
| `collapsed_state_ids` | `uuid[]` | Not null | Empty array | Collapsed state IDs |
| `version` | `integer` | Not null | `1` | Optimistic version |

## Relationships

- `project_id -> pms_projects.id`: many-to-one, `ON DELETE CASCADE`.
- `user_id` and collapsed-state elements have no database foreign keys; managers validate ownership.

## Indexes and rules

- `uq_pms_board_preferences_project_user`: unique `(project_id, user_id)`.
- Single-column indexes on project and user.
- Preferences are inserted lazily on first read and may be updated for archived projects.

## Used by

Board snapshots and board-preference GET/PATCH endpoints.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Board and preferences API](../../backend/services/pms/api.md#board-and-preferences)
