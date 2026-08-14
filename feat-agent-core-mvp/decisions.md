# Decisions

## Decision Inventory

| ID | Decision | Status | Affected contracts |
|---|---|---|---|
| DEC-001 | Start with direct sessionless Runs | Accepted by explicit feature request, 2026-08-12 | REQ-002; SCN-002/006; API-003–008; DATA-003 |
| DEC-002 | Keep one active Project coordinator with immutable versions | Accepted from v2 architecture, narrowed for this feature | REQ-001/003; SCN-001; API-001/002; DATA-001/002 |
| DEC-003 | Limit MCP to one allowlisted read-only system tool | Proposed | REQ-005/006/009/010; SCN-003/004; API-009 |
| DEC-004 | Orchestrate a stepwise agent loop in one root Temporal Workflow and project state to PostgreSQL | Accepted from v2 architecture; step protocol proposed | REQ-004/005/007–009; API-008/010; DATA-003–008 |
| DEC-005 | Reconcile PostgreSQL commands to Temporal without Kafka | Proposed | REQ-002/004/008; API-003/007/008; DATA-007–009 |
| DEC-006 | Preserve bounded-service ownership and make no frontend change | Accepted from repository guide and user scope | All requirements; UI/UX applicability; SLICE-001–004 |
| DEC-007 | Use the Agents SDK only inside one-turn model Activities, with no SDK Session or direct MCP transport | Proposed | REQ-005/006/009; API-008/010; DATA-005/006 |

## DEC-001: Start with direct sessionless Runs

### Status

Accepted by the user's explicit request on 2026-08-12. Revisit only through an explicit feature-scope revision.

### Context

The broad v2 architecture defines Session/Message plus one active mutating Run per Session. The requested first feature excludes complex Session behavior and asks for only the core agent, Temporal, and MCP.

### Decision

API-003 starts a Run directly from one text objective. A Run has no `session_id`, `message_id`, history, follow-up queue, wait-for-input state, summary, or conversation lifecycle. Multiple direct Runs have only Project-level resource limits, not Session concurrency semantics.

### Drivers

- Deliver the smallest vertical core.
- Avoid premature message ordering, follow-up, summary, and Session deletion decisions.
- Preserve Run as the durable seam a later Session layer can invoke.

### Alternatives

- Implement a minimal Session wrapper: rejected because even a thin wrapper creates lifecycle/concurrency/API obligations outside the request.
- Execute synchronously without Run: rejected because it prevents durable asynchronous execution and later composition.

### Consequences

- Acceptance is simpler and can focus on durability/MCP.
- There is no conversational continuity or new-message handling.
- Later Sessions must reference/create the same Run contract internally and add their own compatibility/migration plan.
- This slice does not satisfy the full v2 product MVP alone.

### Reversal Conditions

A separately approved Session/Message feature with explicit concurrency, input, history, closure, deletion, and UX semantics.

### Affected Contracts

REQ-002/008; SCN-002/005/006; API-003–008; DATA-003/004/007; SLICE-002/004.

## DEC-002: Keep one active Project coordinator with immutable versions

### Status

Accepted from the v2 component/agent invariants and existing frontend coordinator concept; narrowed to one Agent kind.

### Context

Execution needs stable instructions/model/tools, while configuration may change concurrently. Workers and coordinator CRUD breadth are not needed to prove the base agent.

### Decision

Each Project may have one stable coordinator Agent, always `active`, pointing to one immutable AgentVersion. A full replace creates a version and advances the pointer with optimistic concurrency. Run creation embeds/references the exact effective version/snapshot.

### Drivers

- Reproducible execution and audit.
- Compatibility with the v2 snapshot invariant.
- Narrow topology without worker CRUD/archive complexity.

### Alternatives

- Mutable coordinator row only: rejected because active Runs would change underneath execution or require unreliable reconstruction.
- Multiple arbitrary agents: deferred to the worker/delegation feature.
- Copy configuration only into Run and keep no versions: rejected because configuration history and API concurrency would be weaker.

### Consequences

- Extra version storage and a pointer transaction are required.
- Old versions cannot be physically deleted while referenced.
- Existing frontend Agent fields need an explicit later adapter; no silent one-to-one compatibility is claimed.

### Reversal Conditions

Only a new architecture contract that changes reproducibility/version semantics. Adding workers does not reverse this decision.

### Affected Contracts

REQ-001/003/010; INV-001/002; SCN-001; API-001–003; DATA-001–003; SLICE-001.

## DEC-003: Limit MCP to one allowlisted read-only system tool

### Status

Proposed. The read-only boundary is fixed for this feature; the exact nominated tool remains replaceable until the MCP owner confirms `get_project` before SLICE-003.

### Context

