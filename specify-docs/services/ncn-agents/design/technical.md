# ncn-agents Technical Design

## Context and Status

**Present:** Vue agent list/settings, FastAPI config router/manager/repository, Pydantic models, `pms_agents` SQLAlchemy table, Sessions placeholder route. **Planned/confirmed design:** modular agent service, Session/Run APIs, Temporal worker, model gateway, MCP/tool gateway, Approval, memory/artifacts, usage/audit/events. Independent deployment and target tables are not verified.

## Components and Responsibilities

| Component/boundary | Status | Responsibility | Inputs/outputs | Owns |
|---|---|---|---|---|
| Agent config API/manager/repository | Present transitional | List/create/update/status with permission/version guards | Config DTOs | Transitional `pms_agents` row |
| Common `ncn-authz` boundary | Present dependency | Resolve persisted actor/project role and authorize named agent actions | API-AUTHZ-003 → Actor/decision | User/ProjectUser/policy, not agent state |
| Session/Run API | Planned | Messages, Run start/read/cancel, approvals, artifacts | API-AGT-003..006 | Product-visible execution state |
| Run orchestrator | Planned | Snapshot, plan validation/revision, node lifecycle | Temporal signals/activities | Run semantics |
| Temporal worker | Planned | Durable deterministic workflow and Activities | Workflow history/activity results | Progress, not business truth |
| Model gateway | Planned | Provider-neutral messages/tools/structured output/usage/errors | Ollama adapters | No domain truth |
| Context/memory module | Planned | Minimized context, ingestion metadata and project-scoped cited recall | PostgreSQL/Qdrant ports | Memory metadata/derived index, not PMS truth |
| Tool/MCP gateway | Planned | Discovery, common authz consumption, agent constraints, Approval, client command identity, invocation/reconciliation | PMS and future external owner tools | Tool execution records |
| Artifact/usage/audit modules | Planned | Metadata, budgets, result/audit evidence | Object storage/metrics/events | Agent-owned metadata |

## End-to-End Flows

Configuration flow: common persisted actor/admin action → current HTTP CRUD/status with JSON `expected_version` → agent-domain validation/transaction. Run flow: common actor/action → transactionally store Message/Run/snapshot → start one Temporal workflow → build context → model coordinator plan → validate/store revision → execute bounded worker/tool/approval nodes in Activities/durable waits → persist progress/result/usage/audit → expose canonical state through the Run API. Async service calls propagate project scope and Session/Run/node/tool/event plus causation IDs.

## State Ownership and Consistency

Agent PostgreSQL is authoritative for config, snapshots, Sessions, Messages, Runs, plan revisions, invocations, tool/approval records, usage, audit, memory metadata and artifact metadata; authz PostgreSQL remains authoritative for User/ProjectUser. Temporal is authoritative only for workflow progress/replay. Qdrant is an agent-owned derived index; MinIO/S3 stores bytes. The Run create transaction prevents missing initial state; terminal/approval/client-command transitions are unique/atomic. API and workflow state reconcile after failures.

## Dependencies and Integrations

Common `ncn-authz`, PMS project references and owner API/MCP tools, Temporal, PostgreSQL, Ollama/model/embedding adapters, Qdrant, MinIO/S3 and the current frontend. External MCP providers are deferred. Each runtime dependency has timeout, retry class, circuit/backpressure, compatibility and degraded result behavior.

## Security Boundaries

Project isolation is mandatory in common authz, API, repository, workflow ID, activity input, memory query, tool request, event, and artifact reference. Model input/output is untrusted. Common actor/action plus agent/tool constraints are rechecked immediately before action; Approval is distinct. Tool allowlist/schema is snapshotted or version referenced. Secret plaintext exists only inside narrow invocation adapter and is zeroized/not logged. Context and logs exclude secrets and unbounded raw prompts.

## Failure Isolation and Recovery

Workflow code stays deterministic; I/O is Activity. Retry profiles differ for model/read, idempotent mutation, non-idempotent mutation, storage, extraction, and embeddings. Structured output repairs at most twice. Durable signals handle input/approval/cancel. Unknown mutation outcomes are reconciled. Hard limits stop future work and form a partial/failure envelope. Temporal/API mismatches are detected by reconciliation job. Backups cover PostgreSQL/object metadata/content; workflows are recoverable by Temporal.

## Observability and Operations

Health covers authz dependency, API, DB, Temporal connectivity/task queue, model, memory index, tool registry and object storage with critical/degraded distinctions. Metrics: Run start/terminal/state age, workflow task/activity failures, node/model/tool latency, retries/repairs, approval age, cancellation, tokens/cost/budget, reconciliation, project denials and audit persistence. Synchronous logs use persisted user UUID; execution evidence uses Session/Run/node/tool/event IDs and redacts content. Audit is separate from progress.

## Performance and Scale

Hard configurable limits exist from first release: plan nodes/revisions, worker depth/count, parallelism, tool calls, duration, tokens, money, context, artifact size. Exact values, concurrent Run load, API p95, progress lag, storage volume and Continue-As-New policy are Open before production.

## Runtime, Compatibility, and Evolution

Target deployment has agent API plus one or more Temporal workers and modular adapters. MVP may remain one service process boundary, but module ports permit later extraction without semantic change. APIs/events/snapshots/schema are versioned. Workflow code changes follow Temporal compatibility/versioning. Data extraction from `pms_agents` uses expand/backfill/dual-read or compatibility facade/switch/verify/contract; dual write is time-bounded and reconciled.

## Alternatives

Nested workers, direct domain DB access, model-decided permissions, polling approvals, global retry, mutable Run configs/plans, Qdrant as primary store, and premature universal plugin framework are rejected by agent invariants.

## Traceability

AGT-REQ-001..006; AGT-INV-001..009; SCN-001..003; API/MODEL/TABLE-AGT; DEC-AGT-001..004.
