# NCN Project Contract

Owner: NCN development team  
Last reviewed: 2026-08-14  
Status: Draft current-development specification for common `ncn-authz`, `ncn-pms`, and `ncn-agents` logical services.

## Executive Contract

NCN currently consists of a common authorization service layer, an authoritative project-management service, and an in-development agent service with one project coordinator and specialized workers. The implemented slice resolves persisted users/project roles and manages projects, boards, stages, work items, epics and agent configuration. The current agent-development contract adds durable Sessions/Runs, controlled tools, memory, approvals, budgets and auditable results without moving PMS or authorization truth into the agent service.

## Evidence and Decision Status

| Topic | Status | Statement | Evidence or rationale |
|---|---|---|---|
| Current services | Confirmed | `ncn-authz`, `ncn-pms`, and `ncn-agents` are the current logical services; authz is physically a shared backend layer | User correction/clarification; repository architecture |
| Common authorization | Confirmed | Persisted User/ProjectUser role supplies the actor/policy used by all services; token/config grants and custom synchronous request metadata are excluded | Explicit user request and authorized backend verification, 2026-08-14 |
| PMS implementation | Confirmed | Vue/FastAPI/SQLAlchemy cover project, board, state, work-item and epic behavior | Authorized implementation inspection |
| Agent configuration implementation | Confirmed | Vue/FastAPI/SQLAlchemy cover agent config and worker status | Authorized implementation inspection |
| Agent execution | Confirmed design; Planned implementation | Coordinator/worker, Session/Run, Temporal, MCP, memory, Approval and audit are the active design contract | `contracts/agents/02-invariants/**` |
| Physical service separation | Confirmed | Microservice configurations have the same backend. In the future them will be divided using Debezium with the same code structure and with shared DB models |
| Future integrations | Confirmed as deferred direction | GitLab, procurement, analytics and other MCP-connected capabilities may be added later | User brief; not current service scope |

## Problem and Audience

Teams need reliable project tracking and bounded AI assistance in the same project context. The solution must identify one persisted actor consistently and prevent cross-project access, hidden side effects, duplicated business state, non-reproducible Runs and unbounded cost. Actors are authenticated users, project admins, members, viewers/approvers, the coordinator, workers, and platform operators.

## Outcomes and Success Measures

| ID | Outcome | Measure | Target or method |
|---|---|---|---|
| OUT-001 | Project work remains consistent and usable | Core project/board/card/epic/stage scenarios pass | `ncn-pms` acceptance |
| OUT-002 | Agent team configuration is protected and reproducible | One coordinator, safe worker lifecycle, version conflict and snapshot tests pass | `ncn-agents` configuration acceptance |
| OUT-003 | A coordinated request is durable, bounded and auditable | Run survives restart, blocks unauthorized effects, handles approval/cancel, and returns structured result | `ncn-agents` execution acceptance |
| OUT-004 | Every service applies one current database-backed authorization policy | Cross-service identity/role/action matrix and telemetry identity agree | `ncn-authz` acceptance |

## Scope

### In Scope

- Projects, project-facing permissions, workflow states, board preferences, work items, epics, ordering, archive/read-only behavior and their current UI/API/persistence.
- Common persisted User/ProjectUser identity, actor dependencies, role-to-service-action policy, local/current-user auth operations, and persisted-user logging/rate identity.
- Project-scoped coordinator and workers, current configuration/status UI/API/persistence.
- In-development Session, Message, Run, immutable snapshots, RunPlan/revisions, model/tool execution, Approval, memory/RAG, artifacts, budgets/usage, cancellation, result and audit contracts inside `ncn-agents`.
- `ncn-agents` access to PMS only through permission-checked owner API/MCP tools.

### Out of Scope

- Separate memory, notification, portal aggregation, PLM, procurement, analytics or integrations services in the current documentation; independent deployment of logical services is not claimed.
- Direct agent access to PMS tables; model-decided permissions; hidden side effects; arbitrary worker nesting or plan loops.
- Claims that Planned agent execution or infrastructure is already implemented.

### Deferred

- MCP integrations with GitLab, procurement, analytics and other external/domain services.
- Additional business domains and any future service decomposition.
- No-code workflow designer, arbitrary agent handoff, OAuth user MCP, advanced RAG ACL/reranking and complex billing.

## Actors and Permissions

