# PMS API

This reference owns project-management routes and contracts. All paths and payloads follow the [shared backend API conventions](../../api.md). Nested routes require an explicit project membership supplied by authz.

## Projects

Prefix: `/api/v1/workspaces/{workspace_slug}/projects`

| Method and path | Request | Response | Permission |
| --- | --- | --- | --- |
| `GET .../projects` | Project list query | `ProjectListResponse` | Authenticated workspace actor; results remain membership-scoped |
| `POST .../projects` | `CreateProjectRequest` | `ProjectResponse`, 201 | Authenticated workspace actor |
| `GET .../projects/{project_id}` | — | `ProjectResponse` | Project membership |
| `PATCH .../projects/{project_id}` | `UpdateProjectRequest` | `ProjectResponse` | `can_edit_project` |
| `POST .../projects/{project_id}/archive` | `confirmation_name` | `ProjectResponse` | `can_archive_project` |
| `POST .../projects/{project_id}/restore` | `{}` | `ProjectResponse` | `can_archive_project` |

Project list query:

| Field | Type | Default |
| --- | --- | --- |
| `search` | `str?` | — |
| `status` | `enum(active, archived)` | `active` |
| `mine` | `bool` | `false` |
| `sort` | `enum(name, -name, created_at, -created_at)` | `name` |
| `cursor` | `str?` | — |
| `limit` | `int` 1–100 | 30 |

`CreateProjectRequest`:

| Field | Type | Rules/default |
| --- | --- | --- |
| `id` | `UUID` | Required client command/resource ID |
| `name` | `str` | 1–255, trimmed/nonblank |
| `identifier` | `str` | 2–10 uppercase letters/digits; normalized uppercase |
| `description` | `null | str` | Optional, max 2000, default `null` |
| `icon` | `{type: enum(emoji, initial), value: str}` | Optional; omitted value derives from name |
| `color` | `str` | Optional `#RRGGBB`, default `#5E6AD2` |
| `access` | `enum(private, workspace)` | Optional, default `private` |

`UpdateProjectRequest` accepts any subset of `name`, `identifier`, `description`, `icon`, `color`, and `access`. Only `description` may be explicitly `null`.

Project creation atomically creates the admin membership, four default Russian states, sets `default_state_id`, and creates the coordinator. Archive requires exact case-sensitive project-name confirmation.

Current scope note: the workspace actor for project list/create is built from the route slug and authenticated user without reading `workspace_users`. Lists remain filtered by explicit project memberships, and every nested project route requires `project_users`; `access=workspace` is stored and returned but does not grant implicit access.

## Agents

Prefix: `/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agents`

| Method and path | Request | Response | Permission |
| --- | --- | --- | --- |
| `GET .../agents` | — | `AgentListResponse` | Project membership |
| `POST .../agents` | `CreateAgentRequest` | `AgentResponse`, 201 | `can_manage_agents` |
| `GET .../agents/{agent_id}` | — | `AgentResponse` | Project membership |
| `PATCH .../agents/{agent_id}` | `UpdateAgentRequest` | `AgentResponse` | `can_manage_agents` |
| `POST .../agents/{agent_id}/enable` | `expected_version` | `AgentResponse` | `can_manage_agents` |
| `POST .../agents/{agent_id}/disable` | `expected_version` | `AgentResponse` | `can_manage_agents` |
| `POST .../agents/{agent_id}/archive` | `expected_version` | `AgentResponse` | `can_manage_agents` |

Create fields are `name` (2–80), `description` (max 240), `instructions` (20–4000), `model` (1–255), `memory_policy: enum(project, session, none)`, `max_steps_per_run: int >= 1`, and `approval_mode: enum(project, always)`.

Update requires `expected_version` and accepts non-null subsets of the create fields. The coordinator is always active and cannot be disabled or archived. Live agent names are unique per project; archived names may be reused.

## States

Prefix: `/api/v1/workspaces/{workspace_slug}/projects/{project_id}/states`

