# Delivery Plan

## Delivery Strategy

Deliver the feature as five dependency-ordered vertical slices. Start with evidence, compatibility, and a shadow seam; then establish SSO User resolution; introduce fail-closed network decisions; add direct workspace/project access administration; and finish PMS bootstrap plus physical authority cutover. Keep one write authority throughout and remove temporary compatibility only after an observation window.

This plan creates documentation only. All implementation surfaces and migrations below are **Planned** until verified in the development workflow.

The MVP persists only DATA-001..004. It has no UserIdentity, durable authz audit, command receipt, or decision table. The frontend uses `ncn-authz` directly through authenticated ingress.

## Dependency Map

```text
Open trust/data contracts
        │
        ▼
SLICE-001 Compatibility inventory + shadow seam
        │
        ├───────────────┐
        ▼               ▼
SLICE-002 SSO User   SLICE-003 Network decisions
        │               │
        └───────┬───────┘
                ▼
SLICE-004 Workspace/project access administration
                │
                ▼
SLICE-005 PMS bootstrap + physical authority cutover
```

SLICE-003 may build after SLICE-001 while the edge contract for SLICE-002 is finalized, but active browser access and final cutover require both. SLICE-004 requires the PMS scope contract, CSRF route, and owner/service policies. SLICE-005 requires the PMS provisioning/compensation decision.

## Slice Inventory

| Slice | Observable outcome | Primary requirements | Main risk retired |
| --- | --- | --- | --- |
| SLICE-001 | Current identities/roles are inventoried and new decisions can be compared without changing users | REQ-008/010 | Unknown data and semantic drift |
| SLICE-002 | Valid SSO sessions resolve one User and never create roles | REQ-001/002/010 | Identity trust/collision and production local-auth risk |
| SLICE-003 | One pilot consumer uses a fail-closed named authorization check with parity evidence | REQ-003/005/007/010 | Policy/network behavior |
| SLICE-004 | Authorized admins directly manage workspace/project roles and service restrictions | REQ-004..007/010 | Privilege escalation, concurrency, accessibility |
| SLICE-005 | PMS creator access converges exactly once and authority can move safely | REQ-008..010 | Cross-service provisioning and extraction |

## SLICE-001: Compatible Data and Decision Seam

### Outcome

The team has an approved inventory/repair report for current Users and ProjectUsers, stable role/action semantics, additive DATA-001..004 schema plans, and a compatibility/shadow seam that observes new decisions without changing the active result.

### Dependencies

- Read current backend models/dependencies/tests and `docs/services/ncn-authz/**` during implementation.
- Confirm production/backup data source and privacy-approved inventory procedure.
- Draft registered action/scope and role matrix with consumer owners.
- Resolve any role values or membership shapes that cannot map to the feature contract.

### In Scope

- Inventory User UUIDs, normalized emails/collisions, active state, password-null distribution, ProjectUser IDs/roles/duplicates, workspace/project references, and projects without admins.
- Produce deterministic repair proposals; do not invent roles or merge Users automatically.
- Define canonical email normalization once.
- Plan/create expand-only compatible schema for DATA-002/004 and required DATA-001/003 fields/constraints through the implementation workflow.
- Add repository/DTO/policy seams compatible with current consumers.
- Register named actions and compare current versus proposed decisions in shadow with safe correlation logging.
- Establish dashboards for data-quality, parity, latency, and failure signals.

### Out of Scope

- Production SSO enablement.
- Network decision cutover.
- Workspace/project access mutations.
- Identity-link, durable audit, receipt, or decision tables.
- Cleanup of legacy reads/writes.

### Implementation Surfaces

**Verified evidence:** current `backend/models/sqlalchemy/users.py`, `project_users.py`, auth dependencies/services, relevant tests, and service docs. Exact symbols must be re-inventoried at implementation start because this plan does not freeze code layout.

**Planned:** additive SQLAlchemy models/fields and migration files, compatibility repositories/DTOs, named policy registry/evaluator seam, shadow hook, reconciliation command/report, metrics/log configuration, tests, and runbooks. The applicable backend workflow decides concrete paths; no migration exists from this plan.

