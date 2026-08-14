# Sessions

Route: `/:workspaceSlug/projects/:projectId/sessions`

Shell: [`WorkspaceShell`](../../general/navbar.md) → [`ProjectLayout`](../../general/project-sidebar.md)

## Purpose

This page communicates the intended agent-session model. It does not implement session persistence or execution.

## Behavior

- Show an empty state for future manual and automation-created sessions.
- Explain that one session permits at most one active run.
- Explain that mutating or risky actions will require project-policy approval.

## Page structure

- **Header**: Sessions title and agent-dialog context.
- **Empty state**: no current sessions.
- **Contract cards**: active-run limit and controlled-action policy.

## States and validation

The page is static. It has no loading, error, form, permissions, or mutation state beyond the surrounding project navigation.

## Data and APIs

No API calls are made. Session, message, run, and approval endpoints are not implemented in the current backend.

## Related documentation

- [Agents](agents.md)
- [Platform scope](../../../README.md#platform-scope)
