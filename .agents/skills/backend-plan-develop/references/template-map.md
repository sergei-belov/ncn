# Backend Template Map

## Read Order

1. `backend/AGENTS.md`
2. `references/database-methods.md` when touching repositories or manager code that calls repositories
3. `references/kafka-streaming.md` when touching Kafka stream models, listeners, or producers
4. The nearest existing backend module in the same layer
5. The matching file in `references/templates/`

## Template Mapping

- `references/templates/sqlalchemy_model.template`
  Target: `backend/models/sqlalchemy/*.py`
- `references/templates/dto_model.template`
  Target: `backend/models/pydantic/dto/*_dto.py`
- `references/templates/api_model.template`
  Target: `backend/models/pydantic/api/*_api.py`
- `references/templates/enum_model.template`
  Target: `backend/models/enum/*.py`
- `references/templates/db.template`
  Target: `backend/api/db/*.py`
- `references/templates/manager.template`
  Target: `backend/api/managers/*.py`
- `references/templates/router.template`
  Target: `backend/api/router/*.py`

## Wiring Checklist

- Export new Pydantic models in `backend/models/pydantic/__init__.py`
- Export new SQLAlchemy models in `backend/models/sqlalchemy/__init__.py`
- Export new enums in `backend/models/enum/__init__.py`
- Register repositories in `backend/api/db/db.py`
- Register managers in `backend/api/managers/managers.py`
- Include new routers in `backend/api/router/router.py`
- Export stream models in `backend/models/pydantic/stream/__init__.py` and `backend/models/pydantic/__init__.py`
- Import stream listener modules in `backend/api/stream/__init__.py`
- Do not add Alembic migrations; state required schema work in the final handoff when schema changes are part of the request

## Repository Rule

- Read `references/database-methods.md` before adding repository-specific methods.
- Use `BaseDatabaseGeneric` methods for simple repository work:
  `create`, `bulk_create`, `get`, `get_by_ids`, `get_list`, `get_paginated_list`, `get_count`, `update`, `upsert`, `delete`, `delete_many`, `delete_list`
- Keep simple filtering and selection logic in managers by passing kwargs such as `id=...`, `project_id=...`, `name=...`
- Do not add thin repository wrappers like `get_by_name`, `get_by_project`, or similar single-filter helpers when the generic API already covers the case
- Add repository-specific methods only for real custom queries such as joins, aggregations, reusable complex statements, or special result shaping

## Local Comparison Targets

- Routers and managers: inspect the nearest matching files under `backend/api/router/` and `backend/api/managers/`
- Repositories: inspect the nearest matching files under `backend/api/db/`
- Kafka listener and producer flow: use `references/kafka-streaming.md` for embedded examples and inspect nearest matching files under `backend/api/stream/` and `backend/api/managers/`
- Registration hubs: `backend/api/db/db.py`, `backend/api/managers/managers.py`, `backend/api/router/router.py`, and `backend/api/stream/__init__.py`

## Preference Rule

If a template is more generic than the real codebase, follow the nearest working module and keep `backend/AGENTS.md` as the architectural baseline.

## Maintenance Note

These bundled templates are a local copy for this skill. When the repo's backend templates evolve, refresh `references/templates/` so the skill stays aligned.
