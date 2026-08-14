# Delivery Plan

## Delivery Strategy

Deliver four dependency-ordered vertical slices. Each leaves `ncn-agents` in a coherent state and can be enabled per Project. Configuration establishes the ownership/version seam; no-tool execution proves the Run/Temporal/model path; read-only MCP proves controlled domain access; hardening proves cancellation/recovery/operability. No slice introduces Sessions or mutating tools.

Open model/MCP/production thresholds do not block local contract implementation. They gate the corresponding real-environment acceptance or production rollout explicitly.

## Dependency Map

```text
SLICE-001 Coordinator contract and immutable versions
    └── SLICE-002 Direct no-tool Run + Temporal + one-turn agent
            └── SLICE-003 Allowlisted read-only system MCP
                    └── SLICE-004 Cancellation, reconciliation, and rollout hardening
```

External readiness gates:

- SLICE-001: confirm logical ownership/physical packaging and database migration ownership.
- SLICE-002: Temporal test/dev environment plus one tool-capable Ollama-compatible model for environment acceptance.
- SLICE-003: system MCP owner confirms `get_project` or equivalent read-only schema and workload audience.
- SLICE-004: operations defines production thresholds before broad enablement.

## Slice Inventory

| Slice | Observable result | Dependencies | Requirements | Status |
|---|---|---|---|---|
| [SLICE-001](#slice-001-configure-one-versioned-core-agent) | Admin creates/reads/revises one immutable-version coordinator | Ownership/package review; planned schema | REQ-001, REQ-003, REQ-010 | Ready for implementation planning |
| [SLICE-002](#slice-002-complete-a-sessionless-no-tool-run) | Caller starts/polls a durable no-tool Run and gets a result | SLICE-001; Temporal; model adapter/fixture | REQ-002–005, REQ-007, REQ-009, REQ-010 | Planned |
| [SLICE-003](#slice-003-complete-a-run-through-read-only-mcp) | Agent reads Project data through an allowlisted system MCP and completes | SLICE-002; confirmed MCP contract/auth | REQ-005–007, REQ-009, REQ-010 | Planned |
| [SLICE-004](#slice-004-cancel-recover-and-operate-runs) | Runs cancel/recover/reconcile safely with rollout evidence | SLICE-003; operations thresholds for production | REQ-004, REQ-007–010 | Planned |

## Requirement Coverage

| Requirement | Scenarios | Acceptance | Delivery slices |
|---|---|---|---|
| REQ-001 | SCN-001 | AC-001 | SLICE-001 |
| REQ-002 | SCN-002 | AC-002 | SLICE-002 |
| REQ-003 | SCN-001/002 | AC-003 | SLICE-001/002 |
| REQ-004 | SCN-005 | AC-004 | SLICE-002/004 |
| REQ-005 | SCN-002/003 | AC-005 | SLICE-002/003 |
| REQ-006 | SCN-003/004 | AC-006 | SLICE-003 |
| REQ-007 | SCN-002/003 | AC-007 | SLICE-002/003/004 |
| REQ-008 | SCN-005/006 | AC-008 | SLICE-004 |
| REQ-009 | SCN-004/005 | AC-009 | SLICE-002–004 |
| REQ-010 | SCN-001/004 | AC-010 | SLICE-001–004 |

## Quality Requirement Coverage

| Quality requirement | Delivery evidence |
|---|---|
| NFR-001 | SLICE-002 replay/restart baseline; SLICE-004 cross-boundary failure injection |
| NFR-002 | Security/redaction checks in every slice; full matrix in SLICE-004 |
| NFR-003 | Boundary tests in SLICE-002/003 and development load probe in SLICE-004 |
| NFR-004 | Baseline metrics in SLICE-002/003 and dashboards/runbook drills in SLICE-004 |
| NFR-005 | Versioned contracts from SLICE-001 onward; upgrade/rollback replay evidence in SLICE-004 |

## SLICE-001: Configure one versioned core agent

### Outcome

An authorized Project admin can create, read, and replace one always-active coordinator through API-001/API-002. Each change creates an immutable version; concurrent/stale/duplicate writes are safe. There is still no Run execution.

### Dependencies

- DEC-001, DEC-002, and DEC-006 accepted.
- Root and `backend/AGENTS.md` conventions read before implementation.
- Architecture owner confirms whether the logical `ncn-agents` module is co-located in the current image or a separate deployable; either choice preserves owner boundaries.
- A migration-owning workflow prepares the planned DATA-001/002/009/010 schema. The repository `backend-plan-develop` workflow must not generate/run table migrations itself.
- Model/tool catalogs may use controlled deployment seed/configuration for the first slice; no network execution is required.

### In Scope

- Product: one coordinator, active-only, immutable AgentVersion, exact field validation.
- API: API-001/002, common authz/errors/idempotency/ETag semantics.
- Data: DATA-001/002/009/010 constraints, canonical configuration hash, transactions.
- Security: `ncn-authz` decision, Project-scoped repositories, no credential fields/responses.
- Operations: configuration audit/log metrics and database health.
- Compatibility: document that existing frontend Agent HTTP routes/data are not silently compatible.

### Out of Scope

Runs, Temporal, model calls, MCP network calls, workers, archive/disable, frontend adapters/UI, bulk/list Agent APIs, and importing browser mock data.

### Implementation Surfaces

| Surface | Status | Expected responsibility-level change |
|---|---|---|
| Root `AGENTS.md`; `backend/AGENTS.md` | **Present** | Instruction source; no feature behavior change |
| `backend/api/router/`, `backend/api/managers/`, `backend/api/db/` | **Present packages; planned modules** | Add `ncn-agents` configuration route/business/repository boundaries and register them through existing hubs |
| `backend/models/pydantic/api/`, `backend/models/pydantic/dto/`, `backend/models/sqlalchemy/`, `backend/models/enum/` | **Present packages; planned models** | Add strict API/DTO/persistence/version/status contracts |
| `backend/migrations/postgres/` | **Present migration infrastructure; migration planned separately** | Add schema/constraints through the repository-approved migration workflow, not ad hoc runtime DDL |
| `backend/tests/unit/`; planned integration/contract test locations | **Present/planned** | Add validation, manager transaction, repository constraint, authz, idempotency, and concurrency evidence |
| `docs/**` and agent contracts | **Present; updates planned on landing** | Reconcile implemented routes/data/project map without changing this feature's authority prematurely |

Exact new module names are selected by the backend workflow after comparing neighboring modules/templates; this plan does not claim unverified symbols are present.

### Contract Changes

Satisfies REQ-001/003/010, SCN-001, API-001/002, DATA-001/002/009/010, DEC-002/006, and AC-001/003/010 for configuration behavior.

### Validation

- Unit: strict field/null/unknown-field/bound validation; canonical hashing; status invariants.
- Manager/repository integration: first create, replace, immutable old version, ETag conflict, uniqueness race, same/different idempotency payload, transaction rollback.
- Authorization/security: missing permission, cross-Project lookup, forged IDs, safe response/log/audit redaction.
- Schema/migration: clean apply through migration workflow, constraints/indexes, rollback compatibility plan, no browser-local backfill.
- Manual API: configure/read/reconfigure and inspect stable IDs/ETags/audit metadata.

### Acceptance Criteria

- REQ-001/SCN-001/AC-001 passes for create/read/replace and concurrent create.
- REQ-003/AC-003 evidence shows an immutable AgentVersion is ready to snapshot; no current-pointer update mutates old content.
- REQ-010/AC-010 cross-Project and permission requests fail closed with no secret/instruction leakage in default response/logs.

### Rollout and Rollback

Deploy schema first, then code/routes disabled, then enable configuration for a test Project. Stop on uniqueness, authz, or audit anomalies. Rollback disables API-001 writes and retains API-002/read-compatible schema and immutable versions; do not drop data in the same rollback.

### Documentation Updates

On implementation, update repository docs/project map, implemented backend routes/data documentation, relevant agent contract status, configuration frontend compatibility note, and operator schema/runbook index.

## SLICE-002: Complete a sessionless no-tool Run

### Outcome

An authorized caller posts one objective, receives `202` and a Run ID with no Session/Message, observes ordered states/events, and gets a schema-valid no-tool result from one durable root Temporal Workflow. A worker restart does not duplicate or lose the Run.

### Dependencies

- SLICE-001 complete.
- DEC-001, DEC-004, DEC-005, DEC-007 accepted for implementation.
- Temporal service/test environment and worker task queue available.
- Agents SDK/Temporal dependency versions selected from implementation-time compatibility review.
- Deterministic fake model required for tests; exact real Ollama model is only an environment-acceptance blocker.

### In Scope

- Product/API: API-003–006; `QUEUED/RUNNING/RETRYING/COMPLETED/PARTIALLY_COMPLETED/FAILED`; result/usage/event polling.
- Agent: construct one coordinator SDK Agent per turn; strict API-010 final/tool action; no direct SDK tools in this slice.
- Temporal: API-008 root Workflow, one-turn model/persistence Activities, stable IDs, finite retry/repair/limits, replay compatibility.
- Data: DATA-003/004/006–009 plus Run acceptance/terminal transactions.
- Security: snapshot server-owned authz/config/limits; objective/instructions/provider data redaction.
- Operations: dispatcher/reconciler START path, readiness, Run/model/dispatch metrics.

### Out of Scope

MCP execution (a tool action may be rejected/fixture-disabled), cancellation API, real worker delegation, Session/Message, model fallback, prices/quotas, token streaming, frontend.

### Implementation Surfaces

| Surface | Status | Expected responsibility-level change |
|---|---|---|
| `backend/pyproject.toml` | **Present** | Add pinned-compatible Temporal/Agents SDK/model-client/schema dependencies through approved dependency workflow |
| Existing backend lifecycle/service-hub/health/metrics packages | **Present; integration planned** | Register Temporal client/worker, model adapter, dispatcher/reconciler, readiness/metrics |
| Existing router/manager/db/model packages | **Present; planned modules** | Add Run APIs, projection, idempotency, dispatch, operations, usage, events |
| Planned `ncn-agents` Temporal/runtime modules | **Planned** | Define versioned Workflow/Activity contracts and the bounded loop |
| Planned migrations for DATA-003/004/006–009 | **Planned separately** | Add Run product/operational schema before enablement |
| `backend/tests/unit/` plus planned integration/Temporal tests | **Present/planned** | Add API, transaction, replay, retry, repair, limit, restart, redaction tests |

### Contract Changes

Satisfies REQ-002–005, REQ-007, REQ-009/010 for SCN-002 and the no-tool/restart portion of SCN-005: API-003–006/008/010; DATA-003/004/006–009; AC-002–005/007/009/010.

### Validation

- API: async `202`, Location, idempotent duplicate/conflict, objective bounds, status/list/event pagination, Project authz.
- Agent adapter: exact final/tool union, unknown fields, invalid output + two repairs, provider error normalization, no SDK Session/handoff/MCP transport.
- Temporal: deterministic replay, time-skipping limits, retry policy, Activity cancellation behavior, Workflow ID collision, worker restart at before/after persistence boundaries.
- Persistence: atomic Run/snapshot/event/dispatch; stable event/usage/operation IDs; single terminal transition; queued dispatch reconciliation.
- Security: no credentials/raw prompts/provider responses/reasoning in snapshot/history/logs/API; snapshot ignores caller override attempts.
- Performance smoke: API p95 target at assumed concurrency using fake model; event query/index plan.
- Manual environment: one real no-tool model Run after model owner provides a capable deployment.

### Acceptance Criteria

- REQ-002/SCN-002/AC-002 returns one direct Run without Session/Message fields and reaches `COMPLETED` through polling.
- REQ-003/AC-003 proves reconfiguration after acceptance does not alter Workflow input/result metadata.
- REQ-004/SCN-005/AC-004 proves replay/worker restart with the same Workflow ID and no duplicate logical results.
- REQ-005/AC-005 proves bounded valid final output and controlled invalid-output failure.
- REQ-007/AC-007 reads all product evidence from PostgreSQL.
- REQ-009/010 limits and redaction tests pass.

### Rollout and Rollback

Deploy schema/dependencies, worker disabled, then API/read projections, then worker/dispatcher for one test Project. Begin with deterministic/stub model in non-production and a real model capability probe. Stop on dispatch backlog, replay nondeterminism, duplicate operations, terminal mismatch, or redaction failure. Rollback disables new starts, drains/cancels active Workflows, leaves reads/schema, and keeps a replay-compatible worker until histories are terminal/expired.

### Documentation Updates

Document implemented Run routes/data, Temporal worker lifecycle/task queue, model adapter configuration, dispatcher/reconciliation runbook, metrics, and verified test commands/results.

## SLICE-003: Complete a Run through read-only MCP

### Outcome

A direct Run requests the approved Project read tool, passes deterministic policy/schema/Project checks, calls the system MCP with workload identity, returns the validated result to the next model turn, and completes. Invalid/unassigned/mutating calls create no outbound request.

### Dependencies

- SLICE-002 complete.
- DEC-003 confirmed with exact MCP owner/tool/schema/audience.
- System MCP deployment and OAuth2 Proxy/Keycloak workload flow available, or an equivalent contract test fixture for automated checks.
- DATA-005 migration available and API-009 discovery snapshot seeded/verified.

### In Scope

- API-009 tool discovery/version/hash and `get_project` call.
- Coordinator allowlist validation during API-001/new AgentVersion and Run snapshot.
- API-008 preparation/policy and MCP Activities; ordered API-010 tool calls; safe tool feedback to model.
- DATA-005 and related events/audit/operation records.
- Audience-specific in-memory token acquisition, schema validation, output bounds, retry/timeout normalization, Project context construction.
- MCP readiness, metrics, schema-mismatch blocking, and denial tests.

### Out of Scope

MCP writes, Approval, idempotency keys for external writes, reconciliation of unknown side effects, public/user MCP, API key/Basic Auth, arbitrary egress/SSRF controls, OAuth user flow, parallel tools, direct domain data persistence.

### Implementation Surfaces

| Surface | Status | Expected responsibility-level change |
|---|---|---|
| Planned `ncn-agents` MCP catalog/gateway/policy modules | **Planned** | Discovery snapshot, allowlist/risk/schema checks, token provider, protocol call/normalization |
| Planned Temporal runtime modules from SLICE-002 | **Planned by prior slice** | Add prepare/execute Activity steps and sequential tool-result feedback |
| Existing configuration/Run models and APIs from prior slices | **Planned by prior slices** | Add tool snapshot, ToolExecution, events, safe errors/read model |
| Keycloak/OAuth2 Proxy/system MCP deployment configuration | **Approved infrastructure; integration planned** | Add audience/client/endpoint via secrets/config without runtime credential persistence |
| Planned MCP mock/contract tests | **Planned** | Assert discovery, schemas, auth, context, retries, zero-call denial, size/redaction |

### Contract Changes

Satisfies REQ-005–007/009/010 for SCN-003/004: API-008–010, DATA-002/003/005/008/010, DEC-003/006/007, AC-005–007/009/010.

### Validation

- Discovery: canonical name, stable schema hash/version, schema change blocks new configuration/Run use.
- Policy: allowed read succeeds; unknown/unassigned/mutating/forged-Project/over-limit/invalid-arguments calls stop before outbound I/O.
- Auth: correct audience token accepted; wrong/expired token normalized; refresh retry bounded; credentials absent from persistence/history/logs/model.
- MCP contract: real or protocol-accurate mock validates request/output schema, empty result, timeout/429/retry, malformed/oversized response.
- Temporal/replay: multiple returned tool calls run sequentially with stable logical IDs; Activity retry does not duplicate local records.
- End-to-end: deterministic model requests `get_project`, consumes returned data, and creates a valid final result/events/usage.

### Acceptance Criteria

- REQ-005/SCN-003/AC-005 completes one model→tool→model loop within bounds.
- REQ-006/SCN-003/004/AC-006 proves all allowlist/schema/Project/risk/limit guards and zero outbound denial.
- REQ-007/AC-007 exposes safe ToolExecution/events/usage in PostgreSQL.
- REQ-009/010/AC-009/010 proves retry exhaustion, output limits, workload auth, and redaction.

### Rollout and Rollback

Deploy catalog/gateway disabled, validate discovery/auth/read call out-of-band, bind the tool to a test coordinator version, then enable MCP Runs for one Project. Stop on schema drift, auth anomaly, cross-Project evidence, unexpected mutation/risk, response overflow, or retry spike. Rollback creates a new coordinator version without the tool and disables new MCP Runs; active snapshots may drain only if the compatible read schema remains available, otherwise fail safely.

### Documentation Updates

Publish the implemented MCP owner/tool/schema/audience contract, configuration/run mapping, token/readiness configuration, schema-drift and outage runbooks, security test evidence, and responsible owner contacts.

## SLICE-004: Cancel, recover, and operate Runs

### Outcome

Authorized callers cancel active Runs; dispatch and cancellation survive API/worker/dependency interruption; Runs reach one terminal state with complete safe evidence; operators have rollout/rollback signals and runbooks.

### Dependencies

- SLICE-003 complete.
- Production threshold decisions are required only before enabling beyond test Projects.
- Operations owner can observe PostgreSQL, Temporal worker, model, MCP auth/schema, dispatcher, metrics, and logs.

### In Scope

- API-007 and `CANCELLING/CANCELLED` state/event/audit semantics.
- CANCEL RunDispatch delivery/reconciliation and stuck cancellation detection.
- Failure injection across commit/start/model/MCP/persistence/cancel/worker-restart boundaries.
- State/data-quality reconciliation, retry exhaustion, single terminal guard, redaction audit.
- Readiness/degraded read behavior, dashboards/alerts, capacity probe, retention/backup/restore configuration, Project allowlist rollout, compatible rollback.
- Cross-slice regression and final documentation reconciliation.

### Out of Scope

Pause/resume, user input/Approval signals, manual status edits, Run retry-as-new, mutating tool reconciliation, Session cancellation semantics, auto-scaling architecture, Kafka, production microservice decomposition.

### Implementation Surfaces

| Surface | Status | Expected responsibility-level change |
|---|---|---|
| Run HTTP/manager/repository/runtime modules from prior slices | **Planned by prior slices** | Add cancellation command, conditional states, signal/cancel handling, terminal evidence |
| Dispatcher/reconciler and service lifecycle | **Planned by prior slices** | Add CANCEL delivery, leases, stale-state/data-quality repair, graceful startup/shutdown |
| Existing Prometheus/logging/health infrastructure | **Present; extension planned** | Add bounded labels, metrics, readiness components, alert inputs, redaction |
| Planned Temporal/integration/security/load tests | **Planned** | Add restart/race/outage/cancel/failure-injection/capacity/restore evidence |
| Deployment configuration/runbooks/docs | **Planned** | Project enablement, thresholds, incident response, rollback, retention |

### Contract Changes

Completes REQ-004/007–010 and SCN-005/006 across API-004–009, DATA-003–010, DEC-004/005/006, AC-004/007–010.

### Validation

- Cancellation: queued/running/retrying races, duplicate/different keys, terminal conflict, in-flight model/MCP cancellation/timeout, delivery outage/restart.
- Recovery: crash before/after Run commit, Workflow start, Activity side effect, event/usage/tool result, terminal commit, Activity acknowledgment.
- Invariants: one Workflow, one terminal transition, stable snapshot/operation IDs, no new work after cancel command, no direct domain access.
- Security: cross-Project/read/cancel permission matrix, forged context, audit separation, log/history/database/API credential/payload scan.
- Operations: readiness degradation, dispatch/cancel lag alerts, retry/failure metrics, dashboard/runbook drill, backup/restore rehearsal for product data and compatible Workflow recovery.
- Performance: API p95 and 20 concurrent development Run probe; set measured production gates before broad rollout.
- Full E2E: SCN-001–006 on real/test Temporal with deterministic model/MCP, plus real model/MCP smoke.

### Acceptance Criteria

- REQ-008/SCN-006/AC-008 reaches `CANCELLED` once and schedules no new work after the durable command.
- REQ-004/SCN-005/AC-004 passes replay/restart at all critical boundaries.
- REQ-007/AC-007 data-quality checks show complete product evidence independent of Temporal query access.
- REQ-009/AC-009 finite retries/limits/cancellation latency/backpressure are verified.
- REQ-010/AC-010 authorization, Project isolation, trusted context, and redaction evidence passes.

### Rollout and Rollback

Enable cancellation/reconciliation first for test Projects, conduct failure drills, then expand a Project allowlist while watching dispatch age, active/terminal mismatch, failure/retry rate, MCP/model latency, and cancellation lag. Stop new Run starts on any isolation, replay nondeterminism, duplicate logical effect, missing terminal evidence, or secret leak. Rollback keeps a compatible worker/read API until active histories terminalize, then disables worker/dispatcher; schema/data remain until retention/cleanup is separately approved.

### Documentation Updates

Finalize repository maps, implemented API/data/architecture contracts, health/metrics dashboards, operations/security runbooks, retention/backup/restore policy, rollout history, and this package's status/remaining open questions.

## Cross-Slice Validation

- Trace every REQ-001–010 to its scenario, interface/data contract, acceptance criterion, and at least one passing test in the slice matrix.
- Run unit, manager/repository integration, HTTP contract, Temporal replay/time-skipping, model adapter, MCP mock/real contract, authorization/security/redaction, failure-injection, and development-load checks.
- Verify root/nearest `AGENTS.md`, backend layered architecture, registration hubs, and bounded-service ownership in review.
- Confirm no Session/Message/worker/Approval/memory/artifact/Kafka/frontend behavior or dependency entered accidentally.
- Confirm active snapshots/histories remain readable/replayable across upgrade and rollback.
- Re-run this package validator after implementation-driven documentation updates.

## Completion Gate

The feature is complete only when:

1. SCN-001–006 and AC-001–010 pass with evidence.
2. INV-001–008 have automated enforcement or explicit review evidence.
3. The real/test Temporal restart path and real system MCP read smoke pass.
4. The exact model and MCP acceptance choices are recorded; production thresholds are resolved before broad rollout.
5. No blocking open decision remains for the enabled environment.
6. Rollout, rollback, security, dispatch, cancellation, and dependency-outage runbooks are exercised.
7. Repository documentation reflects implemented—not merely planned—paths and validation results.

The first safe delivery slice is SLICE-001. Implementation should use `backend-plan-develop` after re-reading `backend/AGENTS.md`; schema migrations require the repository-approved migration workflow because that skill explicitly does not create them.
