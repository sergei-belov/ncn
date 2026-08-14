# Feature: ncn-authz Workspace and Project Access Service

## Executive Contract

Create `ncn-authz` as the authority for NCN application users, workspace roles, project roles, optional project-service access restrictions, and named authorization decisions. Browser SSO remains at oauth2-proxy and provides only allowlisted OIDC identity claims: required `email` with `email_verified=true` and optional `name`. These claims identify or provision a User and never define access. Workspace and project business objects remain owned by `ncn-pms`.

The NCN frontend calls browser-facing `ncn-authz` routes directly through Traefik and oauth2-proxy. No `ncn-portal-api` dependency, aggregation layer, or proxy is part of this feature.

## Evidence and Decision Status

| Evidence | Status | Consequence |
| --- | --- | --- |
| `docs/services/ncn-authz/**` defines authorization ownership, roles, checks, and SSO edge assumptions. | **Confirmed** | This package refines that concept into an implementation-ready feature. |
| `backend/models/sqlalchemy/users.py`, `project_users.py`, and current auth dependencies preserve User UUIDs and project roles. | **Confirmed** | Migration must retain current identifiers and role meaning. |
| Browser login is terminated by oauth2-proxy and routed through Traefik. | **Accepted project constraint** | `ncn-authz` trusts identity only through a proven non-bypassable carrier. |
| `ncn-portal-api` does not exist and must not be used. | **Confirmed user correction** | Browser-facing authz APIs are called directly by the frontend. |
| Verified normalized email is sufficient as the MVP SSO account key. | **Assumed** | Subject/issuer identity linking is deferred; email collision or unsupported change fails safely. |

## Problem and Opportunity

Authorization is currently expressed through shared-backend models and dependencies rather than an explicit service boundary. NCN needs one place to resolve users, manage workspace/project access, evaluate named actions, and support later service extraction without copying project data or treating identity claims as access state.

NCN roles are assigned only through explicit access-management APIs or project bootstrap. The SSO boundary supplies identity attributes only.

## Actors and Permissions

| Actor | Goal | Permission boundary |
| --- | --- | --- |
| SSO user | Enter NCN and see only accessible workspaces/projects | Must present an identity verified by the approved edge; SSO attributes do not grant roles |
| Workspace owner | Manage workspace membership and roles | May manage roles within that workspace, subject to last-owner and privilege-ceiling rules |
| Workspace admin | Manage workspace access allowed by policy | Cannot grant above own authority, change protected owners, or act across workspaces |
| Project admin | Manage project members and optional service restrictions | Cannot grant above own project role, remove the last effective project admin, or act outside the project |
| Consumer service | Ask whether a User may perform a named action | Uses authenticated workload identity and supplies only owned scope identifiers |
| `ncn-pms` | Bootstrap creator access during project creation | May create the one creator-admin binding for the project it owns |
| Local developer/test actor | Use compatibility login outside production | Local credential routes must be disabled in production |

## Outcomes and Success Measures

| ID | Outcome | Measure |
| --- | --- | --- |
| OUT-001 | One authoritative access model | All active decisions use persisted `ncn-authz` User and membership state; SSO claims cannot change a decision |
| OUT-002 | Safe SSO entry | Repeated login for the same normalized verified email resolves the same User; collisions and disabled users fail closed |
| OUT-003 | Self-service scoped administration | Authorized workspace/project admins can list, add, change, and revoke access with privilege and last-owner/admin guards |
| OUT-004 | Compatible extraction | Existing User UUIDs and ProjectUser roles survive migration, and shadow decisions match before cutover |
| OUT-005 | Operable MVP | Access changes and decisions emit privacy-safe structured logs and metrics without introducing a durable audit domain |

## Scope

### In Scope

- User resolution and lazy provisioning from a verified SSO email and display name.
- Local credential compatibility for development/test only.
- Workspace membership roles: `owner`, `admin`, `member`.
- Project membership roles: `admin`, `member`, `viewer`.
- Optional per-project service restrictions that may narrow but never broaden a project role.
- Direct frontend APIs for current User and scoped access administration.
- Internal authorization-check and PMS project-bootstrap APIs.
- Preservation and staged extraction of current User/ProjectUser data and authorization behavior.
- Privacy-safe structured logs and metrics for decisions and mutations.

### Out of Scope

- Owning workspace, project, board, card, or other PMS business records.
- Any SSO-derived role or access rule.
- A separate SSO subject/issuer identity-link table in the MVP.
- Durable authorization audit tables, command-receipt tables, or persisted decision records in the MVP.
- `ncn-portal-api`, frontend aggregation, or proxying other services' domain APIs.
- Global superuser or OIDC-derived administrator privileges.
- Fine-grained resource ACLs beyond workspace, project, and optional project-service scope.

### Deferred

- Stable issuer/subject account linking, email-change recovery, account merge, and multi-provider identities.
- Durable compliance audit retention if later required by an approved contract.
- Bulk membership import, access requests/approvals, temporary grants, and custom roles.
- Caching authorization decisions until invalidation and revocation semantics are approved.

## Requirements

