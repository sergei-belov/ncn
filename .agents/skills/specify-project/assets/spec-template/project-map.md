# Project Map

## Snapshot

| Field | Value |
|---|---|
| Last reviewed | <!-- TEMPLATE: date --> |
| Specification status | <!-- TEMPLATE: status --> |
| Active services | <!-- TEMPLATE: services --> |
| Evidence inspected | <!-- TEMPLATE: documentation only or explicit implementation evidence --> |
| Implementation verification boundary | <!-- TEMPLATE: scope and request --> |

## Reading Routes

| Goal | Route |
|---|---|
| Understand the project | [Project contract](spec.md) → [System architecture](architecture/system.md) |
| Change a service | [Service registry](services/README.md) → selected service README/spec |
| Add a feature | [Feature registry](features/README.md) → owning service feature → affected contracts |
| Change API/events | [Interface map](interfaces/README.md) → service interfaces |
| Change models/tables | [Data ownership](data/README.md) → service data contracts |

## Documentation Map

| Area/service | Purpose | Authority | Status | Owner |
|---|---|---|---|---|
| <!-- TEMPLATE: area/service --> | <!-- TEMPLATE: purpose --> | <!-- TEMPLATE: link --> | <!-- TEMPLATE: status --> | <!-- TEMPLATE: owner --> |

## Service Ownership Map

| Service | Capabilities | Authoritative data | Interfaces/events | Dependencies | Forbidden ownership | Status |
|---|---|---|---|---|---|---|
| <!-- TEMPLATE: service --> | <!-- TEMPLATE: capabilities --> | <!-- TEMPLATE: data --> | <!-- TEMPLATE: contracts --> | <!-- TEMPLATE: dependencies --> | <!-- TEMPLATE: boundary --> | <!-- TEMPLATE: status --> |

## Runtime Entry Points

| Entry point | Kind | Owner | Location/contract | Status | Evidence |
|---|---|---|---|---|---|
| <!-- TEMPLATE: entry point --> | <!-- TEMPLATE: UI/API/event/job/worker/etc. --> | <!-- TEMPLATE: service --> | <!-- TEMPLATE: path or link --> | <!-- TEMPLATE: present/planned/external/unknown --> | <!-- TEMPLATE: source --> |

## Change Impact Map

| Capability/feature | Owner | Affected services | Scenarios | UI/UX | API/events | Models/tables | Decisions | Implementation/tests | Observability |
|---|---|---|---|---|---|---|---|---|---|
| <!-- TEMPLATE: capability --> | <!-- TEMPLATE: service --> | <!-- TEMPLATE: services --> | <!-- TEMPLATE: links --> | <!-- TEMPLATE: link/N/A --> | <!-- TEMPLATE: links --> | <!-- TEMPLATE: links --> | <!-- TEMPLATE: IDs --> | <!-- TEMPLATE: status --> | <!-- TEMPLATE: signals --> |

## Known Gaps

| Gap | Impact | Status | Resolution trigger |
|---|---|---|---|
| <!-- TEMPLATE: gap --> | <!-- TEMPLATE: impact --> | <!-- TEMPLATE: planned/unknown --> | <!-- TEMPLATE: evidence/decision --> |
