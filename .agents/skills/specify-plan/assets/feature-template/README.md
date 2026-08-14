# Feature Plan: <!-- TEMPLATE: Feature name -->

## Status

<!-- TEMPLATE: State the owner if known, last reviewed date, and whether the plan is draft, reviewed, accepted, or superseded. -->

## Start Here

Read [the feature contract](feature.md) for authoritative scope and behavior, then use [the scenario contract](scenarios.md) and [the delivery plan](delivery/plan.md) to trace behavior into implementation slices.

## Reading Routes

| Goal | Read in order |
|---|---|
| Understand the feature | [Feature contract](feature.md) → [User scenarios](scenarios.md) → [Decisions](decisions.md) |
| Review technical design | [Technical design](design/technical.md) → [API contract](interfaces/api.md) → [Data model](data/model.md) |
| Review the experience | [User scenarios](scenarios.md) → [UI/UX design](design/ui-ux.md) → [API contract](interfaces/api.md) |
| Implement the feature | [Delivery plan](delivery/plan.md) → [Technical design](design/technical.md) → applicable interface, data, and UX contracts |
| Resume agent work | [Agent context](AGENTS.md) → [Feature contract](feature.md) → [Delivery plan](delivery/plan.md) |

## Document Map

| Document | Authority |
|---|---|
| [AGENTS.md](AGENTS.md) | Persistent reading order and change rules |
| [feature.md](feature.md) | Scope, requirements, invariants, and acceptance |
| [scenarios.md](scenarios.md) | User behavior, alternatives, failures, and recovery |
| [design/technical.md](design/technical.md) | Component design, flows, ownership, and operations |
| [design/ui-ux.md](design/ui-ux.md) | Information architecture, interactions, states, and accessibility |
| [interfaces/api.md](interfaces/api.md) | API and machine-interface contracts |
| [data/model.md](data/model.md) | Data ownership, schema, lifecycle, and consistency |
| [decisions.md](decisions.md) | Consequential decisions and open decision queue |
| [delivery/plan.md](delivery/plan.md) | Dependency-ordered slices, validation, rollout, and rollback |

## Evidence and Decision Vocabulary

- **Confirmed**: explicitly requested or verified in authoritative artifacts.
- **Assumed**: reversible choice selected with a documented rationale.
- **Open**: unresolved choice with material impact and a named resolution trigger.
- **Present**: path, behavior, or symbol verified in the current workspace.
- **Planned**: proposed but not yet implemented or verified.

## Maintenance Rules

- Keep each contract authoritative in one document and link to it elsewhere.
- Update affected scenarios, designs, interfaces, data, decisions, and slices when a requirement changes.
- Link every added Markdown document from this README or another reachable document.
- Re-run the feature validator after structural or contract changes.
