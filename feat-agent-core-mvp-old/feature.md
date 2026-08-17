# Feature: Agent Core MVP

## Executive Contract

The `ncn-agents` owner will provide one configurable, always-active coordinator per Project and a direct HTTP operation that starts a sessionless Run for a single text objective. One root Temporal Workflow durably executes a bounded model/tool loop, may call one allowlisted read-only system MCP tool, persists product-visible state in PostgreSQL, and returns a validated result envelope through polling APIs.

This feature establishes only the execution core. It does not provide a conversation, multi-agent orchestration, side effects, or a frontend Run experience.

## Evidence and Decision Status

| Topic | Status | Statement | Evidence or rationale |
|---|---|---|---|
| Feature boundary | **Confirmed** | Include the agent, Temporal flow, and MCP; exclude Sessions and complex behavior. | User request, 2026-08-12. |
| Runtime ownership | **Confirmed** | `ncn-agents` owns agent registration, execution, budgets, and Run lifecycle; `agent-core` is an internal runtime boundary. | Root `AGENTS.md`; v2 component contract in `contracts/agents/02-invariants/02-components-and-agent-model.md`. |
| Durable execution | **Confirmed** | One Run maps to one root Temporal Workflow; external I/O occurs in Activities; PostgreSQL remains product state authority. | v2 durable and data invariants. |
| MCP boundary | **Confirmed** | Agents reach domain capabilities through MCP and never through a domain service database. | Root `AGENTS.md`; v2 MCP invariant. |
| Current behavior | **Confirmed** | The repository has a frontend-only Agent configuration projection, while the current backend has no Agent Run, Temporal, MCP, or LLM runtime dependency/wiring. | `docs/features/agent-management.md`, `docs/data/agent-config.md`, `backend/spec.md`, `backend/pyproject.toml`, and inspected `backend/` tree. |
| First MCP capability | **Assumed** | Acceptance uses one deployment-provisioned system MCP exposing the read-only `get_project` tool over Streamable HTTP. | This is the smallest tool named by the v1.3 module design that demonstrates project-scoped MCP access without Approval. |
| Model provider | **Assumed** | A deployment-configured, OpenAI-compatible tool-calling model is available through the approved Ollama infrastructure and is addressed through a provider-neutral adapter. | Root infrastructure contract and v2 model abstraction; exact model is an environment choice. |
| Full v2 MVP relationship | **Confirmed** | This package is a precursor slice, not a claim that the broad v2 MVP is complete. | The v2 product boundary also requires Sessions, workers, Approval, memory, artifacts, and other deferred concerns. |

## Problem and Opportunity

**Confirmed current state:** users can configure Agent-shaped data in the frontend mock/HTTP abstraction, but the verified backend does not execute those agents. The broad agent contracts describe a complete multi-agent product whose Sessions, plans, workers, approval, RAG, artifacts, and automations create too many coupled decisions for a first implementation slice.

**Proposed behavior:** establish a narrow, recoverable core that proves the architecture's hardest base seams: immutable agent configuration, asynchronous Run creation, deterministic Temporal orchestration, provider-neutral model turns, schema-controlled MCP calls, PostgreSQL projections, cancellation, and operational visibility. Later conversational and multi-agent features must compose around this seam rather than replace it.

## Actors and Permissions