MCP must be proved, but mutating tools immediately require Approval, external idempotency, unknown-effect reconciliation, and richer user recovery. User MCP endpoints add SSRF and credential lifecycle concerns.

### Decision

The first integration is a deployment-provisioned system MCP over Streamable HTTP. The acceptance capability is canonical `{server_name}__get_project`, classified `read_only`. Discovery/schema hashing, coordinator allowlisting, Project/policy/schema/limit validation, workload auth, and sequential invocation are mandatory. Unknown/mutating/user MCP tools are denied.

### Drivers

- Demonstrate the real domain boundary without side-effect risk.
- Keep retry safe and remove Approval from this slice.
- Exercise discovery, schema evolution, workload identity, Project isolation, and tool result handling.

### Alternatives

- No MCP, model-only answer: rejected because MCP is explicitly requested.
- Mutating `add_comment` or similar: rejected until Approval/idempotency/reconciliation has its own feature contract.
- Public/user MCP: deferred due to secret and SSRF scope.
- Direct PMS repository access: rejected by domain ownership rules.

### Consequences

- The core can answer only questions served by its objective and the one Project read.
- MCP read retries are safe, but local event/tool records still require stable logical IDs.
- An MCP schema change blocks new use until reviewed; active snapshots remain unchanged.

### Reversal Conditions

An approved mutating-tools/Approval feature or an MCP owner proving a different read-only acceptance tool is more available/relevant.

### Affected Contracts

REQ-005/006/009/010; INV-005/006/008; SCN-003/004; API-008–010; DATA-002/003/005; SLICE-003.

## DEC-004: Orchestrate a stepwise agent loop in one root Temporal Workflow and project state to PostgreSQL

### Status

Accepted architecture: one root Workflow and PostgreSQL-first state. Proposed implementation detail: one-turn model and individual MCP Activities coordinated by the Workflow.

### Context

The system must survive restart and make retries/cancellation explainable. A whole agent loop inside one opaque Activity would cause a retry to repeat prior reads/model work and hide durable step boundaries. Temporal history alone cannot serve product APIs/audit.

### Decision

One Run maps to Workflow `run:{run_id}`. The deterministic Workflow holds counters and schedules separate persistence, one-turn model, policy preparation, and MCP read Activities. It executes tool calls sequentially and finalizes after a schema-valid result. PostgreSQL records every product-visible transition/result with stable operation/event keys.

### Drivers

- Durable restart/replay and bounded cancellation.
- Operation-class retry policies.
- Explainable ordered progress and single terminal transition.
- Provider/SDK and MCP transport replaceability.

### Alternatives

- One retryable `run_agent` Activity: rejected due to coarse replay/retry and duplicate work.
- Workflow performs network/database I/O: rejected because it breaks deterministic replay.
- Temporal-only state: rejected because API/audit/analytics require PostgreSQL.
- Session/Invocation child Workflow topology: deferred because there is one agent and no Session/worker.

### Consequences

- A normalized model action protocol and explicit Activity result schemas are required.
- The database/Temporal boundary needs reconciliation and idempotency.
- Workflow changes require Temporal replay compatibility/versioning discipline.
- Additional Activity round trips are accepted for clearer durability.

### Reversal Conditions

Measured latency/cost proves the stepwise boundary unsuitable and an alternative can demonstrate equivalent replay, cancellation, idempotency, and observability guarantees.

### Affected Contracts

REQ-004/005/007–009; INV-003/004/007/008; SCN-002–006; API-008/010; DATA-003–008; SLICE-002/004.

## DEC-005: Reconcile PostgreSQL commands to Temporal without Kafka

### Status

Proposed for this feature, consistent with the repository rule that Kafka is not required until an asynchronous shared consumer exists.

### Context

Run acceptance and cancellation must commit product state before calling Temporal, but PostgreSQL and Temporal have no shared transaction. Introducing Kafka or direct dual-write would increase infrastructure without changing the single consumer.

### Decision

Write RunDispatch START/CANCEL commands in the same PostgreSQL transaction as their product command. An in-process/background dispatcher claims committed commands and invokes Temporal using stable Workflow/command identity. A reconciler retries pending/stale delivery and treats matching already-started/already-cancelled responses as success.

### Drivers

- Atomic local acceptance.
- Recovery from crash between commit and Temporal call.
- Smallest approved infrastructure path.
- Future replaceability through a dispatch port.

### Alternatives

- Direct call after commit with no durable command: rejected because crash can strand Runs.
- Temporal call before commit: rejected because Workflow can start for rolled-back product state.
- Kafka/outbox publisher: deferred until another durable consumer/integration requires it.
- Distributed transaction: unavailable and unnecessary.

### Consequences

- Delivery is at-least-once and requires stable IDs, leases, metrics, and a reconciliation runbook.
- `QUEUED`/`CANCELLING` may persist temporarily during dependency outage while read APIs remain accurate.
- Dispatcher health is part of execution readiness.

