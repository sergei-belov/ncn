# Workspace access

Route: `/:workspaceSlug/settings/access`

Shell: [`WorkspaceShell`](../../general/navbar.md)

## Purpose

Workspace owners and administrators manage existing NCN users in the routed workspace.

## Behavior

- Search memberships by name, email, or UUID and navigate cursor pages.
- Add a user as `admin` or `member`; the owner role is excluded from the dialog because ownership transfer is a separate, unimplemented operation.
- Change a role with the membership's expected version.
- Revoke access with confirmation and last-owner protection from the backend.
- Hide all management controls when the current session role is insufficient.

## Page structure

- `WorkspaceShell` provides the workspace navigation and session gate.
- `AccessManagementView` supplies the heading, online/read-only notices, search, refresh, desktop table, mobile cards, pagination, and dialogs.
- Member rows show identity, role, and edit/revoke actions.

## States and validation

The view handles session loading, no permission, offline read-only mode, skeletons, empty search, full load failure, stale cached data after refresh failure, and permission loss during a mutation. User input requires an existing user UUID. The backend protects the last owner and enforces optimistic versions.

## Data and APIs

| Trigger | Request | Result |
| --- | --- | --- |
| Resolve shell session | Frontend expects `POST /auth/session/resolve` | Determines visible workspaces and management rights |
| List/search/page | `GET /workspaces/{workspaceId}/members` | Renders a cursor page of memberships |
| Add member | `POST /workspaces/{workspaceId}/members` | Adds canonical membership |
| Change role | `PATCH /workspaces/{workspaceId}/members/{userId}` | Replaces role if `expected_version` matches |
| Revoke | `POST /workspaces/{workspaceId}/members/{userId}/revoke` | Removes access |

FastAPI implements the membership routes but not the session-resolution route. See [HTTP integration status](../../../architecture.md#http-integration-status).

## Related documentation

- [Project access](project-access.md)
- [Authorization API](../../../backend/services/authz/api.md#authorization-and-memberships)
