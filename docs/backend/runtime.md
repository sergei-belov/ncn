# Backend runtime and architecture

The `authz` and `pms` logical services run in the same asynchronous FastAPI application and share one service hub, middleware stack, database session boundary, and deployment lifecycle.

## Runtime stack

| Area | Implementation |
| --- | --- |
| Language | Python 3.13 |
| HTTP | FastAPI and Uvicorn |
| Validation | Pydantic 2 and `pydantic-settings` |
| Persistence | SQLAlchemy 2 async ORM, PostgreSQL, `asyncpg` |
| Authentication | OAuth2 bearer extraction, PyJWT, bcrypt local credentials |
| Migrations | Alembic configuration, currently no checked-in revisions |
| Observability | Prometheus FastAPI instrumentator and structured Python logs |
| Development | Poetry, Poe, pytest, Ruff, mypy configuration |

## Application structure

| Layer | Location | Responsibility |
| --- | --- | --- |
| Bootstrap | `backend/api/main.py` | Middleware, routers, lifecycle, errors, logging, metrics |
| Routers | `backend/api/router/` | Paths, methods, request dependencies, response models |
| HTTP dependencies | `backend/api/dependencies/http/` | Bearer identity, user provisioning, project membership, rate limiting |
| Managers | `backend/api/managers/` | Permissions, invariants, transactions, response assembly |
| Repositories | `backend/api/db/` | Scoped async database operations and aggregates |
| Public models | `backend/models/pydantic/api/` | Strict request, response, query, pagination, and error contracts |
| Internal models | `backend/models/pydantic/dto/` | Manager/repository transfer values |
| Persistence models | `backend/models/sqlalchemy/` | Tables, columns, foreign keys, indexes, and checks |

## Registered runtime services

- `Services.database`: async engine, transaction-scoped sessions, and database health.
- `Services.auth`: OAuth2 bearer extraction and JWT helpers.
- `Services.collector`: request instrumentation and authorization-operation counters.

Kafka, Redis, LLM, storage, and worker libraries are not registered in the service hub.

## Public surfaces

- Authz: `/api/v1/auth`, `/api/v1/authorization`, workspace memberships, project memberships, service restrictions, and creator access.
- PMS: `/api/v1/workspaces/{workspace_slug}/projects` and all nested project resources.
- Shared operations: `/healthcheck`, `/metrics`, `/docs`, and `/openapi.json`.

## Cross-cutting behavior

- Every response receives `X-Correlation-ID`; a valid inbound value is reused.
- Domain, validation, framework, and unexpected failures use a JSON error envelope.
- Authorized users are rate-limited in memory per process; the default is 60 requests per minute.
- CORS is installed only when `CORS_ALLOW_ORIGINS` is non-empty.
- Manager operations share a transaction and commit only on clean session exit.
- Rich text is sanitized to a conservative tag/link allow-list and capped at 100 KiB after sanitization.
- Archived projects reject domain mutations, while personal board preferences remain mutable.

## Operational gaps

- The Alembic versions directory is empty, so schema creation is an external prerequisite.
- Rate limiting is process-local and resets on restart.
- Domain events are structured logs, not durable events or an outbox.
- The gateway must remain the external identity-verification boundary for non-local authentication deployments.
- Current frontend HTTP adapters are not fully compatible with the backend contract; see [HTTP integration status](../architecture.md#http-integration-status).
- Workspace roles and project `access=workspace` are not currently connected to PMS project visibility; nested project routes still require an explicit project membership.

## Related documentation

- [Backend service index](README.md)
- [API conventions](api.md)
- [Cross-service flows](flows.md)
- [Database](../database/README.md)
