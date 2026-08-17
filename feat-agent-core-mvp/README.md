# Feature: Agent Core MVP

Give authenticated project members one backend-only way to submit an objective to the configured project coordinator and poll a durable result. The smallest acceptable core uses PostgreSQL for product state, Kafka/Debezium for committed Run dispatch and lifecycle integration, and Temporal for execution and recovery; crew delegation, tools, memory, and Sessions remain later features.

## Goal

An active project can complete and later read a single-turn coordinator Run through the existing FastAPI application. The implementation must prove project isolation, atomic acceptance, at-least-once Kafka delivery with idempotent Temporal start, workflow replay/retry, bounded provider I/O, and a Run contract that future crew orchestration can extend without replacing its execution foundation.

## Current behavior

- Project creation provisions one active coordinator and the PMS layers support coordinator/worker configuration and optimistic updates ([PMS service](../docs/backend/services/pms/README.md), [`AgentsManager`](../backend/api/managers/agents.py), [`pms_agents`](../backend/models/sqlalchemy/agents.py)).
- The agent and session pages do not execute agents; the Sessions page is a static placeholder ([Agents page](../docs/frontend/pages/pms/agents.md), [Sessions page](../docs/frontend/pages/pms/sessions.md)).
- The backend already contains reusable Kafka/Schema Registry and Debezium libraries, including versioned PostgreSQL connector configuration, CDC envelope models, operation-aware handlers, and listener registration. Agent-core has not yet registered a connector, event-row model/handler/listener, model client, Temporal worker, Run model, or Run route ([platform architecture](../docs/architecture.md), [`cp_kafka`](../backend/libs/cp_kafka/kafka.py), [`cp_debezium`](../backend/libs/cp_debezium), [`backend/pyproject.toml`](../backend/pyproject.toml)).
- The forecasting contract already requires one root Temporal Workflow per Run and PostgreSQL-first state, but currently permits Kafka/Debezium to arrive later ([durable execution](../contracts/agents/02-invariants/04-durable-tools-and-security.md), [deployment](../contracts/agents/02-invariants/06-data-deployment-and-readiness.md)). This plan keeps Temporal and makes Kafka/Debezium mandatory while narrowing unrelated capabilities.

## Target behavior

- `POST /api/v1/workspaces/{workspace_slug}/projects/{project_id}/agent-runs` accepts a client-generated UUID and trimmed 1–8000 character objective. In one transaction it snapshots the active coordinator, inserts a `queued` Run, and appends a safe `run.requested` domain event; it returns `202` with the Run and `Location` for polling.
- A versioned Kafka Connect migration built with `DebeziumPostgresConnectorConfig` publishes committed `agent_run_events` rows to `{KAFKA_TOPIC_PREFIX}.debezium.cdc.agent_run_events.0`. Its explicit column allowlist excludes all user/model content. No router, manager, or Python outbox publisher dual-writes to Kafka.
- A `BaseDebeziumCDCModel` listener delegates to an `AgentRunEventCDC` row handler derived from `DebeziumCDCHandler`. The handler dispatches only created or snapshot-read `run.requested` rows, derives Workflow ID `run:{run_id}`, and starts `AgentRunWorkflow` on Temporal task queue `agent-core`. The broker commits its Kafka offset only after the handler returns following Temporal start or same-Workflow confirmation.
- The deterministic Workflow schedules Activities that conditionally mark the Run `running`, perform one bounded coordinator model invocation, and persist exactly one `completed` or `failed` product result plus safe lifecycle events. PostgreSQL remains the API source of truth; Temporal history contains IDs and safe outcomes, not objectives, instructions, credentials, or raw provider payloads.
- `GET .../agent-runs/{run_id}` returns `queued`, `running`, `completed`, or `failed`. Repeating the same create UUID/input returns the existing Run without a second event; a different input with that UUID returns `RUN_ID_CONFLICT`.
- Kafka, consumer, API-process, or Temporal-worker interruption does not lose an accepted Run. CDC replay and duplicate Kafka delivery converge on the same Workflow ID; Temporal replay resumes Activities; retry exhaustion ends the Run with a safe failure code.

