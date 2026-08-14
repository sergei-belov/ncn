# NCN PMS Backend Application Specification

> Historical snapshot: this file predates the current authorization-management
> routes and tables. Use [`../docs/README.md`](../docs/README.md) for the current
> implementation-derived platform contract.

## Overview

The current backend is the `ncn-pms` FastAPI service. It owns the project-management
MVP described by
[`contracts/pms/plane-project-management-mvp-contract-ru.md`](../contracts/pms/plane-project-management-mvp-contract-ru.md):

- workspace-scoped projects
- project workflow states and their Kanban order
- work items and manual ordering inside states
- epics and epic membership
- aggregated Kanban board snapshots
- per-user board display preferences
- project roles and permission checks

The service is implemented as one asynchronous FastAPI application in
[`api/main.py`](./api/main.py). PostgreSQL is the transactional source of truth.
The application persists authenticated users and project-user roles. It supports
local registration and login when `AUTH_FLOW=local`; otherwise it expects a bearer
token issued by the platform identity system. Workspace creation and workspace
membership management remain outside the service.

**API base path**: `/api/v1`

An optional ASGI deployment prefix can be supplied through `APP_ROOT_PATH` without
changing the router paths declared in source.

---

## Tech Stack

| Category | Technology |
| --- | --- |
| Language | Python 3.13 |
| Web framework | FastAPI 0.141 + Uvicorn |
| Validation and settings | Pydantic 2 + `pydantic-settings` |
| ORM | SQLAlchemy 2.0 async ORM |
| Transactional database | PostgreSQL via `asyncpg` |
| Synchronous migration driver | `psycopg2-binary` |
| Authentication primitives | OAuth2 bearer dependency, PyJWT, bcrypt |
| Schema migrations | Alembic |
| Metrics | Prometheus client + `prometheus-fastapi-instrumentator` |
| Packaging and tasks | Poetry + Poe the Poet |
| Static checks | Ruff + mypy |
| Test configuration | pytest + `pytest-asyncio` |

Current dependency notes:

- The runtime dependency set has no Kafka, Redis, Temporal, Qdrant, object-storage,
  notification, or LLM client.
- Generic Kafka and Redis-oriented code remains under [`libs/`](./libs), but it is
  not wired into the `ncn-pms` application.
- Unit tests use pytest and `pytest-asyncio` and are exposed through the `poe test`
  task.

---

## Application Bootstrap

### FastAPI Application

[`api/main.py`](./api/main.py) defines an `Application` subclass and exports the
ASGI object as `app`.

At initialization the application:

- creates the shared service hub from [`api/services/services.py`](./api/services/services.py)
- configures title, description, and `root_path`
- optionally installs CORS middleware
- includes all active routers
- registers startup and shutdown handlers for external services
- registers typed PMS, validation, HTTP, and fallback exception handlers
- configures Python logging
- instruments FastAPI and exposes Prometheus metrics

### Shared Runtime Services

The active service hub exposes:

| Service | Purpose |
| --- | --- |
| `Services.database` | Async PostgreSQL engine, sessions, health ping, and transaction boundary |
| `Services.auth` | OAuth2 bearer extraction and shared JWT helper |
| `Services.collector` | FastAPI request instrumentation and Prometheus exposition |

Database sessions begin a transaction on entry, commit on a clean exit, and roll
back on an exception. Managers group related domain changes inside one shared
session so project counters, ranks, memberships, command identity, and entity
changes commit atomically.

---

## HTTP Routing Structure

Active routers are composed in [`api/router/router.py`](./api/router/router.py).

```text
/
├── /healthcheck
├── /metrics
├── /docs
├── /openapi.json
├── /api/v1/auth
│   ├── GET /me
│   ├── POST /register
│   └── POST /jwt/login
└── /api/v1/workspaces/:workspace_slug/projects
    ├── GET, POST /api/v1/workspaces/:workspace_slug/projects
    └── /:project_id
        ├── GET, PATCH /api/v1/workspaces/:workspace_slug/projects/:project_id
        ├── POST /archive
        ├── POST /restore
        ├── GET /board
        ├── GET, PATCH /board-preferences
        ├── GET, POST /states
        │   ├── POST /states/reorder
        │   └── PATCH, DELETE /states/:state_id
        ├── GET, POST /work-items
        │   ├── GET, PATCH, DELETE /work-items/:work_item_id
        │   └── POST /work-items/:work_item_id/move
        └── GET, POST /epics
            ├── GET, PATCH, DELETE /epics/:epic_id
            ├── GET, POST /epics/:epic_id/work-items
            └── DELETE /epics/:epic_id/work-items/:work_item_id
```

