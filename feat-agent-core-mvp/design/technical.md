# Technical Design

## Context and Current State

**Present and verified:**

- The repository root assigns agent registration/execution/Run lifecycle to the `ncn-agents` bounded service and Project/domain state to their owner services.
- `backend/` is currently an `ncn-pms` FastAPI/SQLAlchemy application with a shared service hub, PostgreSQL transaction helpers, request IDs, Prometheus instrumentation, and layered router/manager/repository/model conventions.
- `backend/spec.md` and `backend/pyproject.toml` explicitly show no wired Temporal, MCP, or LLM runtime dependency.
- The frontend has Project Agent list/settings behavior and an HTTP port, but its documented Agent fields are configuration values only; there is no implemented execution surface.
- The agent v2 contract mandates PostgreSQL-first product state, one root Temporal Workflow per Run, Activity-based external I/O, immutable configuration snapshots, deterministic permissions, MCP as the domain boundary, bounded execution, structured outputs, cancellation, and audit.

**Conflict resolved by this package:** the broad v2 MVP includes Sessions, workers, Approval, memory, and other subsystems. The user's narrower first slice excludes them. The direct Run seam is designed so a later Session layer calls it rather than replacing its persistence or Workflow identity.

## Proposed Design

Implement a logical `ncn-agents` module/service containing an internal `agent-core` runtime. Its synchronous boundary validates coordinator configuration and atomically accepts direct Run commands. A PostgreSQL-backed dispatcher starts a deterministic root Temporal Workflow after commit. The Workflow owns a small stepwise agent state machine; model and MCP I/O are separate Activities. Product-visible state/events/results are written to PostgreSQL and exposed through polling APIs.

```text
Caller
  │ configure / start / poll / cancel
  ▼
ncn-agents HTTP + authz ───────► PostgreSQL (source of product truth)
  │                                   │ queued dispatch / snapshots / events
  │ idempotent start/signal           ▼
  └────────────────────────────► Temporal RunWorkflow
                                      │ invoke_model Activity
                                      │ authorize/prepare tool Activity
                                      │ execute_mcp_tool Activity
                                      ▼
                         Ollama-compatible model + system MCP
```

The model returns a strict action union: a final `RunResultEnvelope` or a canonical tool request. The Workflow executes tool requests sequentially and stops at configured turn/tool/duration bounds. No SDK-managed Session, nested agent, dynamic DAG, or hidden tool execution exists.

## Components and Responsibilities

| Component or boundary | Status | Responsibility | Inputs and outputs | Owner |
|---|---|---|---|---|
| Existing FastAPI application/service hub patterns | **Present** | HTTP lifecycle, dependency injection, database sessions, request IDs, Prometheus integration | Requests, dependencies, health/metrics | Current backend platform |
| `ncn-agents` HTTP boundary | **Planned** | API-001–007 validation, idempotency, authz, DTO mapping, response/error semantics | HTTP requests/responses | `ncn-agents` |
| Agent configuration manager/repository | **Planned** | Enforce one coordinator, immutable versions, optimistic concurrency, tool/model validation | DATA-001, DATA-002 | `ncn-agents` |
| Run manager/repositories | **Planned** | Atomic Run acceptance, snapshots, events, commands, terminal transitions, query projection | DATA-003–010 | `ncn-agents` |
| Run dispatcher/reconciler | **Planned** | Bridge committed Run/control commands to Temporal idempotently and repair stale queued/cancelling projections | Run ID, Workflow ID, command state | `ncn-agents` |
| `RunWorkflow` | **Planned** | Deterministic bounded state machine, stable turn/tool IDs, retry/cancellation coordination, finalization | API-008 input/result | `ncn-agents` Temporal worker |
| Model invocation Activity/adapter | **Planned** | Build bounded input, call provider-neutral model endpoint, normalize action/usage/errors, validate structured action | Agent snapshot + turn context → final/tool request | `ncn-agents` |
| Tool policy/preparation Activity | **Planned** | Verify schema hash, canonical name, Project, allowlist, risk class, arguments, limits, and trusted context | Model tool request + snapshot → prepared call/denial | `ncn-agents` |
| MCP catalog/gateway Activity | **Planned** | Discover API-009 tools, acquire workload token in memory, call read tool, validate/limit result | MCP list/call contracts | `ncn-agents`; MCP owns domain validation |
| `ncn-authz` adapter | **Planned** | Resolve Project-scoped configure/run/read/cancel authorization | Actor, Project, action/resource → allow/deny | `ncn-authz` authority |
| PostgreSQL | **Present infrastructure; planned schema** | Agent/Run product truth, idempotency, dispatch, events, usage, audit | DATA-001–010 | `ncn-agents` schema ownership |
| Temporal service/worker registration | **Planned** | Durable history, Activity scheduling, retry, cancellation, replay | API-008 | Platform + `ncn-agents` |
| Ollama-compatible model endpoint | **Confirmed infrastructure; planned integration** | Tool-capable model inference through a provider-neutral contract | Structured model request/action | Platform model owner |
| System Project MCP | **Planned integration** | Project-domain read through `get_project`, workload auth, schema and Project checks | API-009 | PMS/MCP owner |

