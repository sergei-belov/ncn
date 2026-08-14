# ncn-agents Service Contract

## Executive Contract

`ncn-agents` provides a controlled project-scoped agent team and durable execution. It consumes the persisted actor and project-action decision from `ncn-authz`. One active coordinator interprets a goal and maintains a validated RunPlan; specialized workers execute bounded tasks; tool calls pass through common authorization, deterministic execution constraints, and Approval; Temporal preserves workflow progress; PostgreSQL preserves product-visible truth, audit, usage, and results.

## Evidence and Status

| Topic | Status | Statement | Evidence/rationale |
|---|---|---|---|
| Agent configuration | Confirmed | Coordinator/worker list, CRUD/settings/status API/UI and SQL mapping are Present | Authorized backend/frontend inspection, 2026-08-13 |
| Durable execution | Confirmed design; Planned implementation | Session/Run/plan/snapshot/approval/MCP/memory semantics are normative | `contracts/agents/02-invariants/**` |
| Sessions UI | Confirmed | Project Sessions route and empty explanatory page are Present, with no verified data API | Authorized frontend inspection |
| Physical ownership | Open | Present table is `pms_agents` with FK to PMS projects, conflicting with target `ncn-agents` ownership | Current implementation vs repository architecture |
| First vertical scenario/limits | Open | Required product/tool/RAG/approval/SLO values are undecided | Agent invariant decision queue |

## Responsibility and Ownership

Own AgentConfiguration and immutable versions/snapshots; coordinator/worker topology; Session/Message/Run; RunPlan/revisions/nodes; AgentInvocation and ToolExecution; execution/tool eligibility constraints after common authz; Approval execution state; usage/budget state; project-scoped memory/RAG metadata and derived-index control; RunEvents/result envelopes; and agent artifact metadata. `ncn-authz` owns User/ProjectUser role/action authorization, PMS owns project-work effects, tool providers own their external effects, and object storage owns bytes behind agent metadata.

## Actors, Systems, and Permissions

| Actor/system | Goal | Allowed | Forbidden/constrained |
|---|---|---|---|
| Project admin | Configure coordinator/workers and project agent policy | Actions allowed by common authz plus agent-domain guards | Cannot disable/archive coordinator or alter active Run snapshot |
| Project member | Converse and request work | Create/read eligible Sessions/Messages/Runs; cancel own/allowed Run | Cannot grant tools, bypass approval, or read another project |
| Approver | Decide a pending risky action | Approve/reject if both authorized and routed | Approval cannot override a deny or changed payload |
| Coordinator | Plan/delegate/aggregate | Revise unstarted plan at safe boundaries; invoke configured workers/tools | Cannot bypass validation, policy, limits, or alter completed/running nodes |
| Worker | Complete a bounded task | Use delegated context, assigned memory/tools; return structured result | Cannot invoke workers, create Run, change plan/scope/policy |
| Temporal worker | Execute deterministic workflow/activities | Resume/retry/signal/cancel according to contract | Temporal is not business system of record |
| Domain/integration tool | Perform bounded operation | Validate owner scope/idempotency and return structured outcome | No implicit authority from model request |

## Feature Inventory

| Feature | Purpose | Status | Contract |
|---|---|---|---|
| Agent configuration | Configure coordinator/workers and status | Active/partial | [feature](features/agent-configuration.md) |
| Coordinated agent execution | Durable Session/Run/plan/tool/approval lifecycle | Draft/Planned | [feature](features/coordinated-agent-execution.md) |

## Requirements

| ID | Requirement | Scenario | Acceptance |
|---|---|---|---|
| AGT-REQ-001 | Maintain exactly one active coordinator per project and configurable workers with versioned settings/status. | SCN-001 | Coordinator remains active; stale update rejected |
| AGT-REQ-002 | Create an immutable configuration snapshot at Run start; later edits cannot affect that Run. | SCN-002 | Concurrent edit test shows stable snapshot |
| AGT-REQ-003 | Represent every execution as one durable Run with validated RunPlan/revisions, bounded nodes, cancellation, and structured result. | SCN-002 | Restart/cancel/limit/end-state tests |
| AGT-REQ-004 | Permit side effects only through explicit tool nodes after common actor/action authorization, agent execution validation, and any required Approval. | SCN-002/003 | Unauthorized/unapproved actions never execute |
| AGT-REQ-005 | Apply retry by operation class and idempotency; unknown external mutation outcomes require reconciliation. | SCN-003 | Duplicate/timeout tests prevent repeated side effect |
| AGT-REQ-006 | Build project-scoped context/memory, validate structured output, account usage/budgets, and preserve audit/result evidence. | SCN-002 | Scope/repair/budget/audit tests |

## Invariants

| ID | Invariant | Enforcement | Verification |
|---|---|---|---|
| AGT-INV-001 | Exactly one active coordinator exists per project; workers cannot be coordinators by escalation. | DB uniqueness/check and manager policy | Concurrent config tests |
| AGT-INV-002 | A Run uses one immutable snapshot and stable identifiers across Temporal replay. | Run-create transaction/workflow | Restart and config-edit tests |
| AGT-INV-003 | One Run maps to one root Temporal Workflow; external I/O occurs only in Activities. | Workflow design/registration | Determinism/replay tests |
| AGT-INV-004 | One mutating Run is active per Session; terminal statuses are COMPLETED, PARTIALLY_COMPLETED, FAILED, or CANCELLED. | Transaction/workflow state machine | Concurrent message/transition tests |
| AGT-INV-005 | Completed/running plan nodes, fixed tool arguments, executed effects, and approval decisions are immutable; only unstarted plan may revise at safe boundary. | Plan validator | Revision adversarial tests |
| AGT-INV-006 | `ncn-authz` determines persisted actor/project action; `ncn-agents` applies snapshot/tool/domain constraints; Approval only gates an otherwise permitted action and becomes invalid if material arguments change. | Common authz plus tool gateway | Policy/approval tests |
| AGT-INV-007 | A worker cannot invoke workers, start Runs, edit plan, expand permissions, disable Approval, or change Project. | Invocation context/tool gateway | Capability tests |
| AGT-INV-008 | Model/tool structured outputs are schema validated; at most two repair attempts precede controlled failure. | Model gateway/node executor | Invalid-output tests |
| AGT-INV-009 | Secrets are absent from read API, model context, logs, events, and Qdrant; primary data remains outside the vector index. | Secret/context/redaction boundaries | Security scans |

