# ncn-authz UI/UX Design

## Applicability

**Not applicable as an owned screen.** `ncn-authz` is a common backend authorization layer and owns no navigation or visual surface. User-visible sign-in, current-user, permission-denied, read-only, rate-limited, and service-unavailable states are rendered by consuming PMS/agents frontend surfaces. Consequence: this service specifies error meaning and accessibility expectations; consumers own layout and interaction.

## Experience Goals

Users should understand whether they need to sign in, request project access, wait for a role/data change, retry after a rate/dependency failure, or continue read-only. Messages must be safe, actionable, and consistent across services without exposing internal membership or resource data.

## Information Architecture

No `ncn-authz` destination is currently exposed. Authentication entry is owned by the product edge/local login flow. Authorization states appear in the consumer route where the operation was attempted. Membership administration UI is Open and must not be invented here.

## User Flows

SCN-001 returns the user to sign-in or provisioning guidance on identity failure. SCN-002 keeps the user on the consumer surface with read-only/access-required feedback. SCN-003 distinguishes rate-limited and unavailable recovery. Successful authorization is invisible except for the enabled actions/permissions rendered by consumers.

## Screen and Interaction Inventory

No AUTHZ-owned screens or `UX-AUTHZ-*` identifiers are registered.

## Interaction States

| Consumer state | Initial/loading | Empty | Success/populated | Validation/error | Disabled/denied/degraded |
|---|---|---|---|---|---|
| Authenticated actor | Resolve current user before protected content | User not provisioned is an error, not empty success | Render consumer data/actions | Invalid local credentials stay with form | Reauthenticate or contact identity owner |
| Project access | Resolve membership/role before project content | No related projects may offer creation where allowed | Render role-appropriate content | Stable access error | Read-only/denied explanation; no elevation controls |
| Dependency/rate | Preserve safe current context | Not applicable | Continue after successful retry | Semantic alert with safe message | Retry only when indicated; avoid destructive repetition |

## Content and Feedback

Use distinct localized messages for authentication required, invalid credentials, access required, action not permitted, rate limited, and service unavailable. Do not show bearer details, password/hash data, database identifiers other than safe public resource IDs, or internal policy names. Consumers must not display a synthetic tracking value.

## Accessibility

Use semantic alerts and headings, associate credential errors with fields, move focus predictably on sign-in navigation, keep denial text available to screen readers, and do not signal role/read-only status by color alone. All retry, sign-in, back, and access-request actions are keyboard reachable. Announce asynchronous recovery without repeated live-region noise.

## Responsive and Platform Behavior

Consumer-owned states must work in desktop/mobile, keyboard/touch, direct-link, and reload flows. Offline authorization is not promised. A cached permission projection must never enable offline mutation or survive a canonical denial.

## Analytics and Success Signals

Consumers may record privacy-safe counts of sign-in redirect, access denial, rate limit, dependency error, and successful retry keyed operationally by persisted user UUID on the backend. Do not capture email, token, password, or sensitive resource content.

## Open Design Questions

| Question | User impact | Owner/evidence | Blocking |
|---|---|---|---|
| Will membership administration receive a dedicated UI? | Determines how users request/add/change access | Product/authz owner when feature starts | No for current common layer |
| What support path is shown for an authenticated but unprovisioned user? | Recovery clarity | Identity/product owner before production OIDC | Yes for production experience |

## Traceability

SCN-001..003 → AUTHZ-REQ-001..010 → API-AUTHZ-001..003 → consumer PMS/agents UI contracts → FEAT-004 acceptance.
