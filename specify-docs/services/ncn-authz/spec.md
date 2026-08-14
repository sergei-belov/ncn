# ncn-authz Service Contract

## Executive Contract

`ncn-authz` provides the common authorization layer for all NCN backend services. A bearer identity supplies a normalized email; the common layer resolves one persisted `users` row and uses its UUID as the application actor. Project-scoped access requires one matching `project_users` relation, and its stored `admin`, `member`, or `viewer` role is evaluated against code-owned service actions. Tokens and runtime settings contain authentication mechanics only and cannot grant application permission.

The current implementation is physically shared with the backend services. `ncn-authz` is the logical owner now so future separation can preserve one policy and data authority.

## Evidence and Status

| Topic | Status | Statement | Evidence/rationale |
|---|---|---|---|
| Common authorization source | Confirmed | User, ProjectUser, common dependencies, role resolution, auth routes, and persisted-user tracking are Present in the shared backend | User-supplied example/rules and authorized backend verification, 2026-08-14 |
| Current deployment | Confirmed logical; physical shared layer | All current services consume the same backend authorization implementation; independent deployment is not claimed | User clarification: common layer for all services |
| Permission source | Confirmed | Project permissions derive from `project_users.role`, not token permission claims or runtime permission settings | Explicit user requirement |
| HTTP metadata | Confirmed | Synchronous interfaces require standard bearer identity plus path/query/body only; tracking uses persisted user UUID | Explicit user requirement |
| Schema readiness | Open | ORM mappings are Present; checked-in migration and deployed legacy data state are not established | Authorized backend/spec verification |
| External identity lifecycle | Open | OIDC user provisioning, disablement, and reconciliation owner is undefined | Common layer requires an existing persisted user |

## Responsibility and Ownership

Own:

- persisted application User identity and optional local password hash;
- ProjectUser membership and role as current authorization input;
- normalized bearer-email resolution and current-user contract;
- common workspace/project actor dependencies;
- role-to-service-action policy evaluation and denial behavior;
- persisted actor identity for security logs, access audit, and user rate limits.

Do not own provider accounts or OIDC credential lifecycle, PMS projects/work, agent configuration/Runs, consumer resources, human Approval, or business validation. Consumers must not copy User/ProjectUser truth or evaluate client/token permission flags independently.

## Actors, Systems, and Permissions

| Actor/system | Goal | Allowed | Forbidden/constrained |
|---|---|---|---|
| Unauthenticated caller | Establish local identity where enabled | Local register/login only in local flow | No protected service access |
| Persisted authenticated user | Become one stable NCN actor | Read own public profile; access collection actions allowed to any persisted user | Cannot gain project access from token claims or path alone |
| Project admin | Use administrative service actions in a related project | Actions registered as admin-capable, including current PMS/agent administration | Cannot cross project/workspace or override domain/archive rules |
| Project member | Use day-to-day project actions | Service actions registered for member role | Cannot perform administrative or delete-any actions |
| Project viewer | Read a related project | Service actions registered for viewer role and personal preferences where defined | Cannot mutate shared domain state |
| OIDC edge | Verify provider identity | Validate signature/issuer/audience/time/subject and forward identity | Cannot grant application role/action |
| Consumer service | Enforce its domain operation | Require common actor and named policy action, then enforce domain rules | Cannot read authorization settings/claims as permission authority |
| Platform operator | Provision identity/schema under policy | Maintain normalized users and operate protected data | Cannot grant project permission through environment configuration |

## Feature Inventory

| Feature | Purpose | Status | Contract |
|---|---|---|---|
| Database-driven authorization | Resolve persisted actors and evaluate current project roles for all services | Active; common source Present, migration Open | [feature](features/database-driven-authorization.md) |

## Requirements

| ID | Requirement | Scenario | Acceptance |
|---|---|---|---|
| AUTHZ-REQ-001 | Resolve every protected identity by normalized bearer email to exactly one persisted User before consumer work. | SCN-001 | Invalid token/missing user denied; valid user supplies one UUID |
| AUTHZ-REQ-002 | Expose public current-user data and local register/login only under the configured authentication flow. | SCN-001/003 | Password data never leaves the service; non-local credential routes are unavailable |
| AUTHZ-REQ-003 | Require exact ProjectUser membership for every project-scoped consumer route. | SCN-002 | Missing/mismatched membership denies before domain side effects |
| AUTHZ-REQ-004 | Evaluate effective action permissions from the stored role through common code and let consumers add only domain guards. | SCN-002 | Cross-service role/action matrix tests pass |
| AUTHZ-REQ-005 | Treat persisted-user existence as the current collection-level authorization input where no project relation exists; project creation establishes creator admin membership atomically. | SCN-002 | Project lists are membership-filtered and creator becomes admin |
| AUTHZ-REQ-006 | Keep workspace, role, and action grants out of authentication configuration and identity claims. | SCN-002 | Configuration/claim audit cannot alter authorization |
| AUTHZ-REQ-007 | Use generic repository filtering for simple User lookup; reserve custom queries for joined authorization projections. | SCN-001/002 | No redundant email-specific getter is part of the contract |
| AUTHZ-REQ-008 | Use persisted User UUID for actor context, authorized logging, access audit identity, and user rate limiting. | SCN-001/003 | All captured identities match the database UUID |
| AUTHZ-REQ-009 | Require no custom synchronous tracking, duplicate-control, or concurrency headers; consumers use JSON domain IDs and expected versions where defined. | SCN-002 | Shared OpenAPI/conformance tests pass with bearer plus JSON only |
| AUTHZ-REQ-010 | Provision normalized unique users, unique project membership, allowed roles, and project/user references before protected production traffic. | SCN-003 | Clean and legacy schema verification pass |

