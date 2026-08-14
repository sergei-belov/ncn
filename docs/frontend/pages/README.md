# Frontend pages by service

Page documentation is grouped by the logical service that owns the page’s primary behavior and contracts. Each service folder contains its own complete page list.

| Logical service | UI responsibility | Page list |
| --- | --- | --- |
| `authz` | Workspace/project membership and service-restriction administration | [Authz pages](authz/README.md) |
| `pms` | Projects, boards, cards, epics, agents, sessions placeholder, and project configuration | [PMS pages](pms/README.md) |

Each page file defines its route, shell, purpose, behavior, page structure, visible states, permissions, and data/API interactions.

## Standalone page

| Page | Route | Definition | Page structure |
| --- | --- | --- | --- |
| [Not found](not-found.md) | `/:pathMatch(.*)*` | Recover from an unknown URL. | Centered icon/message → project-catalog recovery link |

The Not found page stays at the page root because it is outside both service domains and shared navigation shells.

## Redirects

- `/` redirects to `/{VITE_WORKSPACE_SLUG}/projects`.
- `/:workspaceSlug/projects/:projectId` redirects to the project board.

Redirects do not render page components of their own.

## Related documentation

- [Frontend overview](../README.md)
- [General UI](../general/README.md)
- [Components and UI](../components.md)
