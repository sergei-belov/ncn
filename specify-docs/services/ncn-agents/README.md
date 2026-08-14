# Service Specification: ncn-agents

## Status

Owner: Agent platform team. Specification: Draft, last reviewed 2026-08-14. Agent list/configuration/status UI, API, common `ncn-authz` actor consumption, and transitional table are **Present**. Sessions UI is a **Present placeholder**. Durable coordinator/worker execution, Runs, approvals, memory/tool integration, and independent deployment are **Planned** under the normative agent invariants.

## Responsibility

`ncn-agents` owns project-scoped agent registration/configuration, immutable Run snapshots, Sessions, Messages, Runs, plans/revisions, invocations, tool executions, approvals, execution/tool constraints, budgets/usage, memory/RAG metadata, Run events, and agent-produced artifact metadata. It consumes common persisted actor and project-action authorization from `ncn-authz`; it executes work but never owns User/ProjectUser, PMS project-work, or external-system business truth.

## Start Here

Read [the service contract](spec.md), [configuration feature](features/agent-configuration.md), [execution feature](features/coordinated-agent-execution.md), and [scenarios](scenarios.md).

## Reading Routes

| Goal | Read in order |
|---|---|
| Understand the service | [Service contract](spec.md) → [Technical design](design/technical.md) → [Scenarios](scenarios.md) |
| Review agent setup | [Configuration feature](features/agent-configuration.md) → [UI/UX](design/ui-ux.md) → [API](interfaces/api.md) |
| Review execution | [Execution feature](features/coordinated-agent-execution.md) → [Scenarios](scenarios.md) → [Events](interfaces/events.md) |
| Review persistence | [Models](data/models.md) → [Tables](data/tables.md) → [Decisions](decisions.md) |

## Document Map

| Document | Authority |
|---|---|
| [spec.md](spec.md) | responsibility, requirements, invariants, acceptance |
| [scenarios.md](scenarios.md) | configuration, Run, approval/recovery behavior |
| [features/README.md](features/README.md) | feature registry |
| [design/technical.md](design/technical.md) | orchestration, dependencies, trust, operations |
| [design/ui-ux.md](design/ui-ux.md) | agent, Session, Run, approval experience |
| [interfaces/api.md](interfaces/api.md) | Present config and Planned Run APIs |
| [interfaces/events.md](interfaces/events.md) | Planned lifecycle events |
| [data/models.md](data/models.md) | agent/execution models |
| [data/tables.md](data/tables.md) | transitional and Planned persistence |
| [decisions.md](decisions.md) | agent-local decisions/open queue |

## Maintenance Rules

The v2 invariant contract in `contracts/agents/02-invariants/**` is design evidence, but this folder is the living service contract. Update both features and all affected execution/UI/API/event/model/table contracts together. Preserve common authz consumption, coordinator/worker, snapshot, permission/Approval, project isolation, Temporal, MCP, duplicate-safety/reconciliation, and PostgreSQL-first invariants. Present implementation evidence must remain separate from Planned design.
