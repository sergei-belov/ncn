# ncn-authz Service Scenarios

## Scenario Inventory

| Scenario | Actor/system | Requirement/feature | Interfaces | Models/tables |
|---|---|---|---|---|
| [SCN-001](#scn-001-resolve-the-current-user) | External/local authenticated user | AUTHZ-REQ-001/002/007/008; FEAT-004 | API-AUTHZ-001/002 | MODEL-AUTHZ-001/003; TABLE-AUTHZ-001 |
| [SCN-002](#scn-002-authorize-a-project-service-action) | Admin/member/viewer; consumer service | AUTHZ-REQ-003..006/009; FEAT-004 | API-AUTHZ-003 | MODEL-AUTHZ-002..004; TABLE-AUTHZ-002 |
| [SCN-003](#scn-003-handle-identity-data-and-dependency-failures) | User/operator/consumer | AUTHZ-REQ-002/008/010; FEAT-004 | API-AUTHZ-001..003 | TABLE-AUTHZ-001/002 |

## SCN-001: Resolve the Current User

### Actor and Goal

An externally authenticated or local user wants all backend services to recognize one persisted application identity.

### Preconditions and Permissions

External identity reached the backend through the verifying edge, or the bearer was issued by enabled local authentication. Its normalized email identifies one active persisted User. No project permission is required for the current-user operation.

### Trigger

The caller requests the current-user operation or a consumer route that requires an authenticated actor.

### Happy Path

1. The common authentication helper decodes the bearer identity and normalizes email.
2. The common dependency calls the generic User repository filter by email.
3. Exactly one User DTO is returned and password is excluded from public serialization.
4. The persisted UUID becomes the actor, authorized log identity, audit identity, and user rate-limit key.
5. The consumer receives the same actor and begins only its authorized work.

### Alternatives and Edge Cases

Local registration normalizes email and stores only a password hash. Local login accepts normalized email and returns a locally signed bearer. Provider users may have no password. Mixed-case bearer email resolves the normalized row. Concurrent duplicate local registration returns one success and one stable duplicate error.

### Failure and Recovery

Malformed/invalid bearer or absent User returns `401 AUTH_REQUIRED`; the caller reauthenticates or the identity owner provisions/reconciles the User. Local routes outside local mode return `404 AUTH_ROUTE_DISABLED`. Invalid credentials return `401 INVALID_CREDENTIALS`. Consumer work does not start on failure.

### Accessibility

The service owns no screen. Consumer UI must announce sign-in expiry, invalid credentials, and retry/provisioning guidance through semantic alerts and focus-safe navigation.

### Observable Result

The response/consumer actor and operational identity all use one persisted User UUID, with no password or bearer disclosure.

### Traceability

AUTHZ-REQ-001/002/007/008; AUTHZ-INV-002/006; FEAT-004; API-AUTHZ-001/002; MODEL-AUTHZ-001/003; TABLE-AUTHZ-001; DEC-AUTHZ-001/004.

## SCN-002: Authorize a Project Service Action

### Actor and Goal

An admin, member, or viewer wants to invoke a project-scoped operation in PMS, agent configuration, or another backend service.

### Preconditions and Permissions

SCN-001 succeeded. The path has a workspace and project identifier. ProjectUser may or may not exist. The consumer names an action from the common policy and retains ownership of its domain/archive/reference checks.

### Trigger

A project-scoped FastAPI route requests the common authorized actor dependency.

### Happy Path

1. The common layer joins persisted User, exact project/workspace reference, and ProjectUser.
2. It rejects absent relation/role and validates the role enum.
3. It evaluates the stored role against the consumer service action.
4. It logs persisted user UUID, safe path/method, project role, consumer, and action.
5. The consumer manager receives the authorized actor and rechecks project scope, current relation/action, archive state, and its domain invariants.
6. The consumer commits and returns canonical state; permission projections may be returned for UI rendering.

### Alternatives and Edge Cases

A viewer receives read-only domain state; a member receives day-to-day actions but no administration; an admin receives registered administration actions. A relation for another project/workspace is ineffective. Removing or changing a role affects the next request. Project collection listing filters by ProjectUser; creation accepts a persisted user and establishes creator admin membership atomically because no project role exists before creation.

### Failure and Recovery

Missing relation or disallowed action returns `403 FORBIDDEN`; the user waits for membership/role change and does not blind retry. A consumer may use disclosure-safe `404` for independently hidden resources. Archived or invalid domain state is a consumer denial. Database failure produces no consumer side effect. Stale consumer mutations reload canonical state and use current expected versions in JSON.

### Accessibility

No common UI exists. Consumers expose text-based permission denial/read-only reasons, do not rely on hidden controls as enforcement, preserve focus, and provide keyboard-accessible navigation away or retry after authorized state changes.

### Observable Result

All services produce the same allow/deny result for the same User, ProjectUser role, project scope, and named action; consumer-specific domain rules may further deny but never elevate.

### Traceability

AUTHZ-REQ-003..006/009; AUTHZ-INV-001/003..005; FEAT-004; API-AUTHZ-003; MODEL-AUTHZ-002..004; TABLE-AUTHZ-002; DEC-AUTHZ-001..003; PMS SCN-003; agents SCN-001.

## SCN-003: Handle Identity, Data, and Dependency Failures

### Actor and Goal

A user or operator wants a deterministic denial/recovery path when identity data, membership data, rate capacity, schema, or PostgreSQL is unavailable or inconsistent.

### Preconditions and Permissions

The caller attempts an authentication or protected operation; the common layer may encounter invalid input, duplicate data, rate exhaustion, missing schema, or dependency failure.

### Trigger

An auth/common dependency or schema integrity check fails.

### Happy Path

1. The common layer classifies the failure before consumer work.
2. It returns a stable safe status/code or fails readiness for structural data problems.
3. It records only safe operational context; persisted user UUID is present only if resolution completed.
4. The caller follows the allowed recovery, or the operator repairs/provisions data and verifies constraints.
5. A later request re-evaluates canonical PostgreSQL state.

### Alternatives and Edge Cases

Duplicate normalized email or project/user relation is a data-quality violation. Invalid role is denied rather than defaulted. A process-local user rate window resets on restart and is not a distributed security quota. Legacy membership data requires an approved backfill rather than implicit reinterpretation. A gateway bypass finding blocks external-token production use.

### Failure and Recovery

Authentication and permission denials are not automatically retried. Transient database reads may be retried only by infrastructure policy before consumer side effects. Schema/data-quality failures block readiness. Migration rollback restores the prior compatible schema until integrity evidence passes.

### Accessibility

Consumers distinguish sign-in, access-required, rate-limited, and service-unavailable states in text with non-destructive retry. Operator-only diagnostics do not leak into user messages.

### Observable Result

No consumer side effect occurs on common-layer failure; stable error/health evidence identifies the failure class without sensitive data.

### Traceability

AUTHZ-REQ-002/008/010; AUTHZ-INV-003/006; FEAT-004; API-AUTHZ-001..003; TABLE-AUTHZ-001/002; AUTHZ-NFR-001..005; service acceptance.
