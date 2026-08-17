# Data and State Model

## Applicability

Persistent and transient state changes are required. PostgreSQL stores the product-visible configuration and Run projection; Temporal stores durable control-flow history. This document specifies logical contracts and constraints, not table names or an already-existing migration. All database schema/migration work is **Planned**.

No Session, Message, worker, plan/DAG, Approval, secret, memory/vector, artifact, automation, or Kafka projection entity is created by this feature.

## Ownership

- `ncn-agents` owns all DATA-001–010 writes. Other services consume its API/events and do not mutate these records directly.
- PostgreSQL is authoritative for configuration, Run state/result, events, tool metadata, usage, commands/idempotency, dispatch, and audit metadata.
- Temporal is authoritative only for durable execution progress, retry timers/attempts, cancellation propagation, and replay history. It is not queried as the product read model.
- `ncn-authz` owns role/policy truth. Runs store only the immutable authorization decision/revision context needed to explain and constrain that Run.
- The Project/PMS owner owns Project business data. A bounded MCP result is Run evidence, not an authoritative copy or projection of the Project.
- The platform model catalog and system MCP catalog are external/reference owners; DATA-002/DATA-003 snapshot their non-secret effective contract for reproducibility.

## Entity Inventory

| ID | Entity or state | Owner | Purpose | Classification |
|---|---|---|---|---|
| DATA-001 | Agent | `ncn-agents` | Stable one-per-Project coordinator identity/current pointer | Internal metadata |
| DATA-002 | AgentVersion | `ncn-agents` | Immutable executable coordinator configuration | Restricted (instructions/policy) |
| DATA-003 | AgentRun | `ncn-agents` | Direct objective, immutable snapshot, lifecycle, result/error | Restricted user/execution data |
| DATA-004 | RunEvent | `ncn-agents` | Ordered semantic progress for polling | Internal/restricted payload |
| DATA-005 | ToolExecution | `ncn-agents` | Logical MCP call attempts/outcome metadata and bounded safe result | Restricted execution data |
| DATA-006 | ModelUsageRecord | `ncn-agents` | Per-model-call normalized usage and latency | Internal metering metadata |
| DATA-007 | RunDispatch | `ncn-agents` | Reconcile committed start/cancel commands with Temporal | Internal operational state |
| DATA-008 | RunOperation | `ncn-agents` | Deduplicate logical Workflow Activities/terminal writes | Internal operational state |
| DATA-009 | IdempotencyRecord | `ncn-agents` | Deduplicate HTTP mutations and detect payload conflicts | Restricted request metadata |
| DATA-010 | AuditEvent | `ncn-agents` | Security/administrative evidence separate from progress | Restricted audit data |

## Entities and Fields

All persisted identifiers are application-generated UUIDs. All timestamps are `TIMESTAMPTZ` in UTC. JSON fields have versioned application schemas and database size guards where practical.

### DATA-001: Agent

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id` | UUID | Required | Primary key | Stable coordinator ID |
| `project_id` | UUID | Required | Unique for `kind=coordinator`; indexed | Project ownership |
| `kind` | enum | Required / `coordinator` | Only `coordinator` allowed in this feature | Topology role |
| `status` | enum | Required / `active` | Only `active`; cannot archive/disable | Availability invariant |
| `current_version_id` | UUID | Required after create | References DATA-002 owned by same Agent/Project | Current version for new Runs |
| `version` | integer | Required / 1 | Positive; increments on current-pointer change | Optimistic concurrency/ETag |
| `created_at`, `updated_at` | timestamp | Required | UTC; monotonic update time | Lifecycle metadata |

### DATA-002: AgentVersion

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id` | UUID | Required | Primary key | Immutable version ID |
| `agent_id`, `project_id` | UUID | Required | Same-owner references; indexed | Stable Agent and tenancy |
| `version_number` | integer | Required | `UNIQUE(agent_id, version_number)`; positive | Human/debug ordering |
| `name` | string | Required | Trimmed 1–100 | Display name snapshot |
| `description` | string | Required / empty allowed | Max 500 | Safe description snapshot |
| `instructions` | string | Required | Non-blank; max 32 KiB; restricted | System/user instruction snapshot |
| `model_id` | UUID | Required | Logical catalog reference | Model selected for this version |
| `model_settings` | JSON | Required / `{}` | Versioned strict schema; no credential | Bounded generation settings |
| `allowed_tool_names` | string array/JSON | Required / `[]` | Canonical sorted unique; max 10 | Tools this version may request |
| `max_steps_per_run` | integer | Required | 1–8 | Version-level turn bound |
| `configuration_hash` | SHA-256 string | Required | Hash of canonical non-secret effective configuration | Equality/audit evidence |
| `created_by_actor_id`, `created_at` | UUID, timestamp | Required | Immutable | Provenance |

