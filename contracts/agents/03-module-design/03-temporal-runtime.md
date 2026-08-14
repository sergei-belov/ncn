# Temporal runtime

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:1418-1518 -->
<!-- SOURCE-CONTENT-START -->
# Часть VI. Temporal

## 45. Workflow topology

```text
SessionWorkflow
└── RunWorkflow
    ├── CoordinatorInvocationWorkflow
    ├── WorkerInvocationWorkflow
    ├── Approval coordination
    ├── DAG state
    ├── incoming message queue
    └── finalization
```

SessionWorkflow выполняет `Continue-As-New` при необходимости.

Полная история сообщений не хранится в Temporal history.

---

## 46. Workflow IDs

```text
session:{session_id}
run:{run_id}
coordinator:{run_id}:{invocation_number}
worker:{run_id}:{worker_id}:{invocation_number}
```

`project_id` передаётся через Search Attributes и Workflow input.

---

## 47. Task queue

В MVP используется одна очередь:

```text
agent-core
```

---

## 48. Workflow code

Workflow содержит только:

- state machine;
- DAG orchestration;
- branching;
- signals;
- timers;
- Child Workflows;
- retries;
- cancellation;
- вызовы Activities.

Workflow не выполняет:

- HTTP;
- SQL;
- Kafka;
- Qdrant;
- MinIO;
- LLM;
- MCP;
- embeddings.

---

## 49. Activities

```text
load_run_context
persist_run_state
persist_message
persist_trace_event
invoke_model
validate_coordinator_decision
apply_data_mapping
execute_mcp_tool
validate_structured_output
retrieve_memory
generate_embedding
store_artifact
load_artifact
acquire_mcp_service_token
reconcile_side_effect
```

CEL evaluation Activity отсутствует.

`validate_coordinator_decision` проверяет structured decision координатора и допустимость выбранного перехода.

`apply_data_mapping` выполняет только ограниченные JSON Pointer mappings.

`acquire_mcp_service_token` получает и кэширует в памяти Keycloak service token для конкретной audience системного MCP.

---

