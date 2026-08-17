# Implementation checklist

## Checklist

### 1. Align mandatory contracts and environments

- [ ] Revise `contracts/agents/README.md` and `contracts/agents/02-invariants/{00-contract-status,01-product-boundaries,02-components-and-agent-model,03-session-run-and-plan,04-durable-tools-and-security,06-data-deployment-and-readiness,08-design-boundary-and-change-rules}.md`: define this sessionless single-turn core, retain one root Temporal Workflow, make Kafka/Debezium mandatory, and move Sessions, crew delegation, MCP, approvals, memory, artifacts, and advanced planning to roadmap. Verify links and remove conflicting “Kafka optional” or deferred-Temporal language.
- [ ] Resolve and document target Kafka, Schema Registry, Debezium Connect endpoint/credentials, Temporal namespace/endpoint, OpenAI-compatible model, and secret ownership. Prove connectivity with redacted bounded probes; unresolved infrastructure blocks connector migration, integration, and enablement but not generated-config or typed fake tests.

### 2. Establish atomic PostgreSQL and CDC contracts

- [ ] Add `AgentRunStatus`, API/DTO models, `agent_runs`/`agent_run_events` SQLAlchemy mappings, stream package exports, and terminal/event constraints under `backend/models/`; verify strict model construction, redaction shape, and registration in `backend/tests/unit/{test_agent_runs,test_models_and_wiring}.py`.
- [ ] Create reviewed Alembic revisions through the repository-approved migration workflow for Run/event tables, required indexes/foreign keys/checks, filtered-publication prerequisites, and `debezium_heartbeat` when absent. Verify clean upgrade and isolated downgrade; keep migration creation outside workflows that forbid it.
- [ ] Add atomic `accept_run`, scoped read, conditional transition, and idempotent event insertion in `backend/api/db/{agent_runs,agent_run_events}.py` plus `backend/api/db/db.py`. Verify Run and `run.requested` commit/rollback together, `(run_id,event_key)` deduplicates replay, and no row locks or terminal overwrites exist.

### 3. Make `cp_debezium` and Kafka the committed dispatch boundary

- [ ] Add `DB_SCHEMA`, Kafka/Schema Registry/Connect/group/topic/min-ISR settings and direct pinned Kafka dependencies; configure `Services.broker` and its lifecycle without using `produce` for Run dispatch. Verify stream registration happens before broker start and start/stop/ping/readiness behavior is bounded.
- [ ] Add `backend/migrations/kafka_connect/{connectors,migrate}.py`. Extend `DebeziumPostgresConnectorConfig` with the service database/Kafka settings, heartbeat table, `ExportAgentRunEventsConnectorConfigV0`, explicit `agent_run_events` table and safe-column allowlists, and exported `CONNECTORS`; the migration entry point reconciles these definitions through Kafka Connect. Unit-test `to_json()` for schema qualification, connector/slot/publication/topic version `0`, inherited `pgoutput`/RegexRouter/retry/topic defaults, heartbeat columns, secrets-by-setting, and exclusion of objective/snapshot/instructions/result/credentials.
- [ ] Define only the typed `AgentRunEventCDC` selected-row model in `backend/models/pydantic/stream/agent_run_stream.py`; reuse `BaseDebeziumCDCModel`, `DeleteDebeziumCDCModel`, and `DebeziumCDCHandler` instead of defining an agent-specific envelope or operation router. Add `DebeziumAgentRunEventsHandler`: `on_create` dispatches only `run.requested`, while `on_update`/`on_delete` record an append-only invariant violation and never dispatch. Verify callback annotation construction, `c` and snapshot `r` equivalence, lifecycle-event filtering, safe `u/d` handling, handler retries, and redaction.
- [ ] Add the thin `backend/api/stream/agent_runs.py` listener with `@Services.broker.listen(topic=AgentRunEventCDC.Meta.topic)` and `BaseDebeziumCDCModel`, then export it through the stream hub. It delegates to `DebeziumAgentRunEventsHandler.process()`; verify handler failure prevents offset commit, Temporal start/already-started permits commit, redelivery is duplicate-safe, tombstones are harmless, and the physical topic is `{KAFKA_TOPIC_PREFIX}.debezium.cdc.agent_run_events.0` with no Python producer.
- [ ] Apply the Kafka Connect migration against the integration stack with worker-level Avro converters and Schema Registry configuration. Verify committed requested and lifecycle rows reach the versioned topic, only requested rows start Workflows, connector heartbeat/lag is monitored, and CDC values contain none of the forbidden Run/model content.

