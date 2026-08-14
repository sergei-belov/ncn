# Backend Review Checklist

## Core Sources

- `backend/AGENTS.md`
- `backend/pyproject.toml`
- The matching template in `backend/templates/`
- The nearest working module in the same layer

## Cross-Layer Checks

- Keep SQLAlchemy, DTO, API, and enum fields aligned
- Require an Alembic migration when schema changed
- Flag thin repository helper methods when `backend/libs/cp_postgresql/base_repository_generic.py` already provides the needed behavior through `get`, `get_list`, `get_paginated_list`, `get_count`, `update`, `upsert`, `delete`, or related generic methods
- Prefer manager-level filter composition over repository methods like `get_by_name` or `get_by_project` when the logic is just passing simple filter kwargs
- Check aggregator updates:
  `backend/models/pydantic/__init__.py`, `backend/models/sqlalchemy/__init__.py`, `backend/models/enum/__init__.py`, `backend/api/db/db.py`, `backend/api/managers/managers.py`, `backend/api/router/router.py`
- Confirm router prefixes match current backend routes, which are mounted under `/v1/...`
- Confirm PATCH uses partial update models and `exclude_unset`
- Confirm project scoping and auth checks follow neighboring code
- Confirm async DB work uses `Services.database.session()`

## Style Checks

- Keep imports grouped and formatted for Black and isort
- Keep lines within the `120` limit from `backend/pyproject.toml`
- Remove template placeholders and TODO text before approving
- Keep filenames, class names, and DTO or API suffixes consistent with the repo

## Common Misses

- Missing export in an `__init__.py`
- Missing repository registration in `Database`
- Missing manager registration in `Managers`
- Missing router include in `backend/api/router/router.py`
- Missing enum import in `backend/models/enum/__init__.py`
- Missing migration or incomplete downgrade path
