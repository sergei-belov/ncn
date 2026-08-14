# `workspace_users`

## Purpose

Stores one user's role in a workspace that is identified but not owned by this service.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Membership ID |
| `workspace_id` | `varchar(100)` | Not null, indexed | — | External workspace ID/slug |
| `user_id` | `uuid` | Not null, FK, indexed | — | Member user |
| `role` | `varchar(16)` | Not null | — | `owner`, `admin`, or `member` |
| `version` | `integer` | Not null, positive | `1` | Optimistic version |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |

## Relationships

- `user_id -> users.id`: many-to-one, `ON DELETE CASCADE`, deferrable.
- Workspace has no local parent table.

## Indexes and rules

- `uq_workspace_users_workspace_user`: unique `(workspace_id, user_id)`.
- `ck_workspace_users_role`: role allow-list.
- `ck_workspace_users_version_positive`: version greater than zero.
- Single-column indexes on `workspace_id` and `user_id`.

## Used by

Workspace membership list/mutation endpoints and workspace-scoped named policy checks.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Authorization and memberships API](../../backend/services/authz/api.md#authorization-and-memberships)
