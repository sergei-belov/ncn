# Decisions

## Decision Inventory

| ID | Decision | Status | Affected contracts |
| --- | --- | --- | --- |
| DEC-001 | Use an NCN-owned User/access hierarchy without copying workspace/project business ownership. | Accepted constraint | REQ-004/005/008/009; DATA-001..004 |
| DEC-002 | OIDC identifies Users while persisted memberships remain the only authorization truth. | Accepted user direction | REQ-001/003..006; API-001..006; DATA-001..004 |
| DEC-003 | Use verified normalized email as the MVP SSO User key; defer issuer/subject identity links. | Proposed, trust carrier Open | REQ-001/002; API-001/007; DATA-001 |
| DEC-004 | Extract incrementally with one write authority, compatibility adapters, shadow parity, and fail-closed network checks. | Proposed | REQ-007..009; API-002/005; delivery |
| DEC-005 | Use guarded workspace/project roles and a narrowing service restriction; omit durable audit and command receipts from MVP. | Proposed | REQ-004..006/010; API-003/004/006; DATA-002..004 |
| DEC-006 | Let the NCN frontend call browser-facing authz APIs directly through authenticated ingress. | Accepted user correction | REQ-001/004..007; UX-001..004; API-001/003/004/006 |

## DEC-001: Use a Scoped Access Hierarchy and Preserve NCN Domain Ownership

### Status

**Accepted constraint.**

### Context

Current NCN persists Users and ProjectUsers. The requested feature adds workspace memberships and optional per-service restrictions while the repository contract keeps PMS as the workspace/project system of record.

### Decision

Use DATA-001 User, DATA-002 WorkspaceUser, DATA-003 ProjectUser, and DATA-004 ServiceUser. Preserve current User UUIDs and valid ProjectUser roles. Store only opaque PMS scope references in authz and validate lifecycle through owner interfaces. Do not copy workspace/project business models or metadata.

### Drivers

- NCN needs workspace/project role and service-access administration.
- Domain ownership must remain unambiguous.
- Existing actor and project membership IDs must remain compatible.

### Alternatives

- **Copy workspace/project business state into authz:** rejected because it duplicates PMS ownership.
- **Keep only User/ProjectUser:** rejected because workspace roles and optional service access are in scope.
- **Store workspace/project membership in PMS:** rejected because the root contract assigns authorization data to `ncn-authz`.

### Consequences

Authz needs PMS scope validation and lifecycle coordination without cross-service foreign keys. Migration must inventory current User/ProjectUser state and prove compatibility. Service restrictions are additive and optional.

### Reversal Conditions

Reopen only through a project architecture decision that changes domain ownership or eliminates workspace/service-scoped access.

### Affected Contracts

REQ-004/005/008/009; INV-003..006; SCN-002..006; API-002..006; DATA-001..004; SLICE-001/003/004/005.

## DEC-002: OIDC Identifies Users; Persisted Memberships Authorize

### Status

**Accepted user direction.**

### Context

The user explicitly limits SSO to OIDC identity input and `ncn-authz` to users, workspace/project roles, and access. Identity and authorization must therefore remain separate contracts.

### Decision

SSO authentication contributes only required `email`, required `email_verified=true`, and optional `name` to DATA-001 resolution. These identity claims do not create, update, revoke, or constrain DATA-002..004.

Roles change only through the protected workspace/project/service administration APIs or PMS creator bootstrap. API-002 reads committed DATA-001..004 and accepts no OIDC identity input or caller-computed role.

### Drivers

- One comprehensible authorization source of truth.
- No hidden role changes on login.
- Independence between identity-provider configuration and NCN access policy.
- Immediate next-request effect from persisted mutation/revocation.

### Alternatives

- **Derive access from SSO attributes:** rejected as explicitly out of scope and a second policy source.
- **Reconcile memberships at every SSO session:** rejected because login must not mutate access.

### Consequences

New SSO Users start with no access until explicitly assigned. Operators manage access through application APIs. Identity integration needs only the allowlisted OIDC identity fields and no access-reconciliation jobs or identity-provider administration UI.

### Reversal Conditions

Reopen only if product explicitly introduces provider-managed access and accepts a separate specification covering provenance, reconciliation, revocation, migration, and security.

### Affected Contracts

REQ-001/003..006; INV-001/008; SCN-001..004; API-001..006; DATA-001..004; SLICE-002..004.

