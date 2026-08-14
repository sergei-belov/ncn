# ncn-agents Database Tables

## Applicability and Database Status

Applicable. `public.pms_agents` is **Present transitional implementation** verified 2026-08-13. All other logical tables below are **Planned** and names are contract placeholders, not migration claims. PostgreSQL is authoritative; Temporal, Qdrant and frontend projections are not substitutes.

## Table Inventory

| ID | Schema.table | Purpose | Authoritative/derived | Lifecycle | Models |
|---|---|---|---|---|---|
| TABLE-AGT-001 | `public.pms_agents` | Current mutable agent config | Authoritative Present but mis-owned name/FK | Create/update/status; migration Planned | MODEL-AGT-001 |
| TABLE-AGT-002 | `agents.agent_configs` + versions (logical) | Target mutable/published configuration | Authoritative Planned | Version/archive; coordinator invariant | MODEL-AGT-001 |
| TABLE-AGT-003 | `agents.sessions`, `agents.messages` (logical) | Ordered conversation | Authoritative Planned | Create/append/close/retain | MODEL-AGT-003 |
| TABLE-AGT-004 | `agents.run_snapshots` (logical) | Immutable effective configuration | Authoritative Planned | Create once; retain with Run | MODEL-AGT-002 |
| TABLE-AGT-005 | `agents.runs` (logical) | Durable product Run state | Authoritative Planned | Create; guarded transitions; retain | MODEL-AGT-004 |
| TABLE-AGT-006 | `agents.run_plan_revisions`, `run_nodes` (logical) | Immutable plan history/nodes | Authoritative Planned | Append revisions; node transitions | MODEL-AGT-005 |
| TABLE-AGT-007 | `agents.agent_invocations` (logical) | Agent/model attempt/result | Authoritative Planned | Append/terminal | MODEL-AGT-006 |
| TABLE-AGT-008 | `agents.tool_executions` (logical) | Tool attempt/effect/reconciliation | Authoritative Planned | Append; reconcile unknown | MODEL-AGT-007 |
| TABLE-AGT-009 | `agents.approvals` (logical) | Durable approval decision | Authoritative Planned | Pending → one terminal decision/state | MODEL-AGT-008 |
| TABLE-AGT-010 | `agents.usage_records` (logical) | Tokens/cost/resource accounting | Authoritative ledger Planned | Append/retain | MODEL-AGT-009 |
| TABLE-AGT-011 | `agents.artifacts` (logical) | Metadata/object lifecycle | Authoritative metadata Planned | Upload/process/archive/delete policy | MODEL-AGT-009 |
| TABLE-AGT-012 | `agents.run_events` (logical) | Persisted progress and terminal timeline | Authoritative Run read history Planned | Append/retention/replay by API cursor | MODEL-AGT-010 |

## TABLE-AGT-001: Present Transitional Agent Configuration

### Ownership and Purpose

Present shared backend table `pms_agents` stores agent config and points to `pms_projects`. Target owner is `ncn-agents`; PMS may expose/validate project reference but does not own agent rows.

### Columns

| Column | Database type | Null/default | Key/constraint | Sensitivity | Meaning |
|---|---|---|---|---|---|
| base `id`, `project_id` | UUID | Required | PK; FK PMS project cascade; project index | Internal | Identity/scope |
| `kind`, `name`, `status` | varchar | Required/status active | allowed enums; one coordinator/project; live name unique; coordinator active | Internal | Topology/lifecycle |
| `description`, `instructions`, `model` | varchar/text | Required/description empty | length at API boundary | Instructions restricted | Behavior/model |
| `memory_policy`, `max_steps_per_run`, `approval_mode` | enum strings/int | Required | allowed enums; steps >0 | Restricted | Runtime policy settings |
| `system_tool_names` | JSONB | `[]` | Schema checked in API/manager | Security restricted | Current tool metadata |
| `created_by`, timestamps, `version` | UUID/time/int | Required/version 1 | indexes; version >0 | Internal | Audit/concurrency |

### Relationships and Constraints

Partial unique coordinator/project, partial unique live name/project, enum/positive/version/coordinator-active checks are Present. Cross-project access remains manager/repository responsibility. Cascade project delete must be revisited against independent-service retention.

### Access Patterns and Indexes

| Query/access pattern | Filter/order | Expected volume | Index/partition | Verification |
|---|---|---|---|---|
| List agents | project/status/kind | Low per project | project FK index; live-name/coordinator indexes | Present mapping |
| Read/update | project+agent+version | Low | PK + project validation; version check in manager | API tests/inventory |

### Transactions and Concurrency

Update/status compares expected version and increments atomically. Create must serialize coordinator/live-name uniqueness. Run snapshot is not Present and must not read mutable config after start once execution exists.

### Lifecycle, Retention, and Privacy

Workers archive logically; coordinator stays active. Instructions/tool metadata are restricted. Current project cascade conflicts with independent retention and needs migration decision. No plaintext secret belongs in this table.

### Schema Evolution

