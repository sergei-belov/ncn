# ncn-pms Feature Registry

| Feature | Status | Project IDs | Affected services | Contract | Last reviewed |
|---|---|---|---|---|---|
| Project work management | Active | FEAT-001, OUT-001, REQ-001/004 | Frontend, `ncn-agents` tool consumer | [Feature](project-work-management.md) | 2026-08-13 |

## Feature Contract Requirements

Each feature has one owner and defines behavior, permissions, failure/recovery, acceptance, and links across scenarios, UI, interfaces, models, tables, and decisions. Add another PMS feature only when its development starts. Database-driven authorization is owned by [`ncn-authz`](../../ncn-authz/features/database-driven-authorization.md); PMS documents only its consumer/domain enforcement.