## DEC-003: Verified Normalized Email Is the MVP SSO User Key

### Status

**Proposed.** Exact oauth2-proxy carrier and non-bypass proof are **Open** and block production enablement.

### Context

Current NCN resolves users by email. A separate issuer/subject link would better tolerate email change and multiple providers, but the user questioned its MVP need and requested narrower scope.

### Decision

For MVP, oauth2-proxy remains the browser SSO boundary and `ncn-authz` resolves DATA-001 by one canonical normalized provider-verified email. It may refresh a bounded display name. A first valid session may create an active User with no roles. A collision, unverified/missing email, or disabled User fails safely.

Do not add a UserIdentity table. Do not persist tokens or full OIDC payloads. Email change, account merge, and multi-provider linking are deferred rather than guessed.

### Drivers

- Matches the current NCN User data shape.
- Avoids an unneeded MVP entity and migration.
- Keeps SSO responsibility limited to User identification.
- Preserves local development compatibility around the same User row.

### Alternatives

- **Issuer/subject UserIdentity table now:** technically stronger for account continuity but deferred until a concrete provider/change requirement justifies it.
- **Provider-issued email as an unnormalized key:** rejected because case/format variation can duplicate Users.
- **Trust browser-submitted email:** rejected because it bypasses the identity trust boundary.

### Consequences

The IdP must provide a verified email unique enough for MVP. Changing email may require support and can interrupt access until resolved; automatic merge is forbidden. Canonicalization must be identical in SSO, local auth, lookup, and migration.

### Reversal Conditions

Introduce a stable identity-link design before onboarding a provider without stable verified email, supporting automatic email changes/multiple providers, or resolving evidence that email uniqueness is insufficient.

### Affected Contracts

REQ-001/002; INV-002/008; SCN-001/005; UX-001; API-001/007; DATA-001; SLICE-001/002.

## DEC-004: Incremental Extraction With One Write Authority and Shadow Parity

### Status

**Proposed.** Physical deployment topology and consumer inventory are verified during SLICE-001.

### Context

Users and ProjectUsers are currently read by shared-backend code. A direct cutover risks identity changes, role drift, latency regressions, and fail-open consumer behavior. PMS project creation also needs access bootstrap across a service boundary.

### Decision

Use expand/contract schema evolution and compatibility adapters. Keep exactly one write authority for each access relation. Build the new evaluator, compare it in shadow against the active path, resolve all unauthorized mismatches, then cut consumers over incrementally with bounded timeouts and rollback routing.

Preserve User UUIDs and valid ProjectUser roles. API-005 uses a naturally idempotent unique `PUT`, while PMS keeps a project non-ready or compensates until creator access is confirmed. Do not create a command-receipt table.

### Drivers

- No authorization outage or silent access drift.
- Reversible deployment and measurable parity.
- Stable identifiers for downstream references.
- Explicit cross-service project provisioning behavior.

### Alternatives

- **Big-bang database/service move:** rejected because rollback and parity evidence would be weak.
- **Dual writers:** rejected because divergent role state is unsafe.
- **Consumer fallback to copied roles on timeout:** rejected because it can preserve revoked access or grant inconsistently.
- **Command-receipt persistence:** deferred because uniqueness, versions, `PUT`, and canonical reads cover MVP retry behavior.

### Consequences

Delivery requires temporary adapters, shadow telemetry, consumer allowlist rollout, and an observation window. A network call adds latency and availability obligations. Cleanup is a later explicit change.

### Reversal Conditions

Reopen if implementation remains a single deployment/database with no service boundary, or if measured network constraints require an approved alternative with equally strong revocation and consistency semantics.

### Affected Contracts

REQ-007/008/009; INV-003/005/007; SCN-002/005/006; API-002/005; DATA migration/consistency; SLICE-001/003/005.

## DEC-005: Guarded Scoped Roles With Narrowing Service Access

### Status

**Proposed.** Workspace owner-transfer and allowed service catalog are **Open** before those mutations are enabled.

### Context

The required scope is application users plus workspace/project roles and access. The user also explicitly excludes extra MVP audit/receipt/decision entities.

### Decision

Use workspace roles `owner > admin > member` and project/service roles `admin > member > viewer`. DATA-003 is the project capability ceiling. If DATA-004 is absent, service access inherits the project role; if present, it may only equal or narrow that role.

