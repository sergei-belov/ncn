# ncn-agents API and Request/Response Interfaces

## Applicability

Applicable. Agent configuration API is **Present** under `/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agents`. Session/Run/Approval/artifact/memory administration APIs are **Planned**; exact paths/error registry/pagination remain Open and must be fixed before implementation.

## Ownership and Consumers

| Interface family | Owner | Consumer | Trust boundary | Status |
|---|---|---|---|---|
| Agent configuration | `ncn-agents` target; shared backend Present | Current Vue frontend | Common `ncn-authz` project actor into agent domain | Present |
| Session/Run control | `ncn-agents` | Current/future Vue surfaces | User/system initiator to durable runtime | Planned |
| Approval/reconciliation | `ncn-agents` | Frontend/operator | Human/security boundary | Planned |
| Artifact/memory control | `ncn-agents` modules | Frontend/agents | Content and retrieval boundary | Planned |

## Shared Conventions

UUID identities, UTC ISO 8601, `snake_case`, common persisted actor/project scope, stable error envelope, cursor pagination, additive `/api/v1` evolution and redacted audit follow project conventions. Config update/status commands carry `expected_version` in JSON. Long-running operations return Run/operation ID immediately. Run-control commands carry a client-generated `client_command_id` UUID in JSON where duplicate replay must resolve to one command. No custom synchronous tracking, duplicate-control, or concurrency headers are accepted. Progress uses a compatible polling and/or SSE/WebSocket contract selected during frontend implementation; reconnect always reads canonical Run state.

## Operation Inventory

| ID | Kind/entry point | Purpose | Consumer | Requirement/feature |
|---|---|---|---|---|
| API-AGT-001 | `GET/POST .../agents`; `GET/PATCH .../agents/{id}` | List/create/read/update configuration | Frontend | AGT-REQ-001; FEAT-002 |
| API-AGT-002 | `POST .../agents/{id}/enable|disable|archive` | Worker status commands | Frontend | AGT-REQ-001; FEAT-002 |
| API-AGT-003 | Planned Session/Message/Run create/list/read | Conversation and Run initiation/history | Frontend/system initiator | AGT-REQ-002/003/006 |
| API-AGT-004 | Planned Run state/events/cancel/input | Observe/control durable execution | Frontend | AGT-REQ-003/005/006 |
| API-AGT-005 | Planned Approval read/decide | Human risk decision | Frontend/approver | AGT-REQ-004 |
| API-AGT-006 | Planned artifacts/memory/reconciliation | Upload/read/ingest/resolve unknown effect | Frontend/operator | AGT-REQ-005/006 |

## API-AGT-001/002: Agent Configuration and Status

### Contract

List/read return project-scoped Agent. Create makes a worker only. Patch changes selected config fields. Enable/disable/archive are explicit commands and return the canonical Agent.

### Authentication and Authorization

Read requires API-AUTHZ-003 project access. Create/update/status require the common admin agent-management action and an active project. The coordinator cannot be disabled/archived regardless of role. Common authz checks persisted actor/project action before the agent manager; `ncn-agents` retains coordinator, archive, field, and execution-domain guards.

### Request

Create: `name` 2–80, `description` up to 240, `instructions` 20–4000, `model` 1–255, memory policy `project|session|none`, positive `max_steps_per_run`, approval mode `project|always`. Patch includes only changed non-null fields and required `expected_version`. Status JSON includes required `expected_version`. Tool names are currently response metadata, not accepted create fields.

### Response

Agent: UUID, project, kind `coordinator|worker`, fields above, status `active|disabled|archived`, `system_tool_names`, created/updated times, positive version.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Invalid fields/null/status | `422 validation` | Correct form |
| Forbidden/archive/project mismatch | `403 forbidden` or disclosure-safe `404` | No retry |
| Coordinator protected | `409 coordinator_protected` | Keep active |
| Duplicate live name/version stale | `409 duplicate_name` / `version_conflict` | Reload; rename/reapply intentionally |

### State, Idempotency, and Concurrency

Create duplicate safety before service extraction remains Open because the Present request lacks a client resource ID. Update/status compares JSON `expected_version` and increments once. Duplicate status command returns the same semantic state or a stable conflict. Current DB constraints protect coordinator/live name/status.

## API-AGT-003: Session, Message, and Run Initiation

### Contract

Planned operations create/list/read/close Sessions, append ordered Messages, and create a Run or atomically append message+start Run. Long-running execution returns `202` with Session/Message/Run IDs, initial state, snapshot version, and progress link.

### Authentication and Authorization

Validate the common persisted actor/project use-agents action, selected agent/tool policy, project constraints, active Session, and no conflicting mutating Run. A system initiator has separately scoped service identity and duplicate rule.

### Request

Session kind/metadata; Message role/content parts/mentions/artifact refs; Run input envelope, optional coordinator/config version, client-generated `client_command_id`, and permitted budget overrides within project caps. Session/Run IDs provide execution tracking. Size/content types are explicit before implementation.

### Response