An AgentVersion has no update/delete operation in this feature. Credential IDs, plaintext secrets, Session memory policies, workers, approvals, and archive state are absent.

### DATA-003: AgentRun

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id` | UUID | Required | Primary key; Temporal ID derives as `run:{id}` | Run identity |
| `project_id`, `agent_id`, `agent_version_id` | UUID | Required | Same Project; indexed | Ownership and exact configuration |
| `initiator_type` | enum | Required / `user` | Only `user` in this feature | Trigger class |
| `initiated_by_actor_id` | UUID | Required | Indexed under Project | Authenticated initiator |
| `objective` | string | Required | Non-whitespace; max 32 KiB; restricted | Direct sessionless input |
| `input_schema_version` | integer | Required / 1 | Positive | Direct input compatibility |
| `execution_snapshot` | JSON | Required | Immutable strict schema; non-secret; bounded | Effective instructions/model/tools/authz/constraints/limits |
| `snapshot_hash` | SHA-256 string | Required | Canonical immutable hash | Reproducibility/integrity |
| `workflow_id` | string | Required | `UNIQUE`; exactly `run:{id}` | Temporal correlation |
| `workflow_type_version` | integer/string | Required | Versioned | Replay compatibility |
| `status` | enum | Required / `CREATED` | Public lifecycle; indexed | Product state |
| `result` | JSON nullable | Null until valid final/partial result | Versioned; max 256 KiB | Terminal result envelope |
| `error` | JSON nullable | Null absent failure/partial warning | Safe strict schema | Stable terminal/root error |
| `usage_summary` | JSON | Required / zeros | Derived transactionally from DATA-006 | Polling summary |
| `correlation_id`, `trace_id` | UUID/string | Required | Indexed where operationally useful | Cross-boundary correlation |
| `created_at`, `queued_at`, `started_at`, `completed_at` | timestamp nullable by lifecycle | Required as state permits | Monotonic | Lifecycle timing |
| `cancel_requested_at`, `cancelled_at` | timestamp nullable | Set only by cancellation lifecycle | Monotonic | Cancellation timing |
| `terminal_version` | integer | Required / 0 | Conditional single `0→1` terminal update | Terminal race guard |

`session_id`, `message_id`, conversation history, incoming queue, plan/revisions, approval pointers, and artifact pointers do not exist.

### DATA-004: RunEvent

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id`, `project_id`, `run_id` | UUID | Required | Primary/ownership references | Event identity/scope |
| `sequence` | integer | Required | `UNIQUE(run_id, sequence)`; monotonic, gaps allowed | Polling order |
| `logical_key` | string | Required | `UNIQUE(run_id, logical_key)` | Retry/replay deduplication |
| `event_type` | string/enum | Required | Registered versioned semantic type | Event meaning |
| `severity` | enum | Required / `info` | `info`, `warning`, `error` | Consumer presentation hint |
| `message` | string | Required | Safe, bounded, non-secret | Human-readable fallback |
| `payload_schema_version`, `payload` | integer, JSON | Required / 1, `{}` | Strict per type; bounded/redacted | Machine detail |
| `created_at` | timestamp | Required | UTC | Occurrence/persistence time |

Events are append-only. They never contain hidden reasoning, raw prompt/provider response, credentials, auth headers, unrestricted tool arguments/results, or audit-only policy details.

