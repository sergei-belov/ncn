# API and Interface Contract

## Applicability

This feature adds machine-facing contracts in three families:

- Project-scoped HTTP operations for one coordinator and direct Runs;
- the internal Temporal Workflow/Activity protocol;
- the outbound model action and system MCP discovery/tool-call protocols.

No Session, Message, worker, Approval, memory, artifact, Kafka, webhook, CLI, file, streaming-token, or UI interface is added.

## Ownership and Consumers

| Interface family | Owner | Consumer | Trust boundary | Status |
|---|---|---|---|---|
| Agent HTTP v1 | `ncn-agents` | Portal API/internal clients; direct service client in integration tests | Authenticated actor → Project-scoped service | **Planned** |
| Temporal execution v1 | `ncn-agents` | `ncn-agents` API dispatcher and Temporal worker | Committed product command → durable runtime | **Planned** |
| Model action v1 | `ncn-agents` adapter | Approved Ollama-compatible model endpoint | Non-secret bounded context → untrusted structured output | **Planned** |
| System MCP protocol | MCP owner; consumed by `ncn-agents` | MCP catalog/gateway Activity | Trusted workload + server-derived context → domain owner | **Planned integration** |

The existing frontend Agent HTTP adapter is **Present** but not changed by this feature; adapting it to these routes/semantics is deferred.

## Interface Inventory

| ID | Kind | Entry point | Purpose | Requirement |
|---|---|---|---|---|
| API-001 | HTTP | `PUT /api/agents/v1/projects/{project_id}/coordinator` | Create or replace the one coordinator with a new immutable version | REQ-001, REQ-003, REQ-010 |
| API-002 | HTTP | `GET /api/agents/v1/projects/{project_id}/coordinator` | Read current safe coordinator representation | REQ-001, REQ-010 |
| API-003 | HTTP | `POST /api/agents/v1/projects/{project_id}/runs` | Start one direct sessionless Run | REQ-002, REQ-003, REQ-007, REQ-009, REQ-010 |
| API-004 | HTTP | `GET /api/agents/v1/projects/{project_id}/runs/{run_id}` | Read Run state and terminal result/error | REQ-007, REQ-008, REQ-010 |
| API-005 | HTTP | `GET /api/agents/v1/projects/{project_id}/runs/{run_id}/events` | Poll ordered semantic events | REQ-007, REQ-008 |
| API-006 | HTTP | `GET /api/agents/v1/projects/{project_id}/runs` | List recent direct Runs | REQ-007, REQ-010 |
| API-007 | HTTP | `POST /api/agents/v1/projects/{project_id}/runs/{run_id}/cancel` | Idempotently request cancellation | REQ-008, REQ-010 |
| API-008 | Temporal | Workflow ID `run:{run_id}` on task queue `agent-core` | Durably execute one bounded core-agent Run | REQ-004, REQ-005, REQ-008, REQ-009 |
| API-009 | MCP Streamable HTTP | Deployment-provisioned system MCP `tools/list` and `tools/call` for `get_project` | Discover and invoke the one acceptance read capability | REQ-006, REQ-010 |
| API-010 | Model action | Internal provider-neutral `CoreAgentActionV1` | Return a final result or ordered read-tool requests | REQ-005, REQ-009 |

## Authentication and Authorization

- HTTP uses the repository/platform authenticated actor. Every operation requests a Project-scoped decision from `ncn-authz` (or the repository-approved adapter) for `agent.configure`, `agent.run`, `agent.read_run`, or `agent.cancel_run`.
- A Run is scoped by both path `project_id` and persisted `project_id`. Resource lookup never relies on `run_id` alone.
- API-001 validates model/tool catalog references after authorization. Approval cannot grant access because Approval is outside this read-only feature.
- API-008 receives authorization and Project-constraint snapshots created by backend code. Temporal is never called with a bearer/workload/model credential.
- API-009 authenticates `ncn-agents` via an audience-specific workload access token acquired by client credentials and validated by OAuth2 Proxy. The MCP uses server-derived `execution_context.project_id`, not model arguments.
- Denial is fail-closed and audited. Safe client details do not disclose hidden resource/tool existence.

## Common HTTP Conventions

