# Projects

Route: `/:workspaceSlug/projects`

Shell: [`WorkspaceShell`](../../general/navbar.md)

## Purpose

The workspace landing page lists active or archived projects and starts project creation.

## Behavior

- Search by project name or identifier and toggle between active and archived results.
- Open a project on its board route.
- Create a project with name, 2–10 character uppercase identifier, description, and `workspace` or `private` access.
- Archive or restore a project when its permission set allows it.
- A created project receives four workflow states and a coordinator in the current mock and backend implementations.

## Page structure

- **Header**: workspace label, title, description, and New project action.
- **Filters**: search input and Archived switch.
- **Catalog**: responsive project-card grid with role, visibility, identifier, and lifecycle action.
- **Create dialog**: validated project form; API field errors are attached to form fields.

## States and validation

The page has six-card loading skeletons, retryable load errors, first-project, no-results, and empty-archive states. Project creation validates name, identifier, description, and access in the browser. Archive/restore failures produce a toast.

## Data and APIs

| Trigger | HTTP adapter request | Result |
| --- | --- | --- |
| Open/filter page | `GET /workspaces/{workspaceSlug}/projects` | Replaces the project grid |
| Create | `POST /workspaces/{workspaceSlug}/projects` | Adds the project and navigates to its board |
| Archive | `POST /workspaces/{workspaceSlug}/projects/{projectId}/archive` | Moves the project to archived results |
| Restore | `POST /workspaces/{workspaceSlug}/projects/{projectId}/restore` | Returns the project to active results |

The current HTTP adapter's project filters and mutation payloads differ from FastAPI; see [HTTP integration status](../../../architecture.md#http-integration-status).

## Related documentation

- [Board](board.md)
- [Project settings](project-settings.md)
- [PMS API](../../../backend/services/pms/api.md#projects)
