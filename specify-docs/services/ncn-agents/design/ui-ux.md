# ncn-agents UI/UX Design

## Applicability

Applicable. Agent list/settings are **Present**; Sessions has a **Present placeholder**; conversation, Run progress, approvals, artifacts, reconciliation and execution history are **Planned**. The current Vue frontend renders these service-owned behaviors.

## Experience Goals

Admins confidently configure a safe team; members understand what agents are doing and can supply input/cancel; approvers understand exact risk and consequences; all users can distinguish progress, waiting, partial success, failure, and unresolved external outcome without reading raw traces.

## Information Architecture

Within a project: Agents → agent settings; Sessions → session list → conversation → Run detail/progress → plan/invocations/tools/approvals/artifacts/usage. Project navigation remains shared with PMS. Advanced operational/audit views are permission restricted and may be linked from Run detail rather than primary member navigation.

## User Flows

SCN-001 covers configuration and read-only states. SCN-002 begins with new Session/message, immediately returns Run identity, streams/polls progress, pauses for input/approval, allows cancellation, and ends with result summary. SCN-003 opens an approval/reconciliation task preserving exact Run/node context and returns to the same Run after decision.

## Screen and Interaction Inventory

| ID | Surface/interaction | Entry point | Primary action | Permission |
|---|---|---|---|---|
| UX-AGT-001 | Agent list/create | `.../:projectId/agents` | Inspect/create worker/change eligible status | View/manage agents |
| UX-AGT-002 | Agent settings | `.../agents/:agentId/settings` | Edit configuration | Manage agents; read-only otherwise |
| UX-AGT-003 | Sessions/conversation | `.../:projectId/sessions` and Planned child route | Send message/start/follow/cancel Run | Use agents/read Run/cancel policy |
| UX-AGT-004 | Run detail/progress | Session/Run context | Inspect plan, invocations, effects, result, usage | Read Run/audit scope |
| UX-AGT-005 | Approval/reconciliation | Pending task/Run node | Approve/reject or establish uncertain outcome | Eligible approver/operator |

## Interaction States

| Surface | Loading/initial | Empty | Success/populated | Validation/error | Disabled/denied/degraded |
|---|---|---|---|---|---|
| UX-AGT-001/002 | Skeleton/form load | No workers, coordinator still shown | Versioned config/status | Field/conflict/toast with retry/reload | Archived/unauthorized read-only; coordinator status protected |
| UX-AGT-003 | Session history pending | Present placeholder/no sessions | Ordered messages and active/terminal Run | Send/start error retains draft | Model/tools unavailable described before start where known |
| UX-AGT-004 | Snapshot/progress pending | No Run selected | Textual state, plan/effects/sources/usage/result | Stale stream reconnects; partial/failure actions | Some detail redacted by role; cancellation disabled after terminal |
| UX-AGT-005 | Approval details pending | No pending tasks | Exact action/risk/arguments/decision | Expired/changed/stale decision explains recovery | Ineligible user denied; unknown outcome exposes reconciliation, never “retry” blindly |

## Content and Feedback

Use user language (“Сессия”, “Запуск”, “Координатор”, “Ассистент”, “Требуется подтверждение”) and expose technical identifiers only for support. Always label active, waiting for input, waiting for approval, cancelling, completed, partially completed, failed, cancelled, and reconciliation. Approval text names effect/resource/material arguments/risk/expiry. Result names completed/failed work, effects, unresolved items, citations, and usage.

## Accessibility

Async updates use a restrained live region and persistent textual history. Status never relies on color. Keyboard/focus works for messages, cancellation, dialogs, plan expansion, approval, and retry/reconnect. Errors are associated and preserved. Streaming does not steal focus. Reduced motion, zoom/reflow, contrast, and touch sizes follow platform standards.

## Responsive and Platform Behavior

Agent config and conversation are usable on mobile; Run plan/detail stacks rather than requiring wide tables. Approval remains readable without horizontal scrolling. Reconnect after background/mobile interruption reloads owner Run state. Offline submission/execution is not promised; drafts may be browser-local if explicitly labeled.

## Analytics and Success Signals

Privacy-safe measures: config completion/conflict, Session-to-terminal conversion, clarification/approval age, cancellation, partial/failure/reconciliation, stream reconnect, result source usage, accessibility errors. Never record raw prompts, instructions, tool arguments, secrets, or artifact content in analytics.

## Open Design Questions

| Question | User impact | Owner/evidence | Blocking |
|---|---|---|---|
| Active-Run new message behavior | Conversation expectation and concurrency | Product | Yes |
| Progress granularity/redaction by role | Trust versus sensitive reasoning/tool data | Product/security | Yes |
| First approval and reconciliation copy/flow | Safety and comprehension | First vertical scenario | Yes |
| Agent config publish/draft/version UI | Predictability of future Runs | Agent product | No for current config slice |

## Traceability

UX-AGT-001..005 → SCN-001..003 → AGT-REQ-001..006 → API-AGT-001..006 → MODEL/TABLE-AGT → FEAT-002/003 acceptance.
