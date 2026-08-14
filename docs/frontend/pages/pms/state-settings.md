# State settings

Route: `/:workspaceSlug/projects/:projectId/settings/states`

Shell: [`WorkspaceShell`](../../general/navbar.md) → secondary [`ProjectLayout`](../../general/project-sidebar.md); page-local [`SettingsTabs`](../../components.md#settingstabs)

## Purpose

Project administrators define the ordered workflow columns used by the Kanban board.

## Behavior

- Create a state at the end of the workflow.
- Edit its name, color, and semantic group.
- Assign a non-default state as the new default.
- Move states one position up or down.
- Delete a non-default state after selecting a replacement; cards and backend epics are moved transactionally.

## Page structure

- **Header and settings tabs**: state title and conditional Add action.
- **Workflow list**: color, name, semantic group, default badge, and row controls.
- **Dialogs**: create/edit fields and delete replacement selection.

## States and validation

Mutations require `canManageStates` and an active project. Names must be nonblank and backend names are case-insensitively unique. The last or default state cannot be deleted. Reordering must contain every state exactly once and FastAPI compares the project board version.

## Data and APIs

| Trigger | Request | Result |
| --- | --- | --- |
| Open | `GET /workspaces/{workspaceSlug}/projects/{projectId}/states` and `GET /workspaces/{workspaceSlug}/projects/{projectId}` | Loads order and permissions |
| Create | `POST /workspaces/{workspaceSlug}/projects/{projectId}/states` | Appends a state |
| Edit/default | `PATCH /workspaces/{workspaceSlug}/projects/{projectId}/states/{stateId}` | Updates state and board version |
| Move | `POST /workspaces/{workspaceSlug}/projects/{projectId}/states/reorder` | Replaces complete order |
| Delete | `DELETE /workspaces/{workspaceSlug}/projects/{projectId}/states/{stateId}?replacement_state_id={replacementStateId}` | Moves dependents and removes state |

The current frontend state wire fields and reorder payload differ from FastAPI; see [HTTP integration status](../../../architecture.md#http-integration-status).

## Related documentation

- [Board](board.md)
- [States API](../../../backend/services/pms/api.md#states)