| Actor or system | Goal | Allowed actions | Forbidden or constrained actions |
|---|---|---|---|
| Project administrator | Configure the Project coordinator | Create the first coordinator version and replace it with a new immutable version | Cannot create workers, disable/archive the coordinator, grant tools outside the platform/project allowlist, or expose credentials |
| Project member with run permission | Execute and observe the core agent | Start a Run, read its state/events/result, and request cancellation within the same Project | Cannot supply instructions/model/tool permissions inline, access another Project, or mutate domain data through this feature |
| Project viewer without run permission | Inspect only where project policy permits | Read coordinator metadata or Run state if separately authorized | Cannot configure or start/cancel Runs |
| `ncn-agents` runtime | Execute the requested objective | Resolve immutable configuration, invoke the model, validate tool requests, call MCP, persist state, and enforce limits | Cannot bypass `ncn-authz`, Project scope, schemas, tool allowlists, or platform limits |
| Temporal | Maintain durable execution | Schedule Activities, retry allowed failures, deliver cancellation, and replay deterministic Workflow code | Is not product state authority and must not receive plaintext credentials |
| System MCP | Return Project data for an authorized read tool | Validate schema, trusted execution context, Project scope, and its own domain invariants | Cannot trust model-supplied Project identifiers or expand the caller's authority |

Exact permission identifiers are implementation configuration; their required semantics are `agent.configure`, `agent.run`, `agent.read_run`, and `agent.cancel_run`, evaluated by `ncn-authz` or its repository-approved adapter.

## Outcomes and Success Measures

| ID | Outcome | Measure | Target or evaluation method |
|---|---|---|---|
| OUT-001 | A Project has one executable core agent with reproducible configuration | Active Run continues with its original version after coordinator reconfiguration | Automated integration test compares snapshot/version and final result metadata |
| OUT-002 | A user obtains a useful result through a durable asynchronous Run | Direct objective progresses `QUEUED → RUNNING → COMPLETED` and returns a valid result envelope | End-to-end test with deterministic model and real/test Temporal |
| OUT-003 | The agent safely uses a domain capability through MCP | `get_project` is discovered, allowlisted, schema-validated, invoked, and represented in Run events | MCP contract test plus end-to-end scenario |
| OUT-004 | Execution survives ordinary process interruption | Restarting the API or Temporal worker does not lose the Run or duplicate its logical tool call | Failure-injection test using stable Workflow/tool-call identifiers |

## Scope

### In Scope

- One Project-scoped coordinator resource with immutable versions and exactly one active version.
- Coordinator fields needed for execution: display metadata, instructions, logical model identifier, bounded model parameters, canonical allowed tool names, and maximum steps.
- Sessionless Run creation from one non-empty text objective; no conversational history or follow-up input.
- Run status, ordered semantic events, validated result envelope, usage summary, and cancellation APIs.
- One root Temporal `RunWorkflow` per Run with deterministic Workflow code and model, PostgreSQL, authorization-dependent, and MCP I/O in Activities.
- A bounded single-agent loop that returns either a final structured result or one/more sequential tool requests within limits.
- One deployment-provisioned system MCP using Streamable HTTP, discovery/schema hashing, and the read-only `get_project` tool.
- Server-side tool allowlist, schema, Project scope, limit, and read-only-risk checks before every call.
- PostgreSQL as source of truth for agent versions, Run projections, events, tool execution metadata, usage, audit metadata, idempotency records, and dispatch reconciliation.
- Idempotent Run creation, safe read retries, controlled failure, API/worker restart recovery, and cancellation.
- Correlation IDs, redacted structured logs, Prometheus metrics, readiness checks, and separate progress versus audit records.

### Out of Scope

- Session, Message, message history, Session summary, incoming-message signals, waiting for user input, and SDK Session storage.
- Worker agents, delegation, handoffs, child agent workflows, parallel workers, coordinator/worker role routing, dynamic RunPlan/DAG, plan revisions, mapping, and workflow templates.
- Mutating MCP tools, side effects, Approval, ApprovalGrant, unknown-effect reconciliation, and user-configured MCP servers or credentials.
- Memory, RAG, Qdrant, embeddings, ProjectState, artifact extraction/storage, and MinIO.
- Automation, schedules, Kafka, Debezium, event consumers, webhooks, and notifications.
- Monetary quotas, price registry, fallback model routing, advanced budgeting, and billing ledger; hard per-Run limits remain in scope.
- Streaming token deltas, WebSockets/SSE, raw chain of thought, raw prompt/response retention, and a frontend execution screen.
- Worker CRUD, coordinator archive/disable, broad Agent management compatibility work, and model/MCP administration UI.