Session/Message canonical representations and Run summary: state, created/started/updated/terminal times, snapshot reference, result/progress links, current wait reason, and version. Raw chain-of-thought is never returned.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Active Run conflict/session closed | `409 active_run` / `session_closed` | Follow active Run or open Session per policy |
| Model/tool/policy unavailable | `422 not_ready` or `503 dependency_unavailable` | Fix configuration or bounded retry |
| Duplicate client command | Original Run or `409 command_conflict` | Reuse returned Run ID |
| Budget/input invalid | `422 limit_exceeded` | Reduce input/choose allowed config |

### State, Idempotency, and Concurrency

Message ordering and Run initial state/snapshot/audit are atomic. One scoped `client_command_id` maps to one Run/root workflow. New-message behavior during active Run remains Open.

## API-AGT-004: Run Read, Progress, Input, and Cancellation

### Contract

Read Run/detail/events/result; stream or poll progress; submit requested clarification; request cancellation. Response separates active, waiting, and terminal states and includes plan/node summaries, not private reasoning.

### Authentication and Authorization

Project/Session read and action-specific cancel/input permission. Internal-only messages/events remain redacted. Cancellation cannot erase effects or audit.

### Request

Run ID/version, cursor for events, cancellation reason plus `client_command_id`, or input tied to the exact waiting node/input version.

### Response

Canonical Run version/state, wait descriptor, bounded progress events, terminal ResultEnvelope, usage and accessible action availability.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Stale/mismatched wait input | `409 wait_state_changed` | Reload Run |
| Already terminal/cancelling | Stable no-op or `409 invalid_transition` | Render canonical state |
| Stream disconnect | Transport close | Reconnect with cursor then GET canonical state |

### State, Idempotency, and Concurrency

Signals are deduplicated by scoped client command ID and atomically recorded before/with Temporal signaling. Terminal transition occurs once. Events have monotonic Run-local order/cursor.

## API-AGT-005: Approval Decision

### Contract

List/read pending approvals and apply approve/reject to one immutable described action. Backend immediately re-evaluates permission, eligibility, payload hash/version, Run/node state, and expiry.

### Authentication and Authorization

Authenticated user must be both routed approver and authorized for the target action. Approval never grants a forbidden action.

### Request

Approval ID/version, decision `approve|reject`, optional bounded reason, and `client_command_id`. Client cannot replace tool arguments.

### Response

Canonical approval status/decision time/actor and Run state link; no secret arguments.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| Ineligible/permission denied | `403 forbidden` | No retry |
| Changed/expired/already decided | `409 approval_invalidated|expired|decided` | Reload; new approval if workflow creates it |
| Signal temporarily unavailable | Accepted decision with pending delivery or `503` before commit | Reconciler safely signals from committed record |

### State, Idempotency, and Concurrency

Decision applies once in a transaction with audit; duplicate scoped client command ID returns the original decision. Workflow signal delivery is recoverable and cannot reverse it.

## API-AGT-006: Artifacts, Memory, and Reconciliation

### Contract

Upload/initiate authorized artifact, read metadata/download link, request memory ingestion/status through the internal agent memory module, and list/resolve tool executions requiring reconciliation. Exact routes are Open.

### Authentication and Authorization

Project/action/content access is checked at every upload/download/ingest/resolve. Reconciliation requires elevated operation/resource authority and cannot fabricate external evidence.

### Request

Artifact metadata/size/MIME/checksum, signed transfer completion, source/corpus link, or reconciliation decision with evidence/external reference and expected version.

### Response

Operation/artifact/ingestion or tool-execution state, signed short-lived link where applicable, and Run/result impact.

### Errors and Recovery

| Condition | Stable error | Retry/recovery |
|---|---|---|
| MIME/size/checksum/scan invalid | `422 artifact_rejected` | Correct file; no unsafe ingestion |
| Missing object/ingestion failure | `409 incomplete_upload` / controlled failure | Resume/retry idempotent step |
| Insufficient reconciliation evidence | `422 unresolved_outcome` | Investigate; keep unresolved |

### State, Idempotency, and Concurrency

Metadata and object completion use explicit states/checksum. Ingestion/reconciliation commands use scoped client command IDs and expected versions. Owner source deletion propagates to memory/artifact lifecycle.

## Compatibility and Versioning

Config API remains compatible during service extraction. Snapshot schemas and Temporal workflows have explicit versions. Run/event/result enums and stable errors are compatibility contracts. Additive fields are safe; breaking changes need new API/schema versions and workflow migration strategy.

## Limits and Performance

Exact request, history, context, artifact, rate, p95, concurrent Run, duration, node, worker, tool, token, and monetary limits are Open but mandatory before production. Progress is bounded/paginated and backpressured.

## Observability

Record persisted user UUID for synchronous calls plus safe Session/Run/node/tool/event IDs, scope, status/version, latency, duplicate outcome, model/tool class, approvals, usage, cancellation and error code. Exclude secret values, raw credentials, unrestricted prompt/output, private reasoning and artifact bytes.

## Traceability

API-AGT-001..006 consume API-AUTHZ-003 → AGT-REQ-001..006 → SCN-001..003 → UX-AGT-001..005 → MODEL/TABLE-AGT plus authz actor reference → FEAT-002/003/004 acceptance.
