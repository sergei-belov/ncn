# ncn-pms Service Contract

## Executive Contract

`ncn-pms` provides permission-aware project and work management. It consumes the common persisted User/ProjectUser actor decision from `ncn-authz`, then enforces PMS project, archive, reference, and mutation rules. It exposes stable HTTP resources to the current frontend and a future owner API/MCP boundary to `ncn-agents`.

## Evidence and Status

| Topic | Status | Statement | Evidence/rationale |
|---|---|---|---|
| Core behavior | Confirmed | Project, board, state, work-item, epic, and preference flows are Present | `docs_old/**`; authorized frontend/backend verification |
| HTTP API/persistence | Confirmed | `/api/v1/workspaces/{workspace_slug}/projects...` and `pms_*` models are Present | FastAPI routers and SQLAlchemy/Pydantic models inspected 2026-08-13 |
| Identity and project authorization dependency | Confirmed current behavior | Common `ncn-authz` resolves persisted User and ProjectUser role; PMS consumes the actor and rechecks its domain action | User authorization contract and authorized backend verification, 2026-08-14 |
| Membership administration | Open | Creator bootstrap is Present, but invite/remove/role administration and external OIDC user provisioning are not specified | Authorization feature open questions |
| Schema readiness | Open | User and project-user mappings are Present; checked-in migration readiness is not established | Authorization feature data contract |
| Domain events | Open/deferred | No current asynchronous consumer is confirmed | Agent MVP does not require Kafka for first happy path |

## Responsibility and Ownership

Own projects, workflow stages, board version/preferences, work items and assignees, and epics and assignees. Only PMS may enforce or change project-work invariants. `ncn-authz` owns User/ProjectUser identity and role policy; current physical colocation does not transfer that ownership. Exclude authorization truth, agent configuration, Sessions, Runs, plans, tools, approvals and agent memory/artifacts.

## Actors, Systems, and Permissions

| Actor/system | Goal | Allowed | Forbidden/constrained |
|---|---|---|---|
| Persisted authenticated user | Enter one stable application identity | Read own public profile, list related projects, create a project and become admin | Token claims and path values cannot grant project access |
| Admin | Configure project/workflow and manage work | Project, stage, card, epic mutations granted by policy | Archived project is read-only; owner invariants still apply |
| Member | Execute day-to-day work | Authorized card/epic reads and mutations | No project/stage/agent administration without policy |
| Viewer | Inspect project status | Authorized reads | No mutation controls or write API access |
| Frontend | Render the current user experience | Call PMS resource ports/API and cache projections | Cannot write PMS tables or reinterpret permissions |
| Agent | Read or mutate work through approved tools | Operations explicitly allowed by backend/tool policy | No database access or cross-project scope |
| OIDC edge | Verify external identity before backend ingress | Verify issuer/audience/signature/time/subject and forward bearer identity | Cannot grant project role or action permission |

## Feature Inventory

| Feature | Purpose | Status | Contract |
|---|---|---|---|
| Project work management | Manage projects, boards, stages, cards, epics, preferences | Active | [feature](features/project-work-management.md) |

## Requirements

| ID | Requirement | Scenario | Acceptance |
|---|---|---|---|
| PMS-REQ-001 | List/search/create/update/archive/restore projects within workspace scope. | SCN-001 | Returned project and list reflect the mutation; archive is read-only |
| PMS-REQ-002 | Provide board columns, filters, preferences, quick create, and exact card movement. | SCN-001 | Order persists and canonical board/version is returned |
| PMS-REQ-003 | Provide work-item and epic CRUD, membership, dates, assignees, priority, state, and progress. | SCN-001/002 | Owner invariants and date rules hold |
| PMS-REQ-004 | Provide stage CRUD/default/reorder and require transfer before deleting a populated stage. | SCN-002 | Exactly one default remains; no work item is orphaned |
| PMS-REQ-005 | Enforce project scope, permission, archive state, validation, and optimistic concurrency on every mutation. | SCN-001/002 | Unauthorized/stale mutations fail without partial state |
| PMS-REQ-006 | Require the common `ncn-authz` persisted actor/project-role result before every protected PMS operation and recheck PMS domain permission. | SCN-003 | Token/config grants cannot elevate; authz plus PMS guard tests pass |
| PMS-REQ-007 | Preserve the common persisted `user.id` in PMS actor context and safe domain logs. | SCN-003 | PMS actor/log identity matches the authz decision |
| PMS-REQ-008 | Use JSON domain IDs and expected-version fields for duplicate and concurrency behavior; require no custom request metadata headers. | SCN-001/002 | OpenAPI and mutation contract tests pass with standard bearer and JSON only |

## Invariants

