# Authz logical service

Authz owns authentication, persistent actor identity, access relationships, role restrictions, and named authorization decisions. It runs inside the shared `ncn-pms` FastAPI process and supplies the identity and permission context consumed by PMS.

## Responsibilities

- resolve OAuth2 bearer identity and provision or load an active `users` row;
- provide optional local registration and password login;
- administer workspace and project memberships;
- apply per-service role restrictions that may narrow project access;
- evaluate registered workspace, project, and service actions;
- protect role ceilings and the final workspace owner or project admin;
- emit privacy-safe authorization logs and metrics.

## Implementation map

| Layer | Main modules |
| --- | --- |
| Routers | `backend/api/router/auth.py`, `backend/api/router/authorization.py` |
| HTTP dependencies | `backend/api/dependencies/http/http.py` |
| Managers | `backend/api/managers/auth.py`, `backend/api/managers/authorization.py` |
| Repositories | `backend/api/db/users.py`, `workspace_users.py`, `project_users.py`, `service_users.py` |
| Public models | `backend/models/pydantic/api/auth_api.py`, `authorization_api.py` |
| Domain enums | `backend/models/enum/authz.py`, project roles from `backend/models/enum/pms.py` |

## Data ownership

| Table | Role |
| --- | --- |
| [`users`](../../../database/tables/users.md) | Persistent identity and optional local credential |
| [`workspace_users`](../../../database/tables/workspace_users.md) | Workspace role assignment |
| [`project_users`](../../../database/tables/project_users.md) | Project role and membership source |
| [`service_users`](../../../database/tables/service_users.md) | Per-service role restriction |

PMS project routes consume `project_users` through their request dependency and manager capability checks. PMS project creation also bootstraps the creator’s project-admin row through the authz-owned membership model.

## Current boundary gaps

- The frontend HTTP session adapter expects `POST /auth/session/resolve`, which is not exposed by FastAPI.
- Workspace membership is not currently consulted for PMS project list/create visibility.
- Project `access=workspace` does not grant implicit project membership.
- Non-local deployments rely on the gateway as the external token-verification boundary.

## References

- [Authz API](api.md)
- [Authz flows](flows.md)
- [Shared API conventions](../../api.md)
- [Cross-service flows](../../flows.md)
- [PMS logical service](../pms/README.md)
