# NCN Current Development Specification

NCN is a project-management platform with an internal coordinator-and-worker agent runtime and one common authorization layer. This documentation describes three current logical services: `ncn-authz`, `ncn-pms`, and `ncn-agents`. They are physically colocated in the current backend where verified; future integrations and domain expansions remain deferred context.

## Start Here

Read [the project contract](spec.md), [system architecture](architecture/system.md), and [project map](project-map.md).

## Reading Routes

| Goal | Read in order |
|---|---|
| Understand the project | [Project contract](spec.md) → [Product overview](product/overview.md) → [Glossary](product/glossary.md) → [Architecture](architecture/system.md) |
| Understand authorization | [Authz README](services/ncn-authz/README.md) → [feature](services/ncn-authz/features/database-driven-authorization.md) → [common interface](services/ncn-authz/interfaces/api.md) |
| Understand PMS | [PMS README](services/ncn-pms/README.md) → [feature](services/ncn-pms/features/project-work-management.md) → [API](services/ncn-pms/interfaces/api.md) |
| Understand agents | [Agents README](services/ncn-agents/README.md) → [configuration](services/ncn-agents/features/agent-configuration.md) → [execution](services/ncn-agents/features/coordinated-agent-execution.md) |
| Review architecture and technology stack | [Architecture](architecture/system.md) → [approved shared infrastructure](architecture/system.md#approved-shared-infrastructure) → [current adoption](architecture/system.md#current-development-adoption) |
| Review interfaces/data | [Interface map](interfaces/README.md) → [Data ownership](data/README.md) → owner service contract |
| Review evidence/status | [Project map](project-map.md) → selected service README |
| Review decisions | [Project decisions](decisions/README.md) → affected service decisions |

## Sources of Truth

| Concern | Source |
|---|---|
| Current project scope and acceptance | [spec.md](spec.md) |
| Service boundaries, common authorization, flows, and approved technology stack | [architecture/system.md](architecture/system.md) |
| Current services | [services/README.md](services/README.md) |
| Current features | [features/README.md](features/README.md) |
| APIs/events | [interfaces/README.md](interfaces/README.md) |
| Data ownership | [data/README.md](data/README.md) |
| Verified implementation paths | [project-map.md](project-map.md) |

`docs_old/**` is legacy frontend evidence, not active authority. `contracts/agents/**` and `contracts/pms/**` are detailed design evidence reconciled into the current service specifications.

## Status Vocabulary

- **Confirmed**, **Assumed**, and **Open** describe certainty.
- **Present**, **Planned**, **External**, and **Unknown** describe implementation/path evidence.
- A Planned capability may be part of a service currently in development; it is not evidence of implementation.

## Maintenance Rules

Do not create a service folder until that service enters active development and evidence establishes its ownership boundary. Keep future product ideas under Deferred/Open sections. Update every affected current service contract and validate `docs/` after edits.
