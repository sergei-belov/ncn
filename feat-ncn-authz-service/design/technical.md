# Technical Design

## Context and Current State

**Present NCN:** `backend/models/sqlalchemy/users.py` and `project_users.py` persist application Users and project roles. Current backend authentication/dependency code resolves a User by normalized email, provides actor context, and applies role checks inside the shared deployment. `docs/services/ncn-authz/**` describes the intended logical authorization owner. There is no verified independent `ncn-authz` deployment, workspace-access administration, service-restriction layer, or production SSO provisioning flow yet.

This plan uses only NCN repository contracts, documentation, and current implementation as evidence. The requested DATA-002 workspace membership and DATA-004 service restriction are Planned additions, not imported external contracts.

## Proposed Design

Build `ncn-authz` as the authority for DATA-001..004 and a policy decision point using the repository's established FastAPI/Pydantic/SQLAlchemy layers. SSO provides only allowlisted OIDC identity claims and resolves/provisions a User by verified normalized email. Workspace/project roles are created through explicit management APIs or PMS project bootstrap and are the sole authorization truth.

The NCN frontend calls API-001/003/004/006 directly through Traefik/oauth2-proxy. Internal services call API-002, and PMS calls API-005, with workload authentication. `ncn-authz` does not aggregate frontend data, proxy domain APIs, or own workspace/project records.

## Components and Responsibilities

| Component | Status | Responsibility | Inputs → outputs | Owner |
| --- | --- | --- | --- | --- |
| Trusted SSO identity adapter | Planned | Validate accepted edge carrier, canonicalize verified email, resolve/create active User | Edge identity → DATA-001/API-001 | `ncn-authz` |
| User repository/manager | Present concept, planned service ownership | Maintain stable User and local-development credential compatibility | Identity/local commands → DATA-001 | `ncn-authz` |
| Workspace access repository/manager | Planned | CRUD DATA-002 with actor ceiling, scope validation, version, and last-owner guards | API-006 → canonical membership | `ncn-authz` |
| Project/service access repository/manager | Project base Present; expansion Planned | CRUD DATA-003/004 with ceiling, inheritance, version, and last-admin guards | API-003/004/005 → canonical access | `ncn-authz` |
| Named policy registry/evaluator | Planned from current checks/docs | Map registered action/scope to persisted roles and return fail-closed decisions | API-002 + DATA-001..004 → allow/deny | `ncn-authz` |
| PMS scope adapter | Planned | Validate opaque workspace/project relationships and service IDs without copying domain state | Authz command scope → owner validation | Authz adapter / PMS owner |
| Browser API layer | Planned | Session and access-management routes, origin/CSRF, validation, pagination, safe errors | API-001/003/004/006 | `ncn-authz` |
| Internal API layer | Planned | Workload authentication, allowlists, timeouts, bootstrap semantics | API-002/005 | `ncn-authz` |
| Compatibility/shadow adapter | Planned | Preserve current consumers and compare old/new decisions during extraction | Current calls → active + shadow observations | Backend/authz owners |
| Structured telemetry | Planned | Emit privacy-safe decision/mutation logs and metrics | Operations → Loki/Prometheus | `ncn-authz` / platform |

## End-to-End Flows

### SSO identity resolution

```text
Browser → Traefik → oauth2-proxy
  → trusted identity carrier with verified email/name
  → ncn-authz canonical email validation
  → lookup-or-create DATA-001 in PostgreSQL
  → read bounded DATA-002/003 scope summary
  → API-001 response to frontend
```

Only `email`, `email_verified`, and optional `name` are accepted from the OIDC carrier. Identity resolution never calls membership managers. The exact edge encoding and bypass proof remain blocking Open items.

### Authorization decision

```text
Consumer workload → API-002 authentication/allowlist
  → validate registered action and scope shape
  → active User + workspace/project membership lookup
  → optional service restriction (otherwise inherit project role)
  → named role/action evaluation
  → allow/deny + stable reason + policy version
```

The decision uses committed PostgreSQL state on each MVP request. Unknown action, missing/invalid state, timeout, or database error fails closed.

