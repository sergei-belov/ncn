# UI/UX Design

## Applicability

**Not applicable to this feature.** The user explicitly requested only the agent core, Temporal flow, and MCP, and the verified frontend currently exposes Agent configuration but no execution/conversation surface. This package adds backend/machine interfaces only and does not change `frontend/**`, browser routes, screens, components, or client state.

Delivery consequence: there are no UX IDs or frontend acceptance tests in SLICE-001–004. A future frontend Run or Session feature must define its own navigation, polling, progress, cancellation, errors, accessibility, and responsive behavior against API-003–007.

## Experience Goals

**Not applicable for a browser experience.** The non-visual consumer goal is covered by [the API contract](../interfaces/api.md): accepted work is asynchronous, lifecycle states/errors are explicit, events are ordered, cancellation is explicit, and no caller must infer completion from timing.

## Information Architecture

**Not applicable.** No route, navigation item, screen hierarchy, label, or discoverability behavior changes. The existing Agent settings routes remain configuration-only and must not imply that a Run UI exists.

## User Flows

**Not applicable as UI flows.** SCN-001–006 are API/system flows. They do not authorize adding a chat page, Run detail page, Session timeline, streaming response, or Approval dialog.

## Screen and Interaction Inventory

**Not applicable.** There are no `UX-NNN` entries because no user-facing surface or interaction is in scope.

## Interaction States

**Not applicable to a screen.** API consumers can represent `QUEUED`, `RUNNING`, `RETRYING`, `CANCELLING`, and terminal states using API-004/API-005, but this feature does not prescribe a frontend representation.

## Content and Feedback

**Not applicable to interface copy/localization.** Machine-facing error codes and safe details are authoritative in [the API contract](../interfaces/api.md). They must remain stable and non-sensitive so a later UI can localize them without parsing free text.

## Accessibility

**Not applicable because no UI is changed.** A future Run UI must independently cover keyboard operation, focus, semantics, screen-reader announcements, reduced motion, contrast, target size, and error association. The explicit state/event API is intended to make that possible but is not accessibility evidence by itself.

## Responsive and Platform Behavior

**Not applicable.** No viewport, browser, mobile, offline, or input-mode behavior changes.

## Analytics and Success Signals

**Not applicable to product analytics.** Backend operational and audit signals are specified in [the technical design](technical.md#observability-and-operations). No browser analytics event is introduced.

## Open Design Questions

There are no blocking UI design questions. Choosing to expose Runs in the browser reopens UI/UX applicability and requires a separate feature plan.

## Traceability

All REQ-001–010 and SCN-001–006 are served through API-001–009 and SLICE-001–004 with no UX surface. The absence of `UX-NNN` identifiers is intentional under DEC-006.
