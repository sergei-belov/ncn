# Agent settings

Route: `/:workspaceSlug/projects/:projectId/agents/:agentId/settings`

Shell: [`WorkspaceShell`](../../general/navbar.md) → [`ProjectLayout`](../../general/project-sidebar.md)

## Purpose

Users inspect or manage one project agent's configuration and lifecycle.

## Behavior

- Edit name, description, instructions, model, memory policy, maximum steps, and approval policy.
- Enable or disable workers.
- Archive a worker after confirmation; the UI has no restore-from-archive action.
- Keep the coordinator active and non-archivable. Its system tool policy is displayed as locked.

## Page structure

- **Route header**: back link, agent identity, read-only status.
- **Configuration**: reusable validated agent form.
- **Availability**: coordinator lock notice or worker toggle.
- **Danger zone**: worker archive control.

## States and validation

The page renders loading skeletons or a missing-agent state. It is read-only without `canManageAgents`, for archived projects, or for archived agents. Backend changes require the current positive agent version.

## Data and APIs

| Trigger | Request | Result |
| --- | --- | --- |
| Open | `GET /workspaces/{workspaceSlug}/projects/{projectId}/agents/{agentId}` and `GET /workspaces/{workspaceSlug}/projects/{projectId}` | Loads configuration and permissions |
| Save | `PATCH /workspaces/{workspaceSlug}/projects/{projectId}/agents/{agentId}` | Updates configuration |
| Toggle | `POST /workspaces/{workspaceSlug}/projects/{projectId}/agents/{agentId}/enable` or `/disable` | Changes worker status |
| Archive | `POST /workspaces/{workspaceSlug}/projects/{projectId}/agents/{agentId}/archive` | Archives worker and returns to list |

The frontend sends version through `If-Match`, while FastAPI requires `expected_version` in JSON for agent commands.

## Related documentation

- [Agents](agents.md)
- [Agent API](../../../backend/services/pms/api.md#agents)
