# NCN Product Overview

## Problem

Project teams need a clear work-management surface and a controlled way to delegate bounded tasks to AI agents. Ordinary chat assistants do not preserve project scope, durable execution, tool permissions, human approval, or an auditable result.

## Audience

| Segment/actor | Context | Need | Current workaround | Value |
|---|---|---|---|---|
| Project admin | Configures project workflow and agents | Manage projects, stages, coordinator, workers and limits | Separate project and prompt settings | One governed project context |
| Project member | Executes daily project work | Manage cards/epics and request agent help | Board plus manual AI/tool coordination | Work and assistance in one product |
| Viewer/approver | Reviews status or a risky action | Read authorized state and decide eligible approvals | Ad-hoc messages/reports | Explicit read-only and approval states |
| Platform operator | Runs backend/workers/infrastructure | Diagnose Runs, budgets, failures and recovery | Manual service inspection | Correlated execution evidence |

## Value Proposition

NCN combines a common database-backed authorization layer, an authoritative PMS, and a project-scoped agent coordinator with specialized workers. Every service uses the same persisted actor/project role. Agent execution is designed to be durable, bounded, permission-controlled, approval-aware and auditable; agents interact with PMS through its API/MCP boundary rather than its database.

## Primary Use Cases

| Use case | Trigger | Outcome | Owning services |
|---|---|---|---|
| Resolve and authorize a user | User accesses a protected route | One persisted actor UUID and current project role/action decision reach the owning service | `ncn-authz` |
| Manage project work | User opens or edits a project | Projects, workflow stages, cards and epics stay consistent | `ncn-pms` |
| Configure agent team | Admin edits coordinator/workers | Versioned project-scoped configuration is ready for Runs | `ncn-agents` |
| Execute coordinated request | User sends a message | Coordinator plans, workers/tools execute within policy, result/usage/audit persist | `ncn-agents`, using `ncn-pms` tools where needed |

## Product Boundaries and Measures

Current implementation evidence covers the shared authorization layer, PMS, agent configuration, and a Sessions placeholder. Coordinated Run execution is the current in-development contract but not verified as implemented. Future integrations with MCP services such as GitLab, procurement and analytics are deferred; they do not create current service ownership or acceptance obligations. Success is measured by consistent persisted authorization, correct PMS journeys, protected agent configuration, and the eventual end-to-end durable Run acceptance described by `ncn-agents`.