### DATA-005: ToolExecution

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id`, `project_id`, `run_id`, `agent_id` | UUID | Required | Owned references; indexed by Run | Tool execution identity/scope |
| `logical_tool_call_id` | string | Required | `UNIQUE(run_id, logical_tool_call_id)` | Stable retry/replay identity |
| `turn_index`, `call_index` | integer | Required | Non-negative; unique pair per Run | Deterministic order |
| `canonical_tool_name` | string | Required | Must exist in snapshot | Called capability |
| `schema_hash` | SHA-256 string | Required | Must equal Run snapshot | Contract identity |
| `risk_class` | enum | Required / `read_only` | Only `read_only` allowed | Safety classification |
| `arguments_hash` | SHA-256 string | Required | Hash only; no unrestricted arguments | Audit/dedup evidence |
| `status` | enum | Required | `REQUESTED`, `DENIED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED` | Tool lifecycle |
| `attempt_count` | integer | Required / 0 | Non-negative | Transport attempts |
| `safe_result` | JSON nullable | Bounded, schema-valid, redacted | Max 1 MiB before narrower persistence policy | Model/Run evidence, not business truth |
| `error_code`, `retryable` | string/bool nullable | Required on failure/denial | Stable safe semantics | Failure classification |
| `started_at`, `completed_at` | timestamp nullable | By lifecycle | UTC | Timing |

### DATA-006: ModelUsageRecord

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id`, `project_id`, `run_id`, `agent_id`, `agent_version_id` | UUID | Required | Owned/indexed | Usage identity/scope |
| `logical_model_call_id` | string | Required | `UNIQUE(run_id, logical_model_call_id)` | Retry/replay settlement key |
| `turn_index`, `model_id` | integer, UUID | Required | Turn non-negative | Call/model identity |
| `provider_request_id` | string nullable | Provider-defined; unique where reliable | Optional diagnostic dedup |
| `input_tokens`, `output_tokens`, `cached_input_tokens`, `reasoning_tokens` | integer | Required / 0 | Non-negative | Normalized usage |
| `request_count` | integer | Required / 1 | Positive | Logical provider request count |
| `latency_ms` | integer | Required | Non-negative | Performance |
| `status` | enum | Required | `completed`, `failed`, `cancelled` | Outcome |
| `created_at` | timestamp | Required | UTC | Settlement time |

Prompts and outputs are not stored in usage. Monetary price/ledger fields are deferred.

### DATA-007: RunDispatch

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id`, `project_id`, `run_id` | UUID | Required | `UNIQUE(run_id, command_type, command_version)` | Dispatch identity/scope |
| `command_type` | enum | Required | `START` or `CANCEL` | Temporal command |
| `command_version` | integer | Required / 1 | Positive | Multiple semantic command guard |
| `workflow_id` | string | Required | Exactly Run Workflow ID | Target |
| `status` | enum | Required / `PENDING` | `PENDING`, `DELIVERING`, `DELIVERED`, `FAILED` | Delivery lifecycle |
| `attempt_count`, `last_error_code` | integer, string nullable | Non-negative | Operational retry evidence |
| `next_attempt_at`, `delivered_at`, `created_at`, `updated_at` | timestamps nullable by state | Indexed for pending scan | Reconciliation scheduling |

The dispatcher claims due rows with database-safe conditional/skip-locked semantics, preserves START-before-CANCEL ordering per Run, and treats already-started/already-cancelled Temporal responses as delivered when the Workflow identity matches. A Workflow started after cancellation was committed must observe `CANCELLING` through its initial persistence Activity and terminate without a model/tool Activity.

### DATA-008: RunOperation

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id`, `project_id`, `run_id` | UUID | Required | Owned references | Operation identity/scope |
| `operation_key` | string | Required | `UNIQUE(run_id, operation_key)` | Stable logical Activity/effect key |
| `operation_type` | enum/string | Required | Registered model/tool/persist/finalize type | Effect class |
| `status` | enum | Required | `STARTED`, `COMPLETED`, `FAILED`, `CANCELLED` | Idempotent effect state |
| `request_hash`, `result_hash` | SHA-256 nullable | Required as applicable | Detect payload mismatch | Integrity/dedup |
| `safe_result_ref` | JSON/UUID nullable | Bounded pointer/summary only | No secret/raw provider response | Replayed result reference |
| `created_at`, `completed_at` | timestamps nullable | By state | UTC | Timing |