## State and Lifecycle

Agent workers transition active ↔ disabled → archived; coordinator remains active. Session accepts ordered Messages, one active mutating Run, and explicit close. Run transitions among queued/active, waiting-for-input/approval, cancelling, and one terminal state. Plan revisions are immutable; nodes progress through pending/running/waiting/succeeded/failed/skipped/cancelled/reconciliation. Approval is pending then approved/rejected/expired/invalidated, applied atomically once. Artifact and memory lifecycles are agent-owned modules in the current development contract.

## Dependencies and Constraints

Depends on common `ncn-authz` persisted actor/project action, PMS project references and permission-checked owner API/MCP tools, Temporal, PostgreSQL, Ollama/model gateway, Qdrant, MinIO/S3 and the current frontend. Agent execution constraints, memory and MCP/tool control remain modules inside `ncn-agents`; they cannot broaden common authz. Kafka is deferred until a confirmed asynchronous consumer exists. No nested workers, arbitrary plan loops, OAuth user MCP, exactly-once external effects, or universal plugin framework are in MVP.

## Security and Privacy

Every repository/Run/tool operation requires the common persisted actor/action and enforces project isolation plus agent-domain constraints. Model suggestions never authorize. Context is minimized to current request, bounded Session history/summary, completed-node results, selected facts, cited memory, and artifact metadata. Tool credentials use immutable encrypted secret versions and narrow decryption. Audit distinguishes progress from security decisions and redacts raw prompts/responses by default.

## Failure, Recovery, and Observability

Temporal durable waits handle input/approval/cancellation. Reads/model calls may retry transiently; mutating tools retry only under declared idempotency. Non-idempotent unknown outcomes wait for reconciliation. Structured output gets at most two repairs. Hard budget/time/node/tool limits produce controlled partial/failure result. PostgreSQL transaction protects Run creation, approval application, terminal transition, idempotency and audit. Observe Run/node state, queue latency, retry/repair, model/tool latency/error, approval age, usage/budget, cancellation, reconciliation backlog, and project-scope denials.

## Quality Requirements

| ID | Attribute | Requirement | Verification |
|---|---|---|---|
| AGT-NFR-001 | Durability | Run survives API/worker restart without duplicate side effect. | Temporal replay/restart test |
| AGT-NFR-002 | Security | Cross-project/tool escalation and secret leakage are blocked. | Adversarial integration/security tests |
| AGT-NFR-003 | Bounded cost | Configurable hard limits exist for duration, tokens, money, nodes, revisions, workers, parallelism, and tools. | Limit tests; exact values before production |
| AGT-NFR-004 | Explainability | Result/audit identify initiator, snapshot, agents, tools, policy/approval, effects, failures, and usage. | Audit reconstruction exercise |
| AGT-NFR-005 | Accessibility | Session/Run/approval UI communicates asynchronous states accessibly and supports cancellation/decision by keyboard. | UI audit |

## Assumptions

| Assumption | Rationale | Validation | Impact if false |
|---|---|---|---|
| One coordinator plus non-nested workers is sufficient for initial product. | Normative MVP contract | First vertical acceptance | Topology/model changes require contract version |
| Ollama satisfies first model/embedding needs behind adapters. | Approved shared infrastructure | Model capability/load evaluation | Provider adapter/fallback changes |
| Kafka is added only with a confirmed lifecycle consumer. | Agent MVP does not require it for happy path | A current asynchronous feature begins | Events remain persisted and exposed by API until then |

## Open Questions

| Question | Impact | Owner/trigger | Blocking |
|---|---|---|---|
| First user story, tools, worker, RAG corpus, and approval action | Defines executable acceptance | Product before execution implementation | Yes |
| Run message concurrency semantics | Queue/join/new Run UX and locking | Product/agents | Yes |
| Exact model IDs, context, timeout/fallback, credentials, and budget | Runtime safety/cost | Model/platform owner | Yes |
| Exact tables/API/errors/retention and `pms_agents` migration | Data/API compatibility | Agents/data owner | Yes for separation |
| Production SLO/RPO/RTO and limits | Operations acceptance | Platform | Yes for production |

## Service Acceptance

Configuration acceptance covers one coordinator, worker CRUD/status, permissions, archive/read-only, optimistic version, and migration ownership. Execution acceptance requires a full user Message → immutable Run snapshot → coordinator plan → worker/tool → optional Approval → structured result path; restart durability; deny/cross-project/secret tests; cancellation; limit enforcement; idempotent retry and unknown-outcome reconciliation; project-scoped memory citations; usage/audit reconstruction; and accessible Session/Run/Approval UI.

## Traceability

Use [scenarios](scenarios.md), [features](features/README.md), [technical design](design/technical.md), [UI/UX](design/ui-ux.md), [API](interfaces/api.md), [events](interfaces/events.md), [models](data/models.md), [tables](data/tables.md), and [decisions](decisions.md).