### Reversal Conditions

A shared event/automation consumer is approved and Kafka publication becomes an architectural requirement; migrate behind the same command/dispatch semantics.

### Affected Contracts

REQ-002/004/008/009; SCN-002/005/006; API-003/007/008; DATA-003/004/007–009; SLICE-002/004.

## DEC-006: Preserve bounded-service ownership and make no frontend change

### Status

Accepted from root repository instructions and the requested core-only boundary.

### Context

The current physical backend is `ncn-pms`, while root architecture assigns agent execution to `ncn-agents`. The frontend already displays configuration-like Agent data, which could tempt implementation to reuse PMS tables/routes or expand into a Run/chat UI.

### Decision

Implement a logical `ncn-agents` owner with its own manager/repository/schema/API boundaries, even if temporarily deployed in the same Python image/process. Reach Project/PMS through owner APIs/MCP and authorization through `ncn-authz`. Make no `frontend/**` change in this feature.

### Drivers

- Preserve domain ownership and future service separation.
- Avoid presenting mock/configuration fields as execution truth.
- Keep delivery focused on the durable core.

### Alternatives

- Add Agent Run tables to PMS ownership: rejected as a bounded-context violation.
- Create a new microservice repository immediately: not required; physical topology is open.
- Modify existing Agent settings and add Run UI: deferred to explicit compatibility/UI work.

### Consequences

- Implementation must make ownership visible in packages/schema/registration and avoid direct PMS imports for business state.
- Portal/frontend integration is not part of acceptance.
- The physical deployment decision must be reviewed during SLICE-001.

### Reversal Conditions

An explicit architecture decision changes service ownership or the user requests a frontend feature.

### Affected Contracts

All requirements; technical component boundaries; UI/UX applicability; DATA-001–010; SLICE-001–004.

## DEC-007: Use the Agents SDK only inside one-turn model Activities

### Status

Proposed, based on the v1.3 module design's SDK preference while preserving stronger v2 Temporal/replay boundaries.

### Context

The source design favors OpenAI Agents SDK primitives but forbids SDK Session storage and native handoff. Giving an SDK Runner direct MCP network access across an entire loop would make MCP retry/cancellation/persistence opaque to the root Workflow.

### Decision

The model Activity constructs the configured SDK `Agent` and runs one bounded turn through `Runner`/`RunConfig` with strict `CoreAgentActionV1` output. It exposes tool schemas as instructions/action schema but does not give the Runner an MCP transport or credential. The Workflow executes requested tools through separate policy/MCP Activities and supplies validated results to the next one-turn invocation. SDK Session storage, native handoff, provider tracing export, and persisted SDK RunState are not used.

### Drivers

- Retain the repository-selected agent abstraction.
- Keep external model/MCP operations at distinct durable boundaries.
- Keep the model provider adapter replaceable and structured output validated.
- Avoid Session semantics and opaque agent-loop retry.

### Alternatives

- Do not use the Agents SDK: viable fallback if the exact dependency cannot support the strict one-turn adapter, but diverges from detailed source design.
- Give SDK direct `MCPServerStreamableHttp` and run the full loop in one Activity: rejected for coarse durability and credential/tool-policy control.
- Persist SDK RunState: deferred until Approval/input interruption creates a need.

### Consequences

- The adapter must prove that one-turn execution does not secretly invoke network tools and reliably yields API-010.
- Some SDK convenience for native tool loops is intentionally unused.
- Exact SDK version and API surface must come from the implementation dependency review, not be invented in this plan.

### Reversal Conditions

SDK capability tests fail, its one-turn semantics cannot be isolated, or a future approved architecture introduces durable SDK-native tool execution with equivalent guarantees.

### Affected Contracts

REQ-005/006/009; SCN-002–005; API-008/010; DATA-005/006/008; SLICE-002/003.

## Open Decision Queue

| Question | Impact | Owner or evidence needed | Resolution deadline or trigger |
|---|---|---|---|
| Exact Ollama-compatible model, endpoint capabilities, context/output limits, and credentials source | Real model integration and quality/limits | Platform/model owner plus capability probe | Before SLICE-002 environment acceptance |
| Confirm `get_project` or nominate an equivalent first read-only system tool and exact MCP schemas/context carrier | API-009 fixture and end-to-end acceptance | PMS/MCP owner and service contract | Before SLICE-003 begins |
| Physical packaging/deployment of logical `ncn-agents` | Paths, image/process lifecycle, schema registration | Architecture/backend owner using current repository constraints | During SLICE-001 design review |
| Production concurrency, retention, latency, backup/restore, and alert thresholds | Capacity/indexes/operations gate | Operations/SRE measurements and policy | Before enabling beyond test Projects |