- JSON request/response uses `snake_case`; timestamps are ISO 8601 UTC with `Z`; identifiers are UUIDs.
- Every request accepts or receives `X-Request-ID`; responses include it. `correlation_id` is created at Run start and returned in Run/event resources.
- Mutating API-001, API-003, and API-007 require `Idempotency-Key` (1–128 printable ASCII characters). Same key + canonical request hash returns the prior status/body; same key + different hash returns `409 IDEMPOTENCY_KEY_REUSED`.
- The error body is:

```json
{
  "status": 422,
  "code": "RUN_OBJECTIVE_INVALID",
  "detail": "Objective must contain non-whitespace text",
  "trace_id": "019...",
  "field_errors": [{"field": "objective", "code": "blank"}]
}
```

`field_errors` is optional. Error `detail` is safe, human-readable, and not a compatibility key; `code` is stable within v1.
- Unknown JSON fields are rejected on write requests. No request field uses implicit null-to-default coercion.
- Single resources are returned directly. List resources use `{"data": [], "meta": {"total_count": n, "offset": n, "limit": n}}`.

## Operations

### API-001: Put coordinator

#### Contract

`PUT /api/agents/v1/projects/{project_id}/coordinator` creates the first coordinator or fully replaces its editable representation by creating a new immutable AgentVersion. It requires `Idempotency-Key` and either `If-None-Match: *` for first creation or `If-Match: "{version}"` for replacement.

#### Request

```json
{
  "name": "Project coordinator",
  "description": "Answers bounded project questions",
  "instructions": "Use project facts and return concise, sourced answers.",
  "model_id": "01900000-0000-7000-8000-000000000101",
  "model_settings": {
    "temperature": 0.2,
    "max_output_tokens": 2048
  },
  "allowed_tool_names": ["project__get_project"],
  "max_steps_per_run": 8
}
```

| Field | Semantics |
|---|---|
| `name` | Required trimmed string, 1–100 characters |
| `description` | Required string, may be empty, max 500 characters; not nullable |
| `instructions` | Required non-blank string, max 32 KiB; not returned by default read/list logs |
| `model_id` | Required logical catalog UUID; must support the feature's structured action/tool behavior |
| `model_settings.temperature` | Optional finite decimal 0–2; default inherited from catalog |
| `model_settings.max_output_tokens` | Optional integer 1–8192 and within model/platform maximum |
| `allowed_tool_names` | Required array, 0–10 unique canonical names; normalized/sorted; each must be discovered, read-only, active, and platform/project allowed |
| `max_steps_per_run` | Required integer 1–8 for this feature |

#### Response

`201 Created` for first creation or `200 OK` for replacement; `ETag: "{version}"`:

```json
{
  "id": "01900000-0000-7000-8000-000000000201",
  "project_id": "01900000-0000-7000-8000-000000000001",
  "kind": "coordinator",
  "name": "Project coordinator",
  "description": "Answers bounded project questions",
  "model_id": "01900000-0000-7000-8000-000000000101",
  "allowed_tool_names": ["project__get_project"],
  "max_steps_per_run": 8,
  "status": "active",
  "current_version_id": "01900000-0000-7000-8000-000000000202",
  "version": 1,
  "created_at": "2026-08-12T10:00:00Z",
  "updated_at": "2026-08-12T10:00:00Z"
}
```

API-001 returns the safe metadata representation above. Authorized configuration readers retrieve editable `instructions` and `model_settings` through API-002 with `include_configuration=true`. No credential is ever returned.

#### Errors and Recovery

| Condition | Stable error | Retry or recovery |
|---|---|---|
| Missing/invalid precondition | `428 PRECONDITION_REQUIRED` or `412 AGENT_VERSION_CONFLICT` | Re-read API-002 and resubmit intentionally |
| Existing coordinator on create | `409 COORDINATOR_ALREADY_EXISTS` | Read and replace with current ETag |
| Invalid model/tool/field | `422 AGENT_CONFIGURATION_INVALID` | Correct field/capability; no version created |
| Tool schema awaiting review/mutating | `409 TOOL_NOT_AVAILABLE_FOR_AGENT` | Review catalog or choose allowed read tool |
| Unauthorized/cross-Project | `403 PERMISSION_DENIED` or non-disclosing `404` | Obtain authority/use correct scope; do not retry blindly |
| Idempotency payload conflict | `409 IDEMPOTENCY_KEY_REUSED` | Use a new key for a new command |

#### Idempotency and Concurrency