### 4. Execute every Run through Temporal

- [ ] Add pinned Temporal SDK dependency and `backend/api/services/temporal_runtime.py` owning client/worker lifecycle for namespace configuration, task queue `agent-core`, and Workflow registration. Verify start/stop/ping, duplicate Workflow ID normalization, graceful shutdown, and service-hub readiness.
- [ ] Implement ID-only contracts and deterministic `AgentRunWorkflow` in planned `backend/api/workflows/agent_runs.py`, with bounded `mark_running`, `invoke_model`, and `fail_run` Activities in `backend/api/activities/agent_runs.py`. Verify replay/time-skipping, 10-minute Workflow timeout, exact retry policies, non-retryable invalid output, and absence of I/O in Workflow code.
- [ ] Implement the OpenAI-compatible gateway in `backend/api/services/agent_model.py`; the model Activity must load and close DB state before I/O, then conditionally persist result/event in a new transaction. Verify output/token/byte bounds, safe error mapping, terminal fast-return on Activity replay, and the documented response-before-commit duplicate-inference edge.
- [ ] Add POST/GET routes and `AgentRunsManager` registration across API/manager/router/model hubs. POST returns `202`/`Location` after atomic acceptance only; GET polls PostgreSQL; verify exact UUID replay, mismatched conflict, snapshot stability after agent edit, and no synchronous model/Temporal bypass.

### 5. Close recovery, security, and operations

- [ ] Add project-scoped authorization tests for admin/member/viewer, non-member hiding, cross-project IDs, archived start denial, historical GET, missing coordinator, disabled/unready runtime, and zero downstream work on rejection. Verify Kafka/Temporal/model are untouched before accepted commit.
- [ ] Add failure-injection integration tests for DB rollback, Debezium/Kafka outage and recovery, CDC snapshot replay, consumer crash before/after Workflow start and offset commit, Temporal outage, worker restart, Activity acknowledgement loss, persistence retry, and terminal conflicts. Verify one Workflow ID and one logical terminal result/event.
- [ ] Extend metrics, structured logs, `/healthcheck`, and deployment monitoring for Kafka consumer, Debezium lag, Temporal worker/client, queued/running age, Activity/model retries, and terminal outcomes. Verify bounded labels and automated scans of Kafka, Temporal history, logs, and API errors for forbidden content/secrets.

### 6. Validate rollout and canonical documentation

- [ ] Run the mandatory migration-backed fake-model E2E through PostgreSQL, real/protocol-accurate Debezium, Kafka/Schema Registry, and Temporal test/runtime; record commands and prove there is no direct dispatch bypass, Python producer, Session, MCP, approval, memory, worker delegation, automation, or frontend dependency.
- [ ] Run one non-production real-model smoke plus Kafka/consumer/Temporal-worker restart drills. Confirm polling reaches one terminal Run, replay remains idempotent, telemetry is redacted, and all readiness/lag gates pass before enabling the pilot.
- [ ] Update `docs/README.md`, `docs/architecture.md`, `docs/backend/{README,runtime,api,flows}.md`, add `docs/backend/services/agents/{README,api,flows}.md`, and revise PMS/session pages for the configuration handoff and no-UI boundary. Verify all navigation and relative links.
- [ ] Add `docs/database/tables/{agent_runs,agent_run_events}.md`, update database relationships/indexes, and reconcile `contracts/agents/**` with verified behavior, CDC schema, topic/group, task queue, retry policies, runbooks, and remaining roadmap. Rerun the feature validator.

## Completion criteria

- [ ] Every in-scope requirement and acceptance criterion in [README.md](README.md) has implementation and recorded verification evidence.
- [ ] Kafka/Debezium, Temporal, and model environment blockers are resolved for enablement; no synchronous fallback is accepted.
- [ ] Migration, API, CDC/Kafka contract, Temporal replay/restart, authorization/redaction, fake-model E2E, and real-model smoke checks pass.
- [ ] Canonical documentation describes implemented durability, at-least-once/idempotency limits, lifecycle/readiness, rollback, and deferred capabilities accurately.
