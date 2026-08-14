# Current Project Decision Index

## Decision Inventory

| ID | Decision | Status | Owners | Affected services/contracts |
|---|---|---|---|---|
| DEC-001 | Document only `ncn-pms` and `ncn-agents` as current development services. | Accepted | Product/development | [services](../services/README.md), all project maps |
| DEC-002 | Keep PMS as sole project-work owner; agents use PMS API/MCP rather than tables/copies. | Accepted | PMS/agents | REQ-004, [architecture](../architecture/system.md) |
| DEC-003 | Use one root Temporal workflow per Run and PostgreSQL for product-visible agent truth. | Accepted design | Agents | Agent technical/data contracts |
| DEC-004 | Keep current `/api/v1` frontend behavior compatible while logical/physical service boundaries evolve. | Accepted | PMS/agents/frontend | Interface contracts |
| DEC-005 | Treat `pms_agents` as transitional physical persistence owned logically by `ncn-agents`. | Proposed migration boundary | PMS/agents/data | Agent/PMS table contracts |
| DEC-006 | Use the repository-approved shared infrastructure stack and require an explicit architecture decision for competing or baseline-excluded components. | Accepted | Platform/architecture | [Technology stack](../architecture/system.md#technology-stack), NFR-005 |
| DEC-007 | Own common persisted identity/project-role authorization in logical `ncn-authz` while the current runtime remains a shared backend layer. | Accepted transitional boundary | Authz/PMS/agents | REQ-005, INV-006, [authz decisions](../services/ncn-authz/decisions.md) |

## Open Decision Queue

| Question | Impact | Owner/evidence | Resolution trigger |
|---|---|---|---|
| First end-to-end Run, tools, RAG and approval effect | Fixes execution API/UX/permissions/acceptance | Product/agents | Before execution implementation |
| Agent-table extraction/migration and deployment shape | Resolves physical coupling | PMS/agents/data | Before independent deployment |
| Message concurrency, models/fallback/budgets/limits/retention/SLO/RPO/RTO | Product/operations behavior | Agents/platform | Before production |
| Which future MCP integration enters development first? | May add interface or service contract later | Product | When work is authorized and started |
| Authz independent API/deployment and project-bootstrap consistency | Determines extraction availability, latency and transaction boundary | Architecture/authz/PMS | Before independent deployment |
| OIDC User and ProjectUser administration lifecycle | Determines production identity and collaboration | Identity/authz/product | Before production/multi-user management |

Future GitLab, procurement, analytics or other service boundaries are not decisions or current contracts yet.
