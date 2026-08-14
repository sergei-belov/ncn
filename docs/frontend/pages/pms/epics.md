# Epics

Route: `/:workspaceSlug/projects/:projectId/epics`

Shell: [`WorkspaceShell`](../../general/navbar.md) → [`ProjectLayout`](../../general/project-sidebar.md)

## Purpose

The epic catalog groups related cards and exposes their computed completion progress.

## Behavior

- Search epics by name.
- Create an epic with name, description, color, and optional start/target dates in the current frontend model.
- Open an epic as a route-aware desktop sheet or full detail page.
- Show total/completed cards and a progress percentage on every card.

## Page structure

- **Header**: project context and conditional New epic action.
- **Filter card**: search and current visible count.
- **Catalog**: responsive epic-card grid.
- **Create dialog**: validated identity, presentation, and dates.

## States and validation

Creation is available only with `canCreateEpic` on an active project. The page has loading, retryable error, no-results, and first-epic states.

## Data and APIs

| Trigger | HTTP adapter request | Result |
| --- | --- | --- |
| Open/search | `GET /workspaces/{workspaceSlug}/projects/{projectId}/epics` | Loads epic summaries |
| Resolve project | `GET /workspaces/{workspaceSlug}/projects/{projectId}` | Supplies title and permissions |
| Create | `POST /workspaces/{workspaceSlug}/projects/{projectId}/epics` | Adds and opens the epic |

The browser epic model differs materially from FastAPI's epic model; see [HTTP integration status](../../../architecture.md#http-integration-status).

## Related documentation

- [Epic](epic.md)
- [Epic API](../../../backend/services/pms/api.md#epics)
