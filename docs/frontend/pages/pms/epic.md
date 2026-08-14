# Epic

Route: `/:workspaceSlug/projects/:projectId/epics/:epicId`

Shell: [`WorkspaceShell`](../../general/navbar.md) → [`ProjectLayout`](../../general/project-sidebar.md) → route-aware sheet or full page

## Purpose

Users inspect an epic's progress and manage its identity and card membership.

## Behavior

- Render as a desktop sheet over the epic list or as a standalone direct/mobile page.
- Show description, dates, progress, and linked cards with current workflow states.
- Edit epic fields, select its card membership, or delete it.
- Opening a linked card navigates to the work-item route.
- Deleting an epic preserves its cards and clears their epic association.

## Page structure

- **Summary**: color, name, description, edit/delete actions.
- **Progress**: percentage, completed/total counts, progress bar, and dates.
- **Cards**: linked card list and membership-management dialog.

## States and validation

The route combines epic-list and board queries. It shows loading and missing-epic states. Mutations are disabled for archived projects or without `canEditEpic`. A card may belong to one epic; the current mock moves a selected card from another epic.

## Data and APIs

| Trigger | HTTP adapter request | Result |
| --- | --- | --- |
| Open | `GET /workspaces/{workspaceSlug}/projects/{projectId}/epics` and `GET /workspaces/{workspaceSlug}/projects/{projectId}/board` | Locates the epic and related cards/states |
| Edit | `PATCH /workspaces/{workspaceSlug}/projects/{projectId}/epics/{epicId}` | Replaces the epic |
| Set card membership | Frontend expects `POST /workspaces/{workspaceSlug}/projects/{projectId}/epics/{epicId}/work-items/batch` | Replaces selected membership |
| Delete | `DELETE /workspaces/{workspaceSlug}/projects/{projectId}/epics/{epicId}` | Deletes epic and detaches cards |

FastAPI instead uses POST/DELETE membership endpoints and a different epic representation; see [HTTP integration status](../../../architecture.md#http-integration-status).

## Related documentation

- [Epics](epics.md)
- [Work item](work-item.md)
- [Epic API](../../../backend/services/pms/api.md#epics)