### Workspace access administration

The frontend calls API-006 directly. The browser layer validates identity, same-origin/CSRF, and input; the workspace manager validates PMS scope, actor membership/ceiling, target User, expected version, and last-owner coverage. It mutates DATA-002 in one transaction, then emits structured telemetry.

### Project and service access administration

API-003/004 follows the same browser boundary. The manager validates PMS project/workspace relationship, actor ProjectUser, target User, role ceiling, last-admin coverage, and service inheritance. DATA-003 or DATA-004 changes commit atomically. A parent demotion with incompatible restrictions conflicts unless the command explicitly produces a valid final set.

### Project bootstrap

PMS calls API-005 with its workload identity, project/workspace IDs, and creator User UUID. The manager validates authoritative scope, then `PUT` creates or returns the unique creator admin DATA-003. PMS exposes the project as ready only after success or follows its accepted compensation contract.

## State Ownership and Consistency

- PostgreSQL in `ncn-authz` is authoritative for DATA-001..004. Consumer-local caches/copies are not authoritative and no decision cache is introduced in the MVP.
- PMS is authoritative for workspace/project existence and hierarchy. Authz stores opaque IDs and validates them through the accepted owner contract; it does not cross-database foreign-key business rows.
- Each identity insert and access mutation is one local database transaction. Unique constraints and optimistic versions handle duplicates/concurrency.
- Last-owner/admin checks and the associated write share a locking/serializable strategy proven by concurrency tests.
- Project creation is a cross-service workflow without a distributed transaction; visibility/compensation belongs to the PMS contract.
- No identity-link, durable audit, command-receipt, or decision table is created for the MVP.

## Dependencies and Integration

| Dependency | Direction | Contract | Failure behavior |
| --- | --- | --- | --- |
| Traefik + oauth2-proxy | Edge → authz | Authenticated route, verified email carrier, spoofed-header removal | Reject untrusted identity; readiness/cutover blocked without trust proof |
| PostgreSQL | Authz → database | DATA-001..004 and transactional constraints | Fail closed; writes roll back; readiness fails on schema/connectivity defect |
| `ncn-pms` | Authz ↔ PMS | Workspace/project/service validation, lifecycle, creator bootstrap | Mutation rejected/503; no copied business state; PMS keeps project non-ready |
| NCN frontend | Browser → authz | Direct API-001/003/004/006, stable errors, CSRF | Read-only/degraded safe UI; no optimistic access success |
| Consumer services | Services → authz | API-002 workload auth, registered action schemas, bounded timeout | Fail protected operation closed; bounded retry only |
| Loki/Prometheus | Authz → platform telemetry | Safe structured logs and aggregate metrics | Core decision remains available; telemetry failure surfaced/alerted without leaking secrets |

Kafka and Temporal are not on synchronous decision or membership paths. They may be introduced later only for an explicitly approved lifecycle/event requirement.

## Security Boundaries

- Network policy and ingress configuration must make the browser authz route non-bypassable and overwrite/remove user-supplied identity headers.
- Email must be provider-verified; display name is non-authoritative. Tokens and full OIDC payloads do not enter role evaluation or persistence.
- Browser writes require same-origin/CSRF protection; internal interfaces require authenticated workload identity and least-privilege allowlists.
- Managers re-authorize every mutation and never trust UI-hidden actions, caller-supplied roles for the actor, or copied effective decisions.
- Role values, scope IDs, service IDs, search/page size, and strings are allowlisted/bounded.
- Password hashes remain confined to DATA-001/local verification. No secret or raw provider payload appears in API responses or telemetry.

## Failure Isolation and Recovery

- Repository or policy-registry failure cannot return allow. Transaction failure cannot partially change access.
- PMS validation failure affects only the requested mutation/bootstrap, not existing access or unrelated checks.
- Browser ambiguity is resolved by canonical GET before retry. API-005 identical `PUT` converges without a receipt table.
- Shadow mismatch blocks cutover and alerts while the active legacy path remains unchanged.
- During rollout, reader routing can return to the compatible legacy path. One write authority prevents divergent membership state.
- Data repair requires inventory/report review; automated repair never creates a role not derivable from existing valid state or explicit admin intent.