Canonical request hashing normalizes tool ordering. Agent pointer/version, immutable version, idempotency result, and audit metadata commit atomically. A Project uniqueness constraint prevents two coordinators. `If-Match` serializes replacement without mutable version rows.

### API-002: Get coordinator

#### Contract

`GET /api/agents/v1/projects/{project_id}/coordinator` returns the current safe coordinator metadata after Project read authorization. `include_configuration=false` is the default. `include_configuration=true` additionally requires `agent.configure` and adds the current version's `instructions` and `model_settings` so an administrator can perform a deliberate full replacement. It has no side effect.

#### Response

`200 OK`, the API-001 safe response (plus editable fields when requested/authorized), and `ETag`; `404 COORDINATOR_NOT_CONFIGURED` when absent. No list/pagination applies. Neither representation contains a credential, provider endpoint secret, hidden platform policy, or historical version body.

#### Errors and Recovery

Authorization and Project scoping follow the common contract. Transient database errors return `503 SERVICE_UNAVAILABLE`; safe GET retry is allowed.

#### Idempotency and Concurrency

Not applicable to the read. A consistent query returns one current pointer/version; readers may use ETag for later API-001 replacement.

### API-003: Start direct Run

#### Contract

`POST /api/agents/v1/projects/{project_id}/runs` accepts a sessionless objective for the Project's current coordinator. It commits the Run before durable dispatch and never waits for model/MCP completion.

#### Request

```json
{
  "objective": "Summarize this project's name and current status."
}
```

`objective` is required, non-null, non-whitespace UTF-8 text of at most 32 KiB. No `session_id`, `message_id`, agent/model/tool override, arbitrary context, history, role, Project ID, or credential field is accepted.

#### Response

`202 Accepted`, `Location: /api/agents/v1/projects/{project_id}/runs/{run_id}`:

```json
{
  "run_id": "01900000-0000-7000-8000-000000000301",
  "project_id": "01900000-0000-7000-8000-000000000001",
  "agent_id": "01900000-0000-7000-8000-000000000201",
  "agent_version_id": "01900000-0000-7000-8000-000000000202",
  "status": "QUEUED",
  "correlation_id": "01900000-0000-7000-8000-000000000302",
  "created_at": "2026-08-12T10:01:00Z"
}
```

#### Errors and Recovery

| Condition | Stable error | Retry or recovery |
|---|---|---|
| Blank/oversized objective | `422 RUN_OBJECTIVE_INVALID` | Correct request |
| No valid coordinator | `409 COORDINATOR_NOT_READY` | Configure/repair coordinator |
| Model or required MCP readiness unavailable before acceptance | `503 AGENT_EXECUTION_NOT_READY` | Retry after readiness recovery |
| Hard Project concurrency limit reached | `429 RUN_CONCURRENCY_LIMIT` with `Retry-After` | Retry later with same key/payload |
| Commit succeeded but Temporal is temporarily unavailable | `202` with `QUEUED` Run | Poll; dispatcher reconciles |

#### Idempotency and Concurrency

`Idempotency-Key` is mandatory and scoped to actor + Project + operation. Same command returns the same Run. Independent keys may create concurrent Runs because Session concurrency does not exist. A configurable Project active-Run cap provides backpressure. Run/snapshot/event/dispatch/idempotency/audit commit atomically.

### API-004: Get Run

#### Contract

`GET /api/agents/v1/projects/{project_id}/runs/{run_id}` returns the PostgreSQL product projection. It never queries Temporal history on the request path.

#### Response

```json
{
  "id": "01900000-0000-7000-8000-000000000301",
  "project_id": "01900000-0000-7000-8000-000000000001",
  "agent_id": "01900000-0000-7000-8000-000000000201",
  "agent_version_id": "01900000-0000-7000-8000-000000000202",
  "status": "COMPLETED",
  "objective": "Summarize this project's name and current status.",
  "result": {
    "status": "completed",
    "summary": "Project Atlas is active.",
    "data": {},
    "warnings": []
  },
  "error": null,
  "usage": {
    "input_tokens": 420,
    "output_tokens": 58,
    "model_requests": 2,
    "tool_calls": 1
  },
  "correlation_id": "01900000-0000-7000-8000-000000000302",
  "created_at": "2026-08-12T10:01:00Z",
  "started_at": "2026-08-12T10:01:01Z",
  "completed_at": "2026-08-12T10:01:04Z"
}
```