## Scope

### In scope

- A logical agent-core module in the existing Python process, with FastAPI, Kafka consumer, Temporal client/worker, model adapter, and PostgreSQL repositories.
- One direct, sessionless, single-turn coordinator execution; no worker selection or delegation.
- `POST` and project-scoped `GET`, `agent_runs` product state, and append-only `agent_run_events` used for safe CDC dispatch/lifecycle publication.
- Existing `cp_debezium` connector/handler/listener patterns, Debezium `pgoutput`, filtered publication, Avro/Schema Registry Kafka records, one versioned Run-event topic, and one idempotent consumer group.
- One root Temporal Workflow per Run, one task queue, bounded model and persistence Activities, deterministic replay, and finite retry policies.
- OpenAI-compatible Chat Completions behind a typed model gateway; migration, contract, failure-injection, security, and real-infrastructure validation.

### Out of scope

- Session, Message, conversation history, Run listing/event API, plan/revisions, cancellation, pause/resume, or user input while running.
- Worker invocation, delegation, parallelism, handoff, multi-step loops, or OpenAI Agents SDK.
- MCP/tools, approvals, domain mutations, memory/RAG, files/artifacts, streaming, structured result schemas, automation rules, or billing.
- Python Kafka production, Outbox Event Router, polling outbox dispatcher, retry/DLQ topics, additional consumer services, frontend changes, or microservice extraction.

## User scenarios

- **Primary:** A project member posts an objective and receives a queued Run. Commit produces a safe CDC event; Kafka dispatches it; Temporal completes the model Activity; polling returns the persisted final text and usage.
- **Permission or boundary:** A non-member is hidden, an archived project or unhealthy execution runtime is rejected before the transaction, and none creates a Run/event or reaches Kafka, Temporal, or the model.
- **Delivery recovery:** The consumer stops after Temporal accepts a Workflow but before offset commit. Kafka redelivers `run.requested`; the same Workflow ID is treated as success, the offset commits, and only one product result is stored.
- **Execution recovery:** The worker restarts during model or persistence work. Temporal replays and retries within bounds; a terminal database transition/event is idempotent, while exhausted safe provider failures produce one `failed` Run.

## Requirements

- Preserve `router -> manager -> repository -> PostgreSQL`; the Kafka listener only passes `BaseDebeziumCDCModel` to `DebeziumCDCHandler`, the typed handler calls the manager, and Workflow code performs no SQL, HTTP, Kafka, or model I/O directly.
- Insert the Run and `run.requested` event atomically. Publish only through standard Debezium table CDC—never direct PostgreSQL/Kafka dual-write or a Python publisher.
- Reuse `cp_debezium` for connector JSON generation, CDC envelope parsing, `READ -> on_create` mapping, callback model construction, and bounded callback retry. Do not create an agent-specific Debezium envelope or operation dispatcher.
- Treat Debezium/Kafka as at-least-once: use immutable event/Run IDs, `run:{run_id}`, conditional database writes, and duplicate-safe event insertion rather than offsets, LSN, or CDC `op` as business identity.
- Keep objective, instructions, final text, credentials, and raw provider data out of Kafka records, Temporal inputs/results/history, logs, and metric labels.
- Snapshot every value influencing execution before commit. Activities load that immutable snapshot by Run ID; agent edits cannot change accepted work.
- Bound objective size, Workflow duration, Activity attempts/timeouts, provider output tokens/bytes, and persistence retries. Model retry may repeat non-mutating inference but cannot create multiple terminal results.
- Make PostgreSQL, Kafka consumer, Temporal connection/worker, model capability, and external Debezium lag part of readiness/enablement. Existing accepted Runs remain readable during degradation.

## Acceptance criteria