Route notes:

- FastAPI supplies `/docs` and `/openapi.json` using its defaults.
- Prometheus instrumentation supplies `/metrics`.
- `/healthcheck` is supplied by the shared service hub and checks every registered
  external service.
- Local login and registration routes are available only when local auth is
  configured. `/auth/me` resolves the persisted user for either auth flow.
- There are no backend-owned workspace-management, project-user-management,
  WebSocket, file-upload, webhook, or event-consumer routes.

---

## API Resources

### 1. Authentication

Implemented by:

- [`api/router/auth.py`](./api/router/auth.py)
- [`api/managers/auth.py`](./api/managers/auth.py)
- [`api/db/users.py`](./api/db/users.py)

`POST /auth/register` stores a bcrypt password hash, `POST /auth/jwt/login`
returns a signed local bearer token, and `GET /auth/me` returns the current public
user without password data. The two local credential routes return
`AUTH_ROUTE_DISABLED` unless `AUTH_FLOW=local`.

### 2. Projects

Implemented by:

- [`api/router/projects.py`](./api/router/projects.py)
- [`api/managers/projects.py`](./api/managers/projects.py)
- [`api/db/projects.py`](./api/db/projects.py)

The paths in the table below are relative to the `/api/v1` base path.

| Method and path | Current behavior |
| --- | --- |
| `GET /workspaces/{workspace_slug}/projects` | Lists visible active or archived projects with search, ownership, sorting, and cursor pagination |
| `POST /workspaces/{workspace_slug}/projects` | Creates a project, creator admin membership, and four default states |
| `GET /workspaces/{workspace_slug}/projects/{project_id}` | Returns project metadata, counts, member preview, role, and permissions |
| `PATCH /workspaces/{workspace_slug}/projects/{project_id}` | Updates mutable project fields |
| `POST /workspaces/{workspace_slug}/projects/{project_id}/archive` | Archives after exact project-name confirmation |
| `POST /workspaces/{workspace_slug}/projects/{project_id}/restore` | Restores an archived project |

Project creation initializes these Russian workflow states:

| Position | Name | Semantic group | Default |
| ---: | --- | --- | :---: |
| 0 | `Бэклог` | `backlog` | No |
| 1 | `К выполнению` | `unstarted` | Yes |
| 2 | `В работе` | `started` | No |
| 3 | `Готово` | `completed` | No |

Identifiers are normalized to uppercase and must contain 2–10 uppercase letters or
digits. They are unique per workspace. Projects are archived rather than hard
deleted; archived projects are read-only except for restore and personal board
preferences.

### 3. States

Implemented by:

- [`api/router/states.py`](./api/router/states.py)
- [`api/managers/states.py`](./api/managers/states.py)
- [`api/db/states.py`](./api/db/states.py)

Current behavior:

- list ordered states with a work-item count
- create a state at the end or after a supplied state
- change name, color, semantic group, or default status
- reorder every state in one board-version-checked command
- delete a non-default state
- move work items and epics to a replacement state during deletion when required
- increment the owning project's `board_version` after structural changes

State names are case-insensitively unique within a project. A project must retain
at least one state and cannot delete its current default state. Reordering requires
the complete set of state IDs exactly once.

### 4. Work Items

Implemented by:

- [`api/router/work_items.py`](./api/router/work_items.py)
- [`api/managers/work_items.py`](./api/managers/work_items.py)
- [`api/db/work_items.py`](./api/db/work_items.py)

Current behavior:

- list work items with search, state, priority, assignee, epic, due-status,
  creator, sorting, and cursor filters
- create a work item in an explicit or default state
- return detail data with available states, project users, epic picker data, and
  computed permissions
- patch title, sanitized rich description, state, priority, assignees, epic, and dates
- move a card with optimistic work-item and board versions
- delete a card using creator/admin permission rules

Each project allocates monotonically increasing work-item sequence numbers. The
public identifier is composed as `{PROJECT_IDENTIFIER}-{sequence_id}`.

Manual order is stored as a fixed-width opaque `rank`. The repository locks the
destination ordering range, calculates a midpoint between adjacent cards, and
rebalances the state when no midpoint remains. Clients provide neighboring IDs and
never calculate ranks themselves.

