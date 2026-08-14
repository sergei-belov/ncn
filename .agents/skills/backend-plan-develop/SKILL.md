---
name: backend-plan-develop
description: Plan and implement backend changes in this repository using `backend/AGENTS.md`, this skill's bundled template copies in `references/templates/*.template`, and neighboring backend modules as the source of truth. Use when Codex needs to build or modify backend features, APIs, models, repositories, managers, routers, Kafka schema/producer/stream wiring, or related code in `backend/**`, especially when the implementation should be derived from `git diff HEAD -- docs` before falling back to the direct user request. Do not create table migrations, execute project code, or run formatters.
---

# Backend Planner & Developer

## Overview

Implement backend features for this repo by turning either the current `docs/` diff or the direct user request into concrete changes across the FastAPI, Pydantic, SQLAlchemy, Kafka broker, and backend wiring layers.

## Required Start

1. Run `git diff HEAD --name-only -- docs`. Check only docs folder - no global diff.
2. If `docs/` has changes, read `git diff HEAD -- docs`.
3. If the user explicitly asked for a concrete implementation, use the user request as the primary spec and use the docs diff only as supporting context when it does not conflict.
4. If there is no explicit backend ask, treat the docs diff as the primary spec.
5. Read `backend/AGENTS.md`.
6. Read `references/template-map.md`.
7. Read `backend/libs/cp_postgresql/base_repository_generic.py` before adding or changing repository methods.
8. Open the exact templates you need under `references/templates/`.
9. Inspect the nearest existing backend files in the same layer before editing.
10. If the change touches asynchronous commands, events, or stream processing, inspect the run Kafka path: `backend/models/pydantic/schema/runs.py`, `backend/api/managers/runs.py`, and `backend/api/stream/runs.py`.

## Plan Before Editing

- Decide which layers are affected:
  `backend/models/sqlalchemy/`, `backend/models/pydantic/dto/`, `backend/models/pydantic/api/`, `backend/models/pydantic/schema/`, `backend/models/enum/`, `backend/api/db/`, `backend/api/managers/`, `backend/api/router/`, `backend/api/stream/`.
- List the required registration updates before coding:
  `backend/models/pydantic/__init__.py`, `backend/models/pydantic/schema/__init__.py`, `backend/models/sqlalchemy/__init__.py`, `backend/models/enum/__init__.py`, `backend/api/db/db.py`, `backend/api/managers/managers.py`, `backend/api/router/router.py`, `backend/api/stream/__init__.py`.
- Prefer the nearest real module over the raw template when the template is more generic than the established code.

## Hard Constraints

- MUST write Google-style docstrings for every class, function, and method added or modified. Use a short summary for straightforward logic and declarative types such as Pydantic models. Use a detailed docstring for large classes or complex functions and methods, documenting behavior and the applicable `Args`, `Returns`, `Raises`, side effects, and non-obvious invariants. This requirement overrides bundled templates or neighboring code that omit docstrings.
- NEVER create new Alembic migrations or edit existing table migrations in `backend/migrations/postgres/versions/`.
- DO NOT execute code. Limit command usage to read-only inspection such as `git diff`, `rg`, `sed`, `cat`, or similar file-reading commands.
- DO NOT run Python modules, tests, servers, migration commands, compile checks, or any other project/application execution.
- DO NOT run formatters or linters such as `black`, `isort`, `ruff format`, or similar tools.
- If the requested backend change would normally require a migration or runtime validation, leave that work undone and state it explicitly in the final handoff.

## Implementation Rules

