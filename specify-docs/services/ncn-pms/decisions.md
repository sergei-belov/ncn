# ncn-pms Service Decisions

## Decision Inventory

| ID | Decision | Status | Affected contracts |
|---|---|---|---|
| DEC-PMS-001 | Keep PMS PostgreSQL state authoritative and board/read caches derived. | Accepted | PMS-INV-001..006; technical/data contracts |
| DEC-PMS-002 | Use expected entity/board versions and canonical neighbor ordering for concurrent board mutations. | Accepted/Present | PMS-REQ-002/004/005; API-PMS-004/006 |
| DEC-PMS-003 | Treat browser mock persistence as demo-only, never production truth. | Accepted | Technical design, UI/API evidence |
| DEC-PMS-004 | Consume common `ncn-authz` actor/role policy and retain PMS domain denials. | Accepted | PMS-REQ-005..008; SCN-003; technical/API/data contracts |

## DEC-PMS-001: PMS Owns Project Work Truth

### Status

Accepted. Owner: PMS/architecture. Reviewed 2026-08-13.

### Context and Drivers

The frontend and agent runtime need project facts, but duplicated writable project state would break ordering, permissions and recovery.

### Decision

Only PMS APIs/transactions write projects, stages, cards and epics. `ncn-agents` keeps resource/version/effect references in its Run records and the frontend keeps a rebuildable query projection.

### Alternatives

| Alternative | Advantages | Disadvantages | Reason not chosen |
|---|---|---|---|
| Shared table access | Low initial latency | Coupling, bypassed invariants, unsafe deployment | Violates service ownership |
| Consumer-owned copies | Local queries | Divergent truth and dual writes | Violates rebuildable projection rule |
| Owner API/MCP | Clear authority and recovery | Requires compatibility/reconciliation | Chosen |

### Consequences

PMS must expose sufficient APIs/tools and operate reliable transactions; agent calls reconcile against owner state. Any extraction must preserve stable identifiers and semantics.

### Reversal Conditions

Only a project-level ownership decision with full data/interface migration may reopen it.

### Affected Contracts

PMS-REQ-001..005, PMS-INV-001/007, API/MODEL/TABLE-PMS, project DEC-002/004.

## Open Decision Queue

| Question | Impact | Owner/evidence | Resolution trigger |
|---|---|---|---|
| Authz independent interface and project-bootstrap transaction | Access checks and creator membership consistency after separation | Authz/PMS/architecture owners | Before separation |
| Whether the first Run needs a PMS event | Kafka/outbox scope | PMS plus agent team | Confirmed asynchronous need |
| Retention/deletion model | Storage/privacy/audit | Product/data | Before production |
| Rank rebalance and maximum board size | Performance/concurrency | PMS/load evidence | Scale test |
