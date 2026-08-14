# Agents

Route: `/:workspaceSlug/projects/:projectId/agents`

Shell: [`WorkspaceShell`](../../general/navbar.md) → [`ProjectLayout`](../../general/project-sidebar.md)

## Purpose

The agent catalog lists the required project coordinator and configurable worker assistants.

## Behavior

- Sort the coordinator first, live workers before archived workers, then by Russian name.
- Show agent kind, lifecycle status, model, run-step limit, memory scope, and settings action.
- Create a worker with name, description, instructions, model, memory policy, step limit, and approval mode.
- Open an agent's settings route.

## Page structure

- **Header**: agent context and conditional New assistant action.
- **Catalog**: responsive agent-card grid.
- **Create dialog**: reusable agent configuration form.

## States and validation

Only users with `canManageAgents` on an active project can create workers. All project members can view the list. The page has loading, retryable error, and missing-coordinator empty states. The form requires 2–80 characters for name and 20–4000 for instructions.

## Data and APIs

| Trigger | Request | Result |
| --- | --- | --- |
| Open | `GET /workspaces/{workspaceSlug}/projects/{projectId}/agents` | Loads coordinator and workers |
| Resolve permissions | `GET /workspaces/{workspaceSlug}/projects/{projectId}` | Controls create/manage actions |
| Create worker | `POST /workspaces/{workspaceSlug}/projects/{projectId}/agents` | Creates and opens settings |

## Related documentation

- [Agent settings](agent-settings.md)
- [Agent API](../../../backend/services/pms/api.md#agents)