`result` is null until a schema-valid terminal result exists. `error` is null except failed/partial outcomes and contains safe `code`, `detail`, `retryable`, and optional failed step/tool metadata. Snapshot internals and raw provider/tool bodies are not returned. `Retry-After: 2` may be supplied for active states.

#### Errors and Recovery

`404 RUN_NOT_FOUND`, `403 PERMISSION_DENIED`, and `503 SERVICE_UNAVAILABLE` follow common rules. GET retry is safe.

#### Idempotency and Concurrency

Read-only. Terminal response is immutable. Active timestamps/status are monotonically advanced by conditional writes.

### API-005: List Run events

#### Contract

`GET /api/agents/v1/projects/{project_id}/runs/{run_id}/events?after_sequence=0&limit=50` returns semantic progress events after the exclusive sequence.

#### Response

```json
{
  "data": [
    {
      "id": "01900000-0000-7000-8000-000000000401",
      "sequence": 1,
      "type": "run.created",
      "severity": "info",
      "message": "Run accepted",
      "data": {},
      "created_at": "2026-08-12T10:01:00Z"
    }
  ],
  "meta": {"next_after_sequence": 1, "has_more": false, "limit": 50}
}
```

`after_sequence` defaults to `0`; `limit` defaults to `50`, maximum `100`. Events are ascending. Payload schemas are event-type versioned, bounded, redacted, and must not contain reasoning, credentials, raw prompts/responses, or auth headers.

#### Errors and Recovery

Invalid pagination returns `422 EVENTS_QUERY_INVALID`. Polling callers retry transient failures with backoff and preserve the last processed sequence.

#### Idempotency and Concurrency

Each event has a stable logical key and `UNIQUE(run_id, sequence)` plus a uniqueness guard for the logical key. Gaps are allowed; duplicate Activity persistence does not duplicate events.

### API-006: List Runs

#### Contract

`GET /api/agents/v1/projects/{project_id}/runs?offset=0&limit=50&status=RUNNING` lists safe Run summaries newest-first by `(created_at, id)`.

#### Request and Response

`offset` defaults `0`; `limit` defaults `50`, maximum `100`; repeated `status` filters may select public status values. Response uses the common list envelope and omits objective/result by default, returning IDs, status, agent/version, actor-safe metadata, correlation ID, and timestamps.

#### Errors and Recovery

Invalid filters return `422 RUN_LIST_QUERY_INVALID`. Safe GET retry applies.

#### Idempotency and Concurrency

Read-only. Offset pagination can observe concurrent insertions; this is accepted for operational MVP listing and does not affect API-005 event ordering.

### API-007: Cancel Run

#### Contract

`POST /api/agents/v1/projects/{project_id}/runs/{run_id}/cancel` records a durable cancellation command; it does not wait for Activity shutdown.

#### Request

```json
{"reason": "No longer needed"}
```

`reason` is optional, non-null when present, trimmed, maximum 500 characters. It is audit-sensitive and not sent to the model/MCP.

#### Response

`202 Accepted`:

```json
{
  "run_id": "01900000-0000-7000-8000-000000000301",
  "status": "CANCELLING",
  "cancel_requested_at": "2026-08-12T10:02:00Z"
}
```

#### Errors and Recovery

| Condition | Stable error | Retry or recovery |
|---|---|---|
| Run terminal | `409 RUN_ALREADY_TERMINAL` with current status | Treat as final; do not mutate |
| Permission/project violation | `403 PERMISSION_DENIED` or non-disclosing `404` | Do not retry without changed authority |
| Temporal delivery unavailable after command commit | `202 CANCELLING` | Poll; dispatcher reconciles |

#### Idempotency and Concurrency

Mandatory idempotency key. Conditional update permits one active→`CANCELLING` transition; command/audit/event commit together. Multiple commands converge on one cancellation, while different-key races receive the current accepted/terminal state without a second semantic command. START precedes CANCEL for the same Run. When START is still pending, the dispatcher starts the stable Workflow and immediately delivers cancellation; the Workflow must read the durable `CANCELLING` state before scheduling its first model/tool Activity.

### API-008: RunWorkflow v1

#### Contract

One root Workflow with ID `run:{run_id}`, task queue `agent-core`, reuse policy rejecting duplicate active/completed Workflow IDs. Workflow code performs only deterministic state transitions, stable ID derivation, limit checks, Activity scheduling, retry/cancellation coordination, and result assembly.