### 5. Kanban Board and Preferences

Implemented by:

- [`api/router/board.py`](./api/router/board.py)
- [`api/managers/board.py`](./api/managers/board.py)
- [`api/db/board_preferences.py`](./api/db/board_preferences.py)

`GET .../{project_id}/board` returns one aggregated snapshot containing:

- the project and caller permissions
- the current `board_version`
- ordered state columns
- an independently limited first work-item page for each column
- project-user summaries
- up to 100 epic picker entries with computed progress
- the caller's board preferences

Board filters cover search, priorities, assignees, epic, due status, “only mine,”
and per-column page size. Subsequent card pages use the work-item list endpoint and
its state/cursor filters.

Preferences currently control priority, assignee, due-date, and epic visibility,
plus collapsed states. They are created lazily on the first board/preferences read,
so those GET requests can write the initial preference row. Preferences are
versioned per project and user, and may still be changed while the project is
archived.

### 6. Epics

Implemented by:

- [`api/router/epics.py`](./api/router/epics.py)
- [`api/managers/epics.py`](./api/managers/epics.py)
- [`api/db/epics.py`](./api/db/epics.py)

Current behavior:

- list epics with search, state-group, priority, assignee, status, sorting, and
  cursor filters
- create, read, update, and delete epics
- return detail data with available states, members, and permissions
- list an epic's work items
- add up to 100 work items, optionally moving them from other epics
- remove a work item from an epic

Epic identifiers use `{PROJECT_IDENTIFIER}-E{sequence_id}`. Progress is computed
from linked work items: items in a state whose semantic group is `completed` count
as complete. Deleting an epic does not delete its work items; their epic link is
cleared explicitly by the manager, with `ON DELETE SET NULL` as a database
safeguard.

---

## Component Architecture

### Router Layer (`api/router/`)

Routers declare paths, HTTP methods, request dependencies, status codes, and response
models. They delegate domain work to the manager singletons in
[`api/managers/managers.py`](./api/managers/managers.py).

### HTTP Dependency Layer (`api/dependencies/http/`)

The active dependencies:

- yield a request-scoped asynchronous database session
- decode the bearer token and resolve its email to the persisted `users` row
- join `users`, `project_users`, and `pms_projects` for project-scoped authorization
- require the current project-user relation for project-scoped routes
- log and rate-limit authorized requests by the persisted `users.id`
- adapt the authorized user to the actor DTO consumed by domain managers

### Manager Layer (`api/managers/`)

Managers own authorization, project scoping, validation, invariants, transaction
orchestration, response assembly, version checks, and idempotent replay. Shared
helpers in [`api/managers/common.py`](./api/managers/common.py) provide cursor
encoding, filter parsing, HTML sanitization, permissions, access resolution, and
structured domain event logging.

### Repository Layer (`api/db/`)

Repositories extend the generic async database helpers under
[`libs/cp_postgresql/`](./libs/cp_postgresql). They contain scoped SQLAlchemy
queries, row locks, versioned updates, aggregate counts, rank allocation, and
assignee replacement.

The [`api/db/db.py`](./api/db/db.py) registry exposes one repository instance per
active aggregate or association.

### Model Layer (`models/`)

The model layer is split into:

| Path | Purpose |
| --- | --- |
| `models/enum/pms.py` | Domain enums for roles, access, priority, states, statuses, and due filters |
| `models/pydantic/api/` | Strict public request, response, pagination, permission, and error shapes |
| `models/pydantic/dto/` | Internal transfer models aligned with persistence entities |
| `models/sqlalchemy/` | PostgreSQL table mappings and constraints |

Public API models use `extra="forbid"` and `from_attributes=True`. PATCH request
models distinguish omitted fields from explicit `null`; only documented nullable
fields can be cleared.

---

## Persistence Model

| Table | Purpose |
| --- | --- |
| `users` | Persisted authenticated identity and optional local password hash |
| `pms_projects` | Workspace ownership, presentation, access, archive state, versions, and sequence counters |
| `project_users` | Project-to-user authorization relation and role |
| `pms_agents` | Project coordinator and worker-agent configuration and lifecycle state |
| `pms_states` | Ordered workflow states and default-state marker |
| `pms_work_items` | Cards, state, epic link, dates, rank, creator, and version |
| `pms_work_item_assignees` | Work-item-to-member association |
| `pms_epics` | Epics, state, dates, rank, creator, and version |
| `pms_epic_assignees` | Epic-to-member association |
| `pms_board_preferences` | Per-project, per-user display and collapsed-state preferences |

