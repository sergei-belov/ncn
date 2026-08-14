# `pms_epic_assignees`

## Purpose

Associates an epic with one assigned user.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Association ID |
| `epic_id` | `uuid` | Not null, FK, indexed | — | Epic |
| `user_id` | `uuid` | Not null, indexed, no FK | — | Assigned project member |

## Relationships

- `epic_id -> pms_epics.id`: many-to-one, `ON DELETE CASCADE`.
- User membership is manager-validated; `user_id` has no FK.

## Indexes and rules

- `uq_pms_epic_assignees_epic_user`: unique `(epic_id, user_id)`.
- API/manager permits at most 10 unique project-member assignees.

## Used by

Epic list/detail responses and assignee filters.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Epics API](../../backend/services/pms/api.md#epics)
