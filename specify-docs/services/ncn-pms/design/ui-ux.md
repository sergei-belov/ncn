# ncn-pms UI/UX Design

## Applicability

Applicable. PMS owns the behavior contract for project work and the Vue SPA currently renders it through resource adapters. Present routes were verified 2026-08-13.

## Experience Goals

Users should see current work quickly, change it with immediate but reversible feedback, understand permission/archive limitations, and recover from validation, network, or concurrency errors without losing context. Desktop and mobile must support equivalent tasks.

## Information Architecture

Workspace → Projects → Project navigation: Board, Epics, Agents, Sessions, Settings. PMS owns Projects, Board, Work Item, Epics, Project Settings, and State Settings. Agent/Session destinations are owned by `ncn-agents`. Canonical Present route base is `/:workspaceSlug/projects/:projectId`.

## User Flows

SCN-001 begins in project list or board and preserves filters in route query. Card/epic details use contextual desktop sheet where navigation history permits, but direct links/reload/mobile render a full page. SCN-002 uses settings/states with explicit confirmation and recovery. SCN-003 reuses existing authentication, permission-denied, read-only, and retry states; it adds no screen. Permission, membership, or archive changes immediately remove/disable mutation controls but never replace backend enforcement.

## Screen and Interaction Inventory

| ID | Surface/interaction | Entry point | Primary action | Permission |
|---|---|---|---|---|
| UX-PMS-001 | Project list/create | `/:workspaceSlug/projects` | Find/create/open/archive/restore project | View/create/manage project |
| UX-PMS-002 | Kanban board | `.../:projectId/board` | Filter, quick add, collapse, exact move | View/manage work items |
| UX-PMS-003 | Work item / epic detail | `.../work-items/:id`, `.../epics[/:id]` | Edit fields, membership, delete | View/manage relevant resource |
| UX-PMS-004 | Project/stage settings | `.../:projectId/settings[/states]` | Edit project/workflow/default/order/delete | Manage project/stages |

## Interaction States

| Surface | Loading/initial | Empty | Success/populated | Validation/error | Disabled/denied/degraded |
|---|---|---|---|---|---|
| UX-PMS-001 | Skeleton/list pending | No projects with create CTA if allowed | Searchable cards/list | Inline fields, retry/toast | Create/manage hidden or disabled by policy |
| UX-PMS-002 | Column skeletons | Empty board/column with permitted quick add | Ordered columns/cards/filters | Roll back optimistic move; retry/refetch | Read-only archive/viewer; explicit move unavailable without permission |
| UX-PMS-003 | Detail skeleton | Deleted/not-found explanation | Editable or read-only details | Field errors, conflict reload, delete confirmation | Controls absent/read-only with reason |
| UX-PMS-004 | Settings skeleton | No optional items | Current project/stages | Unique/default/replacement/conflict errors | Denied/read-only explanation |

## Content and Feedback

UI labels are Russian in the current slice and use consistent terms Project/Карточка/Эпик/Состояние. Destructive dialogs state resource and consequence. Successful mutations provide toast/inline confirmation; movement announces destination/position. Errors use actionable safe language without exposing tracking metadata. Authentication failure offers sign-in; permission denial explains that access is required; concurrent conflict asks the user to reload current state.

## Accessibility

Use semantic headings, lists, buttons, dialogs, forms, labels, descriptions, and status regions. Support keyboard board navigation and explicit Move dialog instead of requiring drag/drop. Trap/restore focus for dialog/sheet; associate errors; announce async success/failure and movement; meet contrast, 200% zoom/reflow, target size, and reduced-motion expectations.

## Responsive and Platform Behavior

Desktop may use route-aware sheets; direct link, reload, and mobile use full pages. Navigation adapts to mobile without hiding essential destinations. Touch and keyboard paths perform the same mutations. Network degradation preserves read context and offers retry; offline editing is not promised.

## Analytics and Success Signals

Capture privacy-safe route/load success, create/update/move completion, conflict/rollback, empty-state conversion, and accessibility-path usage. Do not capture rich-text content or member-sensitive filters. Thresholds are Open before production.

## Open Design Questions

| Question | User impact | Owner/evidence | Blocking |
|---|---|---|---|
| Should preferences remain browser-local, owner-persisted, or both? | Cross-device consistency | PMS/frontend decision; current backend has a preference table | No for current slice |
| What conflict merge experience is needed beyond reload? | Editing resilience | Usage evidence | No |

## Traceability

UX-PMS-001..004 → PMS-REQ-001..008 → SCN-001..003 → API-PMS-001..009 → MODEL/TABLE-PMS → FEAT-001/004 acceptance.