| Actor/system | Goal | Allowed | Forbidden or constrained |
|---|---|---|---|
| Project admin | Configure project/workflow and agents | Authorized PMS and agent configuration mutations | Cannot bypass backend permissions or disable/archive coordinator |
| Persisted authenticated user | Establish one NCN actor | Read own public profile; use eligible collections; create a project and become admin | Token/config/path alone cannot grant project access |
| Project member | Manage work and request agent help | Authorized cards/epics and future Session/Run actions | No administration without permission |
| Viewer/approver | Read or decide eligible risky action | Authorized reads; future approval decision | No mutation from route access; approval cannot override deny |
| Coordinator | Plan/delegate/aggregate a Run | Invoke configured workers and allowed tools | Cannot bypass policy/limits or change completed/running nodes |
| Worker | Perform bounded specialization | Use delegated context and assigned tools/memory | Cannot invoke workers, create Run, change plan/scope/permission |
| Platform operator | Operate backend/workers/data | Diagnose/recover under operational policy | No implicit project mutation or secret disclosure |
| Common authz layer | Resolve identity and project action | Read current User/ProjectUser and return actor/decision | Cannot own consumer domain state or elevate from token/config |

## Core Journeys

| Journey | Actor | Services | Result | Important failure/recovery |
|---|---|---|---|---|
| Resolve and authorize actor | Authenticated user | Edge/local auth → `ncn-authz` → consumer | One persisted UUID and current role/action decision | Reauthenticate/provision on `401`; role/data change on `403` |
| Manage project work | Admin/member/viewer | `ncn-pms` | Authorized project/card/epic/stage state remains consistent | Version conflict rolls back optimistic UI and reloads owner state |
| Configure agent team | Admin | `ncn-agents` with PMS project reference | One active coordinator and versioned workers | Stale/forbidden/protected transition fails atomically |
| Execute assisted request | Member | `ncn-agents` → `ncn-pms` tool when needed | Durable Run returns structured result/effects/usage/audit | Retry by class, wait for input/approval, cancel, reconcile unknown effect |

## Capability and Service Inventory

| Capability | Owning service | Consumers | Status | Contract |
|---|---|---|---|---|
| Database-driven authorization | `ncn-authz` | All backend services/frontends | Common source Present; migration/extraction Open | [contract](services/ncn-authz/README.md) |
| Project work management | `ncn-pms` | Frontend and `ncn-agents` tools | Present core slice | [contract](services/ncn-pms/README.md) |
| Agent configuration | `ncn-agents` | Frontend and future Runs | Present | [contract](services/ncn-agents/README.md) |
| Coordinated agent execution | `ncn-agents` | Frontend; PMS via tools | In development/Planned implementation | [contract](services/ncn-agents/features/coordinated-agent-execution.md) |

## Requirements