### DATA-009: IdempotencyRecord

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id`, `project_id`, `actor_id` | UUID | Required | Scope | Command ownership |
| `operation` | string | Required | Registered API operation | Namespace |
| `idempotency_key` | string | Required | 1–128 printable ASCII; unique within scope/operation | Client retry key |
| `request_hash` | SHA-256 string | Required | Canonical request including path target | Conflict detection |
| `resource_id` | UUID nullable | Set when command creates/targets resource | Replay target |
| `response_status`, `response_body` | integer, JSON nullable | Set on completion; safe bounded snapshot | Prior response replay |
| `state` | enum | Required | `IN_PROGRESS`, `COMPLETED`, `FAILED_RETRYABLE` | Command lifecycle |
| `created_at`, `expires_at` | timestamp | Required | Expiry after retention window, never before supported client retry window | Lifecycle |

### DATA-010: AuditEvent

| Field | Type | Required/null/default | Constraints | Meaning |
|---|---|---|---|---|
| `id`, `project_id` | UUID | Required | Primary/scope index | Audit identity |
| `actor_type`, `actor_id` | string/enum, UUID nullable | Required as applicable | System actor may be null ID | Who acted |
| `action` | string/enum | Required | Registered audit type | What occurred |
| `resource_type`, `resource_id` | string, UUID nullable | Required as applicable | Indexed | Target |
| `run_id`, `agent_id` | UUID nullable | Context-dependent | Indexed | Agent correlation |
| `decision` | enum nullable | `allowed`, `denied`, `n/a` | Policy result |
| `metadata` | JSON | Required / `{}` | Allowlisted/redacted, versioned | Safe evidence |
| `trace_id`, `correlation_id` | string/UUID | Required | Correlation | Investigation link |
| `created_at` | timestamp | Required | Append-only UTC | Audit time |

## Relationships and Constraints

- `Agent(project_id, kind=coordinator)` is unique. `Agent.current_version_id` must reference an AgentVersion with matching `agent_id` and `project_id`; manager transaction/order prevents dangling pointers.
- AgentVersion rows are append-only and unique by `(agent_id, version_number)`. A Run references one exact version and additionally embeds the effective snapshot.
- AgentRun belongs to one Project/Agent/version and has no Session relationship. Its `workflow_id` is unique and deterministic.
- All Run child records repeat `project_id` for tenancy checks/indexing; repositories require both Project and parent ID, and constraints/triggers or composite references enforce same-Project ownership as the implementation standard permits.
- RunEvent ordering is unique by `(run_id, sequence)`; logical idempotency is unique by `(run_id, logical_key)`.
- ToolExecution and ModelUsageRecord are unique by stable logical call ID per Run. Temporal retry never generates a new logical ID.
- One terminal write is enforced by conditional `terminal_version=0` and terminal-status guards. Terminal status/result/error/timestamps/usage/event commit together.
- JSON schemas and hashes are canonicalized with an implementation-documented algorithm. `null` is never treated as absent unless the field contract says nullable.

## State Transitions

### AgentRun

| From | Trigger | Guard | To | Side effects |
|---|---|---|---|---|
| none | API-003 accepted transaction | Authorized, valid current AgentVersion, idempotency/concurrency permitted | `CREATED` then `QUEUED` in same transaction | Snapshot, event, dispatch, audit, idempotency |
| `QUEUED` | Workflow starts | Same Workflow ID; non-terminal | `RUNNING` | `run.started`, start time |
| `RUNNING` | Retryable Activity failure | Attempts remain, not cancelling | `RETRYING` | Safe retry event/attempt metadata |
| `RETRYING` | Activity attempt starts/succeeds | Not cancelling | `RUNNING` | Retry completion/progress event |
| `QUEUED`/`RUNNING`/`RETRYING` | API-007 cancel command | Authorized, non-terminal | `CANCELLING` | Cancel dispatch/event/audit |
| `RUNNING`/`RETRYING` | Valid completed final result | Limits satisfied; terminal guard zero | `COMPLETED` | Result, usage, terminal event/audit |
| `RUNNING`/`RETRYING` | Valid partial result | Explicit partial semantics; no hidden side effect; terminal guard zero | `PARTIALLY_COMPLETED` | Partial result/error/warnings, usage, terminal evidence |
| `QUEUED`/`RUNNING`/`RETRYING` | Non-retryable/exhausted failure | Terminal guard zero | `FAILED` | Stable error, usage, terminal evidence |
| `CANCELLING` | Workflow acknowledges cancellation | Terminal guard zero | `CANCELLED` | Usage/result metadata so far, terminal evidence |

No transition leaves `COMPLETED`, `PARTIALLY_COMPLETED`, `FAILED`, or `CANCELLED`. There are no `WAITING_FOR_INPUT`, `WAITING_FOR_APPROVAL`, `BUDGET_BLOCKED`, or Session-derived states.

### ToolExecution

```text
REQUESTED → DENIED
REQUESTED → RUNNING → COMPLETED
                    ├→ FAILED
                    └→ CANCELLED
