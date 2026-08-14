# Current Service Registry

| Service | Responsibility | Owned capabilities | Authoritative data | Exposes | Depends on | Status | Contract |
|---|---|---|---|---|---|---|---|
| `ncn-authz` | Common identity and project authorization | Persisted User/ProjectUser, actor resolution, role-to-action policy, access identity | Shared PostgreSQL `users`/`project_users` | Present current-user/local-auth HTTP and common actor dependency; independent API Planned/Open | OIDC-verifying edge/local auth, PostgreSQL, PMS project reference | Common layer Present; independent deployment Open | [Service spec](ncn-authz/README.md) |
| `ncn-pms` | Project work management | Projects, board, stages, cards, epics, ordering/archive | PMS PostgreSQL domain state | Present PMS `/api/v1` API; future tool/events only as required | `ncn-authz`, frontend, PostgreSQL | Present core | [Service spec](ncn-pms/README.md) |
| `ncn-agents` | Agent configuration and coordinated execution | Coordinator/workers, Sessions, Runs, plans, tools, approvals, usage | Agent config/execution PostgreSQL state | Present config API; Planned Run APIs | `ncn-authz`, PMS owner API, frontend; planned Temporal/model/memory/artifacts | Config Present; execution in development | [Service spec](ncn-agents/README.md) |

## Ownership Rules

Only these services are currently in the active registry. Authz owns common identity/role-policy truth, PMS alone writes project-work state, and Agents alone owns agent configuration/execution semantics. Agents calls PMS through an owner API/MCP tool. Physical colocation does not change logical ownership.

## Dependency Rules

Synchronous calls carry the common persisted actor/service identity and workspace/project scope. Domain commands carry client-generated IDs and expected versions in JSON where applicable. Async Run/tool flows use their own Run/node/tool/event and causation IDs. No consumer treats another owner's table as a supported interface outside the current shared common-layer implementation. Future integrations remain deferred until active development creates an evidence-backed contract.