## Observability and Operations

Structured decision logs contain timestamp, correlation ID, authenticated consumer, User UUID when resolved, safe workspace/project/service references, action, effective role, allow/deny reason, policy version, latency, and active/shadow mode. Mutation logs add actor/target UUID, operation, before/after role, version, and result. They are operational records in Loki, not an immutable domain audit ledger.

Metrics cover latency/error by API, identity resolve/create/collision/disabled, allow/deny reason, unknown action, mutation success/conflict, last-owner/admin blocks, invalid service elevation, data-quality defect, shadow mismatch, database health, and bootstrap drift. Alerts fire on unauthorized parity mismatch, identity collision, invalid role/data, sustained unavailability, or missing privileged coverage.

Liveness proves process execution. Readiness proves PostgreSQL, expected schema, policy registry, workload-auth configuration, and required edge/dependency configuration. Runbooks cover SSO trust failure, email collision, last-owner/admin recovery, parity mismatch, database restore, PMS bootstrap drift, and consumer rollback.

## Performance and Scale

- API-002 performs indexed User/membership lookups and one optional restriction lookup; it never scans OIDC payloads or business-domain rows.
- Member lists are cursor-paginated and capped. Scope, role, action, and string inputs are bounded.
- User resolution uses one unique canonical-email lookup/insert and bounded scope summaries.
- Exact traffic, cardinality, latency SLO, pool sizing, and rate limits remain Open pending inventory and load tests.
- No cache is added until invalidation, revocation, and availability tradeoffs have a separate accepted decision.

## Rollout and Compatibility

1. Inventory current User/ProjectUser data and action semantics; introduce compatible repositories/DTOs and shadow evaluator without traffic change.
2. Enable SSO User resolution behind the proven edge; confirm OIDC identity input never alters roles.
3. Run API-002 in shadow, reconcile mismatch, then cut consumers over by allowlist with rollback routing.
4. Enable direct workspace/project access UI/API for pilot scopes after CSRF, guards, concurrency, and accessibility tests.
5. Enable PMS bootstrap and move physical write authority only after its visibility/compensation contract passes.
6. Observe parity and operational signals; remove legacy paths only in a later explicit cleanup.

Schema changes are expand/contract and backward-compatible through the observation window. User UUIDs and valid ProjectUser roles are never rewritten for routing rollback.

## Alternatives

- **Keep authorization in every consumer:** rejected because it preserves duplicated policy and weakens revocation consistency.
- **Derive access from SSO attributes:** rejected because SSO supplies identity only and persisted NCN roles must be authoritative.
- **Add subject/issuer identity links now:** deferred because normalized verified email is the chosen MVP key; revisit when provider/email-change evidence requires it.
- **Add durable audit and command receipts now:** deferred because operational structured logs, uniqueness, versions, and canonical-read recovery meet the MVP boundary.
- **Route browser calls through a frontend aggregation service:** rejected because no such service exists and `ncn-authz` owns its browser-facing access APIs.

## Traceability

| Component / flow | Requirements / scenarios | Interfaces / data | Decisions / delivery |
| --- | --- | --- | --- |
| SSO identity adapter | REQ-001/002/010; SCN-001 | API-001/007; DATA-001 | DEC-002/003/006; SLICE-002 |
| Workspace access manager | REQ-004/006/010; SCN-003 | API-006; DATA-002 | DEC-001/005/006; SLICE-004 |
| Project/service access manager | REQ-005/006/009/010; SCN-004/006 | API-003/004/005; DATA-003/004 | DEC-001/004/005/006; SLICE-004/005 |
| Policy evaluator | REQ-003/005/007/010; SCN-002/005 | API-002; DATA-001..004 | DEC-002/004/005; SLICE-003 |
| Compatibility/extraction | REQ-008; SCN-005 | API-002/005; DATA migration | DEC-004; SLICE-001/003/005 |
