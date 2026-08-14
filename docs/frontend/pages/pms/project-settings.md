# Project settings

Route: `/:workspaceSlug/projects/:projectId/settings`

Shell: [`WorkspaceShell`](../../general/navbar.md) → secondary [`ProjectLayout`](../../general/project-sidebar.md); page-local [`SettingsTabs`](../../components.md#settingstabs)

## Purpose

Project administrators update project metadata and archive or restore the project.

## Behavior

- Edit name, description, and `workspace`/`private` access.
- Display the immutable identifier in this form.
- Archive after confirmation and return to the project catalog.
- Restore an archived project so domain editing becomes available again.

## Page structure

- **Header and settings tabs**: project identity and settings navigation.
- **General card**: form and identifier badge.
- **Danger zone**: archive or restore explanation and confirmation dialog.

## States and validation

Name is 2–80 characters in the frontend form and description is at most 500. Fields and save action are hidden/disabled without `canEditProject`. Archive controls require `canArchiveProject`. Archived projects remain visible but read-only.

## Data and APIs

| Trigger | Request | Result |
| --- | --- | --- |
| Open | `GET /workspaces/{workspaceSlug}/projects/{projectId}` | Populates form and permissions |
| Save | `PATCH /workspaces/{workspaceSlug}/projects/{projectId}` | Updates project metadata |
| Archive | `POST /workspaces/{workspaceSlug}/projects/{projectId}/archive` | Archives and returns to catalog |
| Restore | `POST /workspaces/{workspaceSlug}/projects/{projectId}/restore` | Restores editability |

FastAPI archive requires the exact project name as `confirmation_name`; the current HTTP adapter sends an empty object.

## Related documentation

- [State settings](state-settings.md)
- [Project access](../authz/project-access.md)
- [Projects API](../../../backend/services/pms/api.md#projects)