### Deferred

- A Session adapter that creates Runs through the same internal start command and links Messages without changing Run durability.
- Worker execution and RunPlan semantics built on the same Activity and snapshot contracts.
- Risk-classified mutating tools plus Approval and reconciliation.
- User MCP authentication, memory/RAG, artifacts, automation, Kafka publication, richer usage accounting, and production capacity tuning.
- Adapting the existing frontend Agent settings resource to the backend coordinator contract and adding a Run user experience.

## Requirements

| ID | Requirement | Rationale | Scenario | Acceptance |
|---|---|---|---|---|
| REQ-001 | The system shall let an authorized Project administrator create or replace the single coordinator configuration, producing a new immutable version and leaving prior versions readable by existing Runs. | The agent must exist and be reproducible before execution. | [SCN-001](scenarios.md#scn-001-configure-the-core-agent) | AC-001 |
| REQ-002 | The system shall accept one non-empty text objective for the active coordinator and return a Run identifier/status without waiting for model completion; no Session or Message identifier is required or created. | Delivers the requested sessionless core boundary. | [SCN-002](scenarios.md#scn-002-complete-a-direct-run-without-a-tool) | AC-002 |
| REQ-003 | Run creation shall atomically persist an immutable snapshot of the coordinator version, model settings, tool schemas/allowlist, Project constraints, authorization context, and limits used by that Run. | Configuration changes must not alter active execution. | [SCN-001](scenarios.md#scn-001-configure-the-core-agent), [SCN-002](scenarios.md#scn-002-complete-a-direct-run-without-a-tool) | AC-003 |
| REQ-004 | Each Run shall execute as exactly one root Temporal Workflow with deterministic code; model, database, MCP, and other external I/O shall execute through Activities with stable replay-safe identifiers. | Provides durable, restart-safe execution. | [SCN-005](scenarios.md#scn-005-recover-from-transient-failure-and-worker-restart) | AC-004 |
| REQ-005 | The Workflow shall run a bounded single-agent loop that validates each model turn, processes tool requests sequentially, and terminates with a valid Run result or a controlled error when limits/validation are exhausted. | Proves the agent itself without adding orchestration topology. | [SCN-002](scenarios.md#scn-002-complete-a-direct-run-without-a-tool), [SCN-003](scenarios.md#scn-003-complete-a-run-with-a-read-only-mcp-tool) | AC-005 |
| REQ-006 | Before an MCP call, the runtime shall verify discovered schema hash, canonical tool name, Project scope, coordinator allowlist, authorization/risk policy, arguments, and Run limits; only the read-only `get_project` acceptance tool may be invoked. | MCP is a security boundary, not a model capability grant. | [SCN-003](scenarios.md#scn-003-complete-a-run-with-a-read-only-mcp-tool), [SCN-004](scenarios.md#scn-004-deny-an-invalid-or-unassigned-tool-call) | AC-006 |
| REQ-007 | The system shall persist Run state, ordered semantic events, tool execution metadata, usage, terminal result/error, and audit metadata so an authorized caller can poll and explain the outcome without reading Temporal history. | PostgreSQL must support product APIs and audit. | [SCN-002](scenarios.md#scn-002-complete-a-direct-run-without-a-tool), [SCN-003](scenarios.md#scn-003-complete-a-run-with-a-read-only-mcp-tool) | AC-007 |
| REQ-008 | An authorized caller shall retrieve Run state/events and request cancellation; cancellation and API/worker restart shall lead to a controlled terminal state without duplicate logical calls. | Users and operators need recovery control. | [SCN-005](scenarios.md#scn-005-recover-from-transient-failure-and-worker-restart), [SCN-006](scenarios.md#scn-006-cancel-an-active-run) | AC-008 |
| REQ-009 | Operation-class retry/timeout policies, input/output/step/tool/duration limits, and idempotency controls shall prevent infinite execution and unsafe duplicate work. | Bounds cost and operational failure. | [SCN-004](scenarios.md#scn-004-deny-an-invalid-or-unassigned-tool-call), [SCN-005](scenarios.md#scn-005-recover-from-transient-failure-and-worker-restart) | AC-009 |
| REQ-010 | Every operation shall enforce Project isolation and actor authorization, derive trusted execution context server-side, and keep credentials/hidden reasoning out of model input, API responses, Temporal inputs, events, and logs. | Preserves the repository trust model. | [SCN-001](scenarios.md#scn-001-configure-the-core-agent), [SCN-004](scenarios.md#scn-004-deny-an-invalid-or-unassigned-tool-call) | AC-010 |

## Invariants

| ID | Invariant | Enforcement boundary | Verification |
|---|---|---|---|
| INV-001 | A Project has at most one coordinator and exactly one current immutable version once configured; it cannot be disabled or archived in this feature. | `ncn-agents` manager/repository constraints | Unique/partial index tests and API conflict tests |
| INV-002 | A Run has no Session or Message dependency and keeps the snapshot selected at creation for its full lifetime. | Run manager, database constraints, Workflow input | Reconfiguration-during-Run integration test |
| INV-003 | One Run ID maps to one Temporal Workflow ID `run:{run_id}` and one terminal transition. | Dispatcher, Temporal start policy, conditional database update | Duplicate-start and terminal-race tests |
| INV-004 | Workflow code is deterministic; every network/database operation is an Activity. | Temporal module boundary | Replay test and workflow-code review |
| INV-005 | The model cannot expand Project scope, tool permissions, risk class, schema, credentials, or hard limits. | Policy/validation layer before tool execution | Adversarial model-output tests |
| INV-006 | Only read-only MCP tools are executable; any mutating/unknown-risk tool is denied before outbound I/O. | MCP catalog and gateway | MCP mock assertion that no call was received |
| INV-007 | PostgreSQL is authoritative for product-visible state; Temporal history is insufficient by itself for API, audit, or analytics. | Repositories and terminal persistence Activity | State-rebuild/read API tests independent of Temporal visibility |
| INV-008 | Idempotency/replay identifiers are stable and generated before retries; secrets never enter persisted execution payloads. | API manager, Workflow input builder, secret/token provider | Duplicate-command and redaction tests |

## Quality Requirements

| ID | Requirement | Verification |
|---|---|---|
| NFR-001 | A committed Run shall survive API/worker restart and ordinary transient dependency failure without losing state, changing its snapshot, or duplicating a logical tool/terminal effect. | Temporal replay and failure-injection tests for SCN-005 |
| NFR-002 | All Project, permission, MCP trust, and secret boundaries shall fail closed; persisted/API/log/Temporal content shall pass redaction tests. | Cross-Project, forged-context, credential canary, and audit-separation tests |
| NFR-003 | Under the development profile of 20 concurrent Runs, API-003–005 shall meet p95 ≤500 ms excluding model/MCP execution, while hard bounds cap input, output, turns, tools, and duration. | Integration load probe and boundary tests before rollout |
| NFR-004 | Operators shall detect dispatch backlog, dependency/retry failure, stuck cancellation, terminal-state mismatch, and readiness degradation without inspecting sensitive payloads. | Metrics/dashboard assertions and runbook drills in SLICE-004 |
| NFR-005 | HTTP/snapshot/event/Workflow schemas shall be versioned, and deployment/rollback shall preserve reads and Temporal replay for existing Runs. | Compatibility tests across previous/current worker and API builds |

## State and Lifecycle

The public Run states are `CREATED`, `QUEUED`, `RUNNING`, `RETRYING`, `CANCELLING`, `COMPLETED`, `PARTIALLY_COMPLETED`, `FAILED`, and `CANCELLED`.

Allowed progress is:

```text
CREATED → QUEUED → RUNNING ↔ RETRYING
                         ├→ CANCELLING → CANCELLED
                         ├→ COMPLETED
                         ├→ PARTIALLY_COMPLETED
                         └→ FAILED
```

`CREATED` exists only inside the creation transaction; clients normally first observe `QUEUED`. Terminal states never transition. `PARTIALLY_COMPLETED` is reserved for a valid partial result with completed read/tool work and an explicit warning; it never implies a domain side effect. There are no waiting-for-input or waiting-for-approval states. See [the data model](data/model.md#state-transitions).

## Dependencies and Constraints

- `ncn-agents` is the logical owner. It may share deployment infrastructure during the MVP, but must not place its state under `ncn-pms` ownership.
- `ncn-authz` supplies Project membership/permission decisions. `ncn-pms` remains the Project-domain owner and is reached only through an owner API/MCP boundary.
- Approved infrastructure: PostgreSQL, Temporal, Ollama-compatible model endpoint, Keycloak/OAuth2 Proxy for system MCP workload authentication, Prometheus/Loki/Grafana.
- Kafka, Qdrant, MinIO, Redis coordination, Novu, and new infrastructure are not required for this feature.
- The current backend's FastAPI/SQLAlchemy/Pydantic/service-hub patterns are **Present** and should be reused where compatible. Temporal, MCP, and model runtime dependencies are **Planned**.
- API operations use globally unique backend identifiers, UTC timestamps, request/correlation identifiers, and versioned resource semantics.

## Security and Privacy

- Browser/user identity arrives through the platform authentication edge; `ncn-agents` requests the required Project-scoped authorization decision from `ncn-authz`.
- The server derives `project_id`, actor, `run_id`, `agent_id`, tool-call ID, and correlation identifiers. Model-supplied identity or Project fields are ignored/rejected.
- The coordinator allowlist may only narrow the platform/project tool catalog. A model request is never itself authorization.
- System MCP uses an audience-specific, short-lived workload token acquired immediately before the call and held only in memory. Credentials and auth headers are absent from Workflow inputs/history, PostgreSQL execution payloads, model context, logs, traces, and responses.
- Tool arguments/results are schema-validated, size-limited, and redacted according to the tool contract. Hidden reasoning and raw prompt/response bodies are not retained.
- Cross-Project lookup returns the same not-found/denied behavior chosen by the shared security convention and emits an audit record without exposing resource existence.

## Failure, Recovery, and Observability

- Run start and configuration writes use idempotency keys; conflicting payload reuse fails deterministically.
- A PostgreSQL dispatch record plus idempotent `run:{run_id}` Workflow start reconciles the database/Temporal boundary without Kafka.
- Model calls use up to three transient attempts with bounded backoff and a 200-second Activity `start_to_close` timeout. Invalid structured output receives no more than two repair turns before controlled failure.
- Read-only MCP calls use up to three transient attempts with bounded backoff and a 75-second Activity timeout. Validation/permission failures are not Activity-retried.
- Stable logical tool-call IDs plus unique constraints deduplicate persisted events/executions during Activity retry and Workflow replay.
- API or worker restart leaves the Run queryable from PostgreSQL; Temporal resumes work. Stale `QUEUED`, `RUNNING`, and `CANCELLING` projections are reconciled.
- Cancellation stops scheduling new turns/calls, requests cancellation of in-flight Activities, and persists `CANCELLED` when acknowledged. A terminal Run is not reopened.
- Structured logs and metrics carry `trace_id`, `correlation_id`, and `run_id` but omit payloads/secrets. Required signals include starts, completions by status, duration, active Runs, retries, model/MCP outcomes, dispatch lag, and cancellation latency.
- Progress RunEvents and security/administrative AuditEvents are distinct records.

## Acceptance Criteria

- **AC-001 / REQ-001 / SCN-001:** an authorized admin creates the coordinator, revises it with optimistic concurrency, and an already active Run retains the prior immutable version.
- **AC-002 / REQ-002 / SCN-002:** a valid direct objective returns `202` with a Run ID and no Session/Message ID; polling reaches a terminal result.
- **AC-003 / REQ-003 / SCN-001–002:** the persisted Run snapshot identifies the exact agent version, model settings, tool schema hashes, permissions, Project constraints, and hard limits used.
- **AC-004 / REQ-004 / SCN-005:** a Temporal replay/worker-restart test completes the same Run under Workflow ID `run:{run_id}` with no second logical execution.
- **AC-005 / REQ-005 / SCN-002–003:** deterministic model fixtures prove both a direct final answer and a sequential tool-call/final-answer loop, with invalid final output failing after bounded repair.
- **AC-006 / REQ-006 / SCN-003–004:** `get_project` succeeds only when discovered, schema-matched, allowlisted, and Project-scoped; unassigned/mutating/invalid calls produce no outbound request.
- **AC-007 / REQ-007 / SCN-002–003:** Run state, ordered events, tool metadata, usage, result/error, and audit data are queryable from PostgreSQL without inspecting Temporal history.
- **AC-008 / REQ-008 / SCN-005–006:** restart and cancellation tests reach one controlled terminal state and do not duplicate logical model/tool records.
- **AC-009 / REQ-009 / SCN-004–005:** configured step/tool/duration/payload limits and retry exhaustion produce stable errors and prevent unbounded execution.
- **AC-010 / REQ-010 / SCN-001/004:** cross-Project, insufficient-permission, forged-context, and credential/redaction tests fail closed and emit safe audit/metric evidence.

## Assumptions

| Assumption | Rationale | Validation method | Impact if false |
|---|---|---|---|
| One internal MCP exposes `get_project` with stable input/output schemas and workload authentication. | Smallest representative read integration from the source contract. | MCP owner contract review and mock/real integration probe before SLICE-003. | Replace the named tool and update REQ-006, SCN-003, API-009, snapshots, and acceptance tests. |
| A tool-capable OpenAI-compatible model is available via Ollama. | Matches approved infrastructure and preserves provider neutrality. | Capability probe for structured output and tool calling before SLICE-002 integration. | Select another approved compatible endpoint or revise the model adapter decision. |
| Initial defaults are 8 model turns, 10 tool calls, a 10-minute Run, 32 KiB input, 256 KiB final result, and 1 MiB MCP response. | Conservative development bounds where production measurements do not yet exist. | Load/failure tests and operator review before production enablement. | Tune configuration without changing API semantics; update NFR evidence. |
| Physical co-location with current Python deployment is acceptable only if logical ownership and persistence boundaries remain explicit. | Avoids forcing service decomposition before the first vertical slice. | Architecture review during SLICE-001. | Create a separate `ncn-agents` deployable before implementation proceeds. |

## Open Questions

| Question | Impact | Owner or resolution trigger | Blocking |
|---|---|---|---|
| Which exact Ollama model/deployment and context/output limits satisfy tool calling and structured result validation? | Integration configuration and quality baseline. | Model/platform owner before SLICE-002 real-provider test. | No for code; yes for environment acceptance |
| Is `get_project` the first real system MCP tool, or will the PMS owner nominate another read-only tool? | Tool schema, test fixture, and acceptance wording. | PMS/MCP owner before SLICE-003 starts. | No; mock contract can proceed |
| What are production concurrent-Run, retention, p95 latency, backup, and restore targets? | Capacity, indexes, alerts, and rollout gate. | Operations owner before production enablement. | No for implementation; yes for broad rollout |

## Traceability

Use [user scenarios](scenarios.md), [technical design](design/technical.md), [UI/UX design](design/ui-ux.md), [API contract](interfaces/api.md), [data model](data/model.md), [decisions](decisions.md), and [delivery plan](delivery/plan.md) to trace each requirement into implementation and validation.