`agent-core` is not a new bounded service alongside `ncn-agents`; it is the internal execution module named by the source contract. Physical co-location in the existing Python deployable is permitted for the first slice only if ownership, schema, imports, and owner-interface rules stay explicit.

## End-to-End Flows

### Coordinator configuration

1. API-001 authenticates the Project admin and calls `ncn-authz` for configure authority.
2. The manager validates full replacement input against platform model/tool catalogs and hard maxima.
3. One PostgreSQL transaction inserts the first Agent/AgentVersion or appends a new immutable AgentVersion, advances the stable Agent pointer/version, and writes idempotency/audit records.
4. The API returns the stable resource ID, immutable version ID, numeric version/ETag, and safe representation.

### Direct Run acceptance and dispatch

1. API-003 validates identity, Project run permission, objective bounds, active coordinator, model/tool readiness, and the idempotency key.
2. It builds the immutable snapshot from server-owned data. No caller-supplied permission/model/tool override is accepted.
3. One transaction writes `AgentRun(CREATED→QUEUED)`, snapshot, initial RunEvent, RunDispatch, IdempotencyRecord, and AuditEvent.
4. After commit, the dispatcher calls Temporal start with Workflow ID `run:{run_id}`. `WorkflowExecutionAlreadyStarted` for that ID is success.
5. If start fails transiently, API-003 still returns the committed Run; reconciliation retries until started or an operational terminal policy applies.

### Bounded agent loop

1. `RunWorkflow` input contains only stable IDs, the immutable non-secret execution snapshot, objective, and correlation metadata.
2. A persistence Activity conditionally marks `RUNNING` and appends `run.started`/`agent.started` using stable event keys.
3. `invoke_model` receives bounded objective, instructions, prior validated tool results, and exposed tool schemas. It returns exactly one validated action:
   - `final`: result envelope plus usage; or
   - `tool_calls`: an ordered non-empty list of canonical names and JSON arguments.
4. The Workflow processes calls sequentially. For each, a policy/preparation Activity returns either a prepared call or safe denial.
5. A prepared read uses `execute_mcp_tool`; validated output and normalized metadata are persisted and added to the next model turn.
6. A denial may be returned to the model once as a safe tool error; repetition or exhausted limits fails the Run.
7. A final result is schema/size validated, then one terminal Activity writes usage, result, event, dispatch completion, and terminal status conditionally.

### Polling and cancellation

1. API-004 reads the PostgreSQL Run projection; API-005 reads RunEvents after a monotonic sequence.
2. API-007 atomically writes an idempotent cancel command, moves an active Run to `CANCELLING`, and records audit/progress metadata.
3. The dispatcher preserves per-Run command order. If START was not delivered, it starts the same `run:{run_id}` first and then delivers cancellation; the Workflow's initial/next-boundary persistence Activity observes the durable `CANCELLING` state before any new model/tool Activity.
4. For an already-started Workflow, the dispatcher delivers Temporal cancellation/signal using `run:{run_id}`. The Workflow schedules no new model/tool work and cancels in-flight Activities where supported.
5. Terminal persistence writes `CANCELLED`. Reconciliation repeats delivery while state remains `CANCELLING`.

## State Ownership and Consistency