#### Input

```json
{
  "schema_version": 1,
  "run_id": "UUID",
  "project_id": "UUID",
  "agent_id": "UUID",
  "agent_version_id": "UUID",
  "objective": "string <= 32 KiB",
  "execution_snapshot": {
    "instructions": "string",
    "model": {"logical_id": "UUID", "capabilities_hash": "sha256", "settings": {}},
    "tools": [{"canonical_name": "project__get_project", "schema_hash": "sha256", "input_schema": {}, "output_schema": {}, "risk": "read_only"}],
    "authorization": {"policy_revision": "string", "allowed_tool_names": []},
    "project_constraints": {},
    "limits": {"max_steps": 8, "max_tool_calls": 10, "max_duration_seconds": 600}
  },
  "initiated_by": {"actor_type": "user", "actor_id": "UUID"},
  "correlation_id": "UUID",
  "created_at": "UTC timestamp"
}
```

No Session/Message ID, secret, access token, credential reference that enables decryption, raw auth header, or mutable catalog pointer is allowed. Snapshot schemas are versioned and size-limited.

#### Activities and model protocol

Required logical Activities:

| Activity | Role | Retry class |
|---|---|---|
| `persist_run_transition` | Idempotently persist state/event/terminal data | Bounded PostgreSQL transient retry |
| `invoke_core_agent_model` | Invoke model and validate API-010 plus usage | Model transient retry; invalid output repaired within bounded invocation contract |
| `prepare_mcp_tool_call` | Deterministic-policy validation against current authz service where required and immutable snapshot | Fail closed; only dependency-transient retry |
| `execute_mcp_read_tool` | Acquire token, call API-009, validate/limit output | MCP read retry |

API-010 `CoreAgentActionV1` is exactly one of:

```json
{"action": "final", "result": {"status": "completed", "summary": "...", "data": {}, "warnings": []}}
```

```json
{"action": "tool_calls", "tool_calls": [{"name": "project__get_project", "arguments": {}}]}
```

The union rejects additional fields, an empty tool-call list, mixed final/tool actions, unknown status, and invalid tool arguments. `result.status` is `completed` or `partially_completed`; backend maps it to public Run terminal state after policy/size validation. Tool calls are executed sequentially in returned order.

#### Result

```json
{
  "schema_version": 1,
  "run_id": "UUID",
  "terminal_status": "COMPLETED",
  "result": {"status": "completed", "summary": "...", "data": {}, "warnings": []},
  "error": null,
  "usage_summary": {"input_tokens": 0, "output_tokens": 0, "model_requests": 1, "tool_calls": 0}
}
```

PostgreSQL terminal persistence is the product commit point; Workflow result is operational confirmation. If they momentarily diverge, reconciliation never overwrites a database terminal state.

#### Errors and Recovery

Stable root codes include `MODEL_UNAVAILABLE`, `INVALID_OUTPUT`, `TOOL_NOT_ALLOWED`, `TOOL_SCHEMA_MISMATCH`, `TOOL_ARGUMENTS_INVALID`, `TOOL_LIMIT_EXCEEDED`, `EXECUTION_LIMIT_EXCEEDED`, `MCP_UNAVAILABLE`, `MCP_AUTH_FAILED`, `MCP_RESPONSE_INVALID`, `RESULT_SIZE_EXCEEDED`, `PERSISTENCE_UNAVAILABLE`, and `RUN_CANCELLED`.

Model transient policy: 2-second initial interval, coefficient 2, 20-second maximum, 3 attempts; connect/read/Activity timeouts 10/180/200 seconds. MCP read policy: 1-second initial, coefficient 2, 10-second maximum, 3 attempts; connect/read/Activity timeouts 10/60/75 seconds. Validation/permission/limit errors are non-retryable.

#### Idempotency and Concurrency

Stable logical IDs derive from persisted Run identity and Workflow turn indexes, never wall clock/randomness during replay. Activity persistence uses operation keys. Tool calls are sequential. Cancellation stops new scheduling. Workflow versioning/patching must preserve replay compatibility for existing histories; incompatible logic uses a new Workflow type/version.

### API-009: System MCP discovery and read call

#### Contract