PostgreSQL constraints cover core uniqueness and foreign-key relationships. The
manager layer additionally enforces workspace/project scope, project-user membership,
permission flags, archive state, valid dates, and cross-project reference rules.

There is no separate workspace table owned by this service. `users` and
`project_users` are the identity and role inputs used by the same dependencies and
manager authorization checks. There is no active API for managing project-user
relations.

---

## Authentication and Authorization

### Intended Request Model

All domain routes require an OAuth2 bearer token. The current request dependency
expects claims containing:

- an email used to resolve the persisted `users` row

The token establishes identity only. It does not supply application permissions.
The authenticated email must resolve to an existing `users` row. Project access
then resolves as follows:

- a project user receives the stored `admin`, `member`, or `viewer` role
- users without a `project_users` relation cannot access project resources
- the project dependency rejects a missing project-user relation with `403 FORBIDDEN`
- manager-level checks repeat project scope and role enforcement before domain work
- any persisted authenticated user may create a project and becomes its `admin`

Permission flags are returned to clients but are also checked again by managers.
Admins manage projects and states and can delete any card/epic. Members can create,
edit, move, and delete their own cards/epics. Viewers have read-only domain access.
All roles may change their personal board preferences.

### Authentication Trust Boundary

The mandatory API Gateway is the OIDC identity-verification boundary. It verifies
token signature, issuer, audience, timestamps, and subject
before forwarding a request. The service must therefore be deployed on a network
path that cannot bypass the gateway.

For gateway-authenticated OIDC requests, the backend decodes claims without
performing a second signature verification. It then independently enforces the
current project-user relation, database role permissions, archived-project rules,
cross-project references, and other domain invariants. Local auth flow tokens remain
signature-verified by the shared authorization helper.

---

## HTTP Consistency and Error Behavior

### Response Envelopes

Success responses use `data` and optional `meta`. Paginated responses include:

- `next_cursor`
- `has_more`
- `total_count`

The cursor is currently an opaque URL-safe base64 encoding of an integer offset.
It provides a cursor-shaped API but not keyset pagination.

Errors use a typed envelope:

```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "Project version is stale."
  }
}
```

Validation errors may add `field_errors`; concurrency errors may add `details`.
Malformed query values and unknown query parameters return
`400 MALFORMED_REQUEST`. Body and other field validation failures return
`422 VALIDATION_ERROR`.

### Optimistic Concurrency

- Project, state, work-item, epic, and board-preference resources carry positive
  integer versions.
- State reorder compares `expected_board_version` from the request body.
- Work-item move compares both `expected_work_item_version` and
  `expected_board_version`.
- Agent configuration and lifecycle commands carry `expected_version` in the JSON
  request body.
- Structural mutations increment the project's `board_version`.

### Client-generated command identity

Create payloads use client-generated UUIDs where their public request models expose
an `id`. Managers scope duplicate handling to the authenticated actor and project.
No command metadata is accepted through custom request headers.

### Domain Validation

- descriptions are sanitized through an allow-list HTML parser and capped at
  100 KiB after sanitization
- only users related to the current project may be assigned
- at most 10 unique assignees are allowed
- state, epic, neighbor, and collapsed-state references are constrained to the
  current project
- `start_date <= due_date` when both values exist
- archived projects reject domain mutations

---

## Request Middleware and Observability

### Rate Limiting

Authorized requests are limited to `RATE_LIMIT_PER_MINUTE`, default 60. The rate
window is keyed by the persisted `users.id` resolved by the authentication
dependency, so logging, authorization, and tracking use the same user identity.
The window is maintained in process memory.
Consequences of the current implementation:

- limits are per process, not shared across replicas
- a restart clears all windows
- unauthenticated local registration and login requests are not user-rate-limited

### CORS

CORS is installed only when `CORS_ALLOW_ORIGINS` is non-empty. Allowed methods are
GET, POST, PATCH, DELETE, and OPTIONS. Allowed custom headers include
Authorization, Content-Type.

### Metrics and Logs

- `prometheus-fastapi-instrumentator` exposes default request metrics at `/metrics`.
- Python standard logging is configured by the service hub.
- Domain events such as `project_created`, `work_item_moved`, and `board_loaded`
  are structured log records from `ncn_pms.events`.