- PostgreSQL owns Agent identity/version, Run status/snapshot/result, semantic events, tool metadata, usage, idempotency outcomes, dispatch/control state, and audit metadata.
- Temporal owns durable control flow, timers/backoff, Activity attempts, cancellation propagation, and replay state. Temporal history is operational evidence, not an API read model.
- MCP owns domain data and validates Project/domain invariants. `ncn-agents` stores only bounded execution metadata/result content required for the Run; it never copies PMS business entities as an authoritative model.
- Agent update, Run acceptance, cancel command, and terminal finalization each have explicit single-database transaction boundaries documented in [the data model](../data/model.md#consistency-and-transactions).
- The database/Temporal boundary is deliberately at-least-once. Stable Workflow/operation/event keys and conditional writes make the product effect idempotent.
- Event sequence is unique and monotonic per Run; gaps are allowed. Consumers use `after_sequence`, not timestamps, for ordering.
- Active Run configuration is immutable. Catalog/config changes only affect future Run creation.

## Dependencies and Integration

| Dependency | Direction | Required behavior | Timeout/retry/failure |
|---|---|---|---|
| PostgreSQL | `ncn-agents` → database | Product truth and all local command transactions | 15-second operation timeout; bounded transient retry; readiness critical |
| Temporal | API/worker → Temporal | Workflow start, Activity scheduling, replay, cancellation | Start/signal reconciled idempotently; readiness critical for new Runs |
| `ncn-authz` | `ncn-agents` → owner API/adapter | Project membership and action decision | Fail closed; do not start/configure/cancel on uncertainty |
| Model endpoint | model Activity → Ollama-compatible endpoint | Structured final/tool action and usage | 10-second connect, 180-second read, 200-second Activity; max three transient attempts |
| Keycloak/OAuth2 Proxy | MCP Activity → auth edge | Audience-specific workload token and MCP authentication | In-memory short TTL; refreshable auth retry only; no redirect login |
| System MCP | MCP Activity → Streamable HTTP | `list_tools` and read-only `get_project` | 10-second connect, 60-second read, 75-second Activity; max three transient read attempts |
| Prometheus/Loki/Grafana | service → platform telemetry | Metrics, structured logs, dashboards/alerts | Telemetry failure must not corrupt Run state; local backpressure/drop policy is observable |

Kafka, Debezium, Redis locks, Qdrant, MinIO, and Novu are not on the execution path. No direct PostgreSQL+Kafka dual-write is introduced.

## Security Boundaries

- The ingress/authentication edge supplies verified actor identity; `ncn-authz` is authoritative for Project-scoped actions. Role checks in UI or model output are never authoritative.
- `ncn-agents` is policy decision/enforcement point for agent/tool scope. MCP independently validates request schema, trusted `execution_context.project_id`, domain invariants, and read-only operation semantics.
- Trusted execution context is constructed after policy validation and sent separately from model arguments. Duplicate or conflicting `project_id` in model arguments is rejected.
- Only an allowlisted internal MCP endpoint/audience is configured in this slice; arbitrary URLs, redirects, user headers, API keys, Basic Auth, and public egress are forbidden.
- Workload tokens/model credentials are retrieved inside Activities immediately before calls, never passed through Workflow input/result, and never persisted.
- Raw prompts, raw provider responses, hidden reasoning, auth headers, and full tool payloads are excluded from logs/events/audit. Persisted result/tool excerpts use allowlists, size bounds, and redaction.
- API lookup scopes by Project before resource resolution and follows the repository's non-disclosure error convention.

## Failure Isolation and Recovery

- A configuration failure cannot create a partial version/current-pointer update.
- A committed but undispatched Run stays `QUEUED`; the dispatcher and stale-queue metric expose/recover it.
- Model failures affect one Activity/Run. Operation-class retries are finite; validation and permission failures are never transport-retried.
- MCP failure affects the requesting Run only. There are no writes, so retrying a read is safe; stable logical IDs deduplicate local records.
- Persistence Activities are idempotent. A retry after commit returns the existing logical result rather than appending duplicate events/usage.
- Workflow replay uses snapshot data and stable IDs; it does not re-read mutable configuration to decide past behavior.
- Cancellation is cooperative for I/O already in flight and strict for future scheduling. Every first/next step checks the durable cancel state; ordered START/CANCEL dispatch prevents a late start from bypassing a queued cancellation. A cancellation-lag alert catches stuck Activities.
- `PARTIALLY_COMPLETED` is allowed only when a schema-valid partial result exists; otherwise errors end `FAILED`. No completed domain side effect exists in this feature.
- Recovery never consists of manually flipping status. Operators retry dispatch/signal by stable command or allow the reconciler to do so.

## Observability and Operations

Minimum progress events:

```text
run.created, run.started, run.retrying, run.cancelling,
agent.started, agent.completed,
tool.requested, tool.started, tool.completed, tool.denied, tool.failed,
run.completed, run.partially_completed, run.failed, run.cancelled
```

Minimum audit events:

```text
agent.configuration_changed, run.requested, run.cancel_requested,
tool.access_denied, run.terminalized
```

Minimum metrics (no Project/user IDs as labels):

- `agent_runs_started_total`
- `agent_runs_terminal_total{status}`
- `agent_run_duration_seconds`
- `agent_active_runs`
- `agent_workflow_dispatch_lag_seconds`
- `agent_activity_retries_total{operation}`
- `agent_model_calls_total{outcome}` and `agent_model_call_duration_seconds`
- `agent_mcp_calls_total{tool,outcome}` and `agent_mcp_call_duration_seconds`
- `agent_run_cancellation_latency_seconds`

Readiness for accepting new Runs requires PostgreSQL, Temporal connection/worker registration, one healthy model capability, and—when the selected AgentVersion enables an MCP tool—a valid MCP catalog snapshot plus workload-token acquisition for that MCP. Existing Runs remain readable when execution dependencies are degraded. Health details must not disclose secrets.

Runbooks must cover queued-dispatch backlog, model/MCP outage, schema-hash mismatch, retry spike, stuck cancellation, worker restart/replay, and safe disabling of new Run creation.

## Performance and Scale

Development assumptions, configurable below platform maxima:

| Constraint | Initial value | Verification |
|---|---:|---|
| Objective UTF-8 size | 32 KiB | API boundary tests |
| Model turns per Run | 8 | Workflow limit tests |
| Tool calls per Run | 10, sequential | Workflow/MCP tests |
| Active Run duration | 10 minutes | Temporal timeout/fake clock test |
| Final result size | 256 KiB | schema/size tests |
| MCP response size | 1 MiB | gateway boundary test |
| Run start/status/events p95 | ≤500 ms at 20 concurrent Runs, excluding execution | integration load probe before rollout |
| Events page | default 50, max 100 | API tests |

Production concurrency, retention, availability, backup/restore, and p95 targets remain an operations rollout gate, not a reason to add a queueing platform in this slice.

## Rollout and Compatibility

1. Add compatible PostgreSQL schema and application dependencies while all new routes/workers are disabled.
2. Deploy Temporal worker registration, MCP catalog verification, and readiness diagnostics.
3. Enable coordinator configuration for one test Project; validate immutable versions and authorization.
4. Enable no-tool direct Runs for that Project and exercise restart/replay.
5. Enable read-only MCP Runs after real MCP schema/auth validation.
6. Enable cancellation/hardening gates, observe error/retry/latency metrics, then expand allowlisted Projects.

The API is versioned. Additive response fields are compatible; removing/renaming fields, changing status/error semantics, or adding mandatory request fields requires a new version. AgentVersion and Run snapshots are never rewritten during rollout.

Rollback disables new configuration/Run starts first, lets active Workflows drain or cancels them, and keeps read APIs plus schema available. Application rollback must remain able to read all persisted states introduced by the rollout; schema removal occurs only in a later verified cleanup.

## Alternatives

- **Full v2 agent MVP now:** rejected for this feature because it violates the explicit minimum/sessionless request and multiplies unrelated acceptance paths. See DEC-001 and DEC-003.
- **Run everything in one retryable agent Activity:** rejected because it hides MCP I/O and makes retry/replay duplication difficult to reason about. See DEC-004.
- **Temporal as the only state store:** rejected because API/audit/analytics need PostgreSQL-owned state. See DEC-004.
- **Direct PMS database reads:** rejected because MCP/owner interfaces preserve domain ownership. See DEC-002 and DEC-006.
- **Kafka for dispatch/progress:** deferred; PostgreSQL dispatch reconciliation is sufficient for the first path. See DEC-005.
- **SDK-owned Session/Runner loop:** deferred; the Workflow-owned step protocol is required to keep model and MCP I/O at separate durable boundaries. See DEC-007.

## Traceability

| Design area | Requirements | Scenarios | Interfaces/data | Decisions | Slices |
|---|---|---|---|---|---|
| Configuration/versioning | REQ-001, REQ-003, REQ-010 | SCN-001 | API-001/002; DATA-001/002/009/010 | DEC-002, DEC-006 | SLICE-001 |
| Direct Workflow and model loop | REQ-002–005, REQ-007 | SCN-002 | API-003–005/008; DATA-003/004/007/008 | DEC-001, DEC-003, DEC-004, DEC-007 | SLICE-002 |
| MCP read boundary | REQ-005–007, REQ-010 | SCN-003/004 | API-008/009; DATA-005/006/010 | DEC-003, DEC-006 | SLICE-003 |
| Recovery/cancellation/operations | REQ-004, REQ-008–010 | SCN-004–006 | API-004–008; DATA-003–010 | DEC-004, DEC-005 | SLICE-004 |