### Contract Changes

Implements the compatibility/migration portions of DATA-001..004, DEC-001/004, and the shadow form of API-002. It must not expose new browser writes.

### Validation

- Unit: canonical email, enum/role ordering, service ceiling, action registry, and stable reason translation.
- Data contract: unique/collision/invalid-role/orphan/missing-admin fixtures and deterministic repair output.
- Compatibility: serialize current DTO/error behavior and preserve User/ProjectUser UUIDs.
- Shadow: approved matrix across workspace/project/service actions, including deny cases and optional OIDC display-name changes with no access effect.
- Security: logs/capture contain no email where unnecessary, password/hash, bearer, or full OIDC payload.
- Restore: backup/restore rehearsal and reconciliation rerun produce the same counts/IDs/roles.

### Acceptance Criteria

- AC-008 inventory and reconciliation evidence is reviewed; unresolved collision/invalid access blocks cutover.
- Shadow mismatches are explainable, classified, and do not affect active behavior.
- AC-010 safe telemetry is queryable by correlation ID and contains no prohibited data.
- No second write authority or new role source exists.

### Rollout and Rollback

Deploy additive schema/seams dark, then enable shadow observation for allowlisted traffic. Rollback disables the shadow hook and reverts readers to unchanged current behavior; additive schema remains untouched for diagnosis. Never roll back by rewriting IDs or roles.

### Documentation Updates

Update inventory evidence, resolved assumptions, action matrix, migration notes, current implementation paths, dashboards, and runbooks in this package and affected service docs.

## SLICE-002: SSO User Resolution From OIDC Identity Claims

### Outcome

Through the proven oauth2-proxy route, required `email` with `email_verified=true` and optional `name` resolve or lazily create exactly one active User; repeated login preserves the User UUID, OIDC identity input creates no access, and production local credential routes are disabled.

### Dependencies

- SLICE-001 canonical email and data repairs.
- Exact oauth2-proxy identity carrier, verified-email evidence, spoofed-header removal, route non-bypass proof, and test fixture.
- Product/support agreement that email collision/change fails safely in MVP.
- Direct same-origin route for API-001.

### In Scope

- Trusted identity adapter and API-001 session/current-user behavior.
- DATA-001 lookup-or-create transaction with canonical-email uniqueness and safe profile refresh.
- Disabled/missing/unverified/colliding identity errors and browser recovery.
- Bounded current workspace/project scope summaries from persisted memberships.
- API-007 compatibility and production disablement tests.
- Identity outcome metrics/logs and ingress security tests.

### Out of Scope

- UserIdentity/issuer-subject linking.
- Any SSO-derived access behavior or membership reconciliation on login.
- Workspace/project access administration.
- Automatic email-change merge/recovery.

### Implementation Surfaces

**Verified evidence:** current NCN email-based auth/User model and oauth2-proxy architecture contract.

**Planned:** authz identity adapter/manager/repository/router/schema, trusted-header/token integration configuration, frontend direct authz session adapter and UX-001 states, local-route deployment guard, integration/security tests, dashboards, and runbook.

### Contract Changes

Implements REQ-001/002/010, SCN-001, UX-001, API-001/007, DATA-001, and DEC-002/003/006.

### Validation

- Unit: email normalization/validation, active/disabled state, safe name refresh, and no role mutation code path.
- Integration: first/repeat/concurrent login, case variation, empty memberships, collision, database rollback, and production local-route denial.
- Trust boundary: spoofed headers/direct route rejected; only verified edge email accepted.
- Identity/access separation: changing optional `name` or adding unaccepted carrier fields does not change DATA-002..004 or API-001 access summaries.
- UI: loading, empty, disabled, dependency failure, retry, focus, live announcements, deep-link refresh.
- Secret capture: no bearer, password/hash, full OIDC payload, or full carrier in response/log/metric.

### Acceptance Criteria

- AC-001 and AC-002 pass in the deployment-shaped integration environment.
- AC-010 identity telemetry is safe/queryable.
- A new SSO User has no role unless access already exists or an authorized NCN manager or PMS later creates it.
- Edge trust and non-bypass proof are attached before production enablement.