## Invariants

| ID | Invariant | Enforcement | Verification |
|---|---|---|---|
| AUTHZ-INV-001 | A token identifies a candidate user; it never grants workspace, project, role, or service action. | Edge/auth helper/common dependency | Extra token claims do not change allow/deny |
| AUTHZ-INV-002 | One authorized operation uses the same persisted User UUID for actor, membership, log, audit, and rate-limit identity. | Common dependency | End-to-end identity assertion |
| AUTHZ-INV-003 | One user has at most one ProjectUser role per project, limited to `admin`, `member`, or `viewer`. | Database constraints and enum validation | Duplicate/invalid role tests |
| AUTHZ-INV-004 | Consumer-visible permission flags are projections and are never accepted as command authority. | Common policy/consumer manager | Tampered input cannot elevate access |
| AUTHZ-INV-005 | Membership/role changes affect the next request; no stale authorization cache is in scope. | PostgreSQL read on authorization | Add/change/remove transition tests |
| AUTHZ-INV-006 | Password hashes and bearer contents never appear in public models, errors, logs, metrics, or events. | Serialization/redaction boundary | Schema and log-capture tests |

## State and Lifecycle

An external or local identity is unknown until normalized email resolves to User. It is then an authenticated persisted actor. Project access transitions from absent to role-bearing only through ProjectUser creation; role update changes effective actions; deletion revokes project access on the next request. Project creation is the only currently specified membership write and creates an admin relation for the creator. Invitation, role administration, user disablement, and provider synchronization remain Open.

## Dependencies and Constraints

The shared layer depends on a non-bypassable OIDC-verifying edge for external tokens or local token signature verification, PostgreSQL, the common async repository, and FastAPI dependency injection. Consumer services depend on its actor/policy result but retain domain validation. Current physical project lookup references PMS project data in the shared database; future independent deployment requires an owner interface and consistency contract.

## Security and Privacy

Email and user name are personal data; password is a restricted nullable hash. Apply least disclosure: invalid identity returns `401`, missing project relation/action returns `403`, and consumer resources may use disclosure-safe `404`. Rate limits and logs never trust caller-supplied tracking data. The OIDC network path must not bypass edge verification. The common layer re-evaluates current membership and role on every project request.

## Failure, Recovery, and Observability

Invalid/malformed bearer or missing User returns `401 AUTH_REQUIRED`. Missing relation or disallowed action returns `403 FORBIDDEN`. Duplicate local email returns `409 USER_ALREADY_EXISTS`; invalid credentials return `401 INVALID_CREDENTIALS`; local routes outside local flow return `404 AUTH_ROUTE_DISABLED`; the in-process user window can return `429 RATE_LIMITED`. Database failure is sanitized and no consumer side effect begins. Authorized logs record method, safe path, persisted User UUID, and project role when applicable. Monitor authentication failures, permission denials, user-rate limits, database latency, and role/data-quality anomalies.

## Quality Requirements

| ID | Attribute | Requirement | Verification |
|---|---|---|---|
| AUTHZ-NFR-001 | Security | Deny invalid identity, cross-scope membership, insufficient role, and bypass attempts before consumer side effects. | Negative cross-service matrix |
| AUTHZ-NFR-002 | Privacy | Exclude password/bearer data and minimize email exposure. | Public-schema/log/audit review |
| AUTHZ-NFR-003 | Performance | Use indexed email and project/user membership access with bounded database work per request. | Query-plan and p95 load checks |
| AUTHZ-NFR-004 | Compatibility | Preserve actor IDs, role semantics, stable errors, and common dependency behavior during service extraction. | Consumer contract suite |
| AUTHZ-NFR-005 | Operations | All authorized logs/audit/rate metrics identify the persisted user UUID. | Log/metric integration tests |

## Assumptions

| Assumption | Rationale | Validation | Impact if false |
|---|---|---|---|
| Persisted emails can be lowercase-normalized without collisions. | Generic lookup is exact after normalization. | Pre-migration collision query | Identity merge/resolution is required before unique enforcement |
| Any persisted user may create a project and becomes its admin. | Configurable create permission was explicitly removed. | Product acceptance | Requires a workspace-level relation/policy model |
| External bearer traffic cannot bypass verifying ingress. | Shared backend reads provider identity under that trust boundary. | Deployment/network test | Backend must verify external signatures before production |

## Open Questions

| Question | Impact | Owner/trigger | Blocking |
|---|---|---|---|
| Who provisions, updates, disables, and reconciles OIDC users? | Production identity lifecycle and revocation | Identity/platform owner before OIDC production | Yes |
| Does deployed legacy membership/user data exist and how is it normalized? | Migration/backfill/rollback | Database owner inventory | Yes for migration |
| Which interface administers project membership and roles after creator bootstrap? | Multi-user collaboration | Product/authz owner | No for creator-only slice |
| When does the shared module become an independently deployed `ncn-authz` boundary? | Runtime ownership, latency, failure, consistency | Architecture owner before extraction | No for shared runtime; yes for extraction |

## Service Acceptance

Acceptance requires current-user/local-auth tests; generic user-filter verification; project membership and role/action tests across PMS and agent configuration routes; consumer domain guard tests; stable errors; persisted-user log/audit/rate identity; absence of permission grants in claims/config; absence of custom synchronous request metadata; schema/migration verification; and an ingress bypass test for external authentication.

## Traceability

Use [scenarios](scenarios.md), [features](features/README.md), [technical design](design/technical.md), [UI/UX](design/ui-ux.md), [API](interfaces/api.md), [events](interfaces/events.md), [models](data/models.md), [tables](data/tables.md), and [decisions](decisions.md).
