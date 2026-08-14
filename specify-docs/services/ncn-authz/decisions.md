# ncn-authz Service Decisions

## Decision Inventory

| ID | Decision | Status | Affected contracts |
|---|---|---|---|
| DEC-AUTHZ-001 | Use persisted User and ProjectUser role as current authorization truth. | Accepted | AUTHZ-REQ-001..006; MODEL/TABLE-AUTHZ |
| DEC-AUTHZ-002 | Own authorization logically in `ncn-authz` while the implementation remains a common shared-backend layer. | Accepted transitional boundary | Project architecture; all consumer services |
| DEC-AUTHZ-003 | Keep application grants out of authentication config/claims and custom synchronous request metadata out of the API. | Accepted | AUTHZ-REQ-006/008/009; API-AUTHZ |
| DEC-AUTHZ-004 | Use generic repository filters for simple User lookup and custom SQL only for joined authorization. | Accepted | AUTHZ-REQ-001/007; technical/data contracts |

## DEC-AUTHZ-001: Database Roles Are Authorization Truth

### Status

Accepted. Owner: platform authorization. Reviewed 2026-08-14.

### Context and Drivers

Every backend service needs the same current actor and project-role decision. Token claims can be stale, deployment settings can diverge, and copied per-service membership would create conflicting authority.

### Decision

Resolve normalized bearer email to persisted User. Require ProjectUser for project scope. Evaluate its admin/member/viewer role against common named service actions. Consumers may add domain denials but cannot derive a broader permission source.

### Alternatives

| Alternative | Advantages | Disadvantages | Reason not chosen |
|---|---|---|---|
| Token workspace/permission claims | Fast request path | Stale/revocation drift; issuer/config coupling | Explicitly rejected by user rule |
| Runtime permission settings | Easy deployment variation | Policy differs by environment; unauditable grants | Authorization must be database-driven |
| Per-service user/member copies | Local queries | Divergence and cross-service inconsistency | Violates common-layer ownership |

### Consequences

Authorization reads PostgreSQL on each request; User/ProjectUser schema and identity provisioning are production prerequisites; consumers share stable role/action semantics; future service extraction needs one authoritative interface and fail-closed behavior.

### Reversal Conditions

Only an accepted architecture proving equivalent current-state revocation, one authority, cross-service consistency, audit, and migration may reopen the storage/evaluation mechanism.

### Affected Contracts

AUTHZ-REQ-001..006; AUTHZ-INV-001..005; SCN-001/002; API-AUTHZ-003; MODEL/TABLE-AUTHZ; FEAT-004.

## DEC-AUTHZ-002: Common Layer Is the Current ncn-authz Runtime

### Status

Accepted transitional boundary. Owner: architecture/platform. Reviewed 2026-08-14.

### Context and Drivers

Authorization applies to PMS, agents, and future services, so PMS cannot own it. Current services share one backend and database; an independent policy service interface is not yet implemented.

### Decision

Treat the shared models/repositories/dependencies/policy code as the current physical implementation of logical `ncn-authz`. Every service consumes it. Do not create a second authorization store or network API until an extraction contract is accepted.

### Alternatives

| Alternative | Advantages | Disadvantages | Reason not chosen |
|---|---|---|---|
| Keep feature under PMS | Matches project relation proximity | Wrong ownership for agents/future services | Rejected by user clarification |
| Immediately claim independent service | Matches target topology | No verified API/deployment/migration | Would misstate Present behavior |
| Unowned shared utility | Simple naming | No policy/data accountability | Violates single-owner rule |

### Consequences

Docs register a third logical current service with shared-runtime status. PMS/agents specify consumer behavior. Extraction must preserve interfaces/data and resolve project bootstrap transaction, latency, availability, and migration.

### Reversal Conditions

Reopen only if authorization ownership changes by an explicit project decision; physical deployment changes do not by themselves change logical ownership.

### Affected Contracts

Project service/feature registries, architecture/interface/data maps, PMS/agents dependencies, FEAT-004, all ncn-authz contracts.

## DEC-AUTHZ-003: Authentication and Transport Carry No Application Grants

### Status

Accepted. Owner: platform authorization/API. Reviewed 2026-08-14.

### Context and Drivers

The backend must not depend on configurable permission names, token workspace lists, generated synchronous tracking IDs, or custom duplicate/concurrency headers. Operational identity is already available as persisted User UUID.

### Decision

Keep only authentication mechanics in auth settings/claims. Use standard bearer identity. Use persisted User UUID for logs/audit/rate tracking. Consumer commands carry client domain/command UUIDs and expected versions in JSON when applicable.

### Alternatives

| Alternative | Advantages | Disadvantages | Reason not chosen |
|---|---|---|---|
| Caller tracking metadata | Cross-hop lookup | Spoofing/duplication; unnecessary for user tracking | Persisted User UUID is authoritative |
| Custom mutation metadata headers | Familiar conventions | Explicitly prohibited; splits domain contract | JSON domain fields selected |
| Permission settings/claims | Easy edge denial | Stale/environment-specific application policy | Database role selected |

### Consequences

Synchronous error/log contracts contain no request tracking value. Async agent workflows retain their own Run/node/tool/event identities. Consumer OpenAPI and documentation must stay consistent.

### Reversal Conditions

Only an explicit user/project decision may change this transport boundary; an observability preference alone is insufficient.

### Affected Contracts

AUTHZ-REQ-006/008/009; API-AUTHZ; consumer APIs; project interface/operations contracts.

## DEC-AUTHZ-004: Reuse Generic User Filtering

### Status

Accepted. Owner: backend/common data layer. Reviewed 2026-08-14.

### Context and Drivers

Email equality is already expressible by the generic repository. A custom method adds no domain behavior, while project authorization requires a real multi-table projection.

### Decision

Use the generic `get` filter for normalized email in current-user/register/login flows. Keep a custom joined query only for User + Project + ProjectUser authorization.

### Alternatives

| Alternative | Advantages | Disadvantages | Reason not chosen |
|---|---|---|---|
| Thin email getter | Discoverable name | Duplicates generic behavior | Explicitly removed by user request |
| All joins in managers | Fewer repository methods | Leaks SQL/data responsibility | Violates layer boundary |

### Consequences

Callers must normalize email before the exact generic filter. Joined query remains focused and independently testable. Database normalization remains a migration/data-quality concern.

### Reversal Conditions

Reopen if email resolution gains domain rules that the generic filter cannot express without hiding important behavior.

### Affected Contracts

AUTHZ-REQ-001/007; SCN-001/002; API-AUTHZ-001/003; MODEL/TABLE-AUTHZ; technical design.

## Open Decision Queue

| Question | Impact | Owner/evidence | Resolution trigger |
|---|---|---|---|
| OIDC User provisioning/disable/reconciliation | Production identity lifecycle | Identity/platform owner | Before production OIDC |
| Membership administration interface and audit | Multi-user access lifecycle | Product/authz owner | Before invitation/role feature |
| Legacy data and normalized email migration | Schema safety | Database owner inventory | Before migration |
| Independent service API and project-bootstrap coordination | Extraction availability/consistency | Architecture/PMS/authz owners | Before physical separation |
| Durable access-decision audit requirements | Retention/compliance/operations | Security/product owner | Before production audit acceptance |
