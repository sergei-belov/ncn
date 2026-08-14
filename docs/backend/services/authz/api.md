# Authz API

This reference owns the authentication, membership, restriction, and named-policy routes. All paths and payloads follow the [shared backend API conventions](../../api.md).

## Authentication

| Method and path | Request | Response | Notes |
| --- | --- | --- | --- |
| `GET /api/v1/auth/me` | — | `UserAPI` | Current active user |
| `POST /api/v1/auth/register` | `PostRegisterRequest` | `PostRegisterResponse`, 201 | Local auth only |
| `POST /api/v1/auth/jwt/login` | Form `username`, `password` | `PostLoginResponse` | Local auth only |

`PostRegisterRequest`:

| Field | Type | Rules |
| --- | --- | --- |
| `email` | `str` | 3–100, email-like pattern, trimmed/lowercased |
| `name` | `str` | 1–100, trimmed |
| `password` | `str` | 8–128 |

Login uses `application/x-www-form-urlencoded`; `username` is 3–100 and `password` is 8–128. The response is `{ "access_token": "..." }`.

`UserAPI` contains `id`, `email`, `name`, `is_active`, `created_at`, and `updated_at`.

## Authorization and memberships

| Method and path | Request | Response | Required authority |
| --- | --- | --- | --- |
| `POST /api/v1/authorization/check` | `AuthorizationCheckRequest` | `AuthorizationCheckResponse` | Authenticated user; may check only own `user_id` |
| `GET /api/v1/workspaces/{workspace_id}/members` | List query | `WorkspaceMembershipList` | Workspace owner/admin |
| `POST /api/v1/workspaces/{workspace_id}/members` | `user_id`, `role` | `WorkspaceMembership`, 201 | Workspace owner/admin |
| `PATCH /api/v1/workspaces/{workspace_id}/members/{user_id}` | `role`, `expected_version` | `WorkspaceMembership` | Workspace owner/admin |
| `POST /api/v1/workspaces/{workspace_id}/members/{user_id}/revoke` | `expected_version` | 204 | Workspace owner/admin |
| `GET /api/v1/projects/{project_id}/members` | List query | `ProjectMembershipList` | Project admin |
| `POST /api/v1/projects/{project_id}/members` | `user_id`, `role` | `ProjectMembership`, 201 | Project admin |
| `PATCH /api/v1/projects/{project_id}/members/{user_id}` | `role`, `expected_version` | `ProjectMembership` | Project admin |
| `POST /api/v1/projects/{project_id}/members/{user_id}/revoke` | `expected_version` | 204 | Project admin |
| `PUT /api/v1/projects/{project_id}/members/{user_id}/services/{service_id}` | `role`, `expected_version?` | `ServiceRestrictionResult`, 200/201 | Project admin |
| `DELETE /api/v1/projects/{project_id}/members/{user_id}/services/{service_id}` | JSON body `expected_version` | 204 | Project admin |
| `PUT /api/v1/projects/{project_id}/creator-access` | `workspace_id`, `creator_user_id` | `ProjectMembership`, 200/201 | Authenticated persisted creator |

Membership list query: `search?: str` (max 100), `cursor?: str` (max 512), `limit?: int` (1–100, default 50).

Roles:

- workspace: `owner`, `admin`, `member`;
- project/service: `admin`, `member`, `viewer`;
- project membership source: `manual`, `bootstrap`.

`WorkspaceMembership` contains `id`, `workspace_id`, `user_id`, `role`, positive `version`, `created_at`, and `updated_at`; list items add the safe user summary. `ProjectMembership` adds `project_id`, `source`, and list-item `service_restrictions`. A service restriction contains `id`, `project_user_id`, `service_id`, role, version, and timestamps; PUT responses also expose `effective_role`.

Workspace ownership cannot be granted or transferred through the generic create/update endpoints. The last workspace owner and last project admin are protected. A service restriction may only be equal to or lower than both the target project role and actor authority. Changing a project role below an existing service restriction is rejected.

`AuthorizationCheckRequest` fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `user_id` | `UUID` | Must equal authenticated actor |
| `action` | `str` | Registered policy action, 1–100 |
| `workspace_id` | `str?` | Required by every current action |
| `project_id` | `UUID?` | Required for project/service actions |
| `service_id` | `str?` | Required only for service actions; lowercase ID pattern |
| `resource` | `{type: str, id: str}?` | Must match the action's scope resource |

The response contains `allowed`, a stable `reason`, `effective_role`, `effective_scope`, and `policy_version` (`v1`). Expected denial reasons are `ROLE_ALLOWED`, `NO_MEMBERSHIP`, `ROLE_INSUFFICIENT`, `USER_DISABLED`, and `SCOPE_MISMATCH`; malformed policy requests return errors instead of a deny response.

## Authorization policy

Role ranks are workspace `member < admin < owner` and project `viewer < member < admin`. Service restrictions reuse project roles.

| Named action | Scope | Minimum role |
| --- | --- | --- |
| `workspace.member.read` | Workspace | `admin` |
| `workspace.member.manage` | Workspace | `admin` |
| `project.read` | Project | `viewer` |
| `project.update` | Project | `admin` |
| `project.archive` | Project | `admin` |
| `project.member.read` | Project | `viewer` |
| `project.member.manage` | Project | `admin` |
| `project.service.read` | Service | `viewer` |
| `project.service.manage` | Service | `admin` |
| `project.state.manage` | Project | `admin` |
| `project.agent.manage` | Project | `admin` |
| `project.work_item.read` | Project | `viewer` |
| `project.work_item.write` | Project | `member` |
| `project.work_item.delete_any` | Project | `admin` |
| `project.epic.read` | Project | `viewer` |
| `project.epic.write` | Project | `member` |
| `project.epic.delete_any` | Project | `admin` |

Named authorization decisions are not cached. PMS project responses expose a related capability object derived from project roles and ownership rules.

## Related documentation

- [Authz overview](README.md)
- [Authz flows](flows.md)
- [Shared API conventions](../../api.md)
- [PMS API](../pms/api.md)
- [Authz tables](../../../database/README.md)
