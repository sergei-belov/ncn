# UI/UX Design

## Applicability

Applicable. The existing NCN frontend gains a protected-session state plus workspace and project access-management surfaces. It calls API-001/003/004/006 directly through Traefik/oauth2-proxy. The feature does not introduce a frontend aggregation service, identity-provider configuration UI, or business-object editing owned by PMS.

The frontend implementation paths remain **Planned** until verified during implementation; current route/settings/member patterns are evidence for reuse, not proof that these screens already exist.

## Experience Goals

- Make current workspace/project access understandable without exposing internal policy mechanics.
- Let authorized admins complete common access changes safely and quickly.
- Clearly distinguish workspace role, project role, inherited service access, and explicit service restriction.
- Prevent false success during stale, ambiguous, offline, or dependency-failure states.
- Make permission and destructive-action feedback accessible and privacy-safe.

## Information Architecture

```text
Authenticated NCN shell (UX-001)
├── Workspace settings
│   └── Access (UX-002)
│       └── Add/edit/revoke access dialog (UX-004)
└── Project settings
    └── Access (UX-003)
        └── Add/edit/revoke role or service restriction dialog (UX-004)
```

PMS remains responsible for workspace/project names, navigation, and settings shell. Authz surfaces receive safe display context plus canonical scope IDs and manage access only.

## User Flows

1. **Session entry:** the protected shell calls API-001. Loading blocks protected content; success establishes the User and navigation access; empty access explains that no workspace/project role exists; denial/dependency failure provides sign-in, retry, or support recovery.
2. **Workspace access:** an authorized actor opens UX-002, searches/pages members, opens UX-004, selects an allowed role, confirms a revoke when destructive, submits API-006, and reloads canonical state.
3. **Project access:** a project admin opens UX-003, manages DATA-003 through API-003, and optionally sets/removes DATA-004 through API-004. The UI explains that removing a restriction restores inherited project access.
4. **Stale/ambiguous recovery:** the UI does not assume success. It reloads the canonical row, shows what changed, and requires review before a new mutation.
5. **Permission loss:** a `403` or next API-001 state removes management actions, preserves non-sensitive context, announces the change, and offers a safe route back.

## Screen and Interaction Inventory

| ID | Surface | Audience | Primary content/actions | Interface |
| --- | --- | --- | --- | --- |
| UX-001 | Protected session shell states | All browser users | Resolving, authenticated, no-access, disabled, permission-denied, dependency error | API-001/007 |
| UX-002 | Workspace Access list | Workspace owner/permitted admin | Member identity, workspace role, list/search/page, add/edit/revoke when allowed | API-006 |
| UX-003 | Project Access list | Project admin | Member identity, project role/source, effective service access, add/edit/revoke/restrict | API-003/004 |
| UX-004 | Access mutation dialog/drawer | Authorized workspace/project admin | Target User, scope, allowed role, service inheritance/restriction, confirmation, validation/recovery | API-003/004/006 |

## Interaction States

| State | UX-001 | UX-002/003 | UX-004 |
| --- | --- | --- | --- |
| Initial/loading | Protected skeleton and “Checking access” status | Table skeleton; mutation controls unavailable | Submit disabled until data/options loaded |
| Empty | “You do not have access yet” with safe support guidance | “No members match” or first-member guidance consistent with owner/admin invariant | Search no-result text; no automatic invitation or User creation |
| Populated | Current User and accessible navigation | Paginated rows with text role labels and action menus | Current canonical values and explicit scope summary |
| Validation error | Safe identity guidance | Filter error is local | Field-level error plus focused summary |
| Permission denied | No protected content; return/sign-in action | Management actions absent; safe denial panel | Dialog closes only after announcing permission loss |
| Dependency/degraded | Retry/support with correlation ID | Loaded rows may remain visibly stale/read-only; no mutation | Preserve input, disable submit, offer canonical reload |
| Stale conflict | Reload session/scope | Changed row highlighted after refresh | Show current version/value and require review/resubmit |
| Duplicate/invariant conflict | N/A | Existing row or protected owner/admin remains | Explain duplicate, role ceiling, last owner/admin, or restriction conflict |
| Success | Protected shell/navigation rendered | Canonical list refreshed; focus returns to triggering control/changed row | Non-destructive success announced; dialog closes after canonical response |
| Offline | Browser network state, no authorization assumption | Previously loaded data marked stale/read-only | Submission blocked until online and refreshed |