| ID | Requirement | Owner | Acceptance |
|---|---|---|---|
| REQ-001 | Provide permission-aware project, board, work-item, epic and stage management with archive/read-only and safe concurrency. | `ncn-pms` | [PMS acceptance](services/ncn-pms/spec.md#service-acceptance) |
| REQ-002 | Maintain exactly one active coordinator and configurable project-scoped workers with versioned updates. | `ncn-agents` | [Configuration feature](services/ncn-agents/features/agent-configuration.md) |
| REQ-003 | Execute each request as a durable, bounded, permission/approval-controlled Run with immutable snapshot and structured result. | `ncn-agents` | [Execution feature](services/ncn-agents/features/coordinated-agent-execution.md) |
| REQ-004 | Preserve exclusive PMS ownership: agents use PMS API/MCP and do not copy or directly write project state. | Both | Cross-service tool/API and ownership tests |
| REQ-005 | Resolve one persisted User and enforce current ProjectUser role through the common authorization layer before protected service work. | `ncn-authz`; all consumers | [Authz acceptance](services/ncn-authz/spec.md#service-acceptance) |

## Invariants

| ID | Invariant | Enforcement owner | Verification |
|---|---|---|---|
| INV-001 | PMS PostgreSQL data is project-work truth; frontend cache, mock data, memory/vector results and agent context are non-authoritative. | `ncn-pms`; consumers | Ownership/recovery tests |
| INV-002 | Persisted actor UUID and workspace/project scope propagate through synchronous services; Run/tool/event flows add their own domain lifecycle and causation IDs. | All services | Cross-service scope/audit tests |
| INV-003 | A started Run uses an immutable config snapshot and stable replay identifiers. | `ncn-agents` | Edit/restart test |
| INV-004 | Model output cannot grant permission or directly cause a side effect; backend validation and Approval policy control explicit tool nodes. | `ncn-agents` | Adversarial tool tests |
| INV-005 | Worker topology, retry/idempotency, plan revision, secret and bounded-execution invariants in the agent contract remain mandatory. | `ncn-agents` | Execution acceptance suite |
| INV-006 | Authentication claims/settings never grant application permissions; User/ProjectUser and common policy are the current authorization authority. | `ncn-authz`; consumers | Claim/config tampering and role matrix tests |

## Quality Requirements

| ID | Attribute | Requirement | Verification |
|---|---|---|---|
| NFR-001 | Security | Deny cross-project/unauthorized mutations and keep secrets out of API/log/model context/vector index. | Integration/security tests |
| NFR-002 | Reliability | Owner mutations are atomic/versioned; Runs recover/cancel; unsafe unknown external effects are reconciled. | Concurrency/restart/timeout tests |
| NFR-003 | Accessibility | Current and planned UI supports keyboard, focus/errors, text statuses, responsive details and non-DnD movement. | Automated/manual audit |
| NFR-004 | Compatibility | Current `/api/v1` behavior survives backend/service extraction; breaking changes are versioned. | Contract tests |
| NFR-005 | Operations | Synchronous logs/metrics/audit use persisted User UUID; asynchronous execution uses Run/node/tool/event domain IDs; exact production thresholds are set before release. | Dashboard/incident drill |

## Dependencies and Constraints

Current code uses Vue 3/TypeScript/Vite and FastAPI/PostgreSQL layers. The [authoritative technology stack](architecture/system.md#technology-stack) defines the approved shared platform components and their roles. Agent execution design requires Temporal, model adapters, Qdrant for derived RAG and MinIO/S3 for artifacts, with MCP as the domain-tool boundary. Kafka is the approved event bus but is not required for the first Run happy path; a current flow should use it only when a confirmed asynchronous consumer exists. An approved technology choice must not be marked Present without deployment or implementation verification.

## Assumptions

| Assumption | Rationale | Validation | Impact if false |
|---|---|---|---|
| `ncn-authz`, `ncn-pms`, and `ncn-agents` remain the current logical service contracts. | User clarification and current registry | Development ownership review | Service registry changes when another capability starts |
| The current Vue resource behavior remains compatible as backend boundaries evolve. | Existing implemented UI | Contract suite | API and frontend docs change |
| One coordinator with non-nested workers is sufficient for first Run. | Agent v2 contract | First vertical scenario | Agent architecture revision |

## Open Questions

| Question | Impact | Owner/trigger | Blocking |
|---|---|---|---|
| What is the first agent Run use case, its 1–2 PMS/MCP tools, worker, RAG corpus and approval-gated effect? | Defines end-to-end execution acceptance | Product before execution implementation | Yes |
| How will current `pms_agents` storage become `ncn-agents`-owned while preserving API/IDs? | Resolves logical/physical ownership | PMS/agents data owners | Yes for separation |
| What are Run message-concurrency, model/fallback/budget, limits, retention, p95, RPO/RTO? | Product/operations semantics | Agent/platform owners | Yes before production |
| Who provisions/reconciles OIDC Users and administers ProjectUser roles? | Identity and collaboration lifecycle | Identity/authz/product owners | Yes for production/multi-user management |
| When and how does common `ncn-authz` become an independent deployment without splitting policy/data truth? | Availability, migration, project bootstrap consistency | Architecture/authz/PMS | Yes before extraction |

## Project Acceptance

Current implemented scope is accepted when common authz, PMS, and agent-configuration criteria pass with verified identity/role, UI/API/data consistency, and standard bearer-plus-JSON transport. The current development target is accepted when the selected Session/Run scenario also passes snapshot/restart, permission/Approval, worker/tool, memory, cancellation, duplicate/reconciliation, usage/audit and accessibility criteria while authz and PMS remain their respective sole owners.

## Traceability

Use [service registry](services/README.md), [feature registry](features/README.md), [architecture](architecture/system.md), [interfaces](interfaces/README.md), and [data ownership](data/README.md).