| ID | Requirement |
| --- | --- |
| REQ-001 | Given a non-bypassable verified SSO identity, the service shall normalize the verified email, resolve exactly one active User or lazily create one, refresh safe profile fields, and reject missing, invalid, colliding, or disabled identities without changing roles. |
| REQ-002 | Local credential authentication shall retain required compatibility for development/test, store only password hashes, never return credentials, and be disabled in production. |
| REQ-003 | The service shall answer named authorization checks using only current persisted User, workspace, project, and service-access state; OIDC identity claims shall never define access. |
| REQ-004 | Authorized workspace owners/admins shall list, add, change, and revoke workspace membership within their scope, with unique membership, role-ceiling, stale-write, and last-owner protection. |
| REQ-005 | Authorized project admins shall list, add, change, and revoke project roles and optional service restrictions; service access shall inherit the project role when no restriction exists and shall never elevate it. |
| REQ-006 | Every access mutation shall validate actor scope, target scope, role ceiling, protected last-owner/admin coverage, target User state, and optimistic version before commit. |
| REQ-007 | Browser and internal APIs shall be versioned, authenticated for their audience, return stable errors, enforce bounded timeouts/limits, and fail closed when identity, policy data, or dependencies are unavailable. |
| REQ-008 | Extraction shall preserve existing User UUIDs and valid ProjectUser roles, maintain one write authority, prove data and sampled-decision parity, and support rollback before legacy cleanup. |
| REQ-009 | Successful PMS project creation shall establish exactly one creator ProjectUser with `admin`; duplicate identical bootstrap requests shall converge, while conflicting creator requests shall fail safely. |
| REQ-010 | Authorization decisions and access mutations shall emit privacy-safe structured logs and metrics with correlation ID, actor/consumer, safe scope, result/reason, and policy/version context; tokens, passwords, hashes, and full OIDC payloads shall never be logged. |

## Invariants

| ID | Invariant |
| --- | --- |
| INV-001 | OIDC claims are identity input only and never create or change workspace/project/service roles. |
| INV-002 | A normalized email identifies at most one User in the MVP; a disabled User is denied before membership evaluation. |
| INV-003 | One User has at most one active membership per workspace and per project. |
| INV-004 | A service restriction can only equal or narrow its parent project role; absence means inherit the project role. |
| INV-005 | Only `ncn-pms` owns workspace/project business objects; `ncn-authz` stores opaque scope identifiers and access relationships only. |
| INV-006 | No mutation removes the last workspace owner or last effective project admin, and no actor grants authority stronger than their own. |
| INV-007 | Unknown actions, invalid roles, stale versions, unavailable policy state, and unresolved scope validation deny or reject without partial writes. |
| INV-008 | Secrets, bearer tokens, password material, and full OIDC payloads never appear in responses, logs, metrics, or persisted authorization data. |

## Quality Requirements

| ID | Requirement |
| --- | --- |
| NFR-001 | Authorization checks have a defined service-level target before active cutover, a bounded consumer timeout, and no silent allow fallback. |
| NFR-002 | Membership list and mutation APIs are paginated/bounded and use indexed scope lookups. |
| NFR-003 | Structured security logs are queryable in Loki by correlation ID, User UUID, safe scope ID, action, and result for the platform retention period. |
| NFR-004 | UI access-management flows meet keyboard, focus, semantic status, contrast, and screen-reader feedback requirements. |
| NFR-005 | Deployment supports shadow comparison, reversible reader cutover, schema compatibility, and restore verification. |

## State and Lifecycle

- `User`: absent → active by verified normalized email or local development registration → profile refreshed → disabled. Re-enablement is an explicit operator action outside the login flow.
- `WorkspaceUser`: absent → active (`owner|admin|member`) → role changed → revoked. Revocation is blocked when it would remove the last owner.
- `ProjectUser`: absent → active (`admin|member|viewer`) by manual assignment or creator bootstrap → role changed → revoked. Revocation/demotion is blocked when it would remove the last effective admin.
- `ServiceUser`: absent means project-role inheritance; present means an explicit equal-or-weaker service role; it may be changed or removed to restore inheritance.
- An authorization decision is request-scoped output, not persisted domain state in the MVP.

## Dependencies and Constraints

- Traefik and oauth2-proxy provide the browser ingress and verified SSO boundary.
- PostgreSQL is the transactional source of truth for Users and access relationships.
- `ncn-pms` owns workspace/project existence and lifecycle and must provide an accepted validation/bootstrap contract.
- Frontend routes and API adapters call `ncn-authz` directly through the authenticated ingress.
- Existing backend consumers require compatibility adapters during extraction.
- Redis, Kafka, and Temporal are not required for the MVP authorization decision or membership transaction path.

## Security and Privacy

- Only the trusted edge may supply SSO identity; `ncn-authz` must be unreachable through a path that preserves caller-spoofed identity headers.
- The accepted carrier must prove that email is provider-verified. Name is display metadata, not authority.
- Browser mutations require same-origin routing plus an approved CSRF control. Internal APIs require workload authentication and explicit consumer allowlisting.
- Authorization and mutation input never accepts caller-supplied effective roles or a precomputed allow result.
- Email is personal data. Logs prefer User UUID and safe scope identifiers; email appears only where operationally necessary and approved.

