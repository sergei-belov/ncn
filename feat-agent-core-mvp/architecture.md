# Architecture

## Existing constraints

The backend is one FastAPI deployable with the layered path `router -> manager -> repository -> PostgreSQL`, shared service lifecycle, and no database row locks ([backend architecture](../docs/architecture.md#backend-boundaries), [`backend/AGENTS.md`](../backend/AGENTS.md)). Managers own transactions; repositories use generic CRUD plus conditional statements; routers and Kafka listeners contain no business logic. Registration hubs exist for routers, managers, repositories, services, and `backend/api/stream/`.

PMS owns mutable coordinator configuration in `pms_agents`. The repository includes an unregistered Avro/Schema Registry `KafkaBroker` and reusable `cp_debezium` connector configurations, envelope models, CDC handlers, and listener pattern. It has no agent-core connector migration, event-row model/handler/listener, direct Kafka dependencies in `backend/pyproject.toml`, Run schema, model client, Temporal client, or worker. Checked-in Alembic revisions are also absent ([backend runtime](../docs/backend/runtime.md), [`cp_debezium`](../backend/libs/cp_debezium)).

The canonical design establishes PostgreSQL-first state, standard Debezium CDC without direct dual-write/outbox publisher, one root Temporal Workflow per Run, deterministic Workflow code, and external I/O only in Activities ([Kafka/CDC](../contracts/agents/03-module-design/08-kafka-and-automations.md), [Temporal](../contracts/agents/03-module-design/03-temporal-runtime.md)). This MVP changes one existing invariant: Kafka/Debezium become mandatory for the first path.

## Proposed design

Add an `agents` logical service inside the existing Python image/process. FastAPI accepts and reads Runs; Debezium publishes committed safe domain events; a Kafka consumer starts Temporal; a Temporal worker invokes persistence/model Activities. PostgreSQL, Kafka, Schema Registry, Debezium Connect, Temporal service, and the model endpoint are external runtime dependencies.

```text
POST agent-runs
  -> transaction: insert queued agent_runs + run.requested agent_run_events
  -> 202 + Location
  -> PostgreSQL WAL -> Debezium -> Kafka Run-event CDC topic
  -> agent-core consumer -> start Workflow run:{run_id} -> commit offset
  -> Temporal AgentRunWorkflow on task queue agent-core
       -> mark_running Activity (DB + run.started event)
       -> invoke_model Activity (DB read -> model -> DB + terminal event)
       -> on retry exhaustion: fail_run Activity (DB + run.failed event)
  -> GET agent-runs/{run_id} reads PostgreSQL
```

There is no API-to-Kafka or API-to-Temporal call. The committed event bridges the database transaction to execution; stable IDs make CDC snapshot/replay, Kafka redelivery, and Temporal duplicate start converge safely.

## Boundaries and flow

| Boundary | Responsibility | Contract | Expected location |
| --- | --- | --- | --- |
| HTTP | Validate create/read scope and return async state | `CreateAgentRunRequest -> AgentRunResponse` | `backend/api/router/agent_runs.py`, `backend/models/pydantic/api/agent_run_api.py` |
| Manager/repositories | Authorize, snapshot, atomically accept, scoped reads, conditional transitions/events | Run/event DTOs | `backend/api/managers/agent_runs.py`, `backend/api/db/{agent_runs,agent_run_events}.py` |
| Kafka Connect migration | Generate the versioned filtered PostgreSQL connector with existing defaults | `DebeziumPostgresConnectorConfig -> CONNECTORS` | planned `backend/migrations/kafka_connect/{connectors,migrate}.py` |
| CDC row/handler | Validate safe event columns and map Debezium operations through the shared handler | `BaseDebeziumCDCModel -> AgentRunEventCDC` | `backend/models/pydantic/stream/agent_run_stream.py`, planned `backend/api/stream/debezium_handlers.py` |
| Kafka listener | Pass the shared envelope to the handler and commit only after successful dispatch | CDC envelope -> handler -> manager | `backend/api/stream/agent_runs.py`, existing `backend/api/stream/__init__.py` |
| Temporal runtime | Own client/worker lifecycle and workflow start | Workflow ID `run:{run_id}`, task queue `agent-core` | `backend/api/services/temporal_runtime.py` |
| Workflow/Activities | Deterministic orchestration; DB/model I/O in Activities only | ID-only inputs, safe status results | planned `backend/api/workflows/agent_runs.py`, `backend/api/activities/agent_runs.py` |
| Model gateway | Normalize one bounded OpenAI-compatible request | `AgentModelRequest -> AgentModelResult` | `backend/api/services/agent_model.py` |

## Implementation patterns

### Async HTTP contract (`backend/models/pydantic/api/agent_run_api.py`)

Follow strict `APIModel` and response-envelope conventions from [`agent_api.py`](../backend/models/pydantic/api/agent_api.py).

```python
class CreateAgentRunRequest(APIModel):
    id: UUID = Field(description="Client-generated Run and idempotency identifier")
    objective: str = Field(min_length=1, max_length=8000)

class AgentRun(APIModel):
    id: UUID
    project_id: UUID
    agent_id: UUID
    agent_version: int = Field(ge=1)
    model: str
    status: enum.AgentRunStatus  # queued|running|completed|failed
    objective: str
    result_text: str | None
    error_code: str | None
    input_tokens: int | None
    output_tokens: int | None
    created_at: datetime
    completed_at: datetime | None
```

POST returns `202` and `Location`; exact replay returns current state without another event. GET rejects unknown query parameters. Public responses omit instructions and internal snapshots.

### Kafka Connect migration (`backend/migrations/kafka_connect/connectors.py`)

Do not hand-build connector JSON. Extend the checked-in `DebeziumPostgresConnectorConfig`, using runtime database/Kafka settings and the library's existing `pgoutput`, heartbeat, publication, slot, retry, topic-creation, schema-prefixing, and RegexRouter behavior. Export versioned definitions through `CONNECTORS` for the Kafka Connect migration entry point.

```python
from api.settings import ConstSettings, get_settings
from libs.cp_debezium.connector_configs import DebeziumPostgresConnectorConfig

settings = get_settings()

class ExportBaseConnectorConfig(DebeziumPostgresConnectorConfig):
    microservice_name = ConstSettings.SERVICE
    db_hostname = settings.DB_HOST
    db_port = settings.DB_PORT
    db_user = settings.DB_USERNAME
    db_password = settings.DB_PASSWORD
    db_dbname = settings.DB_DATABASE
    db_schema = settings.DB_SCHEMA
    kafka_topic_prefix = settings.KAFKA_TOPIC_PREFIX
    kafka_min_insync_replicas = settings.KAFKA_MIN_INSYNC_REPLICAS
    heartbeat_table = "debezium_heartbeat"

class ExportAgentRunEventsConnectorConfigV0(ExportBaseConnectorConfig):
    connector_name = "agent_run_events"
    connector_version = 0
    config = {
        "table.include.list": ["agent_run_events"],
        "column.include.list": [
            "agent_run_events.id",
            "agent_run_events.run_id",
            "agent_run_events.project_id",
            "agent_run_events.event_key",
            "agent_run_events.event_type",
            "agent_run_events.error_code",
            "agent_run_events.correlation_id",
            "agent_run_events.created_at",
        ],
    }

CONNECTORS = [ExportAgentRunEventsConnectorConfigV0.to_json()]
```

`to_json()` schema-qualifies tables/columns and adds the heartbeat table/columns. Version `0` yields connector `{SERVICE}.export.agent_run_events.0`, slot `export__agent_run_events__0`, publication `export__agent_run_events__0__publication`, and physical topic `{KAFKA_TOPIC_PREFIX}.debezium.cdc.agent_run_events.0`. Kafka Connect worker configuration owns compatible Avro converters and Schema Registry connectivity; database/Connect credentials come from secrets rather than checked-in JSON. Contract tests inspect generated JSON, not a duplicated expected connector implementation.

### Shared CDC handler and listener

`agent_run_events` contains no user/model content. Define only the typed selected-row model; `cp_debezium.models.pydantic.BaseDebeziumCDCModel` remains the Kafka callback envelope. `DebeziumCDCHandler.process()` selects `before`/`after`, converts snapshot `READ` to `on_create`, constructs the callback's annotated Pydantic type, and applies its existing bounded retry behavior.

```python
class AgentRunEventCDC(OrmModel):
    id: UUID
    run_id: UUID
    project_id: UUID
    event_key: str
    event_type: str
    error_code: str | None = None
    correlation_id: UUID | None = None
    created_at: datetime

    class Meta:
        topic = "debezium.cdc.agent_run_events.0"

class DebeziumAgentRunEventsHandler(DebeziumCDCHandler):
    @classmethod
    async def on_create(cls, obj_model: AgentRunEventCDC, **kwargs) -> None:
        if obj_model.event_type == "run.requested":
            await Managers.agent_runs.dispatch_requested(obj_model)

    @classmethod
    async def on_update(cls, obj_model: AgentRunEventCDC, **kwargs) -> None:
        cls._logger.error("Append-only agent_run_events row updated: id=%s", obj_model.id)

    @classmethod
    async def on_delete(cls, obj_model: DeleteDebeziumCDCModel, **kwargs) -> None:
        cls._logger.error("Append-only agent_run_events row deleted: id=%s", obj_model.id)

@Services.broker.listen(topic=AgentRunEventCDC.Meta.topic)
async def process_agent_run_events(
    debezium_model: BaseDebeziumCDCModel,
) -> None:
    await DebeziumAgentRunEventsHandler.process(cdc_model=debezium_model)
```

With `KAFKA_TOPIC_PREFIX=ncn`, the broker subscribes to `ncn.debezium.cdc.agent_run_events.0`; the consumer group is `ncn-agent-run-starter-v1`. Created terminal lifecycle rows return without dispatch. Unexpected updates/deletes emit safe append-only invariant telemetry but never start a Workflow. Business identity is `event.id`/`run_id`, never CDC `op`, offset, LSN, or transaction metadata. `KafkaBroker.capacitor()` commits only after the listener/handler returns; a Temporal start failure raises through the handler, so the offset is not committed and Kafka redelivers.

### Temporal seam (`backend/api/workflows/agent_runs.py`)

Workflow inputs/results are deliberately content-free. The model Activity loads the persisted snapshot/objective by Run ID, closes the database transaction, invokes the model, then opens a new transaction to finalize.

```python
@dataclass(frozen=True)
class AgentRunWorkflowInput:
    run_id: UUID
    project_id: UUID
    requested_event_id: UUID

@workflow.defn
class AgentRunWorkflow:
    @workflow.run
    async def run(self, command: AgentRunWorkflowInput) -> AgentRunWorkflowResult:
        should_execute = await workflow.execute_activity(mark_running, command, ...)
        if not should_execute:
            return AgentRunWorkflowResult(status="already_terminal")
        try:
            return await workflow.execute_activity(invoke_model, command.run_id, ...)
        except ActivityError as error:
            return await workflow.execute_activity(fail_run, safe_failure(error), ...)
```

Use Workflow execution timeout 10 minutes. Model Activity uses `start_to_close=200s`, maximum 3 attempts, initial interval 2s, coefficient 2, maximum interval 20s. Persistence Activities use maximum 5 attempts starting at 500ms. Invalid model content is non-retryable; transient transport/provider failures are retryable. Activity retry first reads the Run: a terminal row returns without a second call; a crash after model response but before commit may repeat non-mutating inference, which is accepted and measured.

### Atomic acceptance and terminalization (`backend/api/db/agent_runs.py`)

Use conditional SQLAlchemy statements and `ON CONFLICT`, following atomic helpers in [`projects.py`](../backend/api/db/projects.py), without row locks.

```python
async def accept_run(
    self, session: AsyncSession, run: AgentRunCreateDTO, event: AgentRunEventCreateDTO
) -> tuple[AgentRunDTO, bool]: ...  # Run + requested event in one transaction

async def transition(
    self, session: AsyncSession, run_id: UUID, project_id: UUID,
    expected: AgentRunStatus, update: AgentRunUpdateFieldsDTO,
    event: AgentRunEventCreateDTO,
) -> AgentRunDTO | None: ...  # state update + idempotent event
```

Event uniqueness `(run_id, event_key)` makes Activity replay harmless. Allowed transitions are `queued -> running -> completed|failed`; retry exhaustion may use `queued|running -> failed`. No API or consumer edits terminal rows.

### Runtime services and configuration

Register `Services.broker`, `Services.temporal`, and `Services.agent_model` through the existing lifecycle hub. Import the stream hub before service start so the decorator registers its topic. Reuse `KafkaBroker.listen` and extend it only where CDC consumer-only lifecycle or safe health behavior requires it; do not call `produce` for Run dispatch. Add the Kafka Connect migration entry point beside the existing Kafka/schema migration rather than embedding connector creation in API startup.

```text
DB_SCHEMA=public
KAFKA_BOOTSTRAP_SERVERS, KAFKA_SCHEMA_REGISTRY_URL, KAFKA_CONNECT_URL
KAFKA_TOPIC_PREFIX=ncn, KAFKA_MIN_INSYNC_REPLICAS=1
KAFKA_GROUP_ID=ncn-agent-run-starter-v1
TEMPORAL_TARGET, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE=agent-core
AGENT_MODEL_BASE_URL, AGENT_MODEL_API_KEY, AGENT_MODEL_TIMEOUT_SEC
AGENT_RUNS_ENABLED=false
```

Add direct pinned-compatible `aiokafka`, Confluent Schema Registry/Avro, Temporal Python SDK, and async model-client dependencies. Enabling Runs requires successful PostgreSQL, broker/consumer, Temporal client/worker, model capability, and externally monitored Debezium connector/lag checks.

## Contracts and data

`agent_runs` stores UUID, indexed project/agent/creator IDs, `queued|running|completed|failed`, bounded objective, internal JSONB execution snapshot, result/error, non-negative usage/latency, and timestamps. The snapshot contains `schema_version=1`, used agent ID/version/name/instructions/model, execution mode, provider protocol, and limits—never credentials.

`agent_run_events` is append-only product/audit metadata: UUID, run/project IDs, unique `event_key`, event type (`run.requested`, `run.started`, `run.completed`, `run.failed`), safe error class when applicable, correlation ID, and timestamp. It contains no objective, instructions, snapshot, result, credential, or raw error. The `cp_debezium` connector includes only this table plus its heartbeat table in the filtered publication and only the listed safe event columns plus heartbeat columns.

Check constraints enforce terminal field consistency and known statuses/types. Same-database foreign keys to `pms_projects`/`pms_agents` are accepted for the physical MVP. Existing agent APIs and configured memory/approval/tool fields remain unchanged and unused.

## Security, failure handling, and observability

- Reuse bearer authentication, project 404 hiding, and archived-project rules. Readiness failure returns `EXECUTION_UNAVAILABLE` before acceptance; already accepted Runs remain readable.
- Kafka and Temporal carry identifiers, safe types/status/error classes, and correlation IDs only. Model output is untrusted plain text and never treated as a tool/action.
- Kafka at-least-once plus Temporal stable Workflow ID provides effectively-once start, not exactly-once transport. Terminal database transitions/events provide effectively-once product result. Model inference itself may repeat on the narrow response-before-commit crash boundary.
- Metrics cover accepted/terminal Runs, CDC-to-consumer lag, consumer errors/redelivery, Workflow start conflicts, task-queue/Workflow latency, Activity retries, model outcomes, and queued/running age with bounded labels. Logs include IDs/correlation but no content or secrets.
- An outage beginning after Run acceptance leaves the Run queued; a Temporal service outage prevents offset commit; a worker outage leaves Workflow history durable. Malformed/incompatible CDC stops consumption and readiness rather than silently skipping dispatch.

## Rollout and rollback

1. Approve the narrowed contract; add Run/event/heartbeat schema, generate and apply `CONNECTORS` through the Kafka Connect migration, verify the Avro CDC contract, and provision Kafka, Schema Registry, and Temporal namespace/task queue with Runs disabled.
2. Deploy model adapter, Temporal worker, and Kafka consumer; validate lifecycle/readiness, CDC snapshot, duplicate dispatch, replay, and fake model before enabling one non-production project.
3. Run real model and restart/outage drills; watch connector lag, consumer offsets, Workflow starts/retries, queued/running age, terminal mismatch, and leakage scans.
4. Roll back by disabling new Runs and stopping Kafka consumption only after committed requested events are accounted for. Keep a replay-compatible Temporal worker until active Workflows terminalize; retain topics, schemas, tables, and read API until a later cleanup.

## Validation approach

- Model/API/repository tests cover strict fields, atomic Run+event creation, status/event constraints, exact replay, conditional transitions, exports, and routing.
- Connector unit tests call `ExportAgentRunEventsConnectorConfigV0.to_json()` and verify schema-qualified safe columns, heartbeat, connector/slot/publication/topic versioning, and absence of sensitive Run columns. Handler/listener tests use `BaseDebeziumCDCModel` fixtures for `c/r/u/d`, duplicate delivery, offset-before/after-start crashes, incompatible schemas, and payload redaction.
- Temporal tests use the SDK test environment/time skipping for deterministic replay, stable Workflow IDs, Activity policies, API/consumer/worker restarts, terminal idempotency, and retry exhaustion.
- End-to-end tests prove the mandatory full path with a fake model, then one target-environment real-model smoke; direct API-to-model or API-to-Temporal paths must fail architecture review.
- Migration/deployment checks verify clean database upgrade, filtered publication/table list, heartbeat, topic/schema compatibility, lifecycle order, readiness degradation, and rollback with active Workflows.
