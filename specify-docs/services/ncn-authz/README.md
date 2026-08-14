# Service Specification: ncn-authz

## Status

Owner: Platform authorization team. Specification: Draft, last reviewed 2026-08-14. The common backend User/ProjectUser models, authentication helpers, FastAPI dependencies, project-role resolution, and persisted-user tracking are **Present** in the shared backend by authorized verification. Independent `ncn-authz` deployment, external policy API, membership administration, production identity synchronization, and schema migration readiness are not claimed.

## Responsibility

`ncn-authz` is the logical owner of the common identity-to-actor and project-authorization layer used by every backend service. It owns persisted application users, project-user roles, role-to-action policy evaluation, common authorization dependencies, and access audit identity. It does not own project work, agent configuration/execution, authentication-provider accounts, or consumer-domain resources.

## Start Here

Read [the service contract](spec.md), [the authorization feature](features/database-driven-authorization.md), [scenarios](scenarios.md), and [technical design](design/technical.md).

## Reading Routes

| Goal | Read in order |
|---|---|
| Understand the service | [Service contract](spec.md) → [Feature](features/database-driven-authorization.md) → [Scenarios](scenarios.md) |
| Add or revise a feature | [Feature registry](features/README.md) → feature contract → affected service documents |
| Review consumer behavior | [Technical design](design/technical.md) → [API/common interface](interfaces/api.md) → consumer service contract |
| Review user-visible consequences | [UI/UX applicability](design/ui-ux.md) → [Scenarios](scenarios.md) → consumer UI contract |
| Review persistence | [Models](data/models.md) → [Tables](data/tables.md) → [Decisions](decisions.md) |
| Review future separation | [Technical design](design/technical.md) → [Project architecture](../../architecture/system.md) → [Project decisions](../../decisions/README.md) |

## Document Map

| Document | Authority |
|---|---|
| [spec.md](spec.md) | responsibility, behavior, requirements, invariants, acceptance |
| [scenarios.md](scenarios.md) | observable flows, alternatives, failures, recovery |
| [features/README.md](features/README.md) | service feature registry |
| [design/technical.md](design/technical.md) | common-layer components, flows, dependencies, security, operations |
| [design/ui-ux.md](design/ui-ux.md) | non-UI applicability and consumer consequences |
| [interfaces/api.md](interfaces/api.md) | authentication HTTP and common authorization interface |
| [interfaces/events.md](interfaces/events.md) | current event non-applicability and future boundary |
| [data/models.md](data/models.md) | User, ProjectUser, authorized actor, and permission models |
| [data/tables.md](data/tables.md) | `users` and `project_users` persistence contracts |
| [decisions.md](decisions.md) | service-local authorization decisions and open choices |

## Maintenance Rules

Register each authorization feature here and at project level. When identity, project role, permission, error, logging, rate-limit, or trust behavior changes, update every consumer service's scenario and interface contract. Keep provider authentication separate from application authorization. Present claims require explicit evidence; planned service extraction must not create a second source of truth or change observable allow/deny semantics.
