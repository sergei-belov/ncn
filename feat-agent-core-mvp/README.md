# Feature Plan: Agent Core MVP

## Status

**Draft for implementation review.** Owner: **Open** (`ncn-agents` owner). Last reviewed: 2026-08-12. The contract is implementation-ready for local and integration work; the exact tool-capable model deployment and production load thresholds remain rollout decisions.

## Scope Boundary

This package specifies one project-scoped core agent, a direct sessionless Run API, a durable Temporal workflow, and one allowlisted read-only system MCP integration. It is the first vertical slice of the broader agent architecture, not completion of the full v2 multi-agent MVP.

Sessions, Messages, coordinator-to-worker delegation, dynamic RunPlan revisions, approvals, mutating tools, memory/RAG, artifacts, automation, Kafka publication, and frontend execution surfaces are outside this feature.

## Start Here

Read [the feature contract](feature.md) for authoritative scope and behavior, then use [the scenario contract](scenarios.md) and [the delivery plan](delivery/plan.md) to trace behavior into implementation slices.

## Reading Routes

| Goal | Read in order |
|---|---|
| Understand the feature | [Feature contract](feature.md) → [User scenarios](scenarios.md) → [Decisions](decisions.md) |
| Review technical design | [Technical design](design/technical.md) → [API contract](interfaces/api.md) → [Data model](data/model.md) |
| Review the non-UI experience | [User scenarios](scenarios.md) → [UI/UX applicability](design/ui-ux.md) → [API contract](interfaces/api.md) |
| Implement the feature | [Delivery plan](delivery/plan.md) → [Technical design](design/technical.md) → applicable interface and data contracts |
| Resume agent work | [Agent context](AGENTS.md) → [Feature contract](feature.md) → [Delivery plan](delivery/plan.md) |

## Document Map

| Document | Authority |
|---|---|
| [AGENTS.md](AGENTS.md) | Persistent reading order and change rules |
| [feature.md](feature.md) | Scope, requirements, invariants, and acceptance |
| [scenarios.md](scenarios.md) | User/system behavior, alternatives, failures, and recovery |
| [design/technical.md](design/technical.md) | Component design, flows, ownership, and operations |
| [design/ui-ux.md](design/ui-ux.md) | Explicit backend-only UI/UX applicability decision |
| [interfaces/api.md](interfaces/api.md) | HTTP, Temporal, and MCP contracts |
| [data/model.md](data/model.md) | Data ownership, schema, lifecycle, and consistency |
| [decisions.md](decisions.md) | Consequential decisions and open decision queue |
| [delivery/plan.md](delivery/plan.md) | Dependency-ordered slices, validation, rollout, and rollback |

## Evidence Base

- User request dated 2026-08-12: minimum agent core with Temporal, MCP, and the agent itself; no Sessions at this stage.
- `contracts/agents/02-invariants/`: authoritative v2 architecture invariants.
- `contracts/agents/03-module-design/`: lower-priority detailed design evidence where it does not expand this slice.
- `contracts/agents/04-implementation-details/`: retry, timeout, API, and backend-pattern evidence.
- `docs/features/agent-management.md` and `docs/data/agent-config.md`: verified frontend configuration semantics; they do not claim execution behavior.
- `backend/spec.md`, `backend/pyproject.toml`, and the current `backend/` tree: verified current backend lacks Agent Run, Temporal, MCP, and model runtime wiring.

## Evidence and Decision Vocabulary

- **Confirmed**: explicitly requested or verified in authoritative artifacts.
- **Assumed**: reversible choice selected with a documented rationale.
- **Open**: unresolved choice with material impact and a named resolution trigger.
- **Present**: path, behavior, or symbol verified in the current workspace.
- **Planned**: proposed but not yet implemented or verified.

## Maintenance Rules

- Keep each contract authoritative in one document and link to it elsewhere.
- Preserve the sessionless boundary unless the feature is explicitly revised.
- Update scenarios, designs, interfaces, data, decisions, and slices when a requirement changes.
- Link every added Markdown document from this README or another reachable document.
- Re-run the feature validator after structural or contract changes.