- Use `backend/AGENTS.md` for architecture and naming rules.
- Use the matching bundled template from `references/templates/` as the starting point, then adapt it to the concrete resource and the nearest real module.
- Mirror existing route prefixes and registration patterns from real files such as `backend/api/router/*.py`; current routers use `/v1/...`.
- Keep routers thin: declare params, dependencies, and response models, then call managers.
- Put business rules, authorization checks, and cross-repository orchestration in managers.
- Put data access and SQLAlchemy queries in `backend/api/db/`.
- For Kafka-backed workflows, define broker payloads as Pydantic schema models under `backend/models/pydantic/schema/` using `models.pydantic.schema.base.Model`; include topic metadata in `Meta`.
- Produce Kafka messages from managers after durable DB work, following `RunsManager.create_run()` in `backend/api/managers/runs.py` with `Services.broker.produce(...)` and producer flushing when the local pattern does so.
- Handle Kafka consumers under `backend/api/stream/` with `@Services.broker.listen(...)`, typed schema payloads, and manager calls for business logic; use `backend/api/stream/runs.py` as the primary stream-processing example.
- Prefer the generic repository methods already provided by `backend/libs/cp_postgresql/base_repository_generic.py` for simple CRUD and filtered reads:
  `get`, `get_by_ids`, `get_list`, `get_paginated_list`, `get_count`, `update`, `upsert`, `delete`, `delete_many`, and `delete_list`.
- For common and simple lookup logic, keep the decision-making in managers and pass filter kwargs into the generic repository methods instead of adding one-off repository helpers such as `get_by_name`, `get_by_project`, or similar thin wrappers.
- Add custom repository methods only when the query is genuinely custom:
  joins, aggregations, CTE-heavy logic, special ordering, or reusable SQL that cannot be expressed cleanly through the generic methods.
- Keep SQLAlchemy, DTO, and API models aligned on field names, nullability, and semantics.
- For PATCH payloads, prefer `UpdateFields...` models plus `model_dump(exclude_unset=True)`.
- Use `Services.database.session()` for async DB work.
- Never create or edit Alembic table migrations, even when schema changes are part of the requested feature.
- Update every aggregator or import hub touched by new modules.

## Common Pitfalls

- Adding a custom repository helper for a simple filtered read or write that `BaseDatabaseGeneric` already supports through `get`, `get_list`, `get_paginated_list`, `get_count`, `update`, `upsert`, `delete`, or related generic methods.
- Letting field names, nullability, or semantics drift between SQLAlchemy, DTO, API, and enum models.
- Copying a bundled template into production code without reconciling it with the nearest live module, especially around auth checks, project scoping, route prefixes, and response shapes.
- Putting business rules, auth, or cross-repository orchestration in routers or repositories instead of managers.
- Forgetting registration updates in `backend/models/pydantic/__init__.py`, `backend/models/sqlalchemy/__init__.py`, `backend/models/enum/__init__.py`, `backend/api/db/db.py`, `backend/api/managers/managers.py`, or `backend/api/router/router.py`.
- Forgetting Kafka wiring updates in `backend/models/pydantic/schema/__init__.py` or `backend/api/stream/__init__.py`.
- Producing stream messages before the DB state they reference is committed or visible to the consumer.
- Putting stream-processing business rules directly in `backend/api/stream/*.py` instead of delegating to managers.
- Creating or editing migration files even though this skill must not touch table migrations.
- Implementing PATCH with full-update models or plain `model_dump()` instead of `UpdateFields...` models plus `model_dump(exclude_unset=True)`.
- Opening ad hoc DB sessions or bypassing `Services.database.session()` for async database work.
- Introducing route prefixes or endpoint shapes that do not match the current `/v1/...` patterns in neighboring routers.
- Running project code, tests, migration commands, or formatters as part of implementation or verification.

## Completion Checks

- Confirm every added or modified class, function, and method has a complexity-appropriate Google-style docstring.
- Ensure the feature is wired end-to-end: model exports, schema exports, `Database`, `Managers`, router includes, stream imports, and any enums.
- Ensure template placeholders are fully replaced and filenames and class names match repo conventions.
- Ensure auth and project scoping follow neighboring code.
- Do not run formatters, tests, migration commands, compile checks, or other project/application execution as part of this skill.
- Use only static inspection of the edited files and wiring before handing off.

## References

- Read `references/template-map.md` for the template-to-folder mapping and repo wiring checkpoints.
- Read `references/templates/*.template` from this skill, not `backend/templates/`, unless the skill itself is being refreshed.
