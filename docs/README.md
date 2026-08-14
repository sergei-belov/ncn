# NCN platform documentation

This documentation describes the NCN project-management platform as implemented in the current working tree. It covers the Vue frontend, FastAPI backend, PostgreSQL mappings, user-visible pages, shared UI, HTTP contracts, and main system flows.

Verified against the implementation on 2026-08-14.

## Platform scope

NCN currently provides:

- workspace-scoped projects with `admin`, `member`, and `viewer` project roles;
- Kanban states, ordered work items, filters, drag-and-drop, and personal display preferences;
- epics with work-item membership and computed completion progress;
- one required coordinator plus configurable worker agents per project;
- workspace, project, and per-service access administration;
- local demo mode backed by browser `localStorage` and an HTTP mode intended for FastAPI.

Agent sessions have a user interface placeholder only. Workspace creation, comments, files, notifications, realtime updates, background jobs, and agent execution are not implemented.

## Documentation map

| Area | Document |
| --- | --- |
| System boundaries and deployment | [Architecture](architecture.md) |
| Frontend architecture and route inventory | [Frontend](frontend/README.md) |
| Shared frontend shells and navigation | [General UI](frontend/general/README.md) |
| Every implemented page | [Page catalog](frontend/pages/README.md) |
| Shared UI, widgets, and feature components | [Components and UI](frontend/components.md) |
| Backend logical services and shared runtime | [Backend](backend/README.md) |
| Authentication, memberships, and authorization policy | [Authz service](backend/services/authz/README.md) |
| Project-management domain | [PMS service](backend/services/pms/README.md) |
| Shared REST conventions and service API indexes | [API reference](backend/api.md) |
| Cross-service and domain flow indexes | [System flows](backend/flows.md) |
| PostgreSQL tables and relationships | [Database](database/README.md) |

## Current delivery status

The default `VITE_API_MODE=mock` path is the coherent runnable product demonstrated by the frontend. The browser database supplies projects, board data, epics, agents, and authorization state.

The FastAPI service implements the same broad domains, but the current frontend HTTP adapters do not yet match several backend contracts. The important differences are recorded in [HTTP integration status](architecture.md#http-integration-status). HTTP mode should therefore be treated as an integration target, not a verified end-to-end runtime.

## Source of truth

The documents were derived from:

- [frontend routes and implementation](../frontend/src/app/router/routes.ts);
- [frontend shared UI](../frontend/src/shared/ui/);
- [frontend resource adapters](../frontend/src/entities/);
- [backend routers](../backend/api/router/);
- [backend public Pydantic models](../backend/models/pydantic/api/);
- [backend SQLAlchemy mappings](../backend/models/sqlalchemy/).

The older `doc_reference/` tree describes a different QAi test-automation product and is not part of this NCN contract. `backend/spec.md` is retained as a pre-authorization PMS snapshot; this documentation set supersedes it for current platform behavior.
