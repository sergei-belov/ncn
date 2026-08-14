# `pms_agents`

## Purpose

Stores required coordinator and optional worker-agent configuration and lifecycle state.

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | Primary key, not null | Application `uuid4()` | Agent ID |
| `project_id` | `uuid` | Not null, FK, indexed | — | Owning project |
| `kind` | `varchar(16)` | Not null | — | `coordinator` or `worker` |
| `name` | `varchar(80)` | Not null | — | Project-local agent name |
| `description` | `varchar(240)` | Not null | Empty string | Short description |
| `instructions` | `text` | Not null | — | Agent instructions |
| `model` | `varchar(255)` | Not null | — | Model identifier |
| `memory_policy` | `varchar(16)` | Not null | — | `project`, `session`, or `none` |
| `max_steps_per_run` | `integer` | Not null, positive | — | Run step limit |
| `approval_mode` | `varchar(16)` | Not null | — | `project` or `always` |
| `status` | `varchar(16)` | Not null | `active` | `active`, `disabled`, or `archived` |
| `system_tool_names` | `jsonb` | Not null | `[]` | Locked system tool IDs |
| `created_by` | `uuid` | Not null, indexed, no FK | — | Creator user ID |
| `created_at` | `timestamptz` | Not null | `now()` | Creation time |
| `updated_at` | `timestamptz` | Not null | `now()`; ORM `now()` on update | Last update time |
| `version` | `integer` | Not null, positive | `1` | Optimistic version |

## Relationships

- `project_id -> pms_projects.id`: many-to-one, `ON DELETE CASCADE`.

## Indexes and rules

- `uq_pms_agents_project_coordinator`: unique `project_id` where `kind='coordinator'`.
- `uq_pms_agents_project_live_name`: unique `(project_id, name)` where status is not archived.
- Checks validate kind, memory policy, approval mode, status, positive step/version values, and active coordinator status.

## Used by

Agent list/detail/configuration/lifecycle APIs and project initialization. No execution records reference agents yet.

## Related documentation

- [Table index](../README.md)
- [Relationships and shared invariants](../relationships.md)
- [Agents API](../../backend/services/pms/api.md#agents)
