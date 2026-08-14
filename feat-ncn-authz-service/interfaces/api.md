# API and Interface Contract

## Applicability

Applicable. The feature exposes direct browser APIs for session identity and workspace/project/service access administration, plus internal workload APIs for authorization checks and PMS creator bootstrap. It retains local credential compatibility outside production. There is no SSO access-administration interface and no frontend aggregation/proxy interface.

## Ownership and Consumers

| Interface family | Owner | Consumer | Trust path | Status |
| --- | --- | --- | --- | --- |
| Session/current User | `ncn-authz` | NCN frontend | Traefik + oauth2-proxy → verified browser identity | Planned |
| Workspace access administration | `ncn-authz` | NCN frontend | Same-origin authenticated browser + CSRF control | Planned |
| Project/service access administration | `ncn-authz` | NCN frontend | Same-origin authenticated browser + CSRF control | Planned |
| Authorization decision | `ncn-authz` | Allowlisted NCN services | Workload-authenticated internal HTTP | Planned |
| Project bootstrap | `ncn-authz` | `ncn-pms` | PMS workload identity | Planned |
| Local credential compatibility | Current backend, then `ncn-authz` | Development/test clients | Explicitly enabled local route | Present compatibility / planned ownership |

The frontend calls browser interfaces directly through the authenticated ingress. API-002 and API-005 are internal and are never exposed as browser endpoints.

## Shared Conventions

- Base path is `/api/v1`; JSON uses `snake_case`; timestamps are UTC RFC 3339; identifiers are strings containing their canonical UUID/opaque value.
- Successful responses include `X-Correlation-ID`; clients may send a valid bounded ID or receive a generated one. It is diagnostic, not duplicate control.
- Browser mutations use the accepted same-origin/CSRF mechanism. Internal requests use authenticated workload identity and consumer allowlists.
- Errors use `{ "code": string, "message": string, "correlation_id": string, "field_errors"?: object, "current"?: object }`.
- `400` malformed/validation, `401` unauthenticated, `403` authenticated but forbidden, `404` target absent or intentionally concealed, `409` duplicate/stale/invariant conflict, `422` structurally valid but unsupported relationship, `429` rate limited, `503` fail-closed dependency unavailable.
- Writes use database uniqueness and `expected_version` where applicable. No idempotency key or command-receipt storage is part of the MVP. After an ambiguous response, clients read canonical state before retrying.
- List endpoints use opaque cursor pagination with default `limit=50`, maximum `100`, stable ordering by `(created_at,id)`, and `{items,next_cursor}`.
- All request strings and list filters are bounded; exact byte/rate limits are finalized from inventory before production.