No state displays identity-provider authorization metadata or labels access as SSO-managed, because SSO never owns roles.

## Content and Feedback

- Use “Workspace role,” “Project role,” and “Service access” consistently.
- Role labels are localized display text; API enum values remain stable.
- Service access displays `Inherited from project: {role}` when DATA-004 is absent and `Restricted to {role}` when present.
- `source=bootstrap` may display “Created with project” as provenance; it does not imply immutable access.
- Destructive copy names the User and scope: “Remove {name} from {project/workspace}?” It explains immediate next-request access loss.
- Last-owner/admin errors explain that another privileged member must exist first. Owner-transfer copy remains pending the Open policy decision.
- Dependency errors show a copyable correlation ID and safe retry; they never expose stack traces, email collision details of another User, or internal topology.
- Success messages state the committed result, not merely that a request was sent.

## Accessibility

- All lists, filters, row actions, selects, dialogs, confirmations, and retries work with keyboard alone.
- Tab/focus order follows visual order; opening UX-004 focuses its heading or first invalid field; closing returns focus to the trigger or changed row.
- Dialogs have programmatic names/descriptions, trap focus while open, and support Escape when cancellation is safe.
- Loading, validation, conflict, dependency, permission-loss, and success messages use appropriate live-region semantics without duplicate announcements.
- Table headers, row-action labels, roles, inherited/restricted status, and destructive scope have meaningful accessible names.
- Status never relies on color alone; focus indication and contrast meet the repository's accessibility target. Reduced-motion settings are honored.
- Search/list state and errors remain understandable at 200% zoom and with screen-reader virtual navigation.

## Responsive and Platform Behavior

Desktop/tablet use a table when it remains readable. Narrow screens switch to semantic member cards with identical content/order/actions; they do not hide role source, service inheritance, or destructive scope. UX-004 may become a full-height drawer on small screens while preserving heading, focus, and action order.

Browser behavior is the only planned platform. Route refresh/deep link repeats API-001 and scope authorization. Back navigation never restores mutation authority from stale client state.

## Analytics and Success Signals

Use privacy-safe product/operational events already supported by the frontend telemetry contract: surface loaded/empty/error, dialog opened/cancelled, mutation result/error category, stale reload, and time to canonical success. Use User UUID/safe scope IDs only where approved; do not include email, name, full OIDC payloads, or free-form errors.

Success signals map to OUT-002/003: SSO resolution success/error, completion rates for access tasks, frequency of guard/stale errors, recovery success, and accessibility test results. Telemetry failure never blocks authorization or shows false success.

## Open Design Questions

| Question | Owner / trigger | Consequence |
| --- | --- | --- |
| What existing workspace-settings route should host UX-002? | Frontend/PMS owners before SLICE-004 | Route and breadcrumbs remain Planned |
| Is owner transfer a dedicated guided flow? | Product/security decision before API-006 | UX-004 owner controls remain gated |
| Which User lookup is permitted for adding members? | Privacy/product/API review before SLICE-004 | Search fields, result disclosure, and empty state remain limited |
| Which service catalog names/icons are safe to display? | PMS/service catalog owner before API-004 | Use stable IDs/text fallback until resolved |
| What precise CSRF mechanism does the authenticated ingress use? | Platform/frontend security review before browser mutations | Write controls cannot be enabled beforehand |

## Traceability

| UX | Requirements / scenarios | APIs / data | Delivery |
| --- | --- | --- | --- |
| UX-001 | REQ-001/002/007; SCN-001/002/005/006 | API-001/002/005/007; DATA-001 | SLICE-002/003/005 |
| UX-002 | REQ-004/006/010; SCN-003/005 | API-006; DATA-002 | SLICE-004 |
| UX-003 | REQ-005/006/010; SCN-002/004/005 | API-002/003/004; DATA-003/004 | SLICE-003/004 |
| UX-004 | REQ-004/005/006/007; SCN-003/004/005 | API-003/004/006; DATA-002..004 | SLICE-004 |