## Failure, Recovery, and Observability

- Identity ambiguity, disabled User, unknown action, invalid role, missing parent membership, stale version, and dependency timeout fail closed.
- Each membership mutation is one PostgreSQL transaction. A failed guard or write leaves canonical state unchanged.
- Writes do not require a command-receipt table. Clients recover from ambiguous responses by reading canonical state before retrying; naturally idempotent `PUT` bootstrap converges on its unique key.
- Metrics cover resolution outcome, authorization decision/reason, mutation result, stale/duplicate/last-owner conflicts, latency, dependency failure, parity mismatch, and bootstrap drift.
- Structured logs carry correlation ID and safe identifiers while omitting provider payloads and credential material.

## Acceptance Criteria

- **AC-001 / REQ-001 / SCN-001:** repeated valid SSO sessions for one case-normalized verified email resolve one User UUID; first use may create that User, while collision, missing email, or disabled state returns a stable denial and creates no role.
- **AC-002 / REQ-002 / SCN-001:** production rejects local credential routes, and tests/log capture find no plaintext password or hash in responses or telemetry.
- **AC-003 / REQ-003 / SCN-002:** decisions match the approved role/action matrix and do not change when optional OIDC identity attributes change.
- **AC-004 / REQ-004 / SCN-003:** authorized actors complete workspace list/add/change/revoke flows; duplicate, stale, cross-scope, privilege-ceiling, and last-owner attempts are rejected without partial change.
- **AC-005 / REQ-005 / SCN-002/004:** project membership and service restriction behavior matches the approved inheritance/ceiling matrix, including next-request revocation.
- **AC-006 / REQ-006 / SCN-003/004:** all mutation guards are enforced under concurrent requests and canonical state remains valid.
- **AC-007 / REQ-007 / SCN-002/005:** APIs enforce the declared audience, stable errors, limits, and fail-closed behavior without custom caller tracking metadata.
- **AC-008 / REQ-008 / SCN-005:** inventory/backfill validation proves User and ProjectUser counts, identifiers, roles, and sampled decision parity before cutover; rollback preserves them.
- **AC-009 / REQ-009 / SCN-006:** duplicate identical creator bootstrap converges to one admin binding, while conflicting creator input or failed provisioning cannot expose a project as successfully ready.
- **AC-010 / REQ-010 / SCN-002..006:** success and failure paths emit correlation-ready safe logs/metrics, and capture tests find no credentials or full OIDC payloads.

## Assumptions

| Assumption | Basis | Validation | Impact if false |
| --- | --- | --- | --- |
| The IdP provides a verified email that is unique and stable enough for MVP account resolution. | User-directed simplification plus current NCN behavior | Inspect provider contract and collision inventory before SLICE-002 | Add a stable subject-link contract before production SSO |
| Existing ProjectUser roles are already limited to `admin|member|viewer`. | Current docs/models | Inventory production/backup data before migration | Define and approve an explicit legacy-role conversion |
| Service access is a narrowing overlay; absence means inherit project role. | Requested “accesses” scope and least-privilege design | Product approves action/role matrix | Revise DATA-004, API-004, and policy evaluator |
| Workspace roles are `owner|admin|member`. | Current NCN docs and requested workspace-role scope | Product/security review | Update role schema, UI, guards, and migration before delivery |

## Open Questions

| Question | Impact | Owner / resolution trigger | Blocking? |
| --- | --- | --- | --- |
| What exact verified identity carrier does oauth2-proxy forward, and how is bypass prevented? | API-001 parsing and trust boundary | Platform identity owner plus deployed integration test before SLICE-002 | Yes |
| What canonical workspace identifier and lifecycle-validation endpoint does PMS expose? | DATA-002, API-006, cross-service integrity | PMS owner before workspace administration | Yes |
| Who may change a workspace owner, and is transfer a separate operation? | Last-owner and privilege policy | Product/security approval before API-006 enablement | Yes |
| Which same-origin route and CSRF mechanism protect direct browser mutations? | API-003/004/006 security | Frontend/platform owner before browser writes | Yes |
| What is the accepted PMS compensation or non-visible state when creator bootstrap fails? | Project creation user outcome | PMS/authz owners before SLICE-005 | Yes |
| Which service identifiers may receive restrictions? | DATA-004 validation and UX options | Service catalog/PMS owner before API-004 | Yes |
| How should verified-email change or collision recovery work after MVP? | Account continuity | Product/security decision for deferred identity-link work | No for MVP if change fails safely |
| What latency/SLO and log-retention targets apply? | NFR-001/003 sizing and alerts | Platform/security owners before production cutover | Yes for production cutover |

## Traceability

The authoritative cross-document matrix is maintained in `delivery/plan.md`. Each REQ is linked above to acceptance criteria and in `scenarios.md` to an observable flow; API, data, UX, decisions, and delivery slices use the same stable identifiers.
