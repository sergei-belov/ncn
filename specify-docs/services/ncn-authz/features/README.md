# ncn-authz Feature Registry

| Feature | Status | Project IDs | Affected services | Contract | Last reviewed |
|---|---|---|---|---|---|
| Database-driven authorization | Active; common source Present, migration Open | FEAT-004, REQ-005, INV-006 | `ncn-pms`, `ncn-agents`, all future backend services | [Feature](database-driven-authorization.md) | 2026-08-14 |

## Feature Contract Requirements

Each feature defines behavior, permissions, failures/recovery, acceptance, and links across scenarios, common interfaces, models, tables, and decisions. `ncn-authz` owns authorization features; consuming services link to this owner and specify only their domain-side enforcement and user-visible handling.
