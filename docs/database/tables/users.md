# `users`

## Purpose

Stores the stable application identity resolved from bearer tokens and the optional local password hash.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | User ID |
| `email` | `varchar(100)` | Not null, unique, indexed | — | Canonical login email |
| `name` | `varchar(100)` | Not null | — | Display name |
| `password` | `text` | Nullable | — | Local bcrypt hash; mapped as `password_hash` |
| `is_active` | `boolean` | Not null | `true` | Authentication/access switch |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |

## Relationships

- `workspace_users.user_id -> users.id`: one-to-many, delete cascades.
- `project_users.user_id -> users.id`: one-to-many, delete cascades.

## Indexes and rules

- Email is unique and indexed.
- `ck_users_email_canonical`: stored email equals `lower(btrim(email))`.
- `ck_users_is_active`: value must be true or false.

## Used by

Authentication, automatic user provisioning, current-user responses, membership administration, and per-user rate limiting.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Authorization and memberships API](../../backend/services/authz/api.md#authorization-and-memberships)
