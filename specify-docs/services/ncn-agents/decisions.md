# ncn-agents Service Decisions

## Decision Inventory

| ID | Decision | Status | Affected contracts |
|---|---|---|---|
| DEC-AGT-001 | Use one project coordinator and non-nested specialized workers. | Accepted | AGT-INV-001/007; config/execution features |
| DEC-AGT-002 | Use one root Temporal workflow per Run while PostgreSQL remains product truth. | Accepted | AGT-INV-002..004; technical/tables |
| DEC-AGT-003 | Snapshot effective config and keep RunPlan revisions immutable; side effects only in explicit nodes. | Accepted | AGT-REQ-002..004; MODEL-AGT-002/005 |
| DEC-AGT-004 | Consume common authz, separate agent execution constraints from human Approval, and require duplicate-safety classification for tool mutations. | Accepted | AGT-REQ-004/005; Tool/Approval contracts |
| DEC-AGT-005 | Extract Present `pms_agents` data/API ownership into agents without breaking current clients. | Proposed | TABLE-AGT-001/002; project DEC-007 |

## DEC-AGT-002: Durable Run Boundary

### Status

Accepted architecture contract. Owner: Agent platform. Reviewed 2026-08-13.

### Context and Drivers

Long model/tool operations, approvals, cancellation, and worker restarts require durable orchestration, while API/audit/analytics need queryable stable business records.

### Decision

Map one Run to one root Temporal Workflow. Keep deterministic workflow progress in Temporal; persist product-visible Run state, snapshot, plans, approvals, effects, usage and results in PostgreSQL. Perform external I/O only in Activities and reconcile both sides.

### Alternatives

| Alternative | Advantages | Disadvantages | Reason not chosen |
|---|---|---|---|
| In-process background task | Simple | Lost on restart, weak waits/cancel | Fails durability |
| Kafka as workflow engine | Durable messages | Poor per-Run timers/state/signals | Wrong responsibility |
| Temporal-only business state | Less duplication | Poor API/audit/analytics and ownership | Violates PostgreSQL-first contract |

### Consequences

Workflow code needs compatibility discipline and stable replay IDs; DB/workflow reconciliation is required; operators monitor both. It enables durable waits/retries/cancel without polling loops.

### Reversal Conditions

Only an architecture version proving equivalent durable workflow, signal, retry, replay, and queryable truth semantics may reopen it.

### Affected Contracts

AGT-REQ-002..006; AGT-INV-002..004; SCN-002/003; MODEL/TABLE-AGT-003..012.

## Open Decision Queue

| Question | Impact | Owner/evidence | Resolution trigger |
|---|---|---|---|
| First vertical Run/tools/RAG/approval | All exact execution acceptance | Product | Before implementation |
| Active-Run message behavior | Session lock/UX/API | Product/agents | Before Session API |
| Model/fallback/budget/limit values | Safety/cost/performance | Model/platform | Before production |
| Config publication and target schema/migration | Snapshot correctness/service extraction | Agents/data | Before execution/separation |
| Retention/RPO/RTO/Continue-As-New | Recovery/storage | Platform/data | Before production |
