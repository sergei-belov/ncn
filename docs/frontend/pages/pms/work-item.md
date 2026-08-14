# Work item

Route: `/:workspaceSlug/projects/:projectId/work-items/:workItemId`

Shell: [`WorkspaceShell`](../../general/navbar.md) → [`ProjectLayout`](../../general/project-sidebar.md) → route-aware sheet or full page

## Purpose

Users inspect and, when permitted, edit one project card.

## Behavior

- Navigation from the board opens a right sheet on desktop; direct links, reloads, and mobile use a full page.
- Edit title on blur, save rich-text description explicitly, and patch state, priority, epic, assignees, start date, or due date immediately.
- Delete after confirmation and return to the board.
- Show current entity version and save state (`saving`, `saved`, or `error`).

## Page structure

- **Primary panel**: identifier, save feedback, title, rich-text description, and delete action.
- **Properties panel**: state, priority, epic, project members, dates, and version metadata.
- **Container**: `AppSheet` over the board or a standalone page with back navigation.

## States and validation

The page loads its card from the board snapshot. It displays skeleton, missing-card, and access-error fallbacks. Editing is disabled for archived projects or without `canEditWorkItem`. Empty titles are not saved. Backend contracts limit assignees to 10, sanitize description HTML, and require start date not to exceed due date.

## Data and APIs

| Trigger | HTTP adapter request | Result |
| --- | --- | --- |
| Open route | `GET /workspaces/{workspaceSlug}/projects/{projectId}/board` | Locates the card and its state/epic/member lookups |
| Edit any field | `PATCH /workspaces/{workspaceSlug}/projects/{projectId}/work-items/{workItemId}` | Replaces the cached card |
| Delete | `DELETE /workspaces/{workspaceSlug}/projects/{projectId}/work-items/{workItemId}` | Removes the card and returns to the board |

## Related documentation

- [Board](board.md)
- [Work-item API](../../../backend/services/pms/api.md#work-items)
