# PMS frontend pages

These pages own the project-management experience backed by the `pms` logical service. They cover project discovery, Kanban planning, workflow configuration, epics, agents, and the current sessions placeholder.

## Workspace-level PMS page

| Page | Route | Definition | Page structure |
| --- | --- | --- | --- |
| [Projects](projects.md) | `/:workspaceSlug/projects` | Browse, create, archive, and restore workspace projects. | Page header → search/archive filters → project grid or status → create dialog |

## Project pages

These routes use `WorkspaceShell -> ProjectLayout -> page`.

| Page | Route | Definition | Page structure |
| --- | --- | --- | --- |
| [Board](board.md) | `/:workspaceSlug/projects/:projectId/board` | View, filter, create, and move Kanban cards. | Board header → filters → horizontal state columns → display/move dialogs |
| [Work item](work-item.md) | `/:workspaceSlug/projects/:projectId/work-items/:workItemId` | Inspect and edit one card. | Desktop sheet or full page → primary editor → properties panel → delete confirmation |
| [Epics](epics.md) | `/:workspaceSlug/projects/:projectId/epics` | Browse and create planning epics. | Header → search/count → epic grid or status → create dialog |
| [Epic](epic.md) | `/:workspaceSlug/projects/:projectId/epics/:epicId` | Inspect epic progress and card membership. | Desktop sheet or full page → summary → progress → linked cards/dialogs |
| [Agents](agents.md) | `/:workspaceSlug/projects/:projectId/agents` | Browse the coordinator and worker assistants. | Header/action → responsive agent grid → create dialog |
| [Agent settings](agent-settings.md) | `/:workspaceSlug/projects/:projectId/agents/:agentId/settings` | Configure and manage one agent. | Route header → configuration → availability → danger zone |
| [Sessions](sessions.md) | `/:workspaceSlug/projects/:projectId/sessions` | Explain the future session/run contract. | Header → empty state → contract cards |

## Project settings pages

These routes keep the project shells and add the page-local `SettingsTabs` component.

| Page | Route | Definition | Page structure |
| --- | --- | --- | --- |
| [Project settings](project-settings.md) | `/:workspaceSlug/projects/:projectId/settings` | Edit project fields and archive/restore the project. | Settings header → tabs → general form → danger zone/dialog |
| [State settings](state-settings.md) | `/:workspaceSlug/projects/:projectId/settings/states` | Manage ordered Kanban states and the default state. | States header/action → tabs → workflow list → create/edit/delete dialogs |

Project Access occupies the third settings tab but is [documented under authz](../authz/project-access.md) because authz owns its membership and service-restriction behavior.

## Related documentation

- [All frontend services](../README.md)
- [PMS backend service](../../../backend/services/pms/README.md)
- [Components and UI](../../components.md)
