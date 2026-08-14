# Workspace navigation — primary layer

Component: `WorkspaceShell`

Source: `frontend/src/widgets/app-shell/WorkspaceShell.vue`

## Purpose

The workspace navigation is the primary layer and outer shell for every workspace and project route. It resolves the authz session before exposing protected content and renders as a desktop sidebar or mobile navbar.

## Desktop structure

- **Brand block**: Project OS mark and routed workspace slug.
- **Primary navigation**: Projects and, for workspace owners/admins, Workspace access.
- **User block**: avatar initials, display name, and email while expanded.
- **Global controls**: light/dark theme, demo reset, and sidebar collapse.
- **Content outlet**: the active workspace page or nested `ProjectLayout`.

The sidebar appears at the `md` breakpoint, stays full viewport height, and uses `w-56` (14 rem) when expanded or `w-16` (4 rem) when collapsed. Collapsing retains icon-only navigation and controls.

## Mobile structure

Below `md`, the sidebar becomes a compact top navbar with Projects, conditional Access, and a theme toggle. User identity, demo reset, and collapse controls are not rendered in this mobile header.

## Visibility and state

- Workspace access is visible only when `canManageWorkspaceAccess` accepts the current workspace role.
- Active route styling identifies the selected workspace destination.
- Theme choice is persisted through VueUse and applied through the root `.dark` class.
- Session loading, service/identity failure, and no-access states replace the complete shell rather than exposing partial protected content.

## Accessibility

Navigation uses links with active styling. The mobile theme control has an explicit accessible label. Session loading uses status semantics, and error/no-access outcomes use the shared empty-state recovery component.

## Related documentation

- [General UI structure](README.md)
- [Project sidebar](project-sidebar.md)
- [Workspace access page](../pages/authz/workspace-access.md)
- [Authz flows](../../backend/services/authz/flows.md#frontend-startup-and-session-gate)
