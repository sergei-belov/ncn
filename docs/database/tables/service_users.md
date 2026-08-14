# `service_users`

## Purpose

Stores an optional role restriction for one project member in one service.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Restriction ID |
| `project_user_id` | `uuid` | Not null, FK, indexed | — | Parent project membership |
| `service_id` | `varchar(100)` | Not null | — | Stable service identifier |
| `role` | `varchar(16)` | Not null | — | Narrowed project role |
| `version` | `integer` | Not null, positive | `1` | Optimistic version |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |

## Relationships

- `project_user_id -> project_users.id`: many-to-one, `ON DELETE CASCADE`, deferrable.

## Indexes and rules

- `uq_service_users_project_user_service`: unique `(project_user_id, service_id)`.
- `ck_service_users_role` and `ck_service_users_version_positive`.
- Manager policy ensures the restriction cannot elevate the project role; the database does not compare the two rows.

## Used by

Project access UI/API and service-scoped authorization decisions.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Authorization and memberships API](../../backend/services/authz/api.md#authorization-and-memberships)