```

No state reopens. Transport attempts increment `attempt_count` without creating a new logical ToolExecution.

### RunDispatch and idempotency

```text
RunDispatch: PENDING ↔ DELIVERING → DELIVERED
                              └→ FAILED (only after configured operational exhaustion)
IdempotencyRecord: IN_PROGRESS → COMPLETED
                              └→ FAILED_RETRYABLE
```

Delivery leases may return expired `DELIVERING` to `PENDING`; semantic delivery remains deduplicated by Workflow/command identity.

## Consistency and Transactions

Required atomic units:

1. **Coordinator replace:** validate preconditions; insert AgentVersion; insert/update Agent; store idempotency response and `agent.configuration_changed` audit.
2. **Run accept:** insert AgentRun/snapshot; allocate initial event sequence; insert RunEvent, START RunDispatch, IdempotencyRecord response, and `run.requested` AuditEvent.
3. **Cancel accept:** conditional Run status update; insert/update CANCEL RunDispatch; append event; store idempotency response and AuditEvent.
4. **Tool/model result:** complete the relevant RunOperation and upsert ToolExecution or ModelUsageRecord plus RunEvent with stable keys.
5. **Terminalize:** conditional terminal guard/status update; store result/error/usage summary/timestamps; append terminal RunEvent and AuditEvent; mark outstanding dispatch state consistent.

PostgreSQL commit is the local product-state commit point. Temporal delivery occurs after commit and is at-least-once. No database/Temporal distributed transaction is attempted. Reconciliation scans due dispatch and stale active Runs; it cannot mutate terminal history backward.

Per-Run dispatch ordering is part of consistency: START is delivered or reconciled before CANCEL. This preserves INV-003 for a queued cancellation while the Workflow's first Activity reads the committed Run status and prevents any model/tool scheduling when it is already `CANCELLING`.

Concurrent Agent revisions use `If-Match` plus conditional Agent version update. Run creation snapshots one committed Agent current-version pointer within its transaction. Concurrent independent Runs are allowed up to the configured Project cap.

## Retention, Deletion, and Privacy

- **Assumed development retention:** Run/event/tool/usage/idempotency data 30 days; AuditEvents at least 90 days; Agent/AgentVersion retained while any Run references them. Production values are **Open** and must be configured before broad rollout.
- No delete/archive API is in scope. Physical cleanup is a later owner-operated retention job and must respect referential order and audit policy.
- Objective, instructions, result, safe tool result, and error context are restricted Project data. Encryption at rest/in transit follows platform/PostgreSQL/Temporal deployment controls.
- Workload/model credentials, access tokens, auth headers, plaintext secrets, hidden reasoning, and unrestricted raw prompts/provider/tool responses are prohibited from DATA-001–010 and Temporal inputs/results.
- Idempotency response bodies expire only after the supported retry horizon; deleting them earlier may break duplicate semantics.
- Temporal history retention must be at least the maximum active Run duration plus recovery margin and align with operational investigation needs; it is configured separately from product retention.

## Access Patterns and Indexing

Planned indexes/constraints, with final names left to implementation:

- unique Agent coordinator by Project; Agent current version lookup;
- AgentVersion `(agent_id, version_number desc)` and `project_id` ownership;
- AgentRun `(project_id, created_at desc, id desc)`, `(project_id, status, created_at)`, and unique `workflow_id`;
- RunEvent unique `(run_id, sequence)`, unique `(run_id, logical_key)`, and `(run_id, sequence)` scan;
- ToolExecution/ModelUsageRecord `(run_id, turn_index, call_index)` plus logical ID uniqueness;
- RunDispatch `(status, next_attempt_at)` with a partial/predicate index for pending/delivering work;
- RunOperation unique `(run_id, operation_key)`;
- IdempotencyRecord unique `(project_id, actor_id, operation, idempotency_key)` and expiry index;
- AuditEvent `(project_id, created_at desc)`, `(resource_type, resource_id, created_at)`, and `run_id` where non-null.

No cache is required for correctness. If later added, it is a disposable projection and terminal/config mutation invalidates it.

## Migration and Backfill

- **Planned:** create a dedicated `ncn-agents` schema/module migration containing DATA-001–010 tables, enums/checks, indexes, and references within that logical owner.
- There is no backfill from frontend mock/localStorage; browser Agent records are demo projections and are not transactional backend truth.
- Importing existing frontend-configured Agent data is outside this feature. A future adapter/migration must map fields explicitly and must not claim execution history.
- Deployment is expand-first: create nullable/compatible structures, deploy readers/writers/workers disabled, verify constraints/catalogs, then enable configuration and Runs per Project.
- Rollback disables new writes/workflows and keeps the schema/read compatibility. Do not down-migrate while a Run, dispatch row, idempotency response, or retained AgentVersion depends on it.
- Migration verification covers empty database creation, uniqueness/foreign ownership, transition constraints, canonical snapshot hashes, and query plans for Run/event/dispatch access.

## Audit and Observability

- AuditEvent is append-only and separate from RunEvent. It records configuration changes, Run/cancel requests, policy denials, and terminalization with actor/resource/correlation metadata.
- Data-quality signals: queued dispatch age, active Run without recent operation/event, terminal Run missing terminal event/result-or-error, duplicate logical IDs, summary/usage mismatch, MCP schema mismatch, and cancellation age.
- Reconciliation alerts include exact Run/correlation IDs in restricted logs but never objective/instructions/tool bodies or credentials.
- Metrics use aggregate labels only; Project, actor, Run, and correlation IDs must not become Prometheus labels.

## Traceability

| Data | Requirements/invariants | Scenarios | Interfaces | Decisions | Slices |
|---|---|---|---|---|---|
| DATA-001/002 | REQ-001/003/010; INV-001/002/008 | SCN-001 | API-001/002/003 | DEC-002/006 | SLICE-001 |
| DATA-003/004 | REQ-002–005/007–010; INV-002–004/007/008 | SCN-002–006 | API-003–008 | DEC-001/004/005 | SLICE-002/004 |
| DATA-005/006 | REQ-005–007/009/010; INV-005/006/008 | SCN-003–005 | API-004/005/008–010 | DEC-003/004/007 | SLICE-002/003/004 |
| DATA-007/008/009 | REQ-002/004/008/009; INV-003/004/008 | SCN-001/002/005/006 | API-001/003/007/008 | DEC-004/005 | SLICE-001/002/004 |
| DATA-010 | REQ-001/006–008/010; INV-005–008 | SCN-001/003–006 | API-001/003/007–009 | DEC-002/006 | SLICE-001–004 |
