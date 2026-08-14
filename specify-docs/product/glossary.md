# NCN Glossary

| Term | Definition | Owning service/context | Not to be confused with | Status/source |
|---|---|---|---|---|
| Workspace | Top-level URL/tenant scope containing projects | Shared scope used by project-scoped services | Project | Confirmed: current API/UI |
| User | Persisted NCN application identity whose UUID is used by all services after authentication | `ncn-authz` | External provider account or bearer token | Confirmed common model |
| ProjectUser | One User's stored `admin`, `member`, or `viewer` role in one Project | `ncn-authz` | PMS work-item assignee or frontend permission flag | Confirmed common model |
| Project | Authoritative container for project work and agent scope | `ncn-pms` | Run | Confirmed |
| Workflow State / Stage | Ordered project-work state shown as a board column | `ncn-pms` | Run status | Confirmed; UI says “Состояние” |
| Work Item / Card | Trackable unit of project work | `ncn-pms` | RunPlan node | Confirmed |
| Epic | Group of related work items with derived progress | `ncn-pms` | Session | Confirmed |
| Coordinator | Exactly one active project agent that interprets goals and controls the Run plan | `ncn-agents` | Project admin | Confirmed design/config |
| Worker / Assistant | Specialized project agent invoked by the coordinator | `ncn-agents` | Temporal worker process | Confirmed design/config |
| Session | Ordered conversation/system context containing Messages and Runs | `ncn-agents` | Browser session | Confirmed design; UI placeholder Present |
| Run | One durable attempt to achieve a goal using an immutable configuration snapshot | `ncn-agents` | Model invocation | Confirmed design; Planned implementation |
| RunPlan | Validated plan whose revisions are immutable and whose side effects use explicit nodes | `ncn-agents` | PMS board | Confirmed design |
| Permission | Deterministic common-role plus consumer-domain decision that an action is allowed | `ncn-authz` for common role/action; domain owner for additional guards | Approval or token claim | Confirmed design/current permission behavior |
| Approval | Human decision required for a permitted risky action | `ncn-agents` execution | Permission | Confirmed design |
| MCP tool | Governed Model Context Protocol capability available to an agent | `ncn-agents` tool boundary; domain owner for effect | Direct DB access | Confirmed design; integrations deferred |
| Projection | Rebuildable cache/read/search representation | Consumer context | System of record | Confirmed architecture rule |

## Naming Rules

- Canonical current logical service names are `ncn-authz`, `ncn-pms`, and `ncn-agents`.
- UI may use Russian labels; contracts retain canonical English terms.
- Wire DTOs use `snake_case`; current frontend models use `camelCase`.
- Externally addressable entities use stable UUIDs; timestamps are UTC ISO 8601 and business dates are `YYYY-MM-DD`.
- Future services or integrations are not named as current owners until they enter development.
