# User and System Scenarios

## Scenario Inventory

| Scenario | Actor | Requirement | UX or interface | Delivery slice |
|---|---|---|---|---|
| [SCN-001](#scn-001-configure-the-core-agent) | Project administrator | REQ-001, REQ-003, REQ-010 | API-001, API-002; UI N/A | SLICE-001 |
| [SCN-002](#scn-002-complete-a-direct-run-without-a-tool) | Project member | REQ-002, REQ-003, REQ-005, REQ-007 | API-003, API-004, API-005; UI N/A | SLICE-002 |
| [SCN-003](#scn-003-complete-a-run-with-a-read-only-mcp-tool) | Project member and agent runtime | REQ-005, REQ-006, REQ-007 | API-003–005, API-008, API-009; UI N/A | SLICE-003 |
| [SCN-004](#scn-004-deny-an-invalid-or-unassigned-tool-call) | Agent runtime and system MCP | REQ-006, REQ-009, REQ-010 | API-008, API-009; UI N/A | SLICE-003, SLICE-004 |
| [SCN-005](#scn-005-recover-from-transient-failure-and-worker-restart) | Operator, Temporal, and caller | REQ-004, REQ-008, REQ-009 | API-003–005, API-008, API-009; UI N/A | SLICE-002, SLICE-004 |
| [SCN-006](#scn-006-cancel-an-active-run) | Project member | REQ-008 | API-004–007, API-008; UI N/A | SLICE-004 |

## SCN-001: Configure the core agent

### Actor and Goal

An authorized Project administrator wants to establish or revise the one coordinator configuration that direct Runs will execute.

### Preconditions

- The Project exists in the Project system of record.
- The caller has Project-scoped coordinator configuratioИли n permission.
- The logical model identifier and canonical allowed tool names exist in the platform catalog.
- For an update, the caller has the current entity version/ETag.

### Trigger

The administrator submits the complete coordinator representation to API-001 with an idempotency key and either `If-None-Match: *` for creation or `If-Match` for replacement.

### Happy Path

1. The API authenticates the caller and obtains a Project-scoped authorization decision.
2. The manager validates field bounds, the logical model capability, tool names, risk class, and Project/platform limits.
3. One transaction creates or updates the stable Agent resource, inserts a new immutable AgentVersion, changes the current-version pointer, records idempotency/audit metadata, and increments the resource version.
4. The API returns `201` for first creation or `200` for replacement with the stable Agent ID, new AgentVersion ID, entity version, and ETag.
5. API-002 returns the current representation; old versions remain internal and readable by Runs that reference them.
6. If a prior Run is active, its stored snapshot and AgentVersion reference remain unchanged.

### Alternatives and Edge Cases

- Same idempotency key and identical payload returns the original response; a different payload returns `IDEMPOTENCY_KEY_REUSED`.
- Two concurrent first creates yield one coordinator; the loser receives `COORDINATOR_ALREADY_EXISTS` or the idempotent original.
- A stale `If-Match` returns `AGENT_VERSION_CONFLICT` without creating a version.
- Canonical tool order is normalized before snapshot/hash comparison; semantically identical retries do not create a second version.
- Empty instructions, an unsupported model, excessive step limit, unknown tool, or mutating-risk tool fails validation.

### Failure and Recovery

- Authorization or Project lookup failure creates no Agent/AgentVersion.
- Database failure rolls back the Agent, version, idempotency result, and audit metadata together; the caller may safely retry with the same idempotency key.
- Model/MCP availability is not required for saving configuration, but unsupported catalog/capability metadata is rejected before persistence.

### Permissions and Accessibility

There is no new UI in this feature. The machine API provides field-specific validation details and stable errors usable by a future accessible form. Read permission does not imply configure permission.

### Observable Result

Exactly one current coordinator exists for the Project, the returned version is immutable, and an `agent.configuration_changed` AuditEvent identifies actor, Project, Agent, version, and correlation ID without credentials or full instructions.

### Acceptance Links

REQ-001, REQ-003, REQ-010; AC-001, AC-003, AC-010; API-001, API-002; DATA-001, DATA-002, DATA-007; DEC-002, DEC-006; SLICE-001.

## SCN-002: Complete a direct Run without a tool

### Actor and Goal

A Project member wants the configured core agent to answer one objective without creating or managing a conversation.

### Preconditions

- A current coordinator configuration exists and is valid.
- The caller has run permission in the Project.
- PostgreSQL and Temporal are ready; the configured model passes its capability check.
- The deterministic test/provider response returns a valid final result without requesting a tool.

### Trigger

The caller posts one non-empty text objective to API-003 with an idempotency key.

### Happy Path

1. The API validates identity, Project scope, permission, input size, and idempotency.
2. In one database transaction it creates the Run, immutable execution snapshot, `run.created` event, dispatch record, and idempotency result.
3. The API starts or schedules idempotent dispatch of Temporal Workflow `run:{run_id}` and returns `202` without waiting for the model.
4. The Workflow persists `RUNNING`, invokes the model through an Activity, and receives a schema-valid final result.
5. A terminal persistence Activity atomically stores usage, result, `run.completed`, and `COMPLETED`.
6. The caller polls API-004/API-005 and reads the ordered lifecycle and result envelope.

### Alternatives and Edge Cases

- A duplicate start with the same key/payload returns the same Run ID; different payload reuse fails.
- Empty/whitespace input or input above 32 KiB is rejected before a Run exists.
- A configuration replacement immediately after creation does not change this Run's AgentVersion or snapshot.
- A second independent request with a different idempotency key creates another Run; no Session-level concurrency rule applies.
- A result at the size boundary succeeds; an oversized result fails with `RESULT_SIZE_EXCEEDED` and is not partially returned.

### Failure and Recovery

- If Temporal start is temporarily unavailable after commit, the Run remains `QUEUED`; dispatch reconciliation retries the same Workflow ID.
- Model transient failures follow the policy in SCN-005. Invalid structured output receives at most two repair turns, then `INVALID_OUTPUT` and `FAILED`.
- A persistence retry cannot create duplicate terminal events because stable event keys/unique constraints are used.

### Permissions and Accessibility

No browser surface is added. API responses distinguish accepted, active, retrying, and terminal states with stable codes rather than relying on color, animation, or timing.

### Observable Result

The caller receives one Run ID, observes `QUEUED`, `RUNNING`, and `COMPLETED`, and receives a valid result and usage summary. No Session or Message row/identifier/event exists.

### Acceptance Links

REQ-002, REQ-003, REQ-005, REQ-007; AC-002, AC-003, AC-005, AC-007; API-003–005, API-008; DATA-003, DATA-004, DATA-006; DEC-001, DEC-003–005; SLICE-002.

## SCN-003: Complete a Run with a read-only MCP tool

### Actor and Goal

A Project member asks an objective that requires the core agent to read Project data through the allowed system MCP before answering.

### Preconditions

- SCN-002 preconditions hold.
- The configured coordinator allowlists canonical tool name `{server_name}__get_project`.
- MCP discovery has stored/verified the expected name, read-only risk classification, schemas, server version, and schema hash.
- Workload token acquisition and the system MCP are healthy.

### Trigger

The model Activity returns a schema-valid request for `get_project` with arguments that satisfy the discovered input schema.

### Happy Path

1. `RunWorkflow` assigns a stable logical tool-call ID derived from Run and turn.
2. A preparation Activity/policy boundary verifies tool availability, schema hash, coordinator allowlist, Project scope, read-only risk, arguments, and remaining limits.
3. The MCP gateway obtains an audience-specific workload token in memory and invokes API-009 with server-derived execution context; it does not trust a model-supplied Project ID.
4. The MCP validates its schema, scope, and domain invariants and returns a bounded response.
5. The runtime persists tool metadata and safe semantic events, then supplies the validated result to the next model Activity.
6. The model produces a valid final result citing the tool result at a semantic level, and the Run becomes `COMPLETED`.

### Alternatives and Edge Cases

- The model may produce more than one tool request; they execute sequentially in stable order and each consumes the tool-call limit.
- A repeated logical read after retry uses the same tool-call ID; repeated read transport is allowed, while persistence is deduplicated.
- A discovery schema hash change blocks new Runs/configuration until reviewed; it never changes an active Run's snapshot.
- An empty valid MCP result is given to the model as an explicit empty result, not treated as transport failure.
- A response above 1 MiB or invalid against output schema fails as `MCP_RESPONSE_INVALID`.

### Failure and Recovery

- Transient MCP/read timeout is retried up to three times with bounded backoff; exhaustion fails the tool step and normally the Run with `MCP_UNAVAILABLE`.
- Workload authentication failure is retried only when classified as refreshable; persistent failure becomes `MCP_AUTH_FAILED`.
- Safe model-facing errors contain only code, generic detail, and retryability, never internal stack/auth data.

### Permissions and Accessibility

No UI applies. Project scope and tool permission are enforced on every call even though the tool is read-only. API event text is concise and machine-readable for a future accessible progress view.

### Observable Result

Ordered events identify the agent, logical tool, timing, outcome, and correlation ID; the result envelope is valid; audit/metrics show the read call; no domain database was accessed directly and no credentials were persisted.

### Acceptance Links

REQ-005, REQ-006, REQ-007; AC-005–007; API-003–005, API-008, API-009; DATA-003–006; DEC-003–006; SLICE-003.

## SCN-004: Deny an invalid or unassigned tool call

### Actor and Goal

The runtime must contain a model request that is invalid, outside the coordinator's allowlist, mutating, stale, oversized, or cross-Project.

### Preconditions

- A Run is active with an immutable tool/policy snapshot.
- The model produces a tool request that violates at least one validation or policy condition.

### Trigger

The Workflow submits the model's requested tool call to the deterministic preparation/policy boundary.

### Happy Path

1. The boundary evaluates canonical name, schema snapshot/hash, Project, allowlist, risk, arguments, and limits in fail-closed order.
2. It denies the call before workload-token acquisition or MCP network I/O.
3. The runtime records a redacted `tool.denied` progress event and separate security AuditEvent with the stable denial code.
4. At most one safe tool-error result is returned to the model so it may produce a compliant final answer within remaining steps.
5. If the model repeats the denial or cannot produce a valid result, the Run ends `FAILED` with the stable first/root error.

### Alternatives and Edge Cases

- Unknown tool and non-allowlisted tool both fail closed; response wording must not reveal hidden catalog entries.
- A model-supplied `project_id` is removed/rejected; server scope always wins.
- A discovered schema mismatch blocks the call even if name and arguments appear valid.
- Exceeding step/tool limits terminates without another model or MCP Activity.
- Concurrent configuration expansion does not change the active Run's allowlist.

### Failure and Recovery

Validation and permission denial are not retried as Activities. The caller may revise configuration and start a new Run; the active Run is never retroactively granted permission. Internal policy exceptions fail closed as `TOOL_POLICY_UNAVAILABLE`.

### Permissions and Accessibility

The caller sees a stable, non-sensitive Run error/warning. Detailed security context is restricted to authorized audit readers.

### Observable Result

The MCP mock records zero requests, the Run produces one controlled terminal result, and logs/events contain no credential, hidden schema catalog, other-Project data, raw prompt, or reasoning.

### Acceptance Links

REQ-006, REQ-009, REQ-010; AC-006, AC-009, AC-010; API-008, API-009; DATA-003–005, DATA-007; DEC-003, DEC-004; SLICE-003, SLICE-004.

## SCN-005: Recover from transient failure and worker restart

### Actor and Goal

An operator and caller need an in-flight Run to survive API/Temporal-worker interruption or transient model/MCP failure without loss or unsafe duplication.

### Preconditions

- A Run is `QUEUED`, `RUNNING`, or `RETRYING`.
- Test controls can fail dispatch, a model/read Activity, persistence, or the worker process at a known boundary.

### Trigger

A dependency returns a retryable failure or the API/worker process restarts during the Run.

### Happy Path

1. The retryable Activity records/updates safe attempt metadata and Temporal schedules the configured retry using the same logical operation ID.
2. If the worker restarts, Temporal replays deterministic Workflow history and resumes at the pending Activity/boundary.
3. If initial dispatch was incomplete, reconciliation starts `run:{run_id}`; an already-started conflict is treated as success.
4. Unique operation/event/usage keys suppress duplicate product records during replay or persistence retry.
5. The Run either completes once after dependency recovery or fails once with retry-exhausted root cause.

### Alternatives and Edge Cases

- API restart has no effect on Workflow progress and polling resumes from PostgreSQL.
- Model and MCP retry policies differ; validation/permission errors never enter transient retry.
- A restart after terminal persistence but before Activity acknowledgment replays the Activity and returns the prior terminal result.
- A stale projection reconciler may repair state from a durable command/result but cannot move a terminal Run backward.

### Failure and Recovery

Retry exhaustion produces `MODEL_UNAVAILABLE`, `MCP_UNAVAILABLE`, or `PERSISTENCE_UNAVAILABLE` as appropriate. Operators use run ID/correlation ID and metrics to investigate; blind replay as a new Run is never the default recovery.

### Permissions and Accessibility

Only authorized callers read Run state. `RETRYING` is an explicit machine state/event with attempt and next-action metadata; no rapid token-level updates are required.

### Observable Result

There is one Run, one Workflow ID, one terminal transition, and at most one persisted logical tool/model result per stable operation ID. Restart/retry metrics are incremented without payload leakage.

### Acceptance Links

REQ-004, REQ-008, REQ-009; AC-004, AC-008, AC-009; API-003–005, API-008, API-009; DATA-003–007; DEC-004, DEC-005; SLICE-002, SLICE-004.

## SCN-006: Cancel an active Run

### Actor and Goal

An authorized Project member wants to stop a direct Run that is no longer needed.

### Preconditions

- The Run belongs to the caller's Project and is not terminal.
- The caller has cancellation permission according to Project policy.

### Trigger

The caller posts API-007 with an idempotency key and optional bounded reason.

### Happy Path

1. The API authenticates/authorizes, atomically records the cancellation command and audit metadata, conditionally changes active state to `CANCELLING`, and returns `202`.
2. It signals/cancels Temporal Workflow `run:{run_id}`; reconciliation repeats safely if delivery fails.
3. The Workflow stops scheduling new model/tool Activities and requests cancellation of a cancellable in-flight Activity.
4. Terminal persistence records `CANCELLED`, partial read-only metadata if useful, usage so far, and `run.cancelled`.
5. API-004/API-005 show the terminal state and ordered cancellation events.

### Alternatives and Edge Cases

- Repeating the same command returns the original response and sends no semantically new cancellation.
- Two callers racing to cancel create one accepted logical command.
- If START dispatch is still pending, dispatch preserves START-before-CANCEL; the newly started Workflow observes `CANCELLING` before its first model/tool Activity and terminates without doing agent work.
- Cancelling a terminal Run returns `RUN_ALREADY_TERMINAL` with its current state and does not change it.
- Cancellation during model/MCP I/O may wait for Activity cancellation/timeout, but must not start another turn.

### Failure and Recovery

If the signal cannot be delivered immediately, the Run remains `CANCELLING`; the dispatcher/reconciler retries. An alert fires when cancellation exceeds its configured latency threshold. Operators do not edit Run state manually.

### Permissions and Accessibility

No UI applies. The API exposes explicit accepted, cancelling, terminal, denied, and already-terminal semantics suitable for a future keyboard/screen-reader accessible control.

### Observable Result

The Run reaches `CANCELLED` once, no new tool call starts after the durable cancel command, usage and audit data remain queryable, and no Session state exists.

### Acceptance Links

REQ-008; AC-008; API-004–008; DATA-003, DATA-004, DATA-007; DEC-001, DEC-004, DEC-005; SLICE-004.
