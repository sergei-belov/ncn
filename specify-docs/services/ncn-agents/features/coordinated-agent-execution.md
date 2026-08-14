# Feature: Coordinated Agent Execution

## Status

Owning service: `ncn-agents`. Status: Draft/Planned. Owner: Agent platform. Reviewed 2026-08-13. Evidence is the normative v2 agent invariant contract; no execution backend was verified.

## Problem and Goal

Users need agents to complete multi-step project work, but model behavior is probabilistic and external effects can be costly or irreversible. The goal is a bounded, durable, explainable Run in which one coordinator may delegate to non-nested workers, every side effect is explicit, policy and human approval are authoritative, and failures recover without duplicate effects.

## Actors and Permissions

| Actor/system | Goal | Allowed | Forbidden/constrained |
|---|---|---|---|
| Member | Submit goal, follow progress, answer/approve/cancel | Policy-permitted Session/Run actions | Cannot inject authority/tool credentials |
| Coordinator | Build/revise/execute plan | Unstarted safe-boundary revision and worker/tool selection | No hidden side effects or policy bypass |
| Worker | Execute delegated node | Assigned context/memory/tools | No nesting, Run/plan/scope control |
| Approver | Decide a described action | Approve/reject when eligible | Cannot approve changed arguments or forbidden action |
| Temporal/system | Persist execution | Retry/wait/signal/cancel by deterministic workflow | No owner business mutations outside activities/tools |

## Scope

### In Scope

Session/Message; one active mutating Run; immutable snapshot; RunPlan with coordinator/worker/tool/approval/finalization nodes; immutable revisions; bounded parallel `all`; Temporal workflow/activities; model/structured output adapter; scoped memory and artifacts; MCP tools; permission/Approval; retries/idempotency/reconciliation; cancellation; result/usage/audit.

### Out of Scope

Worker-to-worker calls, separate planning agent, arbitrary loops/CEL/JSONPath, joins beyond `all`, no-code workflow designer, user MCP OAuth, exactly-once external effects, complex billing, advanced RAG ACL, unrestricted automation.

## Requirements and Invariants

| ID | Requirement/invariant | Rationale | Acceptance |
|---|---|---|---|
| AGT-RUN-001 | One Run/one root Temporal workflow with deterministic workflow code and I/O in Activities. | Durable replay. | Restart/replay test preserves IDs and effects |
| AGT-RUN-002 | Plan and revisions are validated/immutable; side effects exist only as explicit nodes. | Explainability/control. | Malformed/hidden-effect plans rejected |
| AGT-RUN-003 | Tool execution checks common actor/action authorization, execution policy, Approval, scope, risk, client command identity, and current Run state immediately before call. | Prevent unsafe action. | Adversarial policy/changed-args tests |
| AGT-RUN-004 | Retry is class-specific; unknown mutation outcome becomes reconciliation. | Prevent duplicate external effect. | Timeout/duplicate-safety matrix tests |
| AGT-RUN-005 | Hard limits and structured output validation terminate controllably with partial/failure result. | Bound cost/infinite work. | Budget/node/tool/repair limit tests |
| AGT-RUN-006 | Result and audit expose completed/failed parts, effects, unresolved items, sources, and usage. | User/operator trust. | Reconstruction against Run records |

## Scenarios and Contract Effects

| Scenario | UI/UX | API/events | Models/tables | Affected services |
|---|---|---|---|---|
| SCN-002 execute coordinated Run | UX-AGT-003/004 | API-AGT-003..006 | MODEL-AGT-003..010; TABLE-AGT-003..012 | Frontend, PMS owner tools |
| SCN-003 approve/reconcile risky tool | UX-AGT-004/005 | API-AGT-005/006 | Approval/ToolExecution/RunResult | PMS/external tool owner when applicable |

## Failure, Recovery, and Observability

Transient model/read activities retry within budget; validation does not. Structured output receives at most two repairs. Mutations retry only when an owner-defined client command identity makes replay safe. Unknown outcomes pause for reconciliation; rejected approval becomes a controlled branch/result. Cancellation propagates to cancelable activities and yields a terminal result without erasing completed effects. Observe every state transition, plan revision, invocation, tool attempt, approval age, retry/repair, tokens/cost, effect, and reconciliation item with persisted user and Run/node/tool IDs plus redaction.

## Acceptance Criteria

- The selected first vertical user goal completes end-to-end with at least one coordinator decision, required worker/tool, and structured result.
- Run survives API/worker restart, keeps snapshot, and never duplicates an effect.
- Forbidden/cross-project tool calls and invalid structured outputs fail safely.
- Approval durably pauses/resumes and changed arguments invalidate the decision.
- Cancellation and every hard limit produce a controlled terminal envelope and reconstructable audit.

## Assumptions and Open Questions

Assume bounded sequential execution plus limited parallel `all`. Open and blocking: first use case/tools/RAG/approval, message concurrency semantics, exact models/fallback/budgets, tables/API/errors, retention/SLO/RPO/RTO.

## Traceability

[Service spec](../spec.md), [SCN-002/003](../scenarios.md), [technical design](../design/technical.md), [UI/UX](../design/ui-ux.md), [API](../interfaces/api.md), [events](../interfaces/events.md), [models](../data/models.md), [tables](../data/tables.md), [decisions](../decisions.md), project FEAT-003/REQ-003/006.