## Shared Types

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "is_active": true
  },
  "workspace_membership": {
    "id": "uuid",
    "workspace_id": "workspace-id",
    "user_id": "uuid",
    "role": "owner|admin|member",
    "version": 1
  },
  "project_membership": {
    "id": "uuid",
    "workspace_id": "workspace-id",
    "project_id": "uuid",
    "user_id": "uuid",
    "role": "admin|member|viewer",
    "source": "manual|bootstrap",
    "version": 1
  },
  "service_restriction": {
    "id": "uuid",
    "project_user_id": "uuid",
    "service_id": "service-id",
    "role": "admin|member|viewer",
    "version": 1
  }
}
```

Email is returned only to the authenticated User or an authorized membership administrator who needs it to identify a target. Internal decision APIs use User UUIDs.

## Interface Inventory

| ID | Protocol | Entry points | Purpose | Requirement |
| --- | --- | --- | --- | --- |
| API-001 | Browser HTTP | `POST /api/v1/auth/session/resolve`; `GET /api/v1/auth/me` | Resolve/provision SSO User and read current actor | REQ-001 |
| API-002 | Internal HTTP | `POST /api/v1/authorization/check` | Return current named-action allow/deny | REQ-003/005/007 |
| API-003 | Browser HTTP | `GET/POST /api/v1/projects/{project_id}/members`; `PATCH /.../{user_id}`; `POST /.../{user_id}/revoke` | Administer project membership | REQ-005/006 |
| API-004 | Browser HTTP | `PUT/DELETE /api/v1/projects/{project_id}/members/{user_id}/services/{service_id}` | Administer optional service restriction | REQ-005/006 |
| API-005 | Internal HTTP | `PUT /api/v1/projects/{project_id}/creator-access` | Bootstrap project creator admin | REQ-009 |
| API-006 | Browser HTTP | `GET/POST /api/v1/workspaces/{workspace_id}/members`; `PATCH /.../{user_id}`; `POST /.../{user_id}/revoke` | Administer workspace membership | REQ-004/006 |
| API-007 | HTTP compatibility | Existing local register/login/current-user paths, versioned on extraction | Development/test local authentication | REQ-002 |

## Authentication and Authorization

- API-001/003/004/006 accept browser identity only from the approved oauth2-proxy path. The service must reject spoofable direct identity headers and verify origin/CSRF on mutations.
- API-002 accepts only allowlisted workload identities and checks each consumer's allowed action and scope family.
- API-005 accepts only the PMS workload identity for projects PMS owns.
- API-007 is disabled in production and protected by explicit environment/deployment policy elsewhere.
- Role decisions use DATA-001..004 only. The SSO carrier accepts only verified `email`, `email_verified`, and optional `name`; no endpoint derives access from OIDC input or accepts caller-computed allow results.

## Operations

### API-001: Resolve SSO Session and Read Current User

#### Contract

`POST /auth/session/resolve` validates the trusted identity carrier, canonicalizes verified email, and transactionally resolves or lazily creates DATA-001. `GET /auth/me` reads the already resolved active User and bounded navigation scope summaries. Neither operation changes roles.

#### Request

The browser sends no identity body. Required email verification and optional name arrive only through the accepted trusted carrier. Query options on `/auth/me` may include bounded scope-summary expansion; full member lists use API-003/006.

#### Response

`200` returns `user`, `workspace_access[]`, `project_access[]`, and `policy_version`; first creation may return `201` from resolve. Scope summaries contain IDs and effective navigation roles only, not PMS business data. OIDC identity input is never echoed beyond the canonical User fields.

#### Errors and Recovery

Stable codes include `IDENTITY_UNTRUSTED`, `IDENTITY_EMAIL_REQUIRED`, `IDENTITY_EMAIL_INVALID`, `IDENTITY_EMAIL_CONFLICT`, `USER_DISABLED`, and `AUTHZ_UNAVAILABLE`. Identity errors create no access. Browser shows sign-in/support; transient `503` may be retried with backoff.

#### Idempotency and Concurrency

Canonical-email uniqueness makes repeated/concurrent resolve converge to one User. Profile refresh uses last-write-safe server values and never changes roles. No idempotency key is accepted.

### API-002: Check Authorization

#### Contract

`POST /authorization/check` evaluates one current named action. It is internal, synchronous, bounded, and fail closed.

#### Request

```json
{
  "user_id": "uuid",
  "action": "project.member.read",
  "workspace_id": "workspace-id",
  "project_id": "uuid",
  "service_id": null,
  "resource": {"type": "project", "id": "uuid"}
}
```

`workspace_id`, `project_id`, `service_id`, and `resource` are required/forbidden according to the registered action schema. Unknown fields and caller-supplied effective roles or identity attributes are rejected. Resource IDs remain owned by the consumer/PMS; authz evaluates only registered scope relationships.

#### Response

```json
{
  "allowed": true,
  "reason": "ROLE_ALLOWED",
  "effective_role": "admin",
  "effective_scope": "project",
  "policy_version": "v1"
}
```

Expected denials normally return `200` with `allowed=false` and `NO_MEMBERSHIP`, `ROLE_INSUFFICIENT`, `USER_DISABLED`, or `SCOPE_MISMATCH`. Authentication/validation/dependency failures use HTTP errors.

#### Errors and Recovery

Stable errors include `CONSUMER_FORBIDDEN`, `ACTION_UNKNOWN`, `SCOPE_INVALID`, `POLICY_UNAVAILABLE`, and `AUTHZ_UNAVAILABLE`. Consumer timeout is shorter than its parent operation budget. Consumers retry bounded transient failures only and never convert an error to allow.

#### Idempotency and Concurrency

Read-only. Each request evaluates committed state; the MVP has no decision cache. Ordering is irrelevant and revocation applies to the next completed read.

### API-003: Administer Project Membership

#### Contract

Lists canonical project members and lets an effective project admin add, change, or revoke DATA-003 under actor-ceiling and last-admin guards.

#### Request

- `GET` accepts `cursor`, `limit`, and bounded search.
- `POST` body: `{ "user_id": "uuid", "role": "admin|member|viewer" }`.
- `PATCH` body: `{ "role": "admin|member|viewer", "expected_version": 3 }`.
- Revoke body: `{ "expected_version": 3 }`.

The path supplies project scope; the server derives/validates workspace association through the owner contract. Caller cannot choose `source`.

#### Response

List returns `{items,next_cursor}` with User display summary, role, source, version, and effective service-restriction summary. Mutation returns `201` or `200` canonical `project_membership`; revoke returns `204`.

#### Errors and Recovery

Codes include `USER_NOT_FOUND`, `USER_DISABLED`, `PROJECT_NOT_FOUND`, `SCOPE_MISMATCH`, `MEMBERSHIP_EXISTS`, `MEMBERSHIP_NOT_FOUND`, `ROLE_INVALID`, `ROLE_EXCEEDS_ACTOR`, `LAST_PROJECT_ADMIN`, `SERVICE_RESTRICTION_CONFLICT`, and `VERSION_CONFLICT`. `VERSION_CONFLICT` includes safe `current` state. No failed request partially mutates restrictions.

#### Idempotency and Concurrency

Unique `(project_id,user_id)` prevents duplicates. Patch/revoke require `expected_version`; ambiguous outcomes are recovered by `GET`. The operation has no idempotency key.

### API-004: Administer Service Restriction

#### Contract

`PUT` creates/replaces DATA-004 for a project member; `DELETE` removes it and restores project-role inheritance. Only an effective project admin may act.

#### Request

- `PUT`: `{ "role": "admin|member|viewer", "expected_version": null|integer }`; null means create-if-absent.
- `DELETE`: `{ "expected_version": integer }`.

Project, target User, and service identifiers are path-bound. Service must be allowlisted and the desired role must not exceed the parent project role or actor authority.

#### Response

`PUT` returns `200/201` canonical `service_restriction` plus `effective_role`. `DELETE` returns `204`; subsequent checks inherit DATA-003.

#### Errors and Recovery

Codes include API-003 scope/permission/version errors plus `SERVICE_UNKNOWN`, `PROJECT_MEMBERSHIP_REQUIRED`, `SERVICE_ROLE_ELEVATION`, and `RESTRICTION_EXISTS`. Ambiguous responses require canonical project-member read before retry.

#### Idempotency and Concurrency

Unique `(project_user_id,service_id)` plus `expected_version` serializes writes. Identical `PUT` may return current state without a version bump; conflicting state returns `409`.

### API-005: Bootstrap Project Creator Access

#### Contract

PMS calls `PUT /projects/{project_id}/creator-access` to establish the creator as project admin before the project becomes ready.

#### Request

```json
{
  "workspace_id": "workspace-id",
  "creator_user_id": "uuid"
}
```

The authenticated PMS caller owns `project_id`. The service validates the active User and project/workspace relationship. Caller cannot select a weaker role or source.

#### Response

`200/201` returns canonical `project_membership` with role `admin` and source `bootstrap` when newly created. An identical existing manual admin may satisfy the result without provenance rewrite.

#### Errors and Recovery

Codes include `PMS_CALLER_FORBIDDEN`, `USER_NOT_FOUND`, `USER_DISABLED`, `PROJECT_NOT_FOUND`, `SCOPE_MISMATCH`, `BOOTSTRAP_CONFLICT`, and `AUTHZ_UNAVAILABLE`. PMS keeps the project non-ready or compensates under its accepted contract.

#### Idempotency and Concurrency

The `PUT` target plus unique membership state is naturally idempotent. Repeated identical requests return one canonical admin membership. A different creator or incompatible existing role returns `BOOTSTRAP_CONFLICT`. After ambiguity PMS reads API-003-compatible canonical state before retry.

### API-006: Administer Workspace Membership

#### Contract

Lists workspace members and lets a workspace owner or policy-permitted admin add, change, or revoke DATA-002 under privilege-ceiling and last-owner guards.

#### Request

- `GET` accepts `cursor`, `limit`, and bounded search.
- `POST` body: `{ "user_id": "uuid", "role": "owner|admin|member" }`.
- `PATCH` body: `{ "role": "owner|admin|member", "expected_version": 2 }`.
- Revoke body: `{ "expected_version": 2 }`.

The path supplies the workspace. Owner transfer policy may further restrict creation/change of `owner` before enablement.

#### Response

List returns `{items,next_cursor}` with User display summary, role, and version. Mutation returns `201` or `200` canonical `workspace_membership`; revoke returns `204`.

#### Errors and Recovery

Codes include `WORKSPACE_NOT_FOUND`, `SCOPE_MISMATCH`, `USER_NOT_FOUND`, `USER_DISABLED`, `MEMBERSHIP_EXISTS`, `MEMBERSHIP_NOT_FOUND`, `ROLE_INVALID`, `ROLE_EXCEEDS_ACTOR`, `OWNER_TRANSFER_REQUIRED`, `LAST_WORKSPACE_OWNER`, and `VERSION_CONFLICT`. Current safe state accompanies version conflict.

#### Idempotency and Concurrency

Unique `(workspace_id,user_id)` prevents duplicates. Patch/revoke require `expected_version`; last-owner validation and mutation occur in one transaction. Clients reload after ambiguous or stale responses.

### API-007: Local Credential Compatibility

#### Contract

Preserve only the current registration/login/current-user behavior needed by development and automated tests during extraction. It is not an SSO fallback.

#### Request

Existing compatible schemas remain authoritative until code inventory during SLICE-001. Any new version uses canonical email plus bounded password input and must not accept roles.

#### Response

Returns compatibility token/current User fields required by inspected consumers, never plaintext password or password hash. Deprecation headers are added only after all consumers have a replacement.

#### Errors and Recovery

Production returns `404` or the agreed route-disabled response. Development errors preserve stable invalid-credential/duplicate-email semantics without disclosing whether an unrelated account exists more than current compatibility requires.

#### Idempotency and Concurrency

Canonical-email uniqueness prevents duplicate registration. Login/current-user reads do not mutate access. No command receipt is used.

## Compatibility and Versioning

Current User UUIDs, valid ProjectUser roles, and required local-client behavior remain stable through compatibility adapters. Additive response fields are allowed within v1; renaming/removing fields or changing role/action meaning requires a new version and migration window. API-002 action names and policy versions are registered contracts, not arbitrary strings.

Legacy shared-backend reads remain available only during shadow/cutover. One authority writes memberships at a time. Cleanup/deprecation begins only after the observation window and explicit consumer sign-off.

## Limits and Performance

- Authorization request and response sizes are small and fixed by registered action schemas; batching is deferred.
- Membership lists default to 50 and cap at 100; search text, names, IDs, and correlation IDs have documented bounds before implementation.
- API-002 timeout/SLO, browser rate limits, and workload quotas are **Open** pending inventory, but every client must use a finite deadline.
- Pagination and lookup indexes are specified in `data/model.md`; no unbounded export is part of these routes.

## Observability

Each operation emits latency, result/error code, authenticated audience, and correlation ID. Identity logs include outcome and User UUID when resolved. Decision logs include safe scope, action, effective role, policy version, and reason. Mutation logs include actor/target UUID, safe scope, operation, before/after role, version, and result. Full OIDC payloads, bearers, passwords, hashes, and full identity headers are excluded.

## Traceability

| API | Requirements | Scenarios / UX | Data / decisions / slices |
| --- | --- | --- | --- |
| API-001/007 | REQ-001/002/007/010 | SCN-001/005; UX-001 | DATA-001; DEC-003/006; SLICE-002 |
| API-002 | REQ-003/005/007/010 | SCN-002/005; UX-001/003 | DATA-001..004; DEC-002/004/005; SLICE-003 |
| API-003/004 | REQ-005/006/007/010 | SCN-004/005; UX-003/004 | DATA-003/004; DEC-005/006; SLICE-004 |
| API-005 | REQ-007/009/010 | SCN-005/006; UX-001 | DATA-001/003; DEC-004; SLICE-005 |
| API-006 | REQ-004/006/007/010 | SCN-003/005; UX-002/004 | DATA-002; DEC-005/006; SLICE-004 |
