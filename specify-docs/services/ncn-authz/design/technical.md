# ncn-authz Technical Design

## Context and Status

**Present:** one shared FastAPI backend contains common authentication helpers, User/ProjectUser SQLAlchemy and DTO models, generic repositories, joined authorization lookup, current-user/local-auth routes, FastAPI actor dependencies, role-to-action mapping, safe logging, and process-local per-user rate tracking. **Planned/Open:** checked-in schema migrations, production OIDC user synchronization, membership administration, a distributed rate limiter, and independent `ncn-authz` deployment/interface.

The logical service boundary applies now even though components are physically colocated. Consumer services use the common layer and do not own copies of authorization truth.

## Components and Responsibilities

| Component/boundary | Status | Responsibility | Inputs/outputs | Owns |
|---|---|---|---|---|
| OIDC edge | External/Unknown deployment | Verify external bearer signature/issuer/audience/time/subject | Provider token → verified identity | Provider session only |
| Local/shared auth helper | Present | Verify local tokens; normalize provider/local email; hash/verify local password | Bearer/credentials → identity | Authentication mechanics, not permissions |
| User repository | Present | Generic filter lookup and persisted User writes | Email/DTO ↔ User row | User persistence access |
| Project authorization query | Present | Join User, exact project/workspace reference, and ProjectUser | Email/path → authorized projection or absence | No additional state |
| Common HTTP dependencies | Present | Build User/workspace/project actor; enforce membership; log/rate-limit by user UUID | Request/path/session → actor | Request-scoped authorization result |
| Common policy evaluator | Present current matrix | Map stored role plus consumer action to allow/deny | Role/service/action → decision/projection | Policy semantics |
| Consumer manager guard | Present in current services | Recheck current relation/action and consumer domain/archive/reference rules | Authorized actor + command → domain result | Consumer business state |
| Independent authz API/service | Planned | Preserve the same model/policy behind a network boundary if extracted | Stable identity/policy interface | Same logical data/policy, no copy |

## End-to-End Flows

Current user: bearer → auth helper → normalized email → generic User lookup → persisted actor UUID → safe log/rate identity → consumer.

Project action: current user → exact project/workspace and ProjectUser join → stored role → named service-action policy → authorized actor → consumer manager recheck → consumer transaction. Missing identity stops before authorization; missing relation/action stops before consumer work.

Project creation is the current exception to project-role input: a persisted workspace actor invokes PMS creation; one transaction writes the project, creator admin relation, and bootstrap state. Future physical separation must replace this shared transaction with an accepted owner protocol without exposing a partially accessible project.

No asynchronous authorization flow is Present. Future access events, if approved, use event and causation IDs defined by that event contract, not synchronous HTTP tracking metadata.

## State Ownership and Consistency

PostgreSQL `users` and `project_users` are authoritative. Identity/policy outputs are transient projections. There is no authorization cache; relation and role changes affect the next request. Consumer permission flags are derived display inputs. Project bootstrap is currently one shared database transaction. User registration uses uniqueness handling; schema normalization and legacy backfill remain Planned until migration evidence exists.

## Dependencies and Integrations

Depends on FastAPI dependency injection, the shared authorization helper, common async repositories, PostgreSQL, and the PMS project reference. External identity depends on a non-bypassable verifying edge. Consumers include PMS, agent configuration, and every future project-scoped backend service. Independent extraction requires bounded timeout, denial-safe failure, compatibility, and project lifecycle coordination contracts.

## Security Boundaries

External tokens are trusted only after edge verification; local tokens are signature verified. Tokens establish identity only. Normalize email, require a persisted User, require exact ProjectUser membership, validate the role enum, and evaluate a named consumer action. Never accept permission projections from clients. Keep password hashes/bearer data out of public models and telemetry. Use persisted user UUID for security evidence. Consumer domain validation may reduce access but never elevate it.

## Failure Isolation and Recovery

Authentication/membership/action failure is deterministic and stops the request before consumer side effects. PostgreSQL failure denies safely. Invalid role or duplicate identity/relation is a data-quality failure, never default access. Local registration and project bootstrap are transactional. Consumer stale writes recover through canonical read plus JSON expected versions. Schema/backfill changes require compatibility, verification, rollback, and readiness gates. Frontend/cache state is rebuilt from owners.

## Observability and Operations

Health/readiness covers PostgreSQL and structural schema expectations. Metrics cover authentication failures, missing users, membership/action denials, user-rate limits, dependency latency/errors, and data-quality violations. Authorized logs include persisted user UUID, method, safe path, project role, consumer/action, and safe outcome. They omit passwords, bearer contents, emails where not required, and consumer bodies. Access-audit persistence beyond structured logs remains Open.

## Performance and Scale

User lookup uses indexed unique email; project authorization uses project/user indexes and unique project/user relation. Authorization adds bounded reads per request. Current rate state is per process, resets on restart, and does not coordinate replicas. Production p95, user/project membership volume, database plan, pool impact, and distributed-rate policy require load evidence.

## Runtime, Compatibility, and Evolution

Current runtime is a common module inside the shared backend. All services must use it. Preserve User UUIDs, normalized email semantics, ProjectUser role values, stable errors, actor DTO meaning, named service actions, and JSON transport rules during refactoring. Independent deployment must use expand/backfill/verify/switch/contract, avoid dual policy truth, and keep consumers fail-closed if authz is unavailable.

## Alternatives

Rejected: PMS-owned authorization, per-service copied users/roles, token/config grants, client permission authority, a thin email-specific repository method, and caller-supplied tracking identity. Deferred: distributed rate limiting, access-decision events, and independent deployment. See DEC-AUTHZ-001..004.

## Traceability

AUTHZ-REQ-001..010; AUTHZ-INV-001..006; SCN-001..003; API-AUTHZ-001..003; MODEL-AUTHZ-001..004; TABLE-AUTHZ-001/002; DEC-AUTHZ-001..004; FEAT-004.
