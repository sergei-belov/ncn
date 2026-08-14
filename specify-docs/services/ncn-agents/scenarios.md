# ncn-agents Service Scenarios

## Scenario Inventory

| Scenario | Actor/system | Requirement/feature | Interfaces | Models/tables |
|---|---|---|---|---|
| [SCN-001](#scn-001-configure-an-agent-team) | Project admin | AGT-REQ-001; FEAT-002 | UX-AGT-001/002; API-AGT-001/002 | MODEL-AGT-001/002; TABLE-AGT-001/002 |
| [SCN-002](#scn-002-execute-a-coordinated-run) | Member/coordinator/workers | AGT-REQ-002/003/006; FEAT-003 | API-AGT-003/004 | MODEL-AGT-003..010; Planned tables |
| [SCN-003](#scn-003-approve-or-reconcile-a-risky-tool-call) | Approver/tool provider | AGT-REQ-004/005; FEAT-003 | UX-AGT-004/005; API-AGT-005/006 | Tool/Approval/Result models |

## SCN-001: Configure an Agent Team

### Actor and Goal

A project admin creates/updates specialized workers while keeping a usable coordinator.

### Preconditions and Permissions

Active project, common `ncn-authz` admin action for agent management, existing active coordinator, and current entity version for mutation.

### Trigger

Admin opens agent list/settings or submits configuration/status command.

### Happy Path

1. API returns project-scoped coordinator and workers.
2. Admin creates a worker with validated name, description, instructions, model, memory policy, step limit, and approval mode.
3. API commits worker and returns canonical version.
4. Admin edits or enables/disables/archives a worker with `expected_version` in the JSON command.
5. UI updates detail/list caches, refetches, and records success.

### Alternatives and Edge Cases

Member/viewer and archived project are read-only. Coordinator edit fields may be allowed, but disable/archive is always forbidden. Duplicate live worker name or stale version conflicts. Archived worker is terminal unless a later decision defines restore.

### Failure and Recovery

Optimistic status change restores both list/detail cache on failure. Validation remains inline; conflict reloads canonical config. Do not retry a failed command without confirming idempotency/version.

### Accessibility

Forms have labels/errors; status uses native checkbox/switch semantics; confirmations name consequences; focus returns after dialog; read-only reason is visible.

### Observable Result

Exactly one active coordinator remains, worker status/config/version are consistent, and audit identifies the persisted authz user UUID/outcome without logging instructions.

### Traceability

AGT-REQ-001/002; AGT-INV-001/002; FEAT-002; API-AGT-001/002; MODEL/TABLE-AGT-001/002.

## SCN-002: Execute a Coordinated Run

### Actor and Goal

An authorized member sends a project goal and receives a durable, bounded, explainable result.

### Preconditions and Permissions

Execution feature enabled; common actor/project action authorized; eligible coordinator/workers/tools/models; budgets and project policy configured; required dependencies healthy or clearly degraded.

### Trigger

A Message or approved system initiator requests a Run.

### Happy Path

1. Agents atomically stores Message, Run initial state, stable IDs, and immutable effective configuration snapshot.
2. One root Temporal Workflow starts and the UI receives Run ID/state.
3. Backend builds minimized context and invokes coordinator through model adapter.
4. Structured RunPlan is schema/policy/limit validated and stored as immutable revision.
5. Temporal executes coordinator/worker/tool nodes; workers receive bounded delegation and return structured envelopes.
6. Memory recalls project-scoped cited sources; tools are re-authorized and effects are explicit nodes.
7. Coordinator may revise only unstarted plan at a safe boundary, then aggregates results.
8. PostgreSQL records terminal result, completed/failed parts, effects, unresolved items, usage and audit; UI renders it.

### Alternatives and Edge Cases

Coordinator requests clarification; bounded independent workers run in parallel with `all`; model output repairs at most twice; hard limit yields partial/failed controlled result; a new Message during active Run follows the still-Open concurrency policy; user cancels.

### Failure and Recovery

Temporal replays after restart using stable IDs/snapshot. Transient safe activities retry within budget. Non-idempotent unknown external outcome enters reconciliation. Cancellation stops future nodes and propagates where safe; completed effects remain disclosed. PostgreSQL/API state is reconciled with workflow state.

### Accessibility

Progress uses textual state, not color alone; live updates are throttled/announced without flooding; focus remains stable; cancel/input/approval controls are keyboard reachable; terminal summary describes partial failures and next action.

### Observable Result

Exactly one terminal Run envelope links input, snapshot, plan revisions, invocations, tools/approvals, citations/artifacts, effects, usage, and audit.

### Traceability

AGT-REQ-002/003/006; AGT-INV-002..009; FEAT-003; API-AGT-003/004; MODEL-AGT-003..010.

## SCN-003: Approve or Reconcile a Risky Tool Call

### Actor and Goal

An eligible approver decides a permitted risky action, or an operator/user resolves an external mutation with unknown outcome.

### Preconditions and Permissions

Tool node is explicit, current, permitted by common authz and agent constraints, scoped, risk-classified, and has stable arguments/duplicate-safety classification. Approver is routed and separately authorized.

### Trigger

Execution reaches an Approval boundary or receives an uncertain mutating-tool timeout.

### Happy Path

1. Backend creates pending Approval with human-readable action/arguments/risk and signals durable wait.
2. Approver reviews and approves/rejects.
3. Backend rechecks common actor/action, arguments, execution policy, Run/node state, and atomically applies one decision.
4. On approve, tool gateway invokes with a stable client command UUID in the domain payload when the owner supports safe replay; on reject, plan follows a controlled branch.
5. Outcome and side effect are recorded; workflow resumes.

### Alternatives and Edge Cases

Changed material arguments invalidate prior approval. Duplicate decision is deduplicated. Expired/ineligible decision is rejected. A timeout with unknown effect does not auto-retry a non-idempotent call; safe status lookup or manual reconciliation establishes result.

### Failure and Recovery

Restart retains pending wait/decision. Integration unavailability follows tool retry class. Reconciliation records evidence and never fabricates success. Unresolved item appears in partial/failure result and alerts.

### Accessibility

Approval UI names resource, action, material arguments, risk, consequences, and expiry; approve/reject are distinct and keyboard operable; decision confirmation is announced.

### Observable Result

Audit proves persisted actor/action, approval, exact arguments, tool attempt, duplicate-safety class/client command ID, result/unknown status, reconciliation and resumed terminal outcome.

### Traceability

AGT-REQ-004/005; AGT-INV-005/006/009; FEAT-003; API-AGT-005/006; Approval/ToolExecution/RunResult models.