- A real integration path proves `POST -> PostgreSQL commit -> cp_debezium Kafka Connect migration -> Debezium -> Kafka -> cp_debezium listener/handler -> Temporal -> model Activity -> PostgreSQL terminal state -> GET`; bypassing Kafka or Temporal is not accepted.
- Run/event creation is atomic, the requested event contains only safe identifiers/metadata, and a failed transaction produces neither CDC dispatch nor Workflow.
- Generated connector JSON has the expected versioned connector/slot/publication/topic names, filtered `agent_run_events` plus heartbeat tables, and an explicit safe column allowlist. Kafka Connect worker configuration supplies compatible Avro/Schema Registry converters.
- Duplicate CDC snapshot/replay and Kafka redelivery start at most one Workflow ID and store one requested, started, and terminal logical event/result.
- A Kafka outage beginning after acceptance leaves the committed work `queued` and dispatches it after recovery; consumer restart before offset commit is duplicate-safe; Temporal worker restart resumes the same Workflow.
- Model transient failures follow the finite Temporal retry policy; invalid output fails without transport retry; persistence Activity replay cannot move or duplicate a terminal Run.
- Non-member, cross-project, archived-project, disabled/unready-runtime, and missing-coordinator requests make zero downstream calls and create no Run/event.
- Automated scans of Kafka values, Temporal history, API errors, and logs find no objective, instructions, result text, credential, authorization header, or raw exception/provider payload.
- No Session, MCP, approval, memory, worker-delegation, automation, Python Kafka producer, or frontend capability is required for completion.

## Existing documentation

| Concern | Canonical reference | Planned documentation change |
| --- | --- | --- |
| Platform/runtime topology | [Platform architecture](../docs/architecture.md), [backend runtime](../docs/backend/runtime.md) | Add Kafka/Debezium, Temporal worker, model adapter, lifecycle order, and readiness. |
| Backend service/API flow | [Backend](../docs/backend/README.md), [flows](../docs/backend/flows.md) | Add the `agents` logical service and async Run flow. |
| Existing agent ownership | [PMS service](../docs/backend/services/pms/README.md) | Keep configuration in PMS and document snapshot handoff to agent-core. |
| Database and CDC | [Database](../docs/database/README.md), [relationships](../docs/database/relationships.md) | Add Run/event tables, terminal constraints, filtered publication, and CDC ownership. |
| Sessions placeholder | [Sessions page](../docs/frontend/pages/pms/sessions.md) | State that direct backend Runs exist but no UI/Session integration does. |
| Forecasting contract | [Agent contract map](../contracts/agents/README.md) | Define this smaller core MVP, keep Temporal mandatory, make Kafka/Debezium mandatory, and move other capabilities to roadmap. |

## Plan map

| Document | Purpose |
| --- | --- |
| [Architecture](architecture.md) | Repository-native API, CDC/Kafka, Temporal, persistence, failure, and rollout design. |
| [Implementation checklist](implementation.md) | Dependency-ordered delivery and validation work. |

## Decisions and open questions

### Decisions

- Kafka dispatches only safe domain events captured by standard Debezium CDC; it never carries Run prompts, snapshots, or results.
- Agent-core extends `cp_debezium`; its listener consumes `BaseDebeziumCDCModel`, its handler types the selected row as `AgentRunEventCDC`, and connector configuration is exported as a versioned `CONNECTORS` migration list. No parallel CDC abstractions are introduced.
- Every Run uses root Workflow `run:{run_id}` on task queue `agent-core`; there is no synchronous execution bypass.
- PostgreSQL remains product truth; Temporal owns orchestration durability and Kafka owns the committed integration/dispatch boundary.
- Reuse the mutable PMS coordinator but snapshot used values at acceptance instead of adding AgentVersion and ModelRegistry entities now.
- Keep one model turn and no tools/workers so Temporal/Kafka foundations are proven without implementing the forecast feature set.

### Open questions

- **Blocking infrastructure integration:** Which Kafka, Schema Registry, Debezium Connect endpoint/credentials, and Temporal namespace/endpoint are available for the target environment? Platform ownership must provide them before connector migration, infrastructure integration, and enablement.
- **Blocking real-provider acceptance:** Which OpenAI-compatible base URL, model, and secret source are available? This blocks the real model smoke, not fake-Activity and replay development.
