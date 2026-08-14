# Board

Route: `/:workspaceSlug/projects/:projectId/board`

Shell: [`WorkspaceShell`](../../general/navbar.md) → [`ProjectLayout`](../../general/project-sidebar.md)

## Purpose

Project members view and manage work items across ordered Kanban states.

## Behavior

- Filter by text, priority, epic, and assignee. Filters are stored in route query parameters; text changes are debounced by 300 ms with a 700 ms maximum wait.
- Collapse individual columns; the choice is stored per state in browser storage.
- Create a title-only work item in a selected state.
- Move a card between or within columns by drag-and-drop with edge-aware insertion, or use the explicit start/end move dialog.
- Open a card as a route-aware desktop sheet or full detail page.
- Configure whether cards show assignees, epic, and due date; these choices are stored in the browser.

## Page structure

- **Header**: board identity, project name, archived badge, and View action.
- **Filter bar**: search and select controls with reset.
- **Board**: horizontally scrollable, vertically scrolling columns with counts, cards, drop zones, and quick add.
- **Dialogs**: card display settings and explicit move.

## States and validation

Loading uses fixed-width column skeletons. Errors expose a retry action. Archived projects or users without move permission see a read-only banner; creation and drag/drop are disabled. Successful moves are announced through an `aria-live` region. Optimistic movement snapshots affected board queries and rolls them back on failure.

## Data and APIs

| Trigger | HTTP adapter request | Result |
| --- | --- | --- |
| Open/change filters | `GET /workspaces/{workspaceSlug}/projects/{projectId}/board` | Loads project, states, cards, epics, members, columns, and board version |
| Quick add | `POST /workspaces/{workspaceSlug}/projects/{projectId}/work-items` | Adds a card and refreshes board queries |
| Drag/drop or move dialog | `POST /workspaces/{workspaceSlug}/projects/{projectId}/work-items/{workItemId}/move` | Commits canonical state/order and board version |

The browser mock supplies the flat board model used by this page. FastAPI returns a different board and move shape; see [HTTP integration status](../../../architecture.md#http-integration-status).

## Related documentation

- [Work item](work-item.md)
- [State settings](state-settings.md)
- [Board API](../../../backend/services/pms/api.md#board-and-preferences)