| Method and path | Request | Response | Permission |
| --- | --- | --- | --- |
| `GET .../states` | — | `StateListResponse` | Project membership |
| `POST .../states` | `CreateStateRequest` | `StateResponse`, 201 | `can_manage_states` |
| `POST .../states/reorder` | `ReorderStatesRequest` | `ReorderStatesResponse` | `can_manage_states` |
| `PATCH .../states/{state_id}` | `UpdateStateRequest` | `StateResponse` | `can_manage_states` |
| `DELETE .../states/{state_id}` | Query `replacement_state_id?: UUID` | 204 | `can_manage_states` |

`CreateStateRequest`: `id: UUID`, `name: str` (1–50), `color: #RRGGBB`, `group: enum(backlog, unstarted, started, completed, cancelled)`, `after_state_id?: null | UUID`, `is_default?: bool` (default false).

`UpdateStateRequest` accepts non-null subsets of `name`, `color`, `group`, and `is_default`. `ReorderStatesRequest` requires `ordered_state_ids: UUID[]` containing every state exactly once and `expected_board_version: int >= 1`.

State names are unique per project ignoring case. A project must retain at least one state. The current default cannot be deleted or unset directly. Deleting a nonempty state requires a different valid replacement; work items and epics move before deletion.

## Work items

Prefix: `/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items`

| Method and path | Request | Response | Permission |
| --- | --- | --- | --- |
| `GET .../work-items` | Work-item list query | `WorkItemPage` | Project membership |
| `POST .../work-items` | `CreateWorkItemRequest` | `WorkItemResponse`, 201 | `can_create_work_item` |
| `GET .../work-items/{work_item_id}` | — | `WorkItemDetailResponse` | Project membership |
| `PATCH .../work-items/{work_item_id}` | `UpdateWorkItemRequest` | `WorkItemResponse` | `can_edit_work_item` |
| `POST .../work-items/{work_item_id}/move` | `MoveWorkItemRequest` | `MoveWorkItemResponse` | `can_move_work_item` |
| `DELETE .../work-items/{work_item_id}` | — | 204 | Own-card or any-card delete permission |

List query:

| Field | Type | Default |
| --- | --- | --- |
| `search` | `str?` | — |
| `state_id` | `UUID?` | — |
| `priority` | Comma-separated priorities | — |
| `assignee_id` | Comma-separated UUIDs | — |
| `epic_id` | Comma-separated UUIDs | — |
| `due_status` | `enum(overdue, due_soon, no_due_date)?` | — |
| `created_by` | `UUID?` | — |
| `sort` | `enum(rank, created_at, -created_at, due_date)` | `rank` |
| `cursor` | `str?` | — |
| `limit` | `int` 1–100 | 30 |

`CreateWorkItemRequest` requires `id: UUID` and `title: str` (1–255). Optional non-null fields are `description_html`, `state_id`, `priority`, and `assignee_ids` (max 10). Nullable fields are `epic_id`, `start_date`, and `due_date`. `before_work_item_id` and `after_work_item_id` are optional nullable anchors and are mutually exclusive.

`UpdateWorkItemRequest` accepts the same mutable fields; only epic and dates may be explicitly cleared with `null`.

`MoveWorkItemRequest`:

```text
to_state_id: UUID
before_work_item_id?: null | UUID
after_work_item_id?: null | UUID
expected_work_item_version: int >= 1
expected_board_version: int >= 1
client_mutation_id: UUID
```

All referenced states, epics, members, and neighbors must belong to the project. At most 10 unique project members may be assigned. Rich text is sanitized, dates must be ordered, and the server owns opaque `rank` allocation.

## Board and preferences

Prefix: `/api/v1/workspaces/{workspace_slug}/projects/{project_id}`

| Method and path | Request | Response | Permission |
| --- | --- | --- | --- |
| `GET .../board` | Board query | `BoardResponse` | Project membership |
| `GET .../board-preferences` | — | `BoardPreferencesResponse` | Project membership |
| `PATCH .../board-preferences` | `UpdateBoardPreferencesRequest` | `BoardPreferencesResponse` | Project membership, including archived projects |

Board query fields are `search?`, comma-separated `priority?`, comma-separated `assignee_id?`, comma-separated `epic_id?`, `due_status?`, `only_mine?: bool` (false), and `per_column?: int` (1–50, default 30).