Move to target ownership using stable IDs, scope, versions, enum mapping and API compatibility. Proposed sequence: expand target schema; backfill; verify counts/hashes/invariants; switch owner/facade; reconcile; contract old path only after rollback window. Exact mechanism remains Open; no migration exists by this documentation.

### Backup, Restore, and Data Quality

Check one coordinator/project, coordinator active, unique live name, valid enums, positive versions/steps, existing project reference, and no secret material. Backup is currently with shared PostgreSQL; target restore ownership must be explicit.

## TABLE-AGT-002..012: Planned Execution Schema Contract

### Ownership and Purpose

Agents is sole writer. Tables may be consolidated/split during design, but must preserve the model/invariant/transaction semantics in this contract. Domain owner data is referenced, never copied as writable truth.

### Columns

| Area | Required column semantics | Key/constraint | Sensitivity | Meaning |
|---|---|---|---|---|
| Scope/identity | UUID IDs, workspace/project, created/updated UTC, schema/version | Stable PKs; project-scoped indexes | Internal | Isolation/replay |
| Session/Message | session status/kind; monotonic message sequence; role/visibility/content ref/hash | unique session+sequence; one active Run/session guard | Confidential | Conversation |
| Run/snapshot | workflow/client-command/causation IDs, status/wait, config/schema/hash, terminal result/version | unique workflow/scoped client command; one terminal transition; snapshot immutable | Restricted | Durable execution |
| Plan/node | revision number, node key/kind/status, dependencies, structured input/output refs/hash | unique run+revision/node; immutable revisions | Restricted | Plan history |
| Invocation/tool | attempt, agent/model/tool/schema, authz decision/policy/approval/client command, status/outcome/external ref | unique logical attempt/scoped command; outcome unknown explicit | Confidential/security | Execution/effects |
| Approval | payload hash/version, risk/action, approver routing, expiry/decision/version | one atomic decision; changed payload invalidates | Security/personal | Human gate |
| Usage/artifact/event | dimensions/amount/price; object metadata/checksum/state; event sequence/type | non-negative usage; unique object/checksum policy; unique run event sequence | Commercial/confidential | Accounting/content/progress |

### Relationships and Constraints

All execution children reference Run/project; Run references Session/snapshot; nodes reference revision; invocations/tools/approvals reference exact node. Cross-project references are impossible by application and preferably composite constraints. PMS/tool-provider IDs have no direct cross-service FK and are validated through owner APIs and agent permission policy.

### Access Patterns and Indexes

| Query/access pattern | Filter/order | Expected volume | Index/partition | Verification |
|---|---|---|---|---|
| Active Runs/waits | project/session/status/update time | Open | partial indexes for active/waiting | Load test/design |
| Run timeline | run+event sequence | Potentially high | unique run+sequence; retention/partition Open | Progress/replay test |
| Approval inbox | project/approver/status/expiry | Open | pending/expiry/routing indexes | UX/SLO test |
| Command replay/reconciliation | client command/status/tool/external ref | Open | unique scoped command; unknown-outcome index | Duplicate/timeout tests |
| Usage/audit | project/run/time/model/tool | High | time/project/run indexes; partition Open | Cost/audit queries |

### Transactions and Concurrency

Atomic: Session/Message/Run/snapshot initialization; immutable plan revision append; guarded node transition; approval decision+audit; terminal Run result; usage charge; artifact metadata and RunEvent transitions. Use optimistic/pessimistic locking where competing transitions exist. Temporal signals are reconciled from committed state. Side-effect replay safety is enforced with an owner-supported client command identity or an equivalent owner deduplication mechanism.

### Lifecycle, Retention, and Privacy

Exact retention/deletion/legal hold is Open. Run/audit/effect evidence must outlive transient workflow/cache state and support incident reconstruction. User deletion must not silently erase required effect/audit evidence; use redaction/tombstone where policy requires. Encrypt storage, restrict prompt/content columns, and store object bytes externally.

### Schema Evolution

All names/columns are Planned. Use versioned snapshots/result/event payloads, expand/backfill/switch/contract migrations, Temporal workflow compatibility, data-quality gates and tested rollback. Never mutate historical snapshot/revision meaning in place.

### Backup, Restore, and Data Quality

Define RPO/RTO before production. Restore PostgreSQL and object metadata/content; reconcile active Runs with Temporal, artifacts with object store, internal Run events with Run state, and Qdrant derivatives with source metadata. Check one coordinator, one active Run/session, snapshot immutability, valid transitions, complete terminal result, approval uniqueness, budget sums, event sequence, no orphan objects and no secret leakage.

## Cross-Table Rules

Stable UUIDs/replay IDs, mandatory project scope, UTC time, explicit versions, append-only historical records, owner-only writes, no plaintext secrets and audit/state atomicity are universal.

## Traceability

TABLE-AGT-001..012 → MODEL-AGT-001..010 → AGT-INV-001..009 → SCN-001..003 → API-AGT → DEC-AGT-001..004.