### Rollout and Rollback

Enable for test identities, then pilot workspace, then a measured percentage/all users. Rollback disables API-001 routing and returns browser identity handling to the compatible previous path; DATA-001 UUIDs remain canonical and are not deleted automatically.

### Documentation Updates

Record the final carrier, normalization rule, deployment guard, collision runbook, API examples/errors, and verified frontend/backend paths. Keep subject-link/email-change work Deferred.

## SLICE-003: Network Authorization and Consumer Cutover

### Outcome

At least one pilot consumer uses API-002 for a named workspace/project/service action, with fail-closed timeout behavior and verified parity against the current active decision path.

### Dependencies

- SLICE-001 action matrix, policy seam, data quality, and shadow telemetry.
- Workload identity and consumer/action allowlist.
- Approved timeout/SLO and error translation for the pilot.
- SLICE-002 active User semantics before broad production cutover.

### In Scope

- Internal API-002 request validation, workload auth, allowlisting, stable responses/errors, and finite deadlines.
- Policy evaluation over DATA-001..004 only.
- Project-role ceiling, service inheritance/restriction, disabled User, missing membership, scope mismatch, and unknown-action behavior.
- Shadow comparison and per-consumer active switch.
- Consumer adapter with no local copied-role fail-open path.
- Decision metrics/logs and rollback routing.

### Out of Scope

- Browser exposure of API-002.
- Decision caching or persisted decision rows.
- Custom roles/resource ACLs.
- Workspace/project access management UI.

### Implementation Surfaces

**Verified evidence:** current authorization dependencies and service docs; exact pilot consumer is **Open** until inventory.

**Planned:** internal router/schema, workload authentication, action registry/evaluator, consumer client/adapter, timeout/error translation, policy matrix tests, shadow comparator, dashboards/alerts, and runbooks.

### Contract Changes

Implements REQ-003/005/007/010, SCN-002/005, API-002, the decision use of DATA-001..004, and DEC-002/004/005.

### Validation

- Contract: all registered action/scope combinations and stable allow/deny/error reasons.
- Integration: active/disabled User, workspace role, project role, absent/present service restriction, unknown action, invalid scope, database failure, timeout, retry budget.
- Security: unauthorized workload/action family rejected; OIDC identity input and caller-computed roles rejected by API-002.
- Parity: current/new decisions match approved semantics for representative and boundary fixtures; changed optional OIDC display name has no effect.
- Load/resilience: p95/p99 against approved SLO, bounded pools, dependency loss, recovery, and no allow fallback.

### Acceptance Criteria

- AC-003/005/007/010 pass for the pilot.
- Zero unresolved security-increasing active/shadow mismatch before activation.
- Consumer timeout and authz error cannot produce a protected side effect.
- Logs/metrics identify decision reason and correlation without persisted decision records or sensitive payload.

### Rollout and Rollback

Run shadow first, activate one low-risk action/consumer, observe, then expand the allowlist. Rollback routes that consumer to the compatible prior evaluator while PostgreSQL data remains unchanged. Sustained unavailability or any unauthorized mismatch automatically blocks further rollout.

### Documentation Updates

Record action registry, consumer inventory, SLO/timeouts, error translations, parity evidence, dashboards, alerts, and rollback commands in owner docs and this package.

## SLICE-004: Workspace and Project Access Administration

### Outcome

Authorized browser users directly list and safely manage workspace membership, project membership, and optional service restrictions with complete permission, concurrency, recovery, responsive, and accessibility behavior.

### Dependencies

- SLICE-002 trusted browser User/session path.
- SLICE-003 policy evaluator for actor authorization.
- Canonical PMS workspace/project validation and service allowlist contracts.
- Approved workspace owner creation/transfer policy.
- Same-origin Traefik route and accepted CSRF mechanism.
- User-search/privacy contract for selecting target Users.

### In Scope