The board response contains:

```text
data.project: Project
data.permissions: ProjectPermissions
data.board_version: int
data.columns[]: { state, work_items[], page }
data.included: { members[], epics[] }
data.preferences: { display, collapsed_state_ids[], version }
```

Preferences are created lazily on first read. A patch accepts non-null optional `display: dict[str, bool]` and `collapsed_state_ids: UUID[]`. The backend validates display keys and state ownership in the manager.

## Epics

Prefix: `/api/v1/workspaces/{workspace_slug}/projects/{project_id}/epics`

| Method and path | Request | Response | Permission |
| --- | --- | --- | --- |
| `GET .../epics` | Epic list query | `EpicPage` | Project membership |
| `POST .../epics` | `CreateEpicRequest` | `EpicResponse`, 201 | `can_create_epic` |
| `GET .../epics/{epic_id}` | — | `EpicDetailResponse` | Project membership |
| `PATCH .../epics/{epic_id}` | `UpdateEpicRequest` | `EpicResponse` | `can_edit_epic` |
| `DELETE .../epics/{epic_id}` | — | 204 | Own-epic or any-epic delete permission |
| `GET .../epics/{epic_id}/work-items` | `search?`, `cursor?`, `limit?` | `WorkItemPage` | Project membership |
| `POST .../epics/{epic_id}/work-items` | `AddEpicWorkItemsRequest` | `EpicWorkItemsMutationResponse` | `can_edit_epic` |
| `DELETE .../epics/{epic_id}/work-items/{work_item_id}` | — | `EpicWorkItemsMutationResponse` | `can_edit_epic` |

Epic list query supports `search?`, comma-separated `state_group?`, `priority?`, `assignee_id?`, `status?: enum(active, completed)`, `sort?: enum(rank, created_at, -created_at, due_date, -progress)`, `cursor?`, and `limit` 1–100 (default 30).

`CreateEpicRequest` requires `id: UUID` and `title: str` (1–255). Optional non-null fields are `description_html`, `state_id`, `priority`, and up to 10 `assignee_ids`. `start_date` and `due_date` are nullable. Patch accepts the same mutable fields; only dates may be explicitly cleared.

`AddEpicWorkItemsRequest` contains 1–100 unique `work_item_ids` and `move_from_other_epics: bool`. Deleting an epic detaches rather than deletes its work items. Progress counts work items whose state's semantic group is `completed`.

## Resource response shapes

### Project

The full project contains `id`, `workspace_slug`, `name`, `identifier`, nullable `description`, `icon`, `color`, `access`, actor `role`, explicit `permissions`, `member_preview`, `total_members`, active work-item and epic counts, nullable `archived_at`, timestamps, `version`, `member_ids`, and `default_state_id`.

### State

`State` contains `id`, `project_id`, `name`, `color`, `group`, `position`, `is_default`, `work_items_count`, and `version`.

### Work item

`WorkItemCard` contains identity, project/sequence identifiers, title, state, priority, assignee IDs, nullable epic/dates, opaque `rank`, creator, timestamps, and version. `WorkItem` adds `description_html`. Detail responses add available states, members, epic picker items, and permissions.

### Epic

`EpicListItem` contains identity, project/sequence identifiers, title, state, priority, assignees, dates, rank, work-item totals, progress percentage, creator, timestamps, and version. `Epic` adds `description_html`. Detail responses add states, members, and permissions.

### Agent

`Agent` contains project, kind, name, description, instructions, model, memory policy, step limit, approval mode, lifecycle status, system tool names, timestamps, and version.

## Project capabilities

Admins manage the project, states, agents, all cards, and all epics. Members can create/edit/move cards, delete their own cards, and create/edit/delete their own epics. Viewers are read-only. All roles can read the project. The named actions and minimum roles used by authorization checks are documented in the [Authz API](../authz/api.md#authorization-policy).

## Related documentation

- [PMS overview](README.md)
- [PMS flows](flows.md)
- [Shared API conventions](../../api.md)
- [Authz API](../authz/api.md)
- [PMS tables](../../../database/README.md)
