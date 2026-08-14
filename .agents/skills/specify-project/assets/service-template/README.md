# Service Specification: <!-- TEMPLATE: Service name -->

## Status

<!-- TEMPLATE: State service owner, specification status, last reviewed date, and implementation evidence status. -->

## Responsibility

<!-- TEMPLATE: State the service's single responsibility, owned capabilities/data, and explicit non-ownership. -->

## Start Here

Read [the service contract](spec.md), [scenarios](scenarios.md), and [technical design](design/technical.md).

## Reading Routes

| Goal | Read in order |
|---|---|
| Understand the service | [Service contract](spec.md) → [Technical design](design/technical.md) → [Scenarios](scenarios.md) |
| Add or revise a feature | [Feature registry](features/README.md) → feature contract → affected service documents |
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
| [design/ui-ux.md](design/ui-ux.md) | user-facing surfaces, states, accessibility |
| [interfaces/api.md](interfaces/api.md) | APIs and request/response interfaces |
| [interfaces/events.md](interfaces/events.md) | produced and consumed events |
| [data/models.md](data/models.md) | domain and transport models |
| [data/tables.md](data/tables.md) | physical persistence contracts |
| [decisions.md](decisions.md) | service-local decisions |

## Maintenance Rules

<!-- TEMPLATE: Define feature registration, change propagation, ownership, evidence, and validation rules. -->