- API-006 and DATA-002 workspace list/add/change/revoke with last-owner and actor-ceiling guards.
- API-003 and DATA-003 project list/add/change/revoke with last-admin and actor-ceiling guards.
- API-004 and DATA-004 service restriction create/change/remove with inheritance/ceiling semantics.
- Optimistic versions, unique constraints, transactional privileged-member checks, and canonical-read recovery.
- Direct frontend authz adapter and UX-002/003/004, including responsive and all applicable states.
- Privacy-safe mutation logs/metrics and operational alerts.

### Out of Scope

- Identity-provider-managed roles or an identity-provider administration UI.
- Workspace/project business editing.
- Invitations, bulk import, temporary grants, access approvals, custom roles.
- Durable audit rows or command receipts.

### Implementation Surfaces

**Verified evidence:** current NCN frontend route/settings/member/shared-UI patterns and backend role checks. Concrete reuse is revalidated before edits.

**Planned:** workspace/project/service repositories/managers/schemas/routers; PMS validation adapter; direct frontend entity/API state, access pages/components/dialogs, routes/navigation/permission guards; unit/integration/E2E/accessibility/concurrency tests; dashboards and runbook.

### Contract Changes

Implements REQ-004..007/010, SCN-003/004/005, UX-002..004, API-003/004/006, DATA-002..004, and DEC-001/005/006.

### Validation

- Unit: role ordering, actor ceiling, owner policy, last owner/admin, service ceiling/inheritance, version, scope relationship, and stable errors.
- Transaction/concurrency: duplicate add, simultaneous demotion/revoke, stale patch, parent demotion with restrictions, ambiguous response/canonical recovery.
- Integration/security: direct authenticated route, CSRF/origin, cross-workspace/project concealment, unauthorized User, invalid service, database/PMS failures, no partial writes.
- Frontend E2E: loading/empty/populated, add/change/revoke, service restriction removal/inheritance, validation, duplicate, stale, permission loss, degraded/offline, success/focus recovery.
- Accessibility: keyboard-only, screen reader, 200% zoom, contrast, semantic table/cards/dialogs, live regions, reduced motion.
- Telemetry: safe actor/target/scope/before/after/result and no email/raw identity in generic logs.

### Acceptance Criteria

- AC-004/005/006/007/010 pass for pilot workspaces/projects.
- Concurrency tests cannot remove the last owner/admin or create duplicates/elevation.
- UI never reports success until canonical server state commits and reloads.
- Direct frontend operation has no runtime dependency on an aggregation service.

### Rollout and Rollback

Deploy APIs dark, enable read-only lists for pilot admins, then mutations by scope/operation feature flag. Rollback disables mutation UI/routes and browser write allowlist while retaining canonical data and API-002 reads. Do not delete committed memberships during rollback.

### Documentation Updates

Record final owner-transfer/service-catalog/User-search contracts, routes, component reuse, errors, screenshots/accessibility evidence, operation runbook, and role/action matrix.

## SLICE-005: Project Bootstrap and Physical Extraction

### Outcome

PMS project creation establishes creator admin exactly once before readiness, and approved consumers/data authority can move to the standalone boundary with reversible rollout and reconciled state.

### Dependencies

- SLICE-001 compatibility and clean data.
- SLICE-002 stable User UUID resolution.
- SLICE-003 active decision path and SLO evidence.
- SLICE-004 guarded ProjectUser manager.
- Approved PMS non-visible provisioning/compensation and lifecycle validation contract.
- Backup/restore and deployment rollback rehearsal.

### In Scope

- API-005 naturally idempotent creator-admin `PUT` and PMS workload allowlist.
- Identical duplicate convergence, conflicting creator rejection, and canonical-read recovery after ambiguity.
- PMS provisioning/readiness or compensation behavior and correlated logs.
- Final one-write-authority switch for DATA-001..004 as applicable to deployment topology.
- Consumer rollout completion, data reconciliation, restore/rollback rehearsal, observation window, and cleanup proposal.

### Out of Scope

- Distributed database transactions.
- A command-receipt table or Kafka/Temporal workflow introduced solely for this bootstrap.
- Immediate deletion of compatibility schema/code.
- Project/workspace lifecycle ownership in authz.

### Implementation Surfaces

