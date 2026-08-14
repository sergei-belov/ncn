# NCN Project Map

## Snapshot

| Field | Value |
|---|---|
| Last reviewed | 2026-08-14 |
| Specification status | Draft current-development contract for three logical services in a currently shared runtime |
| Active services | `ncn-authz`; `ncn-pms`; `ncn-agents` |
| Evidence inspected | User brief/corrections and authorization example; repository instructions; existing docs/contracts; authorized narrow inspection of relevant frontend/backend surfaces, including common User/ProjectUser authorization changes |
| Implementation verification boundary | Common authz source, PMS, and agent-configuration UI/API/models plus Sessions placeholder were verified. Authz migration/independent deployment and Agent Run execution remain Open/Planned. No other service is documented as current. |

## Reading Routes

| Goal | Route |
|---|---|
| Understand the current project | [Project contract](spec.md) → [Architecture](architecture/system.md) |
| Understand common authorization | [Authz README](services/ncn-authz/README.md) → [feature](services/ncn-authz/features/database-driven-authorization.md) → [API/common interface](services/ncn-authz/interfaces/api.md) → [data](services/ncn-authz/data/models.md) |
| Understand PMS | [PMS README](services/ncn-pms/README.md) → [feature](services/ncn-pms/features/project-work-management.md) → [UI](services/ncn-pms/design/ui-ux.md) → [API](services/ncn-pms/interfaces/api.md) |
| Understand agent configuration/execution | [Agents README](services/ncn-agents/README.md) → [configuration](services/ncn-agents/features/agent-configuration.md) → [execution](services/ncn-agents/features/coordinated-agent-execution.md) |
| Review architecture and technology stack | [Architecture](architecture/system.md) → [approved shared infrastructure](architecture/system.md#approved-shared-infrastructure) → [current adoption](architecture/system.md#current-development-adoption) |
| Review cross-service boundary | [Interfaces](interfaces/README.md) → [Data](data/README.md) → both service contracts |
| Validate spec | [Documentation instructions](AGENTS.md#validation) → validator → manual ownership/status review |

## Documentation Map

| Area/service | Purpose | Authority | Status | Owner |
|---|---|---|---|---|
| Project | Scope, requirements, invariants, acceptance | [spec.md](spec.md) | Draft/current | Development team |
| Architecture | Two-service/runtime boundary and approved technology stack | [system.md](architecture/system.md) | Draft/current | Architecture |
| Product | Audience/value/language | [overview](product/overview.md), [glossary](product/glossary.md) | Draft/current | Product |
| Services | Current service catalog | [registry](services/README.md) | Current | PMS/agents owners |
| Features | Current feature catalog | [registry](features/README.md) | Current | Product/service owners |
| Interfaces/data/decisions | Cross-service current truth | [interfaces](interfaces/README.md), [data](data/README.md), [decisions](decisions/README.md) | Draft/current | Owners |
| `ncn-pms` | Project work management | [README](services/ncn-pms/README.md) | Present core | PMS owner |
| `ncn-agents` | Agent configuration and execution | [README](services/ncn-agents/README.md) | Config Present; execution in development | Agents owner |
| `ncn-authz` | Common identity and project authorization | [README](services/ncn-authz/README.md) | Common layer Present; extraction/migration Open | Authz owner |

## Service Ownership Map

| Service | Capabilities | Authoritative data | Interfaces/events | Dependencies | Forbidden ownership | Status |
|---|---|---|---|---|---|---|
| `ncn-authz` | User resolution, project membership/role, common actor/action policy, access identity | `users`, `project_users` | Present auth HTTP/common dependency; independent interface Open; no current events | OIDC edge/local auth, PostgreSQL, PMS project reference | PMS/agent domain state, provider accounts | Common layer Present; extraction Open |
| `ncn-pms` | Project, board, stage, card, epic, ordering/archive | PMS domain rows | Present PMS HTTP; future tool/event only when needed | `ncn-authz`, frontend, PostgreSQL | User/role truth; agent config/Runs/memory/tool audit | Present core |
| `ncn-agents` | Agent config, Session/Run, plans, tools, approvals, budgets, memory/artifacts for Runs | Agent config/execution rows | Present config HTTP; Planned Run/control/tool interfaces | `ncn-authz`, PMS owner API; planned Temporal/model/Qdrant/object storage | User/role and project-work truth | Config Present; execution in development |

## Runtime Entry Points

| Entry point | Kind | Owner | Location/contract | Status | Evidence |
|---|---|---|---|---|---|
| Vue bootstrap | Application | Shared frontend | `frontend/src/app/main.ts` | Present | Authorized inspection |
| Project/board/work-item/epic/settings routes | UI | PMS experience | `frontend/src/app/router/routes.ts` | Present | Authorized inspection |
| Agent list/settings routes | UI | Agents experience | `frontend/src/app/router/routes.ts` | Present | Authorized inspection |
| Project Sessions route | UI | Agents experience | `/:workspaceSlug/projects/:projectId/sessions` | Present | Placeholder only; authorized inspection |
| PMS resource API | HTTP | `ncn-pms` | `/api/v1/workspaces/{workspace_slug}/projects...` | Present | FastAPI routers verified |
| Current-user/local-auth API | HTTP | `ncn-authz` | `/api/v1/auth/...` | Present | FastAPI router/models verified 2026-08-14 |
| Common actor/project-role dependency | Internal interface | `ncn-authz` | [authz common interface](services/ncn-authz/interfaces/api.md) | Present | Dependencies/repositories verified 2026-08-14 |
| Agent configuration API | HTTP | `ncn-agents` logical owner | `/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agents...` | Present | FastAPI router/models verified |
| Session/Run/control API | HTTP/progress | `ncn-agents` | [planned contract](services/ncn-agents/interfaces/api.md) | Planned | Agent design contract |
| Run workflow/Activities | Temporal worker | `ncn-agents` | [technical design](services/ncn-agents/design/technical.md) | Planned | Agent design contract |
| PMS MCP/tool boundary for agents | API/MCP | `ncn-pms` owner | [PMS API](services/ncn-pms/interfaces/api.md) | Planned | Agent/PMS contract; exact first tools Open |

## Change Impact Map

| Capability/feature | Owner | Affected services | Scenarios | UI/UX | API/events | Models/tables | Decisions | Implementation/tests | Observability |
|---|---|---|---|---|---|---|---|---|---|
| Database-driven authorization | Authz | PMS, agents, all future services/frontends | [SCN-001..003](services/ncn-authz/scenarios.md) | [Authz UI applicability](services/ncn-authz/design/ui-ux.md) | [Authz API/common interface](services/ncn-authz/interfaces/api.md) | [Authz data](services/ncn-authz/data/models.md) | DEC-007; DEC-AUTHZ-001..004 | Common source Present; focused tests/migration evidence Open | Persisted user UUID, role/action/deny/rate |
| Project work management | PMS | Frontend, agents as tool consumer | [SCN-001..003](services/ncn-pms/scenarios.md) | [PMS UI](services/ncn-pms/design/ui-ux.md) | [PMS API](services/ncn-pms/interfaces/api.md) | [PMS data](services/ncn-pms/data/models.md) | DEC-002/004/007 | Present; tests inventoried | User UUID, API/conflict/board/domain outcome |
| Agent configuration | Agents | Frontend, PMS project reference | [SCN-001](services/ncn-agents/scenarios.md) | [Agent UI](services/ncn-agents/design/ui-ux.md) | [Agent API](services/ncn-agents/interfaces/api.md) | [Agent data](services/ncn-agents/data/models.md) | DEC-004/005 | Present; tests inventoried | Mutation/conflict/protected transition |
| Coordinated execution | Agents | PMS tool boundary, frontend | [SCN-002/003](services/ncn-agents/scenarios.md) | [Run UI](services/ncn-agents/design/ui-ux.md) | [Planned API](services/ncn-agents/interfaces/api.md) | [Planned data](services/ncn-agents/data/models.md) | DEC-002/003 | Planned implementation | Run/node/tool/approval/usage/reconciliation |

## Known Gaps

| Gap | Impact | Status | Resolution trigger |
|---|---|---|---|
| `pms_agents` is physically coupled to PMS despite agents ownership. | Migration/deployment ambiguity | Unknown | Accepted extraction plan and verified migration |
| Authz common source has no verified migration and external User provisioning/role administration is Open. | Clean deployment and production identity lifecycle incomplete | Open | Database/identity/authz owner evidence |
| Independent authz deployment/interface and project-bootstrap consistency are unspecified. | Service extraction could split policy or transaction truth | Open | Accepted architecture/data/interface decision |
| Sessions UI is placeholder; no Run backend verified. | Agent execution unavailable in present slice | Planned | Implementation evidence for FEAT-003 |
| First Run/tools/RAG/Approval scenario is not selected. | Exact execution contracts/acceptance remain open | Unknown | Product decision |
| Exact production limits, retention, SLO, RPO/RTO and model policy are open. | Production readiness incomplete | Unknown | Platform/agent decisions |
| Deployment and current-slice adoption of several approved infrastructure components are unverified. | The approved stack must not be interpreted as a Present runtime inventory. | Unknown | Explicit infrastructure or implementation verification |
| Future GitLab/procurement/analytics/MCP integrations have no current service/interface contract. | Future platform work intentionally unspecified | Planned/deferred | Development starts with named owner and evidence |
| Legacy `docs_old/**` and detailed contracts remain outside active docs. | Potential future contradiction if not retired | Planned | Owner accepts baseline and marks legacy historical |
