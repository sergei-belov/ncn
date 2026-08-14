# Project Specification System

## Contents

- [Baseline structure](#baseline-structure)
- [Document authority](#document-authority)
- [Project contract coverage](#project-contract-coverage)
- [Service and feature ownership](#service-and-feature-ownership)
- [Cross-service contracts](#cross-service-contracts)
- [Consistency rules](#consistency-rules)

## Baseline structure

```text
docs/
├── AGENTS.md
├── README.md
├── spec.md
├── project-map.md
├── product/
│   ├── overview.md
│   └── glossary.md
├── architecture/
│   └── system.md
├── services/
│   └── README.md
├── features/
│   └── README.md
├── interfaces/
│   └── README.md
├── data/
│   └── README.md
└── decisions/
    └── README.md
```

Each service is a child of `docs/services/` and follows the service baseline in `service-system.md`. The project baseline stays small; detail belongs to service owners.

## Document authority

| Concern | Authority |
|---|---|
| Purpose, actors, outcomes, scope, capabilities, invariants, acceptance | `docs/spec.md` |
| Audience and product measures | `docs/product/overview.md` |
| Canonical language and identifiers | `docs/product/glossary.md` |
| System context, service boundaries, shared infrastructure, cross-service flows | `docs/architecture/system.md` |
| Service catalog and links | `docs/services/README.md` |
| Feature-to-owner registry | `docs/features/README.md` |
| Cross-service API/event conventions and interaction map | `docs/interfaces/README.md` |
| Systems of record and cross-service data ownership | `docs/data/README.md` |
| Project-wide decisions and open decision queue | `docs/decisions/README.md` |
| Navigation, path status, entry points, impact | `docs/project-map.md` |

Do not duplicate service-specific fields, tables, payloads, screens, or scenarios at project level. Summarize the boundary and link to the owner.

## Project contract coverage

Make `docs/spec.md` define:

1. the problem, audience, and project thesis;
2. measurable outcomes and success criteria;
3. scope, non-goals, and deferred capabilities;
4. actors, permissions, and primary project journeys;
5. capability inventory and owning service;
6. project-wide functional requirements and invariants;
7. security, privacy, accessibility, reliability, performance, compatibility, and operational requirements;
8. dependencies and constraints;
9. assumptions, open questions, and end-to-end acceptance.

Use stable IDs such as `OUT-NNN`, `REQ-NNN`, `INV-NNN`, and `NFR-NNN` when referenced across service folders.

## Service and feature ownership

Give each business capability and authoritative data set exactly one owning service. Consumers use the owner's API/events; they do not redefine or copy owner state.

Register every service with name, responsibility, owned capabilities/data, interfaces, dependencies, status, and service README link.

Register every feature with:

- canonical feature name and `FEAT-NNN` if useful;
- one owning service and feature contract link;
- affected/consumer services;
- project outcome or requirement links;
- status: proposed, draft, reviewed, accepted, active, complete, superseded, or retired;
- last reviewed date.

Features change the living service specs. Do not create a parallel feature architecture, data model, or delivery plan outside service ownership.

## Cross-service contracts

Use `architecture/system.md` for responsibility and runtime flows, `interfaces/README.md` for interaction protocols, and `data/README.md` for authoritative data ownership.

For each cross-service flow define trigger, ordered participants, authority checks, interface/API/event, correlation and idempotency, state changes, consistency, failure/recovery, observability, and user-visible result.

Record consequential ownership or infrastructure choices in project decisions. Keep service-local choices in the service decision file.

## Consistency rules

| Change | Inspect and reconcile |
|---|---|
| Project scope/outcome/invariant | service specs, feature registry, architecture, acceptance |
| Service responsibility or ownership | service registry, architecture, interfaces, data, decisions, maps |
| New/revised feature | owner and consumer service docs, project registries, cross-service maps |
| API/event contract | consumers, scenarios, models, tables, compatibility, security |
| Model/table/lifecycle | service requirements, APIs/events, transactions, retention, consumers |
| UI flow/state | scenarios, API errors, models, accessibility, permissions |
| Path/status/evidence | project map, service README, AGENTS instructions |
| Document inventory | README routes, registries, validator reachability |

Reject contradictions instead of averaging them. Mark unresolved conflicts **Open** with an impact and resolution trigger.
