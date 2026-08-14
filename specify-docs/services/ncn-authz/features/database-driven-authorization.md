# Feature: Database-Driven Authorization

## Status

Owning service: `ncn-authz` common backend layer  
Status: Active contract; common source **Present**, migration and independent deployment **Open**  
Owner: Platform authorization team  
Last reviewed: 2026-08-14  
Evidence: explicit user rules and supplied dependency example; authorized verification of current shared backend authorization surfaces.

## Problem and Goal

All backend services need the same actor, project membership, role policy, denial, logging, and tracking semantics. Duplicating these rules in PMS or reading authorization from token/configuration would let services disagree. This feature establishes one shared path: normalized bearer email → persisted User → optional project relation → stored role → common service-action policy → consumer domain guard.

## Actors and Permissions

| Actor/system | Goal | Allowed | Forbidden/constrained |
|---|---|---|---|
| Persisted user | Become one application actor | Current-user access and authorized service collections | No permission from token claims |
| Admin/member/viewer | Use a related project under one stored role | Common actions registered for that role | No cross-scope or consumer-domain bypass |
| Consumer service | Receive a trustworthy actor/policy result | Enforce its named action and domain invariants | No independent claim/config policy |
| OIDC edge/local verifier | Authenticate identity | Supply verified/locally validated email | Cannot grant project role/action |
| Operator | Provision common data | Maintain normalized users and schema | No environment-based project grants |

## Scope

### In Scope

- User and ProjectUser persistence/DTO/repository contracts shared by all services.
- Generic user lookup and joined project authorization lookup.
- Authentication decoding, current-user, workspace actor, project actor, logging, and user-rate dependencies.
- Current-user and local credential HTTP operations.
- Stored-role to named service-action evaluation and stable denial behavior.
- Persisted `user.id` for actor, logs, audit identity, and user tracking after authentication.
- JSON domain IDs and expected versions instead of custom synchronous request metadata.

### Out of Scope

- PMS work rules, agent execution policy/Approval, provider account ownership, membership administration UI/API, or a completed independent deployment.
- Token/configuration application grants, consumer-owned copies of authorization data, or custom synchronous tracking/duplicate/concurrency headers.

## Requirements and Invariants

| ID | Requirement/invariant | Rationale | Acceptance |
|---|---|---|---|
| AUTHZ-FEAT-REQ-001 | All services resolve the same persisted User before protected work. | One actor across service boundaries. | Cross-service identity UUID matches. |
| AUTHZ-FEAT-REQ-002 | Project services require exact ProjectUser membership and stored role. | Database is current authorization truth. | Missing/cross-project relations deny. |
| AUTHZ-FEAT-REQ-003 | Common policy maps role to named service actions; consumers recheck domain invariants. | Separate authorization from business validation. | Role/action and domain-guard matrices pass. |
| AUTHZ-FEAT-REQ-004 | Runtime settings/claims contain authentication mechanics only. | Prevent deployment- or token-based privilege drift. | Static/negative tests pass. |
| AUTHZ-FEAT-REQ-005 | Simple email lookup uses the generic repository filter. | Avoid redundant data-access methods. | Repository contract has no thin email getter. |
| AUTHZ-FEAT-REQ-006 | Logs, audit identity, and user rate tracking use persisted User UUID after authorization. | Security evidence must identify the actual actor. | Captured keys equal stored UUID. |
| AUTHZ-FEAT-REQ-007 | Synchronous consumers use bearer plus JSON path/query/body, with domain IDs and expected versions where needed. | Keep metadata and policy deterministic. | Shared conformance test requires no custom metadata. |
| AUTHZ-FEAT-INV-001 | A token never grants workspace/project/role/action. | Only database role and common policy authorize. | Extra claims have no effect. |
| AUTHZ-FEAT-INV-002 | One project/user pair has one allowed role. | No ambiguous access. | DB/DTO constraints pass. |
| AUTHZ-FEAT-INV-003 | Permission projections are outputs only. | Clients cannot elevate themselves. | Tampering has no effect. |

## Scenarios and Contract Effects

| Scenario | UI/UX | API/events | Models/tables | Affected services |
|---|---|---|---|---|
| SCN-001 | Consumer sign-in/current-user handling | API-AUTHZ-001/002; no event | MODEL-AUTHZ-001/003; TABLE-AUTHZ-001 | All backend services/frontends |
| SCN-002 | Consumer denied/read-only states | API-AUTHZ-003; no event | MODEL-AUTHZ-002..004; TABLE-AUTHZ-002 | `ncn-pms`, `ncn-agents`, future project services |
| SCN-003 | Operational/degraded handling | API-AUTHZ-001..003; no event | TABLE-AUTHZ-001/002 | Platform and all consumers |

## Failure, Recovery, and Observability

Invalid identity/missing user returns `401 AUTH_REQUIRED`; missing relation/action returns `403 FORBIDDEN`; local-flow errors remain stable; rate limit uses the persisted user UUID. Database failures prevent consumer work and return sanitized errors. No authorization failure is retried until identity/data changes. Logs record safe method/path, persisted user UUID, project role, consumer/action, and outcome; they omit password, bearer, and sensitive domain content.

## Acceptance Criteria

- Every protected current service route receives the common persisted actor before its manager.
- User, relation, role, log, audit, and rate identities agree on one database UUID.
- Token/configuration changes cannot add project access.
- Admin/member/viewer service-action matrices and consumer domain guards pass.
- Public current-user/local-auth contracts exclude password data.
- OpenAPI/common conformance requires no custom synchronous request metadata.
- Schema verification proves normalized users and unique valid project roles.

## Assumptions and Open Questions

**Assumed:** normalized email is collision-free; persisted users may create projects and become admin; the external-token path cannot bypass verifying ingress.

**Open:** OIDC user synchronization, membership administration, legacy data/backfill, and the independent service interface/deployment remain owner decisions.

## Traceability

Project FEAT-004 / REQ-005 / INV-006 → AUTHZ-REQ-001..010 and AUTHZ-INV-001..006 → SCN-001..003 → API-AUTHZ-001..003 → MODEL-AUTHZ-001..004 → TABLE-AUTHZ-001/002 → DEC-AUTHZ-001..004 → consumer PMS/agents contracts.
