# ncn-pms Technical Design

## Context and Status

**Present:** Vue FSD frontend resource ports with mock/HTTP adapters; FastAPI routers/managers/repositories; Pydantic DTOs; SQLAlchemy/PostgreSQL PMS tables; persisted User/ProjectUser authorization; JSON version inputs for guarded operations; and board movement. Independent deployment, migration readiness, a separate authorization service, and Kafka events are not claimed. Evidence combines authorized 2026-08-13 inspection with the explicitly requested authorization verification on 2026-08-14.

## Components and Responsibilities

| Component/boundary | Status | Responsibility | Inputs/outputs | Owns |
|---|---|---|---|---|
| Vue PMS slices | Present | Routes, queries, forms, board interactions, optimistic cache | Resource ports/domain models | Browser state only |
| FastAPI routers/managers | Present | HTTP validation, permission/business orchestration | `/api/v1/...` | PMS commands/queries |
| Repositories/SQLAlchemy | Present | Scoped transactional persistence | DTOs/rows | PMS tables |
| Mock browser adapter | Present | Standalone demo behavior | Same resource ports | Demo `localStorage`, non-authoritative |
| `ncn-authz` common layer | Present external logical owner | Resolve persisted User/ProjectUser, evaluate PMS action, log/rate-limit by user UUID, produce actor | Bearer/path/session → actor/decision | User/ProjectUser/policy, not PMS state |
| PMS actor/domain guard | Present | Require authz actor, recheck scope/current relation/action, archive and domain invariants | Actor/project/action → PMS command/query | PMS authorization consumption and domain denial |

## End-to-End Flows

Identity/project-role flow is owned by `ncn-authz`: bearer → persisted User → exact ProjectUser → role/action actor. PMS receives that actor; its manager repeats scope/current relation/action plus archive/reference checks before domain work.

Reads: route → resource adapter → PMS API → persisted actor/permission check → manager → scoped repository → DTO → query cache. Guarded mutations add expected versions and client-generated domain/command UUIDs in JSON, commit owner state atomically and return canonical representation. Board movement optimistically updates all matching UI query variants but owner response remains canonical.

## State Ownership and Consistency

PostgreSQL PMS tables are authoritative for project work. Authz `users` and `project_users` are authoritative for actor/role and are consumed through the current common layer; there is no token-role fallback. A current shared transaction coordinates project creation, authz creator admin membership, default stage, sequence numbers, board version, ranks, and epic links. UI/TanStack Query and mock storage are derived or demo state. JSON expected entity/board versions prevent lost updates where defined. Agent calls reconcile from the owner API.

## Dependencies and Integrations

`ncn-authz`, PostgreSQL, the current frontend and future `ncn-agents` PMS tools. Synchronous calls use bounded timeouts; an authz denial/failure stops PMS work, and agent tool failure never changes committed owner truth unless the PMS command completed.

## Security Boundaries

Require the common authz actor and decision before PMS routing/manager work. Recheck workspace slug, project/resource relationship, current relation/action, and archive/domain state. Never trust token permission claims or UI permission flags. Sanitize/escape rich text. PMS logs preserve persisted `user.id` and omit bearer/password/content/member-sensitive bodies. Tools receive only requested resource fields and no repository access.

## Failure Isolation and Recovery

Use local transactions for related owner writes, including project plus creator admin relation. Authentication, validation, permission and conflict failures are non-retryable without a state change. Client-generated resource and command UUIDs support duplicate safety. UI rollback/refetch recovers optimistic failures. Agent tool calls use owner-defined command identity and canonical lookup for reconciliation. PostgreSQL backup/restore is required; frontend projections are rebuilt.

## Observability and Operations

Expose liveness/readiness, HTTP latency/error, DB pool/transaction, authentication failure, user rate limit, conflict/permission denial, board move/rebalance and agent-tool reconciliation signals. Authorized logs include persisted user UUID, method, safe path, scope, project role, operation, resource/version and safe outcome. Planned asynchronous agent flows use their domain Run/node/tool identifiers rather than synchronous request-tracking metadata.

## Performance and Scale

Current APIs cap common pages at 100 and board items per column at 50. Index workspace/project, archive, state, due date, epic, user, and ordering queries. Production p95, concurrency, project/card volume, rank rebalance, and history retention thresholds remain Open and must be load-tested.

## Runtime, Compatibility, and Evolution

Present runtime is a shared FastAPI backend plus Vue SPA. Preserve `/api/v1`, the authz actor/role semantics, stable errors, and JSON version/command fields during extraction. Database changes use backward-compatible migration/backfill/verification/rollback. No consumer receives direct tables. Independent authz deployment requires an owner interface, failure model, and project-bootstrap consistency contract before in-process calls can be removed.

## Alternatives

Token/config permission grants, direct agent/database writes and frontend-owned server truth are rejected. A custom repository method for a simple email filter is rejected in favor of the generic repository. Browser mock mode remains a demo adapter, not production authority.

## Traceability

PMS-REQ-001..008; PMS-INV-008/009; SCN-001..003; FEAT-001 plus FEAT-004 consumer; API/MODEL/TABLE-PMS; API/MODEL/TABLE-AUTHZ; DEC-PMS-001..004; project DEC-002/004/007.
