# Components and UI

## Design system

The UI uses semantic HSL tokens for background, foreground, cards, primary/secondary/accent colors, destructive actions, borders, inputs, focus rings, and radius. The `.dark` class replaces the complete token set and declares the browser color scheme. `WorkspaceShell` persists theme choice through VueUse.

Global conventions include a reusable visible focus ring, subtle surface shadows, custom scrollbars, a 320 px minimum body width, and top-right rich toast notifications. The interface text is Russian; Vue I18n is initialized with Russian as both locale and fallback.

## Shared UI primitives

All primitives are exported from `frontend/src/shared/ui/index.ts`.

| Component | Contract and use |
| --- | --- |
| `AppAvatar` | Image or initials fallback; `sm` and `md` sizes; optional title |
| `AppBadge` | Compact label with `default`, `secondary`, `outline`, or `danger` variant |
| `AppButton` | Default, secondary, outline, ghost, and destructive variants; four sizes; loading disables the button and shows a spinner |
| `AppDialog` | Reka modal with overlay, title, optional description, close action, scrolling, and `sm`/`md`/`lg` widths |
| `AppEmptyState` | Dashed status panel with icon, title, description, and optional recovery action |
| `AppFormField` | Label, required marker, one validation error or fallback hint, and input slot |
| `AppInput` | String-model native input with focus method, disabled state, autocomplete, and accessible label support |
| `AppProgress` | Clamped 0–100 progress bar with ARIA progress semantics |
| `AppSelect` | Nullable native select over typed options, placeholder, and disabled options |
| `AppSheet` | Right-side Reka dialog used by desktop detail routes; full-width up to `sm:max-w-2xl` |
| `AppSkeleton` | Configurable pulse placeholder |
| `AppTextarea` | Resizable string-model textarea with disabled state |
| `AppToggle` | Accessible checkbox switch with label and optional description |
| `RichTextEditor` | Tiptap editor with bold, bullet-list, and ordered-list controls; supports read-only mode |

## Shells and navigation

| Component | Responsibility |
| --- | --- |
| [`WorkspaceShell`](general/navbar.md) | Authorization-session gate, workspace navigation, identity display, theme, demo reset, desktop collapse, and mobile navigation |
| [`ProjectLayout`](general/project-sidebar.md) | Project loading, project identity, archived badge, project section navigation, responsive desktop/mobile layout |
| `SettingsTabs` | Page-local General, workflow-state, and conditional access tabs within project settings |

### `SettingsTabs`

`SettingsTabs` is a page-local component rendered by each project-settings page after its header. It is not part of the persistent general shell.

| Tab | Route | Visibility |
| --- | --- | --- |
| General | `/:workspaceSlug/projects/:projectId/settings` | Available after entering project settings |
| States | `/:workspaceSlug/projects/:projectId/settings/states` | Available after entering project settings |
| Access | `/:workspaceSlug/projects/:projectId/settings/access` | Project admin according to authz session |

The component reads `workspaceSlug` and `projectId` from the route, builds named-route links, and marks the active tab with a primary bottom border.

## Page widgets

| Widget | Responsibility |
| --- | --- |
| `ProjectBoardView` | Route filters, board query, display settings, read-only banner, quick create, move dialog, and navigation to cards |
| `KanbanBoard` | Horizontally scrolling set of ordered state columns with auto-scroll |
| `KanbanColumn` | Persisted collapsed state, drop target, card count, quick add, and empty drop zone |
| `KanbanCard` | Drag handle, edge-aware insertion target, identifier, title, priority, epic, date, assignees, and explicit move action |
| `QuickAddWorkItem` | Inline title-only creation with Enter/Escape keyboard behavior |
| `WorkItemDetail` | Editable title, sanitized rich text, state, priority, epic, assignees, dates, version status, and delete confirmation |
| `EpicList` | Searchable epic cards, project permission checks, and create flow |
| `EpicDetail` | Progress, dates, linked cards, edit, membership management, delete, and card navigation |
| `AgentList` | Coordinator-first agent catalog and worker creation |
| `AccessManagementView` | Workspace/project member table and mobile cards, search, cursor navigation, mutation safety, service restrictions, offline handling, and permission-loss recovery |

## Entity UI

| Component | Responsibility |
| --- | --- |
| `ProjectCard` | Project identity, description, visibility, role, archived state, open action, and archive/restore action |
| `EpicCard` | Epic summary, work-item count, dates, and computed progress |
| `AgentCard` | Kind, status, model, step limit, memory scope, and settings navigation |

## Feature components

| Feature | Components and behavior |
| --- | --- |
| Project management | `ProjectFormDialog` validates create input; project settings use update and archive mutations |
| Card creation and movement | `QuickAddWorkItem`, `MoveWorkItemDialog`, optimistic move orchestration, update, and delete mutations |
| Epic management | `EpicFormDialog`, `AddWorkItemsToEpicDialog`, create/update/delete and membership mutations |
| State management | Create/update/default/reorder/delete mutations with cache invalidation |
| Agent management | `AgentConfigForm`, `AgentFormDialog`, and `AgentSettingsPanel` for worker lifecycle and guarded coordinator behavior |
| Access management | `AccessMemberDialog`, `RevokeAccessDialog`, and `ServiceRestrictionDialog` with optimistic membership versions |
| Demo reset | `ResetDemoButton` replaces the local browser database and refreshes queries |

## Accessibility and interaction

- Dialogs and sheets use Reka focus and modal semantics.
- Icon-only controls have explicit accessible labels in the implemented pages.
- The board announces successful moves through an `aria-live` region and retains an explicit move dialog as a keyboard-accessible alternative to drag-and-drop.
- Columns expose expanded/collapsed state and associated content IDs.
- Access management uses table headers on desktop, card layouts on mobile, status/alert roles, and live announcements after mutations.
- Loading views use skeletons and status semantics; destructive actions use confirmation dialogs.

## Known UI limitations

- Sessions are explanatory only and have no create, message, or run components.
- The Kanban column “more” button is visual and has no action menu.
- Board card display preferences and collapsed columns are stored in browser storage by the current widget, even though backend preference endpoints also exist.
- The frontend HTTP wire models are not yet aligned with every FastAPI response; see [HTTP integration status](../architecture.md#http-integration-status).
