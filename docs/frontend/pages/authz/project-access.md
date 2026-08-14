# Project access

Route: `/:workspaceSlug/projects/:projectId/settings/access`

Shell: [`WorkspaceShell`](../../general/navbar.md) → secondary [`ProjectLayout`](../../general/project-sidebar.md); page-local [`SettingsTabs`](../../components.md#settingstabs)

## Purpose

Project administrators manage project roles and optional per-service restrictions.

## Behavior

- Add an existing user as `admin`, `member`, or `viewer`.
- Change or revoke a project membership with its expected version.
- Show whether membership was created manually or during project bootstrap.
- Create or update a service restriction whose role is no higher than the project role.
- Remove a service restriction to restore inherited project access.

## Page structure

- **Project header and tabs**: context and settings navigation.
- **Access view**: searchable, cursor-paginated desktop table/mobile cards.
- **Dialogs**: add/edit member, revoke confirmation, and service restriction.

## States and validation

The project is loaded before the access view. Missing projects, no permission, offline mode, archived read-only mode, load failures, cached stale data, and permission loss are represented explicitly. FastAPI protects the last project admin and rejects project-role changes below an existing service restriction.

## Data and APIs

| Trigger | Request | Result |
| --- | --- | --- |
| Open | `GET /projects/{projectId}/members` | Lists member and service access |
| Add | `POST /projects/{projectId}/members` | Creates membership |
| Change role | `PATCH /projects/{projectId}/members/{userId}` | Applies versioned role change |
| Revoke | `POST /projects/{projectId}/members/{userId}/revoke` | Removes membership and cascading restrictions |
| Put restriction | `PUT /projects/{projectId}/members/{userId}/services/{serviceId}` | Creates or replaces narrowing role |
| Remove restriction | `DELETE /projects/{projectId}/members/{userId}/services/{serviceId}` | Restores project-role inheritance |

## Related documentation

- [Workspace access](workspace-access.md)
- [Authorization API](../../../backend/services/authz/api.md#authorization-and-memberships)
