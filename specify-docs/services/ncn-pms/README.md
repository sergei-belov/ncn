# Service Specification: ncn-pms

## Status

Owner: PMS service team. Specification: Draft, last reviewed 2026-08-14. Project/board/work-item/epic/state UI, FastAPI API, models, and PostgreSQL mappings are **Present** by authorized inspection. PMS consumption of the common `ncn-authz` actor boundary is Present. Independent deployment is not claimed.

## Responsibility

`ncn-pms` is the system of record for project work: projects, boards, stages, cards, epics and ordering. It consumes the common persisted actor and project-role decision from `ncn-authz`, then enforces PMS domain/archive/reference rules. It does not own users, project roles/policy, agent configuration, Sessions or Runs.

## Start Here

Read [the service contract](spec.md), [scenarios](scenarios.md), and [technical design](design/technical.md).

## Reading Routes

| Goal | Read in order |
|---|---|
| Understand the service | [Service contract](spec.md) → [project-work feature](features/project-work-management.md) → [authz dependency](../ncn-authz/features/database-driven-authorization.md) → [Scenarios](scenarios.md) |
| Review the experience | [UI/UX design](design/ui-ux.md) → [Scenarios](scenarios.md) → [API](interfaces/api.md) |
| Review interfaces | [API](interfaces/api.md) → [Events](interfaces/events.md) → [Models](data/models.md) |
| Review persistence | [Models](data/models.md) → [Tables](data/tables.md) → [Technical design](design/technical.md) |
| Review rationale | [Decisions](decisions.md) → affected contracts |

## Document Map

| Document | Authority |
|---|---|
| [spec.md](spec.md) | responsibility, behavior, requirements, invariants, acceptance |
| [scenarios.md](scenarios.md) | observable flows, alternatives, failures, recovery |
| [features/README.md](features/README.md) | service feature registry |
| [design/technical.md](design/technical.md) | components, flows, dependencies, security, operations |
| [design/ui-ux.md](design/ui-ux.md) | project-work surfaces and states |
| [interfaces/api.md](interfaces/api.md) | PMS HTTP operations |
| [interfaces/events.md](interfaces/events.md) | planned domain events |
| [data/models.md](data/models.md) | PMS domain/read/command models |
| [data/tables.md](data/tables.md) | verified PMS persistence contracts |
| [decisions.md](decisions.md) | service-local decisions and open choices |

## Maintenance Rules

Register each current PMS feature here and at project level. Update UI, API, model, table, permission, scenario and acceptance contracts together. `ncn-pms` alone writes PMS domain state; the frontend and agents use supported APIs/tools. Present claims require renewed implementation evidence. Agent configuration currently colocated in the backend is excluded from PMS ownership. PMS must require the common `ncn-authz` actor/policy result and must never reinterpret token or runtime settings as permission.
