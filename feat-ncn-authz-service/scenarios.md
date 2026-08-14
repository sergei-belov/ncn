# User Scenarios

## Scenario Inventory

| Scenario | Actors | Requirements | UX / interfaces | Delivery |
| --- | --- | --- | --- | --- |
| [SCN-001](#scn-001-resolve-and-provision-an-sso-user) | SSO user, oauth2-proxy | REQ-001/002 | UX-001; API-001/007 | SLICE-002 |
| [SCN-002](#scn-002-authorize-a-service-action) | User, consumer service | REQ-003/005/007/010 | UX-001/003; API-002 | SLICE-003 |
| [SCN-003](#scn-003-administer-workspace-access) | Workspace owner/admin | REQ-004/006/010 | UX-002/004; API-006 | SLICE-004 |
| [SCN-004](#scn-004-administer-project-access) | Project admin | REQ-005/006/010 | UX-003/004; API-003/004 | SLICE-004 |
| [SCN-005](#scn-005-handle-authz-dependency-or-data-failure) | User, consumer, operator | REQ-007/008/010 | UX-001..004; API-001..007 | SLICE-001/003/005 |
| [SCN-006](#scn-006-bootstrap-project-access) | Project creator, `ncn-pms` | REQ-009/010 | UX-001; API-005 | SLICE-005 |

## SCN-001: Resolve and Provision an SSO User

### Actor and Goal

An authenticated SSO user wants to enter NCN as the same application User on every login while access remains controlled by persisted NCN roles.

### Preconditions

- Traefik/oauth2-proxy has authenticated the browser and supplies the accepted non-spoofable identity carrier.
- The carrier contains a provider-verified email and may contain a display name.
- Production local credential routes are disabled.

### Trigger

The frontend calls API-001 through the authenticated ingress while loading the protected application shell.

### Happy Path

1. `ncn-authz` validates that the request arrived through the accepted trust path.
2. It validates and canonicalizes the verified email.
3. It resolves DATA-001 by canonical email or creates one active User with no memberships.
4. It refreshes safe display metadata without changing access relationships.
5. API-001 returns the stable User UUID and accessible-scope summary for navigation.

### Alternatives and Edge Cases

- Concurrent first sessions for the same canonical email converge through the unique constraint to one User.
- Case and surrounding whitespace normalize to the existing User.
- Only `email`, `email_verified`, and optional `name` are accepted from the OIDC identity carrier; every other field is ignored or rejected according to the finalized carrier contract.
- A new User with no memberships receives the authenticated empty-access experience, not a default role.
- A disabled User is denied before membership lookup.
- Local API-007 may create/resolve a development User only when the deployment explicitly enables local authentication.

### Failure and Recovery

Missing/unverified email, malformed identity carrier, non-unique canonical email, database failure, or untrusted route returns a stable error and creates neither a User nor membership. The UI shows a safe sign-in/support message and may retry only transient dependency failures. Email-change/collision recovery is deferred and never auto-merges accounts.

### Permissions and Accessibility

The endpoint resolves only the authenticated identity; callers cannot submit another email. Loading and errors use semantic live status, focusable retry/sign-in actions, and no color-only meaning.

### Observable Result

Repeated valid login resolves one User UUID, OIDC identity input creates no roles, and structured logs contain only safe identity outcome/reason data.

### Acceptance Links

REQ-001/002/010; INV-001/002/008; NFR-003/005; AC-001/002/010; UX-001; API-001/007; DATA-001; DEC-002/003/006; SLICE-002.

## SCN-002: Authorize a Service Action

### Actor and Goal

An authenticated consumer service wants a current allow/deny answer for a User, named action, and workspace/project/service scope.

### Preconditions

- The consumer has an allowlisted workload identity.
- The User UUID, named action, and scope identifiers use the API-002 contract.
- The policy registry includes the action and role matrix.

### Trigger

The consumer calls API-002 before performing a protected operation.

### Happy Path

1. `ncn-authz` authenticates the consumer and validates its allowed action/scope family.
2. It resolves an active DATA-001 User.
3. It loads the relevant DATA-002 and/or DATA-003 relationship.
4. For a service-scoped action it applies DATA-004 when present; otherwise it inherits the project role.
5. It evaluates the named action and returns `allowed`, a stable reason, effective role/scope, and policy version.
6. It emits bounded decision metrics and a privacy-safe structured record keyed by correlation ID.

### Alternatives and Edge Cases

- Missing membership returns deny with `NO_MEMBERSHIP`.
- A disabled User returns deny with `USER_DISABLED`.
- An explicit weaker service role narrows the project role; it never elevates it.
- Changed optional OIDC display attributes have no effect because API-002 reads only PostgreSQL access state.
- Revocation or demotion affects the next uncached request; the MVP has no decision cache.
- Unknown actions and malformed/cross-workspace scopes deny or return stable validation errors as defined by API-002.

### Failure and Recovery

Database unavailability, timeout, unavailable policy registry, or invalid authoritative state fails closed. Consumers do not fall back to local copied roles. They may retry only within their bounded operation budget and use the correlation ID for support.

### Permissions and Accessibility

API-002 is internal and not callable by browsers. The frontend translates resulting `403` behavior into a permission-denied state with a reachable return action and preserved context.

### Observable Result

The returned decision matches the persisted membership/action matrix and safe logs/metrics explain the result without persisting a decision entity.

### Acceptance Links

REQ-003/005/007/010; INV-001/002/004/005/007/008; AC-003/005/007/010; UX-001/003; API-002; DATA-001..004; DEC-002/004/005; SLICE-003.

## SCN-003: Administer Workspace Access

### Actor and Goal

A workspace owner or permitted workspace admin wants to list members and grant, change, or revoke workspace roles.

### Preconditions

- The actor has an active DATA-002 role in the target workspace and the policy permits the requested operation.
- PMS confirms the workspace identifier under the accepted owner contract.
- The target User exists and is active for mutation operations.

### Trigger

The actor opens UX-002 or submits a mutation through API-006.

### Happy Path

1. The frontend loads a paginated canonical member list from API-006.
2. The actor opens UX-004, chooses an allowed User and role, and reviews the scope.
3. The frontend submits the target and current `expected_version` for change/revoke operations.
4. `ncn-authz` checks same-origin/CSRF, actor scope, privilege ceiling, target state, version, and last-owner coverage.
5. One transaction creates, updates, or removes DATA-002.
6. The API returns canonical membership state and the UI announces success and refreshes the list.

### Alternatives and Edge Cases

- An empty list state explains how the first allowed member can be added; an established workspace cannot reach zero owners.
- Duplicate add returns the existing/conflict state and never creates another relation.
- A workspace admin cannot grant `owner`, modify a protected owner, or grant stronger authority than their own.
- Self-demotion/revocation is allowed only when another owner remains and policy permits it.
- Concurrent changes with a stale version return conflict; the UI reloads and makes the actor review the new state.
- Pagination changes do not cause duplicate or skipped stable membership IDs under the declared cursor ordering.

### Failure and Recovery

Validation errors stay attached to fields. Permission, last-owner, stale, or duplicate conflicts leave state unchanged and keep the dialog open with safe guidance. On an ambiguous dependency response, the frontend reloads canonical membership before offering a retry.

### Permissions and Accessibility

Unauthorized users receive a permission-denied surface, not disabled controls that reveal hidden actions. The list, menus, dialog, confirmation, status, and focus return work by keyboard and screen reader. Destructive revoke identifies the User and workspace in text.

### Observable Result

The member list and subsequent API-002 decisions agree with the committed workspace role; structured mutation logs contain actor, target UUID, safe workspace ID, before/after role, result, and correlation ID.

### Acceptance Links

REQ-004/006/010; INV-003/005/006/007/008; AC-004/006/010; UX-002/004; API-006; DATA-001/002; DEC-001/005/006; SLICE-004.

## SCN-004: Administer Project Access

### Actor and Goal

A project admin wants to manage project roles and optional service restrictions without exceeding their authority or leaving the project unmanaged.

### Preconditions

- The actor is an effective project admin in the target project.
- PMS confirms the project/workspace relationship.
- The service identifier, when used, is allowlisted.

### Trigger

The actor opens UX-003 or submits API-003/API-004.

### Happy Path

1. UX-003 loads the canonical project member list and effective access summaries.
2. The actor opens UX-004 and selects add/change/revoke or a service restriction.
3. The request carries the target, desired role/restriction, and `expected_version` where a row already exists.
4. `ncn-authz` validates actor authority, User/scope, privilege ceiling, service ceiling, version, and last-admin coverage.
5. One transaction changes DATA-003 or DATA-004.
6. The UI refreshes canonical state and announces the result.

### Alternatives and Edge Cases

- Adding an existing project member returns a duplicate conflict with the canonical membership ID.
- Removing DATA-004 restores inherited project access; it does not remove project membership.
- A restriction stronger than the parent ProjectUser role is rejected.
- Demoting a ProjectUser with now-invalid service restrictions requires an explicit compatible set of restriction changes or returns conflict; the server never silently broadens access.
- The last effective project admin cannot be demoted or revoked.
- Concurrent/stale changes return the canonical current version for reload.

### Failure and Recovery

Field validation is localizable. Permission, cross-scope, ceiling, last-admin, dependency, and stale conflicts leave committed data unchanged. Following an ambiguous response, the client reloads API-003/004 state before retrying.

### Permissions and Accessibility

Only permitted actions are exposed. The UI explains inheritance versus explicit restriction in text. Dialog focus, confirmation, error summary, row-menu navigation, and success announcements meet UX-004.

### Observable Result

Membership/restriction lists and next-request decisions reflect the committed state; safe mutation logs explain the change or rejection.

### Acceptance Links

REQ-005/006/010; INV-003..008; AC-005/006/010; UX-003/004; API-003/004; DATA-001/003/004; DEC-001/005/006; SLICE-004.

## SCN-005: Handle Authz Dependency or Data Failure

### Actor and Goal

A user, consumer, or operator needs predictable denial and recovery when identity, policy data, migration state, or a dependency is unavailable or invalid.

### Preconditions

- Stable error translations and correlation IDs are configured.
- Legacy and new decision paths can run in shadow mode before cutover.

### Trigger

An authz request encounters timeout, database failure, malformed data, invalid scope ownership, parity mismatch, or unavailable service.

### Happy Path

1. The failing component stops before an allow response or partial write.
2. The API returns the stable fail-closed error class and correlation ID appropriate to its audience.
3. Browser UI preserves context and offers retry, return, or sign-in recovery only when safe.
4. Internal consumers honor bounded timeouts and do not use copied role fallbacks.
5. Metrics/logs identify component, operation, safe scope, active/shadow mode, and reason.
6. Operators repair data/dependency state and validate canonical reads and parity before restoring traffic.

### Alternatives and Edge Cases

- A shadow mismatch does not affect the active decision, but blocks cutover and alerts.
- An active-path regression triggers the approved reader rollback while the previous compatible path remains available.
- Invalid roles, duplicate memberships, missing admin coverage, or email collisions block migration/cutover until repaired.
- A process restart cannot clear PostgreSQL access state.
- Degraded list UI may show already loaded rows as stale/read-only, but never permits optimistic mutation.

### Failure and Recovery

Retries are bounded and use canonical reads after ambiguous writes. Rollback changes routing/read authority rather than rewriting User or membership identifiers. Repair scripts produce reviewable reports and do not invent access.

### Permissions and Accessibility

User messages avoid leaking service internals or other memberships. Error summaries, retry controls, focus, and offline/degraded status are perceivable without color or motion.

### Observable Result

No failure grants access or leaves partial membership state; operators can correlate the safe error and restore or roll back using measured evidence.

### Acceptance Links

REQ-007/008/010; INV-002..008; NFR-001..005; AC-007/008/010; UX-001..004; API-001..007; DATA-001..004; DEC-004; SLICE-001/003/005.

## SCN-006: Bootstrap Project Access

### Actor and Goal

A project creator and `ncn-pms` need the creator to become the initial project admin exactly once as part of project provisioning.

### Preconditions

- PMS has authenticated workload identity and owns the target project UUID and workspace relationship.
- The creator is an active DATA-001 User.
- The accepted PMS non-visible provisioning or compensation contract is active.

### Trigger

PMS calls API-005 for a newly reserved project.

### Happy Path

1. PMS reserves/creates the project in its provisioning state.
2. PMS sends the project UUID, workspace ID, and creator User UUID through authenticated API-005.
3. `ncn-authz` validates the caller, User, scope relationship, and existing membership state.
4. It creates one DATA-003 `admin` row with `source=bootstrap`, or returns the identical existing row.
5. PMS marks the project ready only after canonical bootstrap success.
6. Safe correlated logs exist on both sides.

### Alternatives and Edge Cases

- A repeated identical `PUT` returns the same canonical membership and creates no duplicate.
- A request for the same project with another creator returns `BOOTSTRAP_CONFLICT` and changes nothing.
- An existing identical manual admin row satisfies access and may be returned canonically without rewriting provenance.
- Concurrent identical requests converge through the unique `(project_id,user_id)` constraint.

### Failure and Recovery

If authz is unavailable or rejects the command, PMS does not expose the project as ready and follows the accepted retry/compensation contract. After an ambiguous response PMS reads canonical project membership before retrying. No cross-database transaction is implied.

### Permissions and Accessibility

Only the PMS workload identity can call API-005. The creator UI presents provisioning/retry status and does not claim completion until access is established; status is announced accessibly.

### Observable Result

One creator admin exists before the project becomes ready, duplicates converge, conflicts fail safely, and correlated logs support recovery.

### Acceptance Links

REQ-009/010; INV-003/005/006/007/008; AC-009/010; UX-001; API-005; DATA-001/003; DEC-001/004; SLICE-005.
