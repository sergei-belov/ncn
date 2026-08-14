# `pms_work_item_assignees`

## Purpose

Associates a work item with one assigned user.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Association ID |
| `work_item_id` | `uuid` | Not null, FK, indexed | — | Work item |
| `user_id` | `uuid` | Not null, indexed, no FK | — | Assigned project member |

## Relationships

- `work_item_id -> pms_work_items.id`: many-to-one, `ON DELETE CASCADE`.
- User membership is validated by managers; `user_id` has no FK.

## Indexes and rules

- `uq_pms_work_item_assignees_item_user`: unique `(work_item_id, user_id)`.
- API/manager permits at most 10 unique assignees, all current project members.

## Used by

Card list/detail/board responses and assignee filters.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Work items API](../../backend/services/pms/api.md#work-items)