- These events are not persisted to an outbox and are not published to Kafka.

Healthcheck behavior:

- `/healthcheck` pings every `BaseService` instance.
- PostgreSQL checks its connection.
- The in-process `PrometheusCollector` reports healthy after construction.

---

## Configuration

Configuration is defined in [`api/settings.py`](./api/settings.py).

| Group | Settings |
| --- | --- |
| Application | `APP_ROOT_PATH`, `CORS_ALLOW_ORIGINS`, `RATE_LIMIT_PER_MINUTE` |
| Authentication | `AUTH_FLOW`, login URL, local secret/algorithm, and token expiry |
| PostgreSQL | host, port, username, password, database, pool logging, pool size, retry period, statement timeout |

Unknown environment settings are ignored.

[`backend/.env.local`](./.env.local) exists, but normal ASGI initialization calls
`get_settings()` without naming an env file. The process environment therefore has
to provide runtime values unless the launcher loads that file. Poe's Alembic tasks
explicitly select `.env.local` as their env file.

---

## Migrations and Development Tasks

[`alembic.ini`](./alembic.ini) and
[`migrations/postgres/env.py`](./migrations/postgres/env.py) configure PostgreSQL
schema migration and load the SQLAlchemy metadata.

Poe tasks currently cover:

- Ruff check/fix and format for `api` and `models`
- creating the Alembic versions directory
- upgrade to head
- autogenerating a PostgreSQL revision
- downgrading one PostgreSQL revision
- running pytest

Current migration state:

- [`migrations/postgres/versions/`](./migrations/postgres/versions) is empty.
- No checked-in revision creates the ten active application tables.
- Database schema provisioning is therefore a separate prerequisite before this
  service can run against a clean database.

The files under [`migrations/kafka/`](./migrations/kafka) are generic legacy
schema-registry tooling. They reference Kafka settings and schema models that the
current PMS settings/model packages do not define, and they are not wired into the
application or Poetry tasks.

---

## File Structure

```text
backend/
├── api/
│   ├── db/
│   │   ├── board_preferences.py
│   │   ├── db.py
│   │   ├── epics.py
│   │   ├── project_users.py
│   │   ├── projects.py
│   │   ├── states.py
│   │   ├── users.py
│   │   └── work_items.py
│   ├── dependencies/
│   │   └── http/
│   │       └── http.py
│   ├── managers/
│   │   ├── auth.py
│   │   ├── board.py
│   │   ├── common.py
│   │   ├── epics.py
│   │   ├── managers.py
│   │   ├── projects.py
│   │   ├── states.py
│   │   └── work_items.py
│   ├── router/
│   │   ├── auth.py
│   │   ├── board.py
│   │   ├── epics.py
│   │   ├── projects.py
│   │   ├── router.py
│   │   ├── states.py
│   │   └── work_items.py
│   ├── services/
│   │   └── services.py
│   ├── stream/
│   │   └── __init__.py
│   ├── main.py
│   └── settings.py
├── libs/
│   ├── cp_aiostorage_orm/
│   ├── cp_common/
│   ├── cp_kafka/
│   ├── cp_postgresql/
│   └── cp_prometheus/
├── migrations/
│   ├── kafka/
│   └── postgres/
│       ├── versions/
│       ├── env.py
│       └── script.py.mako
├── models/
│   ├── enum/
│   │   └── pms.py
│   ├── pydantic/
│   │   ├── api/
│   │   └── dto/
│   └── sqlalchemy/
├── tests/
│   └── unit/
│       └── test_review_fixes.py
├── AGENTS.md
├── README.md
├── alembic.ini
├── pyproject.toml
├── ruff.toml
└── spec.md
```

---

## Current Structural Notes and Gaps

1. The live domain is PMS projects, states, work items, epics, and board
   preferences. Pipeline, run, variable, AI-generation, and project-graph source
   modules are absent; names for them survive only in compiled `__pycache__`
   artifacts and are not active architecture.
2. Gateway-bypassing network access must be prevented because the gateway is the
   OIDC signature-verification boundary.
3. PostgreSQL mappings exist, but no Alembic revision creates them.
4. `api/stream/` is empty, Kafka/schema-registry code is not configured, and domain
   events are logs only.
5. Shared `libs/` contains broader generic infrastructure than this service uses;
   directory presence alone should not be treated as an active integration.
6. The implementation has no background jobs, event outbox, distributed cache,
   realtime transport, file storage, or external notification integration.