| ID | Invariant | Enforcement | Verification |
|---|---|---|---|
| PMS-INV-001 | Every stage, work item, epic, preference, defect, and gate is scoped to exactly one project. | Repository/manager constraints | Cross-project API tests |
| PMS-INV-002 | A work item belongs to one stage and at most one epic; an epic deletion detaches, not deletes, its cards. | FK/transaction logic | Delete/link tests |
| PMS-INV-003 | A project has exactly one default stage; the default or sole stage cannot be deleted. | Unique constraint and manager guard | Concurrent stage tests |
| PMS-INV-004 | Card/stage ordering and `board_version` change atomically; stale movement cannot overwrite canonical order. | Transaction and version checks | Concurrency tests |
| PMS-INV-005 | `start_date <= due_date` when both are set. | Validation and DB check | API/DB constraint tests |
| PMS-INV-006 | Archived projects expose no effective mutation. | Permission/manager guard and UI state | API plus UI tests |
| PMS-INV-007 | Agent configuration in `pms_agents` is transitional physical data and not PMS business ownership. | Architecture/data decision | Ownership review |
| PMS-INV-008 | PMS never treats tokens, authentication settings, or client permission projections as authority; it consumes `ncn-authz`. | Common authz dependency plus PMS manager | Extra claims/config/client fields cannot change PMS authorization |
| PMS-INV-009 | Every protected PMS request and domain log preserves the persisted actor UUID supplied by `ncn-authz`. | Router/dependency/manager | Cross-layer identity-consistency tests |

## State and Lifecycle

Projects are active or archived and may be restored. Work items and epics move among ordered stages; their own lifecycle derives from stage group unless a later feature defines another state machine. Stages may be created, renamed, recolored, regrouped, reordered, and made default; deletion requires a valid replacement and atomic transfer. Board preferences are per user/project and versioned. Deletes preserve audit/history according to future retention decisions.

## Dependencies and Constraints

PMS depends on `ncn-authz` for authenticated persisted actor and project-role decisions, PostgreSQL for PMS truth, and the current frontend. It retains domain permission/archive/reference checks. `ncn-agents` consumes the same authz boundary and may call project work only through a future permission-checked PMS API/MCP tool boundary. Kafka/outbox is deferred until a current consumer requires it.

## Security and Privacy

Every protected request first resolves a normalized bearer email to a persisted user. Every project query and mutation then validates the exact workspace/project relation and action from the stored role. Permissions returned to UI are advisory presentation inputs; backend enforcement is authoritative. Rich-text inputs are untrusted and sanitized at the presentation/serving boundary. Member details and project access are scoped. Logs and audit use persisted `user.id`, resource, action, versions, and outcome without password, bearer, or sensitive body dumps.

## Failure, Recovery, and Observability

Authentication, validation, not-found, permission, archived and conflict errors are stable and not blindly retried. Current UI snapshots matching board queries, rolls back failed optimistic movement and refetches canonical state. Create commands use client-generated identifiers; moves include a client mutation ID and expected work-item/board versions in JSON. Agent tool uncertainty is reconciled by reading canonical PMS state. Monitor latency, error/conflict rates, board moves, transaction rollbacks, rate limits and project-scope denials using persisted user identity.

## Quality Requirements

| ID | Attribute | Requirement | Verification |
|---|---|---|---|
| PMS-NFR-001 | Consistency | Project/stage/card/epic mutations are atomic and version guarded. | Transaction/concurrency tests |
| PMS-NFR-002 | Accessibility | Board and forms support keyboard use, focus/error semantics, and explicit move dialog. | Automated/manual UI audit |
| PMS-NFR-003 | Performance | Board pagination/column limits prevent unbounded payloads; production p95 is set before release. | API load test |
| PMS-NFR-004 | Compatibility | `/api/v1` changes are additive or versioned and retain stable errors. | Contract tests |
| PMS-NFR-005 | Security/operations | Authentication data cannot grant application permissions; safe logs and per-user rate tracking use persisted user UUID. | Negative authorization and log/rate-key tests |

## Assumptions

| Assumption | Rationale | Validation | Impact if false |
|---|---|---|---|
| Present shared backend behavior will be preserved when boundaries evolve. | Current frontend relies on it. | Compatibility suite | API and migration contracts change |
| Any persisted user may create a project under a supplied workspace slug and becomes its admin. | Configurable create permission was explicitly removed. | Product acceptance of SCN-003 | A separate workspace membership model becomes necessary |

## Open Questions

| Question | Impact | Owner/trigger | Blocking |
|---|---|---|---|
| Who provisions, disables, and reconciles OIDC identities in `users`? | Production authentication and revocation | Identity/platform owner | Yes for production OIDC |
| What is the authoritative workspace membership source if creation later becomes workspace-restricted? | Project creation policy | Architecture/access decision | No for current persisted-user rule; yes for a restricted policy |
| Who administers project membership and roles after creator bootstrap? | Multi-user collaboration | Product/access owner | No for creator-only slice |
| Is a PMS event required for the first agent Run, or is the owner API sufficient? | Determines Kafka/outbox scope | First Run scenario | No for current HTTP slice |
| What retention and deletion rules apply to archived projects and current work data? | Privacy/storage/recovery | Product/data owner | Yes for production |

## Service Acceptance

Acceptance requires resolving every protected request to one persisted user; database-backed role and route-guard tests; permission-aware project CRUD/archive/restore; board load/filter/preference and exact optimistic movement with rollback; work-item/epic CRUD and linkage; stage default/reorder/delete-with-transfer; JSON-based version/command identity behavior; date/project-scope/concurrency constraints; accessible desktop/mobile states; API compatibility; schema provisioning evidence; and PostgreSQL backup/restore.

## Traceability

Use [scenarios](scenarios.md), [features](features/README.md), [technical design](design/technical.md), [UI/UX](design/ui-ux.md), [API](interfaces/api.md), [events](interfaces/events.md), [models](data/models.md), [tables](data/tables.md), and [decisions](decisions.md).