The transport is MCP Streamable HTTP over the deployment-provisioned internal endpoint. Discovery uses the protocol's tool listing operation and records canonical name `{server_name}__get_project`, description, input/output JSON Schemas, read-only risk classification, server version, discovery time, and schema hash. Tool execution uses MCP `tools/call` with name `get_project`.

#### Request

The gateway passes the protocol-native arguments required by the discovered schema plus a trusted execution-context envelope/header defined jointly with the MCP owner. Semantically it contains:

```json
{
  "project_id": "UUID",
  "run_id": "UUID",
  "agent_id": "UUID",
  "tool_call_id": "stable string",
  "initiated_by_user_id": "UUID",
  "correlation_id": "UUID"
}
```

The transport carries an audience-specific bearer workload token. Model-supplied context/identity is not forwarded as trusted context. Arguments must match the snapshotted input schema and may not override Project scope.

#### Response

The MCP protocol response must fit 1 MiB and validate against the snapshotted output schema before use. The acceptance schema must return only the minimum Project fields needed for the question; `ncn-agents` persists bounded safe metadata/result excerpts, not an authoritative Project copy.

#### Errors and Recovery

Protocol/transport errors normalize to safe codes. `429` respects bounded `Retry-After`; `401` may reacquire one expired workload token; schema, authorization, Project, or domain validation failures are non-retryable. An output-schema/hash mismatch blocks the call and marks the integration not ready for new Runs.

#### Idempotency and Concurrency

The feature permits reads only, so transport retry is safe. `tool_call_id` remains stable across attempts and deduplicates local events/records. There is no external write or exactly-once claim.

## Compatibility and Versioning

- `/v1` request required fields, public states, result semantics, and stable error codes are compatibility contracts.
- New optional response fields/event types are additive; callers ignore unknown response fields/event types but not unknown terminal statuses.
- Request schemas remain strict. New optional request fields require a defined default; new mandatory behavior uses a new API version.
- AgentVersion, execution snapshot, Temporal Workflow input/result, API-010, and event payloads contain explicit schema versions/hashes. Existing snapshots/histories are never rewritten after catalog evolution.
- MCP schema changes create a new catalog version/hash and block new use until reviewed; active Runs retain the snapshot and may finish only if the MCP remains compatible with that version.

## Limits and Performance

- Common write body maximum: 64 KiB; objective 32 KiB; instructions 32 KiB; Run result 256 KiB; MCP response 1 MiB.
- API list/event limit defaults 50, maximum 100.
- Run start/status/events target p95 ≤500 ms at the development load assumption, excluding agent execution.
- Active Run, model-turn, tool-call, output-token, duration, and Project concurrency limits are snapshot/configuration values capped by platform maxima.
- Long operations return `202` and are polled. No HTTP request remains open for a Run, model call, or MCP call.

## Observability

- All boundaries propagate/generate `X-Request-ID`, `trace_id`, `correlation_id`, and `run_id` as applicable.
- HTTP access logs exclude request objective/instructions/result. Model/MCP logs exclude raw prompts/responses, arguments/results by default, tokens, credentials, and headers.
- API-005 carries progress only; AuditEvents are stored/read under a separate privileged audit contract outside this feature's public route set.
- Metrics and readiness are defined in [technical design](../design/technical.md#observability-and-operations). Alerts correlate dispatch lag, retries, MCP/model failure, and cancellation lag without high-cardinality identity labels.

## Traceability

| Interface | Requirements | Scenarios | Data | Validation | Slice |
|---|---|---|---|---|---|
| API-001/002 | REQ-001, REQ-003, REQ-010 | SCN-001 | DATA-001/002/009/010 | Authz, concurrency, immutability, idempotency tests | SLICE-001 |
| API-003–006 | REQ-002, REQ-003, REQ-007, REQ-009/010 | SCN-002/003/005 | DATA-003/004/006–010 | API, transaction, polling, result tests | SLICE-002/003/004 |
| API-007 | REQ-008, REQ-010 | SCN-006 | DATA-003/004/009/010 | Cancel race/delivery/restart tests | SLICE-004 |
| API-008/010 | REQ-004/005/008/009 | SCN-002–006 | DATA-003–009 | Temporal replay/time-skip/failure tests | SLICE-002/004 |
| API-009 | REQ-006, REQ-010 | SCN-003/004 | DATA-005/010 | MCP discovery/auth/schema/denial tests | SLICE-003 |
