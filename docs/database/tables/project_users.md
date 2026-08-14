# `project_users`

## Purpose

Stores one user's canonical role and membership source for a project.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Membership ID |
| `project_id` | `uuid` | Not null, indexed, no FK | — | PMS project ID |
| `workspace_id` | `varchar(100)` | Not null, indexed | — | Denormalized parent workspace |
| `user_id` | `uuid` | Not null, FK, indexed | — | Member user |
| `role` | `varchar(16)` | Not null | — | `admin`, `member`, or `viewer` |
| `source` | `varchar(16)` | Not null | `manual` | `manual` or `bootstrap` |
| `version` | `integer` | Not null, positive | `1` | Optimistic version |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |

## Relationships

- `user_id -> users.id`: many-to-one, `ON DELETE CASCADE`, deferrable.
- `service_users.project_user_id -> project_users.id`: one-to-many, delete cascades.
- Project and workspace consistency is enforced by managers because `project_id` has no FK.

## Indexes and rules

- `uq_project_users_project_user`: unique `(project_id, user_id)`.
- `ck_project_users_role`, `ck_project_users_source`, and `ck_project_users_version_positive`.
- Single-column indexes on project, workspace, and user.

## Used by

Project route authorization, permission resolution, project membership APIs, project lists, members/assignees, and creator bootstrap.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Authorization and memberships API](../../backend/services/authz/api.md#authorization-and-memberships)