**Verified evidence:** current PMS/project creation paths and physical service topology must be re-inventoried; no exact implementation path is asserted here.

**Planned:** API-005 router/manager, PMS client/provisioning-state or compensation changes, workload configuration, creator-access tests, reconciliation tooling, traffic/write-authority switches, backup/restore/rollback procedures, dashboards/alerts, and later cleanup issue.

### Contract Changes

Implements REQ-008/009/010, SCN-005/006, API-005, DATA-003 bootstrap/migration, and DEC-001/004.

### Validation

- Contract/integration: first call, identical repeat, concurrent repeat, conflicting creator, disabled/missing User, invalid scope, unauthorized workload, timeout, lost response, canonical recovery.
- PMS E2E: project remains non-ready or compensates on authz failure; becomes ready only after one admin exists.
- Migration: IDs/counts/roles/source/scope/unique constraints and sampled active decisions reconcile before and after switch.
- Resilience: authz/PMS/database restart, rollback routing, backup restore, no dual writes, bootstrap drift alert.
- Security/telemetry: workload least privilege, no user credentials or full OIDC payloads, correlated safe logs across PMS/authz.

### Acceptance Criteria

- AC-008/009/010 pass with reviewed reconciliation and rollback evidence.
- Exactly one canonical creator admin exists for every ready newly created project.
- Ambiguous or conflicting bootstrap cannot expose a project as successfully ready.
- One write authority is demonstrable at each rollout step.

### Rollout and Rollback

Enable for test projects, then pilot workspace, then measured production cohorts. Switch write/read authority only after parity and restore evidence. Rollback stops new bootstrap traffic or routes through the compatible prior authority while PMS keeps affected projects non-ready/compensates. Legacy cleanup waits for the agreed observation window and separate approval.

### Documentation Updates

Update PMS/authz owner contracts, deployment topology, bootstrap sequence, workload identity, readiness/compensation states, migration evidence, dashboards, rollback runbook, and cleanup/deprecation plan.

## Cross-Slice Validation

| Concern | Required evidence before completion |
| --- | --- |
| Requirements | Every REQ-001..010 has passing acceptance evidence in its mapped scenario/slice |
| Identity | Trusted-edge proof, canonical-email collision handling, repeat/concurrent resolution, disabled state, production local-auth denial |
| Identity/access separation | Automated tests prove optional OIDC identity-field changes and unaccepted carrier fields never change DATA-002..004 or a decision |
| Authorization | Approved action/role/scope matrix, deny/error behavior, next-request revocation, workload allowlist, finite deadlines |
| Access integrity | Unique membership, role ceiling, last owner/admin, service inheritance/restriction, stale/concurrent transaction tests |
| Data migration | Counts, UUIDs, roles, scope links, collision/repair reports, parity, backup/restore, reversible authority routing |
| Browser security | Direct ingress route, CSRF/origin, permission checks, bounded inputs, safe errors, no aggregation dependency |
| UX/accessibility | All declared states, keyboard/screen-reader/zoom/contrast, responsive behavior, canonical success/recovery |
| Privacy/operations | Capture tests for prohibited secrets/full OIDC payloads, correlation-ready logs, metrics/dashboards/alerts/runbooks, approved retention |
| Cross-service bootstrap | PMS readiness/compensation and identical/conflicting/ambiguous call behavior |

## Completion Gate

- Feature package remains validated and affected project/service documentation reflects resolved contracts.
- All blocking Open questions for an enabled surface are closed by named owners and evidence.
- AC-001..010 and cross-slice evidence pass for the released scope.
- Only the allowlisted OIDC identity claims enter SSO resolution; all access originates from protected NCN APIs or PMS bootstrap. No identity-link table, durable authz audit table, command-receipt table, or persisted decision entity exists in MVP.
- No active browser or runtime path depends on `ncn-portal-api` or another invented aggregation service.
- One write authority, fail-closed consumer behavior, migration parity, restore, and rollback are demonstrated.
- Security, privacy, accessibility, SLO, dashboards, alerts, and runbooks receive owner sign-off.
- Legacy cleanup is separately scheduled after the observation window; completion does not require premature deletion.