Mutation managers enforce actor scope/ceiling, active target User, authoritative scope validation, unique membership, optimistic version, and last workspace owner/project admin protection in the same transaction. No actor may grant above their own effective authority. Access mutations emit privacy-safe structured logs but no durable domain-audit row. No command receipt is used.

### Drivers

- Simple explainable role semantics.
- Protection from privilege escalation and orphaned administration.
- Simple project-service restriction without generalized ACLs.
- Narrow MVP persistence boundary.

### Alternatives

- **Service roles independent of project membership:** rejected because they could elevate or orphan access.
- **No service restrictions:** possible simplification but does not cover the requested scoped-access model; it can be removed only by product decision.
- **Custom permissions/ACL rows:** deferred because named action policy over fixed roles is sufficient for MVP.
- **Durable audit/receipt/decision entities:** deferred until a concrete compliance or retry requirement exists.

### Consequences

Parent-role changes must validate existing restrictions. UI/API must explain inherited versus restricted access and concurrency conflicts. Logs provide operational evidence but are not an immutable compliance ledger.

### Reversal Conditions

Reopen when product needs custom roles, positive service grants beyond a project role, immutable compliance audit, or different workspace owner semantics.

### Affected Contracts

REQ-004..006/010; INV-003/004/006/008; SCN-002..004; UX-002..004; API-002/003/004/006; DATA-002..004; SLICE-003/004.

## DEC-006: Direct Frontend-to-Authz Browser Interfaces

### Status

**Accepted user correction.**

### Context

Earlier planning incorrectly routed browser authorization functions through `ncn-portal-api`. The user confirmed that service does not exist and must be removed. Authz-owned session/access behavior still requires browser APIs.

### Decision

The NCN frontend calls API-001/003/004/006 directly through a same-origin Traefik/oauth2-proxy route. `ncn-authz` owns browser API concerns for its domain: session identity, CSRF/origin checks, pagination, validation, stable errors, and safe response shaping.

API-002/005 remain internal workload-authenticated interfaces. Domain-resource APIs remain with their owner; authz is not a general frontend aggregator or proxy.

### Drivers

- Matches the actual architecture and explicit user direction.
- Keeps access APIs with their data/policy owner.
- Avoids inventing a nonexistent dependency.
- Preserves the central oauth2-proxy SSO boundary.

### Alternatives

- **Use a portal/aggregation service:** rejected because it does not exist and is outside this feature.
- **Put access mutations in PMS:** rejected because authz owns membership policy/state.
- **Expose internal decision API to the browser:** rejected because workload and browser trust boundaries differ.

### Consequences

Traefik needs an explicit same-origin authz route. The frontend needs a direct authz adapter. Browser routes require CSRF/origin protection and user-safe errors; no aggregation service is introduced.

### Reversal Conditions

Reopen only if a future accepted architecture introduces an actual frontend boundary and includes migration/ownership/security contracts.

### Affected Contracts

REQ-001/004..007; SCN-001/003..005; UX-001..004; API-001/003/004/006; technical dependencies/security; SLICE-002/004.

## Open Decision Queue

| Decision needed | Affected contract | Owner / evidence | Deadline |
| --- | --- | --- | --- |
| Exact verified email carrier and ingress bypass proof | API-001, DEC-003 | Platform identity owner + deployment integration test | Before SLICE-002 production enablement |
| Canonical workspace ID and PMS validation/lifecycle interface | DATA-002/003, API-003/006 | PMS owner contract | Before workspace/project writes |
| Workspace owner creation/transfer policy | REQ-004/006, API-006, UX-004 | Product/security approval | Before owner mutation enablement |
| Allowlisted service catalog and ownership | DATA-004, API-004 | PMS/service owners | Before service restrictions |
| Same-origin route and CSRF mechanism | API-003/004/006, DEC-006 | Platform/frontend security test | Before browser mutations |
| PMS non-visible/compensation behavior on bootstrap failure | REQ-009, API-005 | PMS/authz owners | Before SLICE-005 |
| Decision latency/SLO and Loki retention targets | NFR-001/003 | Platform/security evidence | Before production cutover |
| Post-MVP email-change/account-link recovery | DEC-003 deferred scope | Product/security plus provider evidence | Non-blocking for MVP if collision fails safely |
