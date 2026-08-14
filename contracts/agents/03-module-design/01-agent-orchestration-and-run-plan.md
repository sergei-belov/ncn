# Оркестрация агентов и RunPlan

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:676-1015 -->
<!-- SOURCE-CONTENT-START -->
# Часть III. Оркестрация агентов

## 16. Модель делегирования

Используется:

```text
Temporal-managed delegation
```

Native SDK handoff между координатором и работниками не используется.

Последовательность:

```text
RunWorkflow
→ CoordinatorInvocationWorkflow
→ WorkerInvocationWorkflow
→ CoordinatorInvocationWorkflow
→ Finalization
```

Координатор формирует структурированное поручение.

Temporal запускает работника как отдельный Child Workflow.

Работник возвращает `WorkerResultEnvelope`.

После этого RunWorkflow запускает следующую coordinator invocation либо продолжает DAG.

---

## 17. Топология агентов

Разрешено:

```text
Coordinator → Worker
```

Запрещено:

```text
Worker → Worker
Worker → новый Coordinator task
Worker → self
```

Возвращение результата работника координатору не считается новым делегированием.

---

## 18. Лимиты

```text
max_coordinator_invocations = 5
max_worker_invocations = 5
max_parallel_workers = 2

coordinator_max_turns = 12
worker_max_turns = 8
run_max_agent_turns = 30
max_tool_calls_per_invocation = 20
```

Model-level retry внутри Invocation не считается новой Invocation.

Повторный полноценный запуск агента считается новой Invocation.

При превышении лимита создаётся:

```text
EXECUTION_LIMIT_EXCEEDED
```

---

## 19. DelegationPacket

Работнику не передаётся полная история Session.

Координатор формирует:

```json
{
  "objective": "Цель поручения",
  "expected_output": {
    "schema_id": "optional"
  },
  "relevant_context": {},
  "constraints": [],
  "permissions": [],
  "linked_entities": [],
  "artifacts": [],
  "deadline": null
}
```

DelegationPacket:

- сохраняется во внутреннем trace;
- не показывается пользователю;
- не содержит reasoning;
- не содержит credentials;
- является частью контекста работника.

Работник может использовать read-only tools:

```text
search_session_messages
get_session_message
search_project_memory
get_task
get_project_state
get_artifact_metadata
```

---

# Часть IV. Workflow и DAG

## 20. Источники Workflow

Workflow зависит от типа задачи.

Пользователь Project может:

- собрать ограничивающий DAG через конфигурацию;
- связать WorkflowVersion с automation rule.

WorkflowVersion определяет допустимые nodes, edges, обязательные Approval, разрешённых работников, MCP tools и limits.

Координатор может динамически сформировать или уточнить план только внутри разрешённой WorkflowVersion и configuration snapshot Run. Для ручного Run без WorkflowVersion используется synthetic root plan координатора.

---

## 21. Типы DAG nodes

В MVP поддерживаются:

```text
agent
mcp_action
coordinator_decision
parallel
wait
approval
timer
human_task
subworkflow
finalize
```

Тип `condition` и язык CEL в MVP не используются.

`coordinator_decision` запускает координатора для выбора одного из заранее допустимых переходов либо для формирования разрешённого изменения ещё не выполненной части плана.

---

## 22. Статическая валидация

Перед публикацией проверяются:

- JSON Schema Workflow;
- поддерживаемые node types;
- наличие start node;
- наличие finalize node;
- достижимость;
- отсутствие запрещённых циклов;
- ссылки на работников;
- ссылки на MCP tools;
- input schemas;
- output schemas;
- JSON Pointer mappings;
- schema результата `coordinator_decision`;
- существование всех `allowed_edges`;
- permissions;
- invocation limits;
- parallelism limits;
- обязательные Approval nodes;
- отсутствие архивированных зависимостей.

Dry run в MVP не используется.

---

## 23. Версионирование Workflow

```text
WorkflowDefinition
└── WorkflowVersion
    ├── draft
    ├── published
    ├── deprecated
    └── archived
```

Опубликованные версии immutable.

Automation rule ссылается на конкретную опубликованную версию.

Активный Run продолжает использовать исходную WorkflowVersion.

---

## 24. Семантическое ветвление координатора

CEL и другие пользовательские expression languages в MVP отсутствуют.

Семантическое ветвление выполняет координатор через structured output.

Пример node:

```json
{
  "key": "choose_next_action",
  "type": "coordinator_decision",
  "allowed_edges": [
    "continue_automatically",
    "request_approval",
    "ask_user",
    "finish"
  ],
  "decision_schema": {
    "type": "object",
    "additionalProperties": false,
    "required": ["selected_edge", "summary"],
    "properties": {
      "selected_edge": {
        "type": "string",
        "enum": [
          "continue_automatically",
          "request_approval",
          "ask_user",
          "finish"
        ]
      },
      "summary": {
        "type": "string"
      },
      "plan_updates": {
        "type": "array",
        "items": {"type": "object"},
        "default": []
      }
    }
  }
}
```

Backend обязан проверить:

- structured result по JSON Schema;
- существование `selected_edge`;
- допустимость перехода из текущего node;
- доступность следующего node;
- AgentVersion и MCP references;
- limits и parallelism;
- permissions и Project constraints;
- обязательность Approval;
- отсутствие изменения уже выполненных nodes и side effects.

Координатор не может:

- расширить permissions;
- отключить Approval;
- изменить `project_id`;
- добавить неразрешённого Worker или MCP tool;
- повысить limits;
- изменить завершённые или выполняющиеся nodes;
- принимать окончательное решение о security policy или доменных инвариантах.

Security, Approval, permissions, quotas, Project isolation и доменные правила всегда вычисляются детерминированным backend-кодом и MCP/domain services.

Отдельный decision-agent в MVP не создаётся.

---

## 25. Data mapping

Полноценный JSONPath runtime в MVP не используется.

Для передачи данных между nodes применяется ограниченный mapping:

```text
source context или source node
+
JSON Pointer source path
+
JSON Pointer target path
+
required/default/cardinality
```

Пример:

```json
{
  "source": {
    "node": "search_supplier",
    "path": "/data/selected_supplier_id"
  },
  "target": "/supplier_id",
  "required": true,
  "cardinality": "single"
}
```

Допустимые source scopes:

```text
input
trigger
run
project
node
```

Правила:

- `path` и `target` используют RFC 6901 JSON Pointer;
- recursive search, filters, expressions и functions отсутствуют;
- неявное преобразование типов отсутствует;
- `default` применяется только при отсутствии значения;
- explicit `null` считается найденным значением;
- итоговый input обязательно проверяется JSON Schema следующего node;
- одинаковый target нельзя записывать несколькими mappings;
- mapping не может получать credentials, hidden reasoning или значения вне разрешённого Run context.

Ошибки:

```text
DATA_MAPPING_SYNTAX_ERROR
DATA_MAPPING_SOURCE_MISSING
DATA_MAPPING_CARDINALITY_ERROR
DATA_MAPPING_TARGET_CONFLICT
DATA_MAPPING_SCHEMA_ERROR
DATA_MAPPING_SIZE_EXCEEDED
```

