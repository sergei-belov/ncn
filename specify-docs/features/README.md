# Current Feature Registry

| ID | Feature | Owning service | Affected services | Project outcome/requirement | Status | Contract | Last reviewed |
|---|---|---|---|---|---|---|---|
| FEAT-001 | Project work management | `ncn-pms` | Frontend, `ncn-agents` as tool consumer | OUT-001; REQ-001/004 | Active/Present core | [contract](../services/ncn-pms/features/project-work-management.md) | 2026-08-13 |
| FEAT-002 | Agent configuration | `ncn-agents` | Frontend, PMS project-reference boundary | OUT-002; REQ-002 | Active/Present | [contract](../services/ncn-agents/features/agent-configuration.md) | 2026-08-13 |
| FEAT-003 | Coordinated agent execution | `ncn-agents` | PMS tool boundary and frontend | OUT-003; REQ-003/004 | Draft/in development | [contract](../services/ncn-agents/features/coordinated-agent-execution.md) | 2026-08-13 |
| FEAT-004 | Database-driven authorization | `ncn-authz` common layer | `ncn-pms`, `ncn-agents`, all future backend services | OUT-001/002; REQ-005 | Active; common source Present, migration/extraction Open | [contract](../services/ncn-authz/features/database-driven-authorization.md) | 2026-08-14 |

## Registry Rules

- Register only features currently implemented or actively in development.
- Assign one owning service and update the other service only for actual dependency effects.
- Keep future integrations under Deferred/Open until development begins.
