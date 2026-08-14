# ncn-authz API and Common Authorization Interfaces

## Applicability

Applicable. Current-user and local credential HTTP operations plus an internal FastAPI dependency interface are **Present** in the shared backend. A network authorization API is **Planned/Open** only if the common layer is independently deployed; no such route is claimed now.

## Ownership and Consumers

| Interface family | Owner | Consumer | Trust boundary | Status |
|---|---|---|---|---|
| Current user/local credentials | `ncn-authz` common layer | Frontend and backend callers | Bearer/credential to persisted identity | Present |
| Common actor/policy dependency | `ncn-authz` common layer | PMS, agents, future services | Persisted identity/project role to consumer | Present internal interface |
| Independent policy API | `ncn-authz` | Future independently deployed consumers | Service-to-service authorization | Planned/Open |

## Shared Conventions

HTTP uses `/api/v1`, JSON `snake_case`, UUID identities, and stable `{error:{code,message,field_errors?}}`. Protected calls use standard bearer authorization. No synchronous interface accepts or returns custom request-tracking, duplicate-control, or concurrency headers. Consumer mutations carry client-generated domain/command UUIDs and expected versions in JSON where their owner contract defines them. Authorized telemetry uses persisted User UUID.

Authentication establishes identity. Authorization always re-reads current User/ProjectUser state. Role/action flags in responses are advisory. Local credential routes are enabled only in local flow. Password hashes and bearer contents are never serialized.

## Operation Inventory

| ID | Kind/entry point | Purpose | Consumer | Requirement/feature |
|---|---|---|---|---|
| API-AUTHZ-001 | `GET /api/v1/auth/me` | Return public persisted current user | Frontend/all services | AUTHZ-REQ-001/002/008; FEAT-004 |
| API-AUTHZ-002 | `POST /api/v1/auth/register`; `POST /api/v1/auth/jwt/login` | Local-only identity creation/login | Local frontend/developer | AUTHZ-REQ-002; FEAT-004 |
| API-AUTHZ-003 | Internal User/workspace/project actor dependency and service-action check | Guard all protected service routes | PMS, agents, future backend services | AUTHZ-REQ-003..009; FEAT-004 |

## API-AUTHZ-001: Current User

### Contract

Resolve standard bearer email to the persisted User with the generic repository filter and return public identity.

### Authentication and Authorization

Valid configured authentication is required. No project role is required. A decoded identity without a User row is unauthenticated for application purposes.

### Request

No body or custom metadata. Standard bearer only.

### Response

`200` User: UUID `id`, normalized `email`, display `name`, UTC `created_at`. Password is absent.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Missing/invalid bearer | `401 AUTH_REQUIRED` | Reauthenticate |
| No persisted User | `401 AUTH_REQUIRED` | Identity owner provisions/reconciles user |
| User rate exceeded after resolution | `429 RATE_LIMITED` | Retry after bounded window |
| PostgreSQL unavailable | Sanitized service error | Bounded safe retry; no consumer work |

### State, Idempotency, and Concurrency

Read-only. It uses current canonical User state and creates no tracking record.

## API-AUTHZ-002: Local Registration and Login

### Contract

Registration creates one normalized User with bcrypt password hash. Login validates form credentials and returns a local bearer. Both are unavailable outside local flow.

### Authentication and Authorization

No prior identity is required. These operations authenticate only and grant no project relation or service action.

### Request

Register JSON: email 3–100 in valid form, name 1–100 after trim, password 8–128. Login form: normalized email as username and password 8–128. No custom metadata.

### Response

Register `201` returns public User. Login `200` returns `access_token`; token type follows the shared bearer scheme. Password/hash is absent.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Flow not local | `404 AUTH_ROUTE_DISABLED` | Use configured external identity flow |
| Duplicate normalized email | `409 USER_ALREADY_EXISTS` | Sign in or use another identity under policy |
| Invalid credentials | `401 INVALID_CREDENTIALS` | Correct credentials; no detail disclosure |
| Invalid fields | `422 VALIDATION_ERROR` | Correct fields |

### State, Idempotency, and Concurrency

Email uniqueness serializes duplicate registration; concurrent duplicates yield one User. Login is read-only apart from token issuance. Neither creates project access.

## API-AUTHZ-003: Common Actor and Service-Action Interface

### Contract

Internal FastAPI dependencies provide current User, workspace actor, or project-authorized actor. Project resolution joins normalized email, exact project/workspace reference, and ProjectUser; then evaluates role against a named consumer action. Consumers recheck domain scope/state before mutation.

### Authentication and Authorization

User actor requires persisted User. Workspace actor currently requires persisted User and adopts the requested workspace for collection operations; it grants no existing project access. Project actor requires exact relation and role. Tokens/settings cannot supply fallback permission.

Current base role semantics: admin receives registered administrative and work actions; member receives registered read/day-to-day work actions; viewer receives registered read actions. Each named action and any personal-preference exception is defined in the affected owner service contract and registered in common policy.

### Request

Internal inputs: Request method/safe path, normalized email, database session, optional workspace slug, project UUID, and named service action. No caller-provided permission flags or tracking identity.

### Response

User DTO or authorized actor containing persisted User UUID/display name, workspace/project scope, ProjectUser relation identity, and role. Consumer permission projections may be derived from the decision.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Missing User | `401 AUTH_REQUIRED` | Provision/re-authenticate |
| Missing project relation/role or denied action | `403 FORBIDDEN` | Wait for authorized data/policy change |
| Hidden consumer resource | Consumer disclosure-safe `404` | Do not retry without scope change |
| Invalid role/data inconsistency | Deny plus operational data-quality signal | Repair canonical data |

### State, Idempotency, and Concurrency

Authorization reads canonical state on every request and has no cache. Membership/role changes affect the next request. Consumer commands own transaction, duplicate, and optimistic-concurrency behavior through JSON domain fields.

## Compatibility and Versioning

User UUID, normalized-email semantics, role enum, actor fields, stable errors, and named action meaning are compatibility contracts. Additive actor fields are allowed. Independent deployment requires a versioned service interface and overlap while keeping one data/policy authority.

## Limits and Performance

Current user rate default is 60/minute per process and configurable as an operational limit, not an authorization grant. Exact production rate, authorization p95, membership volume, timeout, and availability objectives are Open.

## Observability

Record method, safe path, persisted User UUID after resolution, workspace/project, role, consumer action, decision, latency, rate outcome, and safe error code. No synthetic request tracking value, password, bearer content, or sensitive consumer body is recorded.

## Traceability

API-AUTHZ-001..003 → AUTHZ-REQ-001..010 → SCN-001..003 → MODEL-AUTHZ-001..004 → TABLE-AUTHZ-001/002 → DEC-AUTHZ-001..004 → FEAT-004 acceptance.
