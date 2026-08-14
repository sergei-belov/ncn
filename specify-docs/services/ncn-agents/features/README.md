# ncn-agents Feature Registry

| Feature | Status | Project IDs | Affected services | Contract | Last reviewed |
|---|---|---|---|---|---|
| Agent configuration | Active/partial | FEAT-002, OUT-002, REQ-002 | Frontend, PMS project-reference/migration boundary | [Feature](agent-configuration.md) | 2026-08-13 |
| Coordinated agent execution | Draft/in development | FEAT-003, OUT-003, REQ-003/004 | Frontend, PMS tool boundary | [Feature](coordinated-agent-execution.md) | 2026-08-13 |

## Feature Contract Requirements

Configuration and execution are separate contracts because one is Present and the other Planned. Changes to agent fields/status still require inspecting snapshot, Run UI/API, permission, memory, tool, table, and migration consequences.
