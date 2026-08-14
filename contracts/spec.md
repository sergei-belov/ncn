# Контракт реализации мультиагентного ядра

## Версия 1.3-draft

## Статус документа

Документ является рабочим согласованным контрактом реализации мультиагентного ядра платформы NCN.

Версия 1.3-draft:

- сохраняет архитектурные инварианты версии 1.0;
- включает согласованные решения по PostgreSQL-first, Debezium CDC, ролям, Approval, Model Registry, MCP authorization и secrets;
- исключает OAuth пользовательских MCP из MVP;
- исключает CEL и полноценный JSONPath runtime из MVP;
- закрепляет семантическое ветвление за координатором с обязательной backend-валидацией;
- использует ограниченные JSON Pointer mappings для передачи данных между nodes;
- остаётся draft до закрытия остальных открытых вопросов 138–172.

Решения из этого документа считаются обязательными, пока не изменены следующей версией контракта.
---

# Часть I. Описание системы

## 1. Назначение продукта

Система является мультиагентным ядром SaaS-платформы управления проектами.

Основной пользовательский продукт — проектная среда, близкая по назначению к Jira, но с интегрированным ИИ-менеджером.

В платформе существуют:

- пространства;
- проекты;
- пользователи;
- задачи;
- ответственные сотрудники;
- комментарии;
- статусы;
- сроки;
- зависимости;
- проектные документы;
- автоматизации;
- ИИ-координатор;
- конфигурируемые ИИ-работники;
- подключаемые MCP-серверы.

Помимо основного сервиса управления задачами платформа может включать вспомогательные домены:

- закупки;
- CRM;
- разработку;
- документооборот;
- аналитику;
- внешние интеграции;
- другие проектные сервисы.

Мультиагентное ядро не заменяет доменные сервисы. Оно координирует действия, анализирует проектное состояние и использует доступные доменные функции через MCP, внутренние API и события.

---

## 2. Роль ИИ-менеджера

В каждом Project обязательно существует основной агент-координатор.

Координатор выполняет роль ИИ-менеджера проекта.

Он способен:

- анализировать пользовательские сообщения;
- анализировать события проекта;
- реагировать на automation rules;
- получать данные о задачах;
- получать состояние проекта;
- выявлять блокеры;
- выявлять риски;
- отслеживать сроки;
- строить план выполнения запроса;
- выбирать подходящих работников;
- делегировать работникам отдельные подзадачи;
- запускать работников последовательно;
- запускать до двух работников параллельно;
- агрегировать результаты;
- изменять ещё не выполненную часть плана;
- задавать уточняющие вопросы;
- создавать задачи;
- связывать задачи;
- назначать ответственных пользователей;
- менять разрешённые поля задач;
- оставлять комментарии;
- прикреплять артефакты;
- предлагать внешние действия;
- выполнять разрешённые внешние действия;
- запрашивать подтверждение человека;
- возвращать пользователю итоговый текст и структурированный результат.

Координатор всегда подключён к системному MCP управления задачами.

Пользователь может изменять пользовательскую часть конфигурации координатора, но не может:

- удалить координатора;
- архивировать координатора;
- отключить обязательный task-management MCP;
- снять project constraints;
- изменить внутренний workload authentication protocol системного MCP;
- отключить security policy;
- отключить permission validation;
- получить или заменить системные credentials;
- повысить platform limits.

---

## 3. Роль работников

Работник — специализированный агент Project.

Примеры работников:

- специалист по закупкам;
- CRM-аналитик;
- аналитик проекта;
- технический аналитик;
- специалист по документации;
- специалист по рискам;
- помощник разработчика;
- агент подготовки отчётов.

Работники создаются и конфигурируются `project_admin`.

Работник может:

- анализировать предоставленный контекст;
- использовать проектную память;
- читать разрешённые задачи и связанные сущности;
- использовать разрешённые MCP tools;
- анализировать документы;
- формировать отчёты;
- возвращать structured output;
- предлагать действия;
- выполнять разрешённые действия;
- задавать пользователю уточняющие вопросы;
- возвращать результат координатору.

Работник не может:

- вызвать другого работника;
- создать независимый Run;
- самостоятельно расширить свои разрешения;
- отключить Approval;
- получить MCP tool, который не был разрешён;
- изменить `project_id`;
- передать credentials модели;
- стать полноценным assignee задачи.

---

## 4. Агенты и задачи

Агент не является полноценным исполнителем задачи.

Основной assignee задачи — человек.

Агент может:

- помогать ответственному;
- проводить анализ;
- готовить рекомендации;
- собирать данные;
- выполнять исследование;
- готовить документы и отчёты;
- предлагать изменения;
- выполнять ограниченные действия;
- создавать вспомогательные задачи;
- оставлять комментарии.

Связь агента с задачей хранится отдельно от человеческого assignee.

Предпочтительная модель:

```text
task_agent_assignments
```

Она позволяет связать одну задачу с несколькими агентами без превращения агентов в основных исполнителей.

---

## 5. Бизнес-сценарий: закупка батареек

В задаче пользователь оставляет комментарий:

```text
Нужно выбрать поставщика для закупки партии батареек.
```

В Project настроено automation rule, которое реагирует на:

- новый комментарий;
- назначение задачи;
- mention координатора;
- другое подходящее условие.

Последовательность:

1. Task-домен публикует событие.
2. Событие попадает в Kafka.
3. Сервис `pipelines` сопоставляет событие с automation rule.
4. `pipelines` создаёт trigger event.
5. Agent-core получает trigger event.
6. Для срабатывания создаётся новая системная Session.
7. Создаётся Run.
8. Координатор загружает:
   - задачу;
   - комментарий;
   - связанные сущности;
   - состояние проекта;
   - permissions snapshot;
   - релевантную проектную память.
9. Координатор выбирает работника по закупкам.
10. Temporal запускает отдельный `WorkerInvocationWorkflow`.
11. Работник получает `DelegationPacket`.
12. Работник использует разрешённый procurement MCP.
13. Работник:
   - получает список поставщиков;
   - сравнивает цены;
   - анализирует сроки;
   - оценивает риски;
   - формирует рекомендацию.
14. Если требуется только аналитика, работник возвращает результат.
15. Если требуется создать заказ, система проверяет:
   - разрешение агента;
   - project policy;
   - risk policy;
   - ApprovalGrant;
   - наличие подтверждения.
16. При необходимости Run переходит в `WAITING_FOR_APPROVAL`.
17. Ответственный пользователь или инициатор подтверждает действие.
18. После подтверждения SDK RunState восстанавливается.
19. Выполняется MCP tool call.
20. Координатор агрегирует результат.
21. В задаче создаётся комментарий с рекомендацией.
22. При необходимости создаётся вспомогательная задача для человека.
23. Системная Session закрывается.
24. Создаётся summary.
25. Summary индексируется в Qdrant.

---

## 6. Бизнес-сценарий: приближение deadline

Automation rule срабатывает при приближении срока задачи.

Координатор:

1. получает сведения о задаче;
2. получает зависимости;
3. получает текущий статус;
4. получает ProjectState;
5. проверяет блокеры;
6. анализирует историю связанных событий;
7. при необходимости вызывает специализированного работника;
8. формирует рекомендацию;
9. может:
   - оставить комментарий;
   - создать задачу на устранение блокера;
   - предложить изменение приоритета;
   - предложить перераспределение;
   - запросить status update у ответственного;
   - сформировать предупреждение.

Опасные или изменяющие внешние данные действия проходят Approval policy.

---

## 7. Бизнес-сценарий: ручной диалог

Пользователь создаёт Session на уровне всего Project.

Session может не быть связана с задачей.

Пользователь спрашивает:

```text
Какие основные блокеры сейчас есть в проекте?
```

Координатор получает:

- Project context;
- актуальный ProjectState;
- связанные задачи;
- релевантные записи памяти;
- разрешённые артефакты.

Координатор может:

- ответить самостоятельно;
- делегировать анализ работнику;
- запросить дополнительные данные;
- сформировать structured output;
- создать связанные задачи после подтверждения или при наличии разрешения.

---

## 8. Бизнес-сценарий: прямое обращение к работнику

Frontend передаёт структурированный mention или `target_agent_id`.

Сообщение всё равно попадает в общий Session timeline и активный Run.

Координатор формирует `DelegationPacket`.

Работник получает запрос и может:

- сформировать ответ;
- использовать разрешённые read-only tools;
- использовать разрешённые MCP tools;
- задать уточняющий вопрос пользователю.

Ответ работника сохраняется как публичное Message от работника.

После завершения результат возвращается координатору.

---

## 9. Бизнес-сценарий: уточнение от работника

Работнику не хватает информации.

Он создаёт публичное Message с вопросом.

Run переходит в:

```text
WAITING_FOR_INPUT
```

Пользователь отвечает с:

```text
target_agent_id = worker_id
```

Сообщение присоединяется к существующему Run.

Ожидающий `WorkerInvocationWorkflow` получает ответ и продолжает работу.

Новый независимый вопрос в этой Session нельзя выполнять параллельно. Для него требуется:

- новая Session;
- либо отмена текущего Run.

---

## 10. Бизнес-сценарий: документы

Пользователь загружает PDF или DOCX размером до 50 MiB.

Файл сохраняется в MinIO.

После загрузки:

1. проверяется Project access;
2. проверяется размер;
3. определяется фактический MIME type;
4. вычисляется SHA-256;
5. создаётся Artifact;
6. извлекается текст;
7. текст разбивается на chunks;
8. создаются embeddings через Ollama;
9. chunks индексируются в Qdrant;
10. Artifact можно передать координатору или работнику.

Для scanned PDF без текстового слоя OCR в MVP не выполняется.

Пользователь получает предупреждение о неподдерживаемом scanned document.

---

## 11. Бизнес-сценарий: остановка

Пользователь отправляет команду отмены.

Run публично сразу получает:

```text
CANCELLING
```

Далее:

- прекращается запуск новых DAG nodes;
- отменяются незапущенные WorkerInvocation;
- текущим Child Workflow отправляется cancellation;
- новые tool calls запрещаются;
- модельный HTTP request отменяется, если возможно;
- уже выполненные side effects не откатываются;
- неидемпотентное действие с неизвестным результатом получает `SIDE_EFFECT_UNKNOWN`;
- при возможности запускается reconciliation.

Финальный статус:

```text
CANCELLED
```

или `FAILED`, если возникло необрабатываемое состояние.

---

## 12. Основные функции платформы

### Управление координатором

- получение текущей конфигурации;
- полная замена пользовательской конфигурации через PUT;
- частичное обновление через PATCH;
- выбор модели;
- настройка инструкций;
- настройка memory policy;
- настройка limits;
- настройка Approval preferences;
- настройка доступных работников.

### Управление работниками

- создание;
- получение;
- получение списка;
- PUT;
- PATCH;
- архивирование;
- включение и отключение;
- выбор модели;
- настройка output schema;
- настройка permissions;
- подключение MCP tools;
- настройка memory policy;
- настройка limits;
- настройка approval policy.

### Управление MCP

- создание Project MCP configuration;
- Streamable HTTP transport;
- API key в настраиваемом header;
- Basic Auth;
- discovery tools;
- ручной refresh discovery;
- выбор разрешённых tools;
- повторное подтверждение изменённой schema;
- отключение;
- архивирование;
- управление Project credentials.

OAuth для пользовательских MCP не входит в MVP. Machine-to-machine `client_credentials` системного MCP является отдельным workload-механизмом и описан в разделе 98.

### Управление Workflow

- создание WorkflowDefinition;
- создание draft WorkflowVersion;
- PUT draft;
- PATCH draft;
- статическая валидация;
- публикация;
- deprecation;
- archive;
- привязка automation rule к опубликованной версии.

### Управление Session и Run

- создание Session;
- отправка Message;
- присоединение Message к активному Run;
- polling состояния;
- polling RunEvent;
- отмена;
- resume после budget block;
- закрытие Session;
- удаление Session и связанных данных.

### Управление Approval

- получение списка;
- получение конкретного Approval;
- approve;
- reject;
- редактирование аргументов;
- создание ограниченного ApprovalGrant;
- отзыв grant.

### Управление Artifact

- создание multipart upload;
- завершение upload;
- получение metadata;
- получение presigned URL;
- привязка к Session;
- извлечение текста;
- индексирование;
- удаление.

---

# Часть II. Организационная и доменная модель

## 13. Мультитенантность

Основная иерархия:

```text
Space
└── Project
    ├── Users
    ├── Sessions
    ├── Coordinator
    ├── Workers
    ├── MCP configurations
    ├── Workflows
    ├── Automation rules
    ├── Secrets
    ├── Artifacts
    └── Memory
```

Границей изоляции agent-core является Project.

По Project изолируются:

- агенты;
- версии агентов;
- Session;
- Run;
- Message;
- Workflow;
- MCP;
- MCP credentials;
- Approval;
- Artifact;
- Qdrant records;
- traces;
- budgets;
- project state;
- automation triggers.

`project_id` добавляется системой и не доверяется LLM-generated arguments.

---

## 14. Пользовательские роли

Базовые роли:

```text
platform_admin
space_admin
project_admin
project_member
```

### `platform_admin`

Управляет platform control plane:

- создаёт и изменяет ModelDefinition;
- подключает platform model credentials;
- устанавливает ModelPriceVersion;
- запускает capability verification и health checks моделей;
- включает и отключает модели;
- назначает platform model defaults;
- задаёт platform quota defaults и максимумы Space;
- просматривает глобальный model usage и platform audit.

`platform_admin` не получает автоматического доступа к Session, Message, Artifact, trace и MCP credentials конкретного Project. Для data-plane доступа требуется обычная роль соответствующего Project.

### `space_admin`

Управляет Space control plane:

- создаёт и архивирует Project;
- назначает и отзывает `project_admin`;
- задаёт Project quotas в пределах максимума Space;
- определяет список моделей, разрешённых в Space;
- просматривает агрегированное административное состояние Project;
- просматривает административный audit Space.

`space_admin` не наследует `project_admin` и не получает автоматического доступа к данным Project.

Break-glass механизм не вводится. Для доступа к данным конкретного Project `space_admin` должен получить обычную роль этого Project.

### `project_admin`

Может:

- выполнять все действия `project_member`;
- изменять координатора;
- создавать, изменять и архивировать работников;
- подключать MCP;
- выбирать MCP tools;
- создавать и ротировать Project secrets через безопасный API;
- отменять Run;
- удалять Session и историю;
- создавать и публиковать Workflow;
- управлять automation configuration;
- управлять Project approval policy;
- создавать AgentVersion с разрешённой approval policy;
- просматривать Project quotas и usage.

### `project_member`

Может:

- создавать Session;
- запускать агентов;
- отправлять Message;
- подтверждать действие, если включён в `allowed_approver_ids`;
- просматривать traces при наличии permission;
- просматривать доступные Session Project;
- скачивать доступные Artifacts.

---

## 15. Сущности исполнения

### Session

Долгоживущий проектный диалог.

В одной Session могут участвовать несколько пользователей.

Session может быть:

- пользовательской;
- системной, созданной automation rule.

### Message

Содержательный элемент timeline.

Message может быть создан:

- пользователем;
- координатором;
- работником;
- системой.

### Run

Durable-исполнение одного или нескольких входных сообщений или trigger event.

В одной Session одновременно существует не более одного активного Run.

### AgentInvocation

Один полноценный запуск координатора или работника.

### ToolCallExecution

Один вызов:

- function tool;
- MCP tool;
- memory tool;
- artifact tool;
- system tool.

### RunEvent

Append-only событие выполнения для polling frontend и диагностики.

### AuditEvent

Append-only security или administrative event.

---

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

# Часть V. Session и Run

## 26. Session statuses

```text
ACTIVE
CLOSING
CLOSED
```

Session не может быть повторно открыта после `CLOSED`.

---

## 27. Session properties

Минимальные поля:

```text
id
space_id
project_id
status
session_type
title
primary_entity_type
primary_entity_id
active_run_id
initiator_type
initiator_id
created_by_user_id
created_at
closed_at
summary_artifact_id
```

`title` nullable.

Пользователь может установить его позже через PATCH.

---

## 28. Связанные сущности

Session может быть связана с несколькими сущностями.

```text
SessionEntityLink
├── id
├── project_id
├── session_id
├── entity_type
├── entity_id
├── relation_type
└── created_at
```

Примеры `entity_type`:

```text
task
pipeline
crm_deal
purchase_request
supplier
document
project
```

---

## 29. Session participants

Отдельная ACL-таблица участников не создаётся.

Доступ определяется Project membership.

Фактические участники могут быть вычислены по Message, Run и Approval.

---

## 30. Message

Message immutable.

Пользователь не может:

- отредактировать Message;
- удалить отдельное Message;
- заменить content;
- заменить mentions.

Для исправления пользователь:

1. отменяет активную генерацию;
2. отправляет новое Message.

---

## 31. Message content

Поддерживаются блоки:

```text
text
structured
artifact_reference
```

Одно Message может содержать несколько блоков.

---

## 32. Message ordering

Каждое Message имеет:

```text
sequence
```

Ограничение:

```text
UNIQUE(session_id, sequence)
```

Порядок определяется sequence.

---

## 33. Message visibility

В MVP:

```text
session
internal
```

### `session`

Доступно Project members с правом просмотра Session.

### `internal`

Доступно backend-компонентам.

Технические события преимущественно хранятся как RunEvent, а не Message.

---

## 34. Structured mention

Frontend передаёт mention отдельно от текста:

```json
{
  "content": "Подключи специалиста по закупкам",
  "mentions": [
    {
      "type": "agent",
      "id": "UUID"
    }
  ]
}
```

Backend проверяет:

- принадлежность агента Project;
- существование;
- отсутствие archive;
- permission на обращение.

Парсинг `@name` не является источником истины.

---

## 35. Добавление Message

Endpoint:

```http
POST /api/sessions/v1/projects/{project_id}/sessions/{session_id}/messages
```

Ответ:

```json
{
  "message_id": "UUID",
  "session_id": "UUID",
  "run_id": "UUID",
  "run_created": false,
  "status": "accepted"
}
```

Если активного Run нет:

```json
{
  "run_created": true
}
```

Используется:

```http
Idempotency-Key: <client-generated-value>
```

Одинаковый ключ и одинаковый payload возвращают прежний результат.

Одинаковый ключ и другой payload возвращают конфликт.

---

## 36. Присоединение Message к активному Run

Новое Message:

1. сохраняется в PostgreSQL;
2. привязывается к активному Run;
3. передаётся через Temporal Signal;
4. помещается во входную очередь;
5. не прерывает текущий model call;
6. обрабатывается на безопасной границе.

Координатор может:

- продолжить план;
- изменить план;
- отменить незапущенные nodes;
- добавить nodes;
- изменить приоритет.

Выполненные side effects не откатываются.

---

## 37. Условия завершения Run

```text
DAG завершён
AND нет активных AgentInvocation
AND нет активных tool calls
AND очередь сообщений пуста
AND нет Approval
AND нет Timer/Wait
```

Используется внутренний статус:

```text
FINALIZING
```

Публично он отображается как `RUNNING`.

---

## 38. Run statuses

```text
CREATED
QUEUED
RUNNING
WAITING_FOR_APPROVAL
WAITING_FOR_INPUT
BUDGET_BLOCKED
RETRYING
CANCELLING
COMPLETED
PARTIALLY_COMPLETED
FAILED
CANCELLED
```

Внутренний:

```text
FINALIZING
```

---

## 39. Run initiator

```text
user
automation
schedule
external_event
system
```

Для automation сохраняются:

```text
automation_rule_id
source_event_id
```

---

## 40. RunInputEnvelope

```json
{
  "trigger_type": "message",
  "message_ids": [],
  "mentions": [],
  "linked_entities": [],
  "trigger_payload": {},
  "received_at": "UTC+00:00"
}
```

Envelope immutable.

Новые входные сообщения добавляются в очередь, не изменяя исходный envelope.

---

## 41. Configuration snapshot Run

Ссылки:

```text
coordinator_version_id
workflow_version_id
project_state_version
```

JSONB snapshots:

```text
permission_snapshot
model_snapshot
mcp_snapshot
limits_snapshot
project_context_snapshot
```

---

## 42. Закрытие пользовательской Session

Закрытие возможно после завершения или отмены активного Run.

Последовательность:

1. Session получает `CLOSING`.
2. Новые Message запрещаются.
3. Генерируется summary.
4. Summary сохраняется.
5. Summary индексируется в Qdrant.
6. Session получает `CLOSED`.

---

## 43. Automation Session

Каждое новое срабатывание automation rule создаёт новую Session.

После завершения Run системная Session автоматически закрывается.

---

## 44. Удаление Session

Удаление Session выполняется отдельным идемпотентным deletion workflow.

Удаляются:

- Message;
- Run;
- AgentInvocation;
- ToolCallExecution;
- Approval;
- ApprovalGrant;
- RunEvent payload;
- Session summary;
- Qdrant records;
- Session-owned Artifacts;
- SDK RunState;
- связанные orchestration records.

В security audit остаётся обезличенное событие:

```text
session_deleted
project_id
deleted_by
deleted_at
records_count
```

---

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

## 50. Retry policies

### Model call

```text
initial_interval = 2 seconds
backoff_coefficient = 2
maximum_interval = 20 seconds
maximum_attempts = 3
```

### MCP read

```text
initial_interval = 1 second
backoff_coefficient = 2
maximum_interval = 10 seconds
maximum_attempts = 3
```

### Idempotent MCP write

```text
initial_interval = 2 seconds
backoff_coefficient = 2
maximum_interval = 15 seconds
maximum_attempts = 3
```

### Non-idempotent MCP write

```text
maximum_attempts = 1
```

### PostgreSQL persistence

```text
initial_interval = 500 milliseconds
backoff_coefficient = 2
maximum_interval = 5 seconds
maximum_attempts = 5
```

### Qdrant

```text
initial_interval = 1 second
backoff_coefficient = 2
maximum_interval = 10 seconds
maximum_attempts = 3
```

### MinIO

```text
initial_interval = 1 second
backoff_coefficient = 2
maximum_interval = 15 seconds
maximum_attempts = 3
```

### Embeddings

```text
initial_interval = 2 seconds
backoff_coefficient = 2
maximum_interval = 20 seconds
maximum_attempts = 3
```

---

## 51. Timeouts

### Model call

```text
connect_timeout = 10 seconds
read_timeout = 180 seconds
start_to_close = 200 seconds
```

### MCP read

```text
connect_timeout = 10 seconds
read_timeout = 60 seconds
start_to_close = 75 seconds
```

### MCP write

```text
connect_timeout = 10 seconds
read_timeout = 90 seconds
start_to_close = 105 seconds
```

### Coordinator invocation

```text
active_execution_timeout = 15 minutes
```

### Worker invocation

```text
active_execution_timeout = 30 minutes
```

Ожидание Approval, input и budget не входит в active execution timeout.

### Artifact extraction

```text
10 minutes
```

### Embedding batch

```text
2 minutes
```

### PostgreSQL

```text
15 seconds
```

### Qdrant

```text
30 seconds
```

### MinIO metadata

```text
30 seconds
```

---

# Часть VII. OpenAI Agents SDK

## 52. Основные SDK-примитивы

Используются максимально:

```text
Agent
Runner
Runner.run_streamed
RunConfig
ModelSettings
RunContextWrapper
RunState
function_tool
MCPServerStreamableHttp
```

Native handoff не используется.

---

## 53. Runner

Используется:

```python
Runner.run_streamed(...)
```

Streaming применяется для внутренних semantic events.

Raw token delta не сохраняются и не передаются frontend.

Frontend использует polling.

---

## 54. SDK Session

Встроенное Session storage SDK не используется.

Каждый Invocation получает явно собранный input.

---

## 55. Runtime context

```text
AgentRuntimeContext
├── space_id
├── project_id
├── session_id
├── run_id
├── agent_id
├── agent_version_id
├── invocation_id
├── initiated_by_user_id
├── permissions_snapshot
├── delegation_packet
├── trace_id
└── correlation_id
```

Credentials в context не передаются.

---

## 56. SDK RunState

При interruption:

1. создаётся `RunState`;
2. сериализуется;
3. шифруется;
4. сохраняется в PostgreSQL;
5. Child Workflow ожидает Signal;
6. применяется approve/reject/input;
7. Runner продолжается с RunState.

RunState:

- не показывается пользователю;
- не передаётся в Kafka;
- не индексируется;
- удаляется после Invocation;
- удаляется при удалении Session.

---

## 57. Tool calls

Модель может выполнить несколько tool calls внутри Invocation.

В MVP все tool calls выполняются последовательно.

Параллельность существует только между WorkerInvocation:

```text
max_parallel_workers = 2
```

---

## 58. Structured output

Для пользовательских JSON Schema используется:

1. schema в runtime instructions;
2. безопасный JSON parser;
3. валидация через `jsonschema`;
4. Pydantic `TypeAdapter`, где применимо;
5. помещение результата в envelope.

Pipeline:

```text
primary generation
→ repair 1
→ repair 2
→ fallback model
→ fallback repair
→ INVALID_OUTPUT
```

---

## 59. Tool error для модели

Модель получает только безопасный ответ:

```json
{
  "code": "MCP_UNAVAILABLE",
  "detail": "Tool is temporarily unavailable",
  "retryable": true
}
```

Stack trace и внутренние детали не передаются.

---

## 60. SDK tracing

Экспорт в OpenAI tracing backend отключён.

Используются:

- streamed events;
- Runner hooks;
- внутренний trace processor;
- RunEvent;
- AuditEvent.

Hidden reasoning не сохраняется.

---

# Часть VIII. Модели и бюджеты

## 61. Model Registry

Используется одна сущность:

```text
ModelDefinition
```

Отдельное версионирование ModelDefinition не используется. Если требуется другая функциональная конфигурация модели, создаётся новая ModelDefinition с новым UUID.

```text
ModelDefinition
├── id
├── display_name
├── provider_type
├── api_compatibility
├── base_url
├── configured_model_name
├── resolved_model_name
├── resolved_at
├── credential_secret_id
├── capabilities
├── context_window
├── max_output_tokens
├── supports_tools
├── supports_structured_output
├── supports_streaming
├── supports_cancellation
├── supports_vision
├── supports_responses_api
├── supports_embeddings
├── embedding_dimension
├── verification_status
├── health_status
├── enabled
├── created_at
└── updated_at
```

После первого использования ModelDefinition её функциональные поля считаются immutable. Для изменения provider, endpoint, model name, capabilities, limits, adapter mode или embedding dimension создаётся новая ModelDefinition.

Разрешено изменять operational metadata, health state, enabled state и ссылку на ротируемый credential.

Provider alias может быть указан в `configured_model_name`, но при verification сохраняется фактически разрешённый `resolved_model_name`. Изменение результата разрешения alias считается configuration drift и требует новой ModelDefinition.

Пользователь Project выбирает только модель, которая одновременно:

```text
enabled platform model
AND allowed for Space
AND healthy or degraded
AND verification_status = verified
```

Собственные пользовательские model credentials не поддерживаются.

### ModelPriceVersion

Цена хранится независимо от ModelDefinition:

```text
ModelPriceVersion
├── id
├── model_definition_id
├── currency
├── input_per_million
├── cached_input_per_million
├── output_per_million
├── effective_from
├── effective_to
└── created_at
```

ModelPriceVersion immutable. Изменение цены создаёт новую запись и не требует новой ModelDefinition.

---

## 62. Model adapter

Все модели рассматриваются как provider-neutral OpenAI-compatible endpoints. Понятие `local model` в доменной модели не используется.

```text
supports_responses_api = true
→ Responses-compatible adapter

supports_responses_api = false
→ Chat Completions-compatible adapter

supports_embeddings = true
→ Embeddings-compatible adapter
```

Ollama, vLLM, SGLang и другие совместимые endpoints подключаются через `base_url`, model name и optional credential secret.

---

## 63. Model gateway

Отдельный HTTP model gateway в MVP не создаётся.

Внутри agent-core существуют:

```text
ModelRegistryRepository
ModelClientFactory
ModelInvocationService
ModelCapabilityVerificationService
ModelHealthService
ModelUsageRecorder
```

---

## 64. Model credentials и deployment configuration

Model credentials относятся к platform scope.

`ModelDefinition` хранит только `credential_secret_id`, nullable для endpoints без authentication.

Credential:

- не возвращается через API;
- не сохраняется в AgentVersion;
- не попадает в trace;
- не передаётся в Temporal input;
- расшифровывается непосредственно перед model call.

Допускается in-memory cache с TTL не более пяти минут.

Deployment может bootstrap model endpoints и model-role defaults из отдельных environment variable groups. Environment variables не являются runtime source of truth после успешной инициализации и не должны логироваться.

Логические model roles:

```text
coordinator_model_id
worker_model_id
structured_output_fallback_model_id
summary_model_id
embedding_model_id
```

---

## 65. Fallback

Fallback model задаётся через `structured_output_fallback_model_id` и используется только после нескольких невалидных structured outputs.

Fallback не используется для timeout, rate limit, недоступности primary, provider error или budget limit.

---

## 66. ModelUsageRecord

```text
id
project_id
session_id
run_id
agent_invocation_id
agent_id
agent_version_id
model_id
model_price_version_id
provider_request_id
input_tokens
output_tokens
cached_input_tokens
reasoning_tokens
request_count
latency_ms
estimated_cost
status
created_at
```

Prompt и output в usage table не сохраняются.

Расчёт стоимости выполняется по ModelPriceVersion, активной на момент начала model call. Если endpoint имеет нулевую цену, usage всё равно сохраняется.

---

## 67. Бюджеты и квоты

Поддерживаются дневная и недельная Project cost quota, token budgets Run/Invocation, output token limit, tool-call limit и invocation limit.

Monetary amounts хранятся в фиксированной минимальной единице без floating-point arithmetic.

Используется post-factum settlement без предварительного reservation.

Перед model call проверяется уже зафиксированный usage. Если quota уже исчерпана, новый model call не начинается и Run получает `BUDGET_BLOCKED`.

После ответа фактическое usage атомарно добавляется в quota ledger. Параллельные Run могут совместно превысить лимит; отрицательный остаток допускается и сохраняется как overdraft. Уже начатый model call не отменяется.

Используются:

```text
project_quota_policies
project_quota_buckets
quota_ledger
```

`quota_reservations` не используется.

Settlement идемпотентен по `ModelUsageRecord.id` и, при наличии, `provider_request_id`.

Иерархия limits:

```text
platform default / maximum
→ Space override / maximum
→ Project override
```

`Project limit ≤ Space maximum ≤ platform maximum`. Отсутствие Project override означает наследование, а не unlimited.

# Часть IX. Контекст, память и RAG

## 68. История Session

Полная история хранится для:

- аудита;
- UI;
- построения summary;
- поиска;
- расследования.

Полная история не передаётся модели автоматически.

История не переносится между Session как разговорный контекст.

---

## 69. Контекст координатора

```text
system instructions
project context
permissions snapshot
active task and linked entities
project state
current trigger or user input
relevant RAG results
workflow state
completed worker results
```

---

## 70. Prompt layers работника

```text
1. platform system policy
2. immutable security policy
3. project policy
4. user worker instructions
5. DelegationPacket
6. runtime tool/output instructions
```

Верхний слой имеет приоритет.

---

## 71. Qdrant

Используется одна общая collection для совместимой embedding model.

Обязательный filter:

```text
project_id = current_project_id
```

Опциональные filters:

```text
source_type
source_id
session_id
task_id
created_at
visibility
content_version
```

---

## 72. Индексируемые данные

Индексируются:

- session summaries;
- сообщения;
- комментарии;
- задачи;
- документы;
- результаты работников;
- решения;
- ProjectState;
- CRM-данные;
- procurement-данные;
- разрешённые артефакты.

Секретные данные в RAG не добавляются.

---

## 73. Embeddings

Embedding model подключается как отдельная ModelDefinition с `supports_embeddings = true` через OpenAI-compatible embeddings endpoint.

Предпочтительная модель MVP:

```text
Qwen3-Embedding-8B
embedding_dimension = 4096
context_length = 32768
```

Допустимая конфигурация при меньшем доступном объёме ресурсов:

```text
Qwen3-Embedding-4B
embedding_dimension = 2560
context_length = 32768
```

Выбранные модель и размерность фиксируются на уровне deployment и Qdrant collection. Смена модели или размерности выполняется только через embedding migration.

Defaults ingestion:

```text
chunk_size = 800 tokens
chunk_overlap = 120 tokens
embedding_batch_size = 32
default_top_k = 10
```

---

## 74. Embedding migration

При смене модели:

1. создаётся новая collection;
2. выполняется переиндексация;
3. проводится проверка;
4. переключается alias;
5. старая collection сохраняется для rollback;
6. затем удаляется административно.

Metadata:

```text
embedding_model_id
embedding_dimension
embedding_version
```

---

## 75. Session summary

Для summary используется отдельная ModelDefinition, указанная в `summary_model_id`.

Summary model подключается через тот же OpenAI-compatible API contract и не классифицируется как локальная или внешняя.

Structured result:

```json
{
  "summary": "...",
  "decisions": [],
  "open_questions": [],
  "completed_actions": [],
  "pending_actions": [],
  "linked_entities": [],
  "important_facts": [],
  "memory_tags": []
}
```

Summary создаётся при закрытии Session и индексируется в Qdrant.

---

## 76. ProjectState

Доменные сервисы предоставляют факты.

Отдельный аналитический процесс создаёт summary и риски.

```json
{
  "project_id": "UUID",
  "version": 1,
  "stage": "execution",
  "health": "at_risk",
  "summary": "...",
  "blockers": [],
  "risks": [],
  "critical_tasks": [],
  "overdue_tasks": [],
  "dependencies": [],
  "upcoming_deadlines": [],
  "decisions_required": [],
  "generated_at": "UTC+00:00",
  "source_versions": {}
}
```

LLM-поля должны отличаться от детерминированных фактов.

---

# Часть X. MCP

## 77. Системный MCP

Task-management MCP:

- отдельный HTTP-сервис;
- работает во внутренней сети;
- не отключается пользователем;
- endpoint не меняется;
- координатор получает mutating tools согласно permissions;
- работники получают только read-only tools.

Read tools:

```text
get_task
search_tasks
get_project
get_project_state
list_tasks
list_comments
get_user
get_task_dependencies
get_task_artifacts
```

Mutating tools:

```text
create_task
update_task
change_status
assign_user
add_comment
link_task
attach_artifact
delete_task
```

---

## 78. Пользовательские MCP

Поддерживаются:

- внутренние MCP;
- публичные пользовательские MCP.

Transport MVP:

```text
Streamable HTTP
```

Публичный MCP:

- только HTTPS;
- TLS verification;
- SSRF protection;
- запрет loopback;
- запрет link-local;
- запрет metadata endpoints;
- защита от DNS rebinding;
- redirect control;
- timeout;
- response size limit;
- egress filtering.

---

## 79. MCP auth

### Пользовательские MCP

В MVP поддерживаются только:

```text
API key в настраиваемом HTTP header
Basic Auth
```

Credentials принадлежат Project и хранятся через `Secret`/`SecretVersion`.

OAuth authorization code flow, PKCE, callback API, access/refresh tokens, OAuth discovery, refresh и revoke не входят в MVP.

### Системные MCP

Системные MCP используют workload authentication `agent-core` через Keycloak `client_credentials` и OAuth2 Proxy. Это отдельный machine-to-machine механизм и не означает поддержку OAuth для пользовательских MCP.

---

## 80. MCP discovery

Discovery выполняется:

- при создании;
- вручную.

Сохраняются:

```text
tool name
description
input schema
output schema
server version
discovery timestamp
schema hash
```

Описание tool нельзя менять.

---

## 81. Schema changes

При изменении schema:

1. создаётся новая версия;
2. старая сохраняется;
3. tool блокируется для новых Run;
4. `project_admin` повторно разрешает tool;
5. новая schema становится активной.

---

## 82. MCP lifecycle

Системный MCP использует pooled connection.

Пользовательский MCP подключается на время Invocation.

Tool names:

```text
{server_name}__{tool_name}
```

---

# Часть XI. Permissions и Approval

## 83. Permission model

Permission и Approval policy являются независимыми механизмами.

Permission отвечает на вопрос, имеет ли агент право вызвать tool. Approval policy отвечает на вопрос, требуется ли подтверждение человека перед уже разрешённым вызовом.

Approval не может расширить базовые permissions.

Порядок вычисления:

```text
1. platform security policy
2. Agent permission
3. tool risk policy
4. Project approval policy
5. Workflow node policy
6. AgentVersion approval policy
7. Run ApprovalGrant
8. Specific Approval
```

```text
DENY сильнее ALLOW
REQUIRE_APPROVAL сильнее BYPASS_APPROVAL
нижний уровень не может ослабить обязательное требование верхнего уровня
```

---

## 84. Project и Agent approval policy

Project approval policy является risk-based policy, а не одним глобальным boolean.

```json
{
  "default_mode": "risk_based",
  "risk_rules": {
    "low": "allow",
    "medium": "require_approval",
    "high": "require_approval",
    "critical": "require_approval"
  },
  "server_overrides": [],
  "tool_overrides": [],
  "agent_overrides": []
}
```

Если любое применимое правило требует Approval, итоговое решение — `REQUIRE_APPROVAL`.

Постоянный bypass разрешён для `low`; для `medium` может быть разрешён `project_admin`; для `high` и `critical` запрещён.

AgentVersion approval policy создаётся `project_admin`, проходит проверку верхних policies, создаёт AuditEvent и не влияет на уже активные Run.

---

## 85. Approvers и routing

Approvers выбираются по fallback-цепочке:

```text
1. explicit approvers из Workflow node
2. explicit approvers из AutomationRule
3. активные ответственные связанной задачи
4. инициатор Run
```

Используется первый непустой допустимый уровень. Если ответственных несколько, все входят в `allowed_approver_ids`, и первое валидное approve/reject завершает Approval.

Для automation/system Run без approver возвращается `APPROVER_NOT_CONFIGURED`. `project_admin` не является неявным approver.

При создании Approval сохраняется snapshot списка и источника approvers. При решении повторно проверяется Project membership и актуальность доступа.

Reroute выполняется явно: старый Approval получает `superseded`, создаётся новый Approval с новым routing snapshot.

---

## 86. Approval

Approval связан с точным payload hash и содержит `allowed_approver_ids`, `approver_source`, `approver_source_entity_id` и стандартные identifiers Run/Agent/Workflow/tool.

Разрешение Approval подчиняется общему архитектурному правилу CDC-идемпотентности. Конкретный immutable `resolution_id` определяется в event-сценарии Approval.

---

## 87. Редактирование Approval payload

После изменения аргументов создаётся revision, выполняются schema, permission, constraints и risk validation, затем создаётся новый hash. Если требуется другой approver или routing, старый Approval становится `superseded`, а новый создаётся отдельно.

---

## 88. ApprovalGrant

Run-level grant ограничен:

```text
project_id
run_id
agent_id
tool_name
constraints
max_uses
expires_at
```

Grant не расширяет permissions, не действует для будущих Run, прекращается после исчерпания uses/expiry/завершения Run/отзыва/выхода payload за constraints и не может отменить верхнюю security policy.

# Часть XII. Ошибки и идемпотентность

## 89. Классификация ошибок

```text
TRANSIENT
RATE_LIMITED
AUTH_EXPIRED
INVALID_OUTPUT
BUSINESS_REJECT
PERMISSION_DENIED
VALIDATION_ERROR
SIDE_EFFECT_UNKNOWN
FATAL
```

---

## 90. Поведение

```text
TRANSIENT
→ retry

RATE_LIMITED
→ retry с Retry-After

AUTH_EXPIRED
→ refresh credentials и retry

INVALID_OUTPUT
→ repair/fallback

BUSINESS_REJECT
→ альтернативное решение координатора

PERMISSION_DENIED
→ без retry

VALIDATION_ERROR
→ исправление аргументов

SIDE_EFFECT_UNKNOWN
→ reconciliation

FATAL
→ завершение
```

---

## 91. Идемпотентность MCP

Для внутренних mutating tools обязателен:

```text
idempotency_key
```

Формат:

```text
project_id:run_id:node_id:attempt_group
```

Для пользовательских MCP поддержка не обязательна.

Без idempotency blind retry запрещён.

---

# Часть XIII. Kafka и автоматизации

## 92. Kafka и CDC

PostgreSQL является source of truth materialized business state. Kafka используется как интеграционная шина, а публикация изменений PostgreSQL выполняется стандартным Debezium PostgreSQL Connector через WAL/`pgoutput`.

Не используются:

- Debezium Outbox Event Router;
- Python outbox publisher;
- polling/claim/lease outbox rows;
- прямой dual-write PostgreSQL + Kafka для одного логического изменения.

Для semantic event допускается обычная доменная append-only таблица `events`, публикуемая как standard table CDC без Outbox Event Router.

---

## 93. Pipelines

Сервис `pipelines` отвечает за automation rules, получение доменных CDC/events, сопоставление условий, trigger log и создание trigger records.

Agent-core отвечает за deduplication, создание Session/Run, запуск Temporal, DAG, агентов, MCP, Approval и traces.

---

## 94. CDC contract

Используется стандартный Debezium envelope. Операции `c`, `u`, `d` и snapshot `r` являются частью transport contract.

Schema changes таблиц, включённых в CDC, считаются Kafka schema changes и требуют совместимого rollout.

Business logic не должна использовать PostgreSQL LSN, Kafka offset, Debezium transaction metadata или `op` как долговечный business idempotency key.

---

## 95. Automation deduplication

Для каждого trigger/event scenario определяется стабильный business operation identifier. Для automation rule базовый кандидат:

```text
automation_rule_id + source_event_id
```

Повторная доставка не должна создавать новый Run или повторять side effect.

---

## 96. Архитектурное правило идемпотентности CDC

Debezium и Kafka обеспечивают at-least-once delivery, а не exactly-once business effect.

Каждая CDC-triggered операция с side effect обязана иметь стабильный business operation identifier.

Если immutable `id` сущности однозначно идентифицирует одноразовую операцию, используется он. Если entity ID не различает конкретный переход или повторяемое действие, создаётся immutable `resolution_id` или `idempotency_id` атомарно с бизнес-переходом.

Тот же identifier используется при retry, Kafka replay и snapshot replay и передаётся в Temporal, MCP и конечную систему.

Конечный handler обязан распознавать duplicate и не повторять business effect.

Не используются как business idempotency key:

- PostgreSQL LSN;
- Kafka topic/partition/offset;
- Debezium `op`;
- transaction metadata;
- сравнение `before/after` само по себе.

Append-only table PK пригоден только если одна строка действительно является одной независимой бизнес-операцией.

Целевая гарантия:

```text
at-least-once CDC delivery
+ idempotent consumption
+ idempotent target operation
= effectively-once business effect
```

Система не заявляет exactly-once delivery между PostgreSQL, Debezium, Kafka, Temporal и внешними сервисами.

# Часть XIV. Безопасность

## 97. Пользовательская аутентификация

Используются Keycloak, единый realm, OAuth2 Proxy и `ncn-authz-api`.

Project roles хранятся в `ncn-authz-api`. Agent-core получает проверенный identity payload и самостоятельно проверяет `project_id`, actor identity и Project constraints.

Workload OAuth системного MCP не используется для пользовательского login flow и не передаётся агентам.

---

## 98. Machine-to-machine системного MCP

Применяется паттерн централизованной авторизации через доверенный `agent-core`.

```text
Keycloak
→ аутентифицирует workload agent-core
→ выдаёт service access token через client_credentials

OAuth2 Proxy
→ проверяет signature, issuer, audience, exp и nbf
→ разрешает доступ только доверенному agent-core

agent-core
→ является PDP и PEP для Agent permissions/Approval
→ формирует trusted execution context
→ вызывает разрешённый MCP tool

MCP
→ доверяет authorization decision agent-core
→ проверяет schema, Project scope, domain invariants и idempotency
```

Для каждого системного MCP используется отдельная audience. Один token не должен содержать audiences других системных MCP.

Service token может использоваться для нескольких MCP-вызовов до `exp`, хранится только в памяти и не передаётся в PostgreSQL, Temporal, Kafka, traces или logs. Рекомендуемый TTL — 1–5 минут, refresh margin — 30 секунд.

OAuth2 Proxy не должен перенаправлять API-клиента на interactive login, принимать arbitrary issuer, использовать trusted-IP bypass или пропускать authentication routes.

Входящие identity headers удаляются или перезаписываются. Проверенный bearer token не передаётся upstream MCP application.

Непосредственно перед MCP call agent-core проверяет Agent permission, Project constraints, tool risk policy, Approval policies/grants, payload constraints, Project isolation и idempotency key.

MCP использует только `execution_context.project_id`, сформированный backend-кодом, и не доверяет `arguments.project_id`.

Компрометация процесса agent-core или его client credentials признаётся компрометацией доступных ему системных MCP. Если эта доверительная граница перестаёт быть допустимой, требуется per-call capability token, online PDP/introspection или mTLS + отдельный PDP.

---

## 99. Secrets

Используются:

```text
Secret
└── SecretVersion
```

SecretVersion immutable и имеет статус:

```text
active
superseded
revoked
destroyed
```

Project secrets включают MCP API keys, Basic Auth и другие Project integration credentials.

Bootstrap/platform secrets включают PostgreSQL, Kafka, Temporal, Keycloak service-account credentials, model provider credentials и master-key ring.

Plaintext secret API отсутствует. Доступны create, replace/rotate, revoke и metadata.

---

## 100. Encryption и master-key rotation

Для каждого SecretVersion создаётся отдельный случайный DEK.

```text
plaintext
→ AES-256-GCM with DEK
→ ciphertext

DEK
→ AES-256-GCM with active master key
→ encrypted_dek
```

PostgreSQL хранит ciphertext, nonce/tag, encrypted_dek, master_key_id/version и metadata. Master keys в PostgreSQL не хранятся.

Для обычного Docker/deployment bootstrap secrets и key ring передаются через environment variables, `.env` вне Git или mounted secret. Для Kubernetes — через Kubernetes Secrets; дополнительные требования к Kubernetes hardening определяются отдельно.

Ротация master key:

1. добавить новый key version;
2. сделать его active;
3. новые SecretVersion шифровать новым key;
4. перешифровать только DEK существующих записей;
5. проверить отсутствие ссылок на старый key;
6. удалить старый key из deployment secret.

Расшифрованный Project secret существует только на время Invocation. Для model provider credentials допускается отдельный TTL cache до пяти минут.

# Часть XV. Artifact storage

## 101. MinIO

Используется MinIO.

Максимальный файл:

```text
50 MiB
```

MIME types:

```text
application/pdf
application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

Используется multipart upload.

Bucket не публичный.

Доступ через presigned URL.

Object key:

```text
projects/{project_id}/artifacts/{artifact_id}/source
```

---

## 102. PDF

Извлекается только текстовый слой.

Metadata:

```text
page_number
chunk_index
content_hash
```

OCR отсутствует.

---

## 103. DOCX

Извлекаются:

- headings;
- paragraphs;
- простой текст таблиц;
- порядок элементов.

---

# Часть XVI. Tracing и аудит

## 104. Trace

Пользователи с permission на trace видят одинаковое представление.

Отображаются:

- план;
- статусы nodes;
- agents;
- workers;
- tools;
- approvals;
- warnings;
- errors;
- model usage;
- duration;
- retries;
- итог.

Не отображаются:

- reasoning;
- chain of thought;
- secrets;
- auth headers;
- plaintext credentials;
- service access tokens системного MCP;
- полный RunState.

---

## 105. RunEvent

```text
run.started
plan.created
plan.updated
agent.started
agent.completed
worker.started
worker.completed
tool.started
tool.completed
approval.requested
approval.resolved
warning.created
error.created
run.budget_blocked
run.resumed
run.cancelling
run.completed
run.failed
```

Polling:

```http
GET /api/sessions/v1/projects/{project_id}/sessions/{session_id}/runs/{run_id}/events
    ?after_sequence=120
    &limit=100
```

---

## 106. AuditEvent

Используется для:

- конфигураций;
- secrets;
- Approval;
- permissions;
- удаления;
- административных действий;
- cancellation;
- security investigations.

---

# Часть XVII. API

## 107. Namespace

```text
/api/{service}/v{version}/projects/{project_id}
```

Примеры:

```text
/api/sessions/v1/projects/{project_id}
/api/agents/v1/projects/{project_id}
/api/workflows/v1/projects/{project_id}
/api/approvals/v1/projects/{project_id}
/api/mcp/v1/projects/{project_id}
/api/models/v1/projects/{project_id}
/api/memory/v1/projects/{project_id}
/api/artifacts/v1/projects/{project_id}
```

---

## 108. Errors

Ошибки описываются отдельными моделями на базе:

```text
HTTPExceptionResponse
```

Базовая структура:

```json
{
  "status": 404,
  "detail": "Run not found",
  "code": "RUN_NOT_FOUND",
  "trace_id": "UUID"
}
```

---

## 109. Pagination

Используется:

```text
offset
limit
```

Query-модель наследуется от:

```text
ViewListQueries
```

Response:

```json
{
  "data": [],
  "meta": {
    "total_count": 0,
    "offset": 0,
    "limit": 50
  }
}
```

Используются:

```text
ViewList
MetaList
```

---

## 110. Single-resource response

Одиночный ресурс возвращается напрямую без `data` envelope.

---

## 111. PUT

PUT полностью заменяет редактируемое представление ресурса.

PUT не является optimistic locking.

Для Agent PUT создаёт новую AgentVersion.

Для Workflow PUT применяется только к draft.

---

## 112. PATCH

PATCH выполняет sparse update.

```python
data.model_dump(exclude_unset=True)
```

Отсутствующее поле не меняется.

`null` очищает nullable field.

PATCH версионируемой сущности создаёт новую immutable version.

---

# Часть XVIII. PostgreSQL и данные

## 113. Общая база

Для MVP:

```text
один PostgreSQL instance
одна database
одна schema
```

Модули могут читать чужие таблицы.

Mutating business logic должна проходить через Manager владельца.

При будущем разделении используется Kafka и Debezium.

---

## 114. Идентификаторы

```text
UUIDv4
```

Генерируются приложением.

---

## 115. Время

Хранение:

```text
TIMESTAMPTZ
UTC+00:00
```

API:

```text
ISO 8601 с Z
```

Frontend выполняет локализацию.

---

## 116. Foreign keys

Внутри логического модуля разрешены foreign keys.

Между будущими сервисами используются UUID без обязательных FK.

---

## 117. Удаление

Soft delete:

```text
Agent
MCPConfiguration
WorkflowDefinition
AutomationRule
Artifact
```

Session удаляется deletion workflow.

---

## 118. Транзакции

Все связанные изменения materialized business state выполняются в одной:

```text
Services.database.session()
```

PostgreSQL commit является точкой фиксации business state.

Явный `SELECT FOR UPDATE` по умолчанию не используется. Для защиты применяются:

- unique constraints;
- partial unique indexes;
- conditional updates;
- `ON CONFLICT`;
- retry conflicts;
- idempotency keys.

После commit Debezium читает WAL и публикует standard CDC records в Kafka.

Запрещён direct dual-write PostgreSQL + Kafka для одного логического изменения.

Если необходим semantic event, доменный Manager атомарно записывает обычную append-only строку в domain-owned `events` table в той же транзакции. Эта таблица публикуется стандартным CDC без Outbox Event Router.

---

# Часть XIX. Backend-регламент

## 119. Порядок источников

```text
1. <backend>/AGENTS.md
2. контракт задачи
3. database-methods.md
4. kafka-streaming.md
5. ближайший рабочий модуль
6. template
```

Ближайший рабочий код имеет приоритет над универсальным template.

---

## 120. Слои

```text
models/sqlalchemy
models/pydantic/dto
models/pydantic/api
models/pydantic/stream
models/enum
api/db
api/managers
api/router
api/stream
```

---

## 121. Router

Router:

- тонкий;
- объявляет endpoint;
- принимает dependencies;
- вызывает Manager;
- не содержит business logic;
- не содержит SQL;
- не вызывает MCP и LLM.

Итоговый path формируется:

```text
/api/{service}/v1
+
/projects/{project_id}/...
```

---

## 122. Manager

Manager отвечает за:

- authorization;
- project scope;
- business validation;
- orchestration repositories;
- DB transaction;
- Kafka production;
- DTO;
- API response;
- перевод ошибок.

---

## 123. Repository

Repository наследуется от:

```text
BaseDatabaseGeneric
```

Обязательные generic attributes:

```text
database
_table
_id
_model
_model_create
_model_update
```

---

## 124. Generic methods

```text
create
bulk_create
get
get_by_ids
get_list
get_paginated_list
get_count
update
bulk_update
upsert
bulk_upsert
delete
delete_many
delete_list
```

Не создаются thin wrappers для простых filters.

Custom methods — только для:

- join;
- aggregation;
- CTE;
- tuple filter;
- сложной сортировки;
- custom DTO.

---

## 125. DTO

```text
ResourceDTO
ResourceCreateDTO
ResourceUpdateFieldsDTO
```

Используются:

```text
OrmModel
UUIDModel
NoneValidationMixin
```

---

## 126. API models

```text
ResourceAPI
ResourceListItemAPI
GetResourceResponse
GetResourceListQueries
GetResourceListResponse
PostResourceRequest
PostResourceResponse
PutResourceRequest
PutResourceResponse
PatchResourceRequest
PatchResourceResponse
```

Фактический состав зависит от домена.

---

## 127. SQLAlchemy

Модели наследуются от:

```text
SQLAlchemyBase
```

Поля DTO, API и SQLAlchemy должны совпадать по:

- имени;
- типу;
- nullable;
- семантике.

---

## 128. Kafka models

Stream model:

```python
class TriggerEventStream(OrmModel):
    ...

    class Meta:
        topic = "..."
```

Topic берётся только через:

```text
Model.Meta.topic
```

KafkaBroker сам выполняет Avro и Schema Registry operations.

---

## 129. Listener

```python
@Services.broker.listen(...)
```

Listener:

- имеет точную Pydantic-аннотацию;
- может принимать batch;
- только логирует получение;
- вызывает Manager.

---

## 130. Producer

```python
await Services.broker.produce(
    topic=Model.Meta.topic,
    message=Model(...),
)
```

При batch выполняется один flush после цикла.

---

## 131. Registration hubs

Обязательная регистрация:

```text
models/pydantic/__init__.py
models/pydantic/stream/__init__.py
models/sqlalchemy/__init__.py
models/enum/__init__.py
api/db/db.py
api/managers/managers.py
api/router/router.py
api/stream/__init__.py
```

---

## 132. Ограничения skill реализации

Skill не должен:

- создавать Alembic migrations;
- редактировать migrations;
- запускать код;
- запускать тесты;
- запускать сервер;
- запускать formatter;
- запускать linter;
- выполнять compile checks.

В handoff указываются:

- требуемые migrations;
- непройденные runtime checks;
- непройденные tests;
- внешние зависимости.

---

# Часть XX. Deployment и health

## 133. MVP deployment

Используется один Python image и один Python process для FastAPI, Kafka consumers, Temporal worker и background supervisors.

PostgreSQL, Kafka, Debezium Connect, Temporal, Qdrant, MinIO, Keycloak, OAuth2 Proxy, model endpoints и MCP services являются внешними runtime dependencies deployment.

Python outbox publisher отсутствует.

---

## 134. Lifecycle

Startup:

1. инициализация Services;
2. проверка PostgreSQL, Temporal, Kafka и критичных bootstrap secrets;
3. проверка Keycloak service token для системного MCP;
4. запуск Temporal worker;
5. запуск Kafka consumers;
6. запуск background supervisors;
7. готовность API.

Shutdown:

1. запрет новых mutating requests;
2. остановка Kafka consumption;
3. завершение handlers;
4. graceful Temporal worker shutdown;
5. отмена background tasks;
6. закрытие connections.

---

## 135. Health

`GET /health` проверяет FastAPI lifecycle, PostgreSQL, Temporal worker/connection, Kafka consumers, Keycloak connectivity/token acquisition для обязательных системных MCP и background supervisors.

Debezium health/lag контролируется как отдельная deployment dependency.

При критической ошибке возвращается `503 Service Unavailable`.

# Часть XXI. Форматы результатов

## 136. WorkerResultEnvelope

```json
{
  "status": "completed",
  "summary": "Краткий результат",
  "data": {},
  "artifacts": [],
  "proposed_actions": [],
  "performed_actions": [],
  "warnings": [],
  "errors": [],
  "requires_follow_up": false
}
```

Статусы:

```text
completed
partial
failed
cancelled
waiting_for_approval
blocked
```

---

## 137. RunResultEnvelope

```json
{
  "status": "completed",
  "message_id": "UUID",
  "summary": "...",
  "data": {},
  "artifacts": [],
  "warnings": [],
  "completed_at": "UTC+00:00"
}
```

Статусы:

```text
completed
partially_completed
failed
cancelled
```

---

# Часть XXII. Открытые вопросы

Открытые вопросы не отменяют утверждённые решения. Они должны быть закрыты в следующих версиях контракта до реализации соответствующего участка.

## 138. Первый объём реализации

Необходимо определить первый вертикальный срез:

- только Agents CRUD;
- Agents + Model Registry;
- Agents + MCP;
- Sessions + Runs;
- полный минимальный happy path;
- automation-triggered сценарий.

---

## 139. Точные PostgreSQL-таблицы

Необходимо зафиксировать:

- полный перечень таблиц;
- поля;
- типы;
- nullable;
- indexes;
- unique constraints;
- внутренние foreign keys;
- JSONB schemas;
- ownership модулей.

---

## 140. Точные API-контракты

Для каждого service namespace необходимо определить:

- endpoints;
- request DTO;
- response DTO;
- PUT support;
- PATCH support;
- archive/disable commands;
- status codes;
- HTTPExceptionResponse models;
- pagination filters;
- sorting;
- search fields.

---

## 141. Регламент pagination

Известно, что используются:

```text
ViewListQueries
ViewList
MetaList
offset
limit
```

Требуется изучить фактические базовые модели репозитория и зафиксировать:

- точные поля;
- default limit;
- maximum limit;
- sort syntax;
- filter syntax;
- search semantics.

---

## 142. `space_admin` — закрыто

`space_admin` является отдельной control-plane ролью, не наследует `project_admin`, не получает автоматического доступа к данным Project и не использует break-glass. Для data-plane доступа назначается обычная Project role.

---

## 143. Approval routing — закрыто

Зафиксированы fallback-цепочка approvers, one-of-many resolution, snapshot списка, повторная проверка membership и explicit reroute через `superseded` старого Approval.

---

## 144. Agent approval policy и ApprovalGrant — закрыто

Permission и Approval разделены. Постоянная AgentVersion policy управляется `project_admin` и может ослаблять Approval только для допустимых low/medium операций. Run-level ApprovalGrant строго ограничен scope.

---

## 145. Project approval mode — закрыто

Используется risk-based Project policy с overrides. `DENY` и `REQUIRE_APPROVAL` имеют приоритет.

---

## 146. Project quotas — закрыто

Зафиксированы monetary/token limits, post-factum settlement без reservation, допустимый concurrent overdraft, quota ledger и наследование platform → Space → Project.

---

## 147. Model Registry administration — закрыто на уровне архитектуры

Используются `platform_admin`, одна immutable-after-use ModelDefinition без ModelVersion, отдельная ModelPriceVersion, capability verification, health state и model allowlists.

---

## 148. Конкретные модели — закрыто на уровне ролей и embedding

Coordinator/worker/fallback/summary model IDs задаются deployment configuration. Для embedding предпочтительна Qwen3-Embedding-8B/4096, допустима Qwen3-Embedding-4B/2560.

---

## 149. MCP OAuth — исключено из MVP

OAuth пользовательских MCP, callback, PKCE, access/refresh tokens, discovery, refresh и revoke не реализуются. Поддерживаются API key и Basic Auth. Workload `client_credentials` системного MCP описан отдельно в разделе 98.

---

## 150. Machine-to-machine системного MCP — закрыто

Принят Keycloak service account `agent-core` + отдельная audience каждого MCP + OAuth2 Proxy. Agent-core является authorization authority для агентов; MCP сохраняет schema/domain/idempotency validation. Per-call delegation JWT, собственные ES256/JWKS и custom Keycloak grant не используются.

---

## 151. Secrets production path — закрыто для MVP

Bootstrap secrets передаются через `.env`/environment/mounted secret, для Kubernetes — Kubernetes Secrets. Dynamic Project secrets хранятся как encrypted SecretVersion в PostgreSQL с master-key rotation. Vault/KMS не являются обязательными компонентами.

---

## 152. CEL runtime — исключено из MVP

CEL, Python CEL library и `condition` nodes не используются. Семантическое ветвление выполняет координатор через `coordinator_decision` и strict structured output. Возврат CEL возможен post-MVP для детерминированного no-code конструктора правил.

---

## 153. Data mapping runtime — закрыто для MVP

Полноценный JSONPath не используется. Применяются ограниченные source scopes и RFC 6901 JSON Pointer для source/target paths, без filters, expressions и неявного type coercion.

---

## 154. Dynamic coordinator plan — частично закрыто

Зафиксировано:

- отдельный decision-agent не создаётся;
- координатор выбирает только разрешённые WorkflowVersion/plan snapshot переходы;
- решения возвращаются как strict structured output;
- backend валидирует references, permissions, Approval, limits и plan mutations;
- уже выполненные nodes и side effects immutable;
- CEL в dynamic plan отсутствует.

Точный JSON Schema DynamicPlanRevision, limits revisions и полный набор validation errors остаются для следующего уточнения.

---

## 155. ProjectState pipeline

Не определены:

- источники фактов;
- частота расчёта;
- инициатор расчёта;
- model prompt;
- structured schema;
- confidence;
- stale-state rules;
- повторная генерация;
- storage table.

---

## 156. RAG ingestion

Необходимо определить:

- Kafka events для индексации;
- reindex commands;
- batching;
- failure queue;
- tombstones;
- duplicate chunks;
- content version;
- stale chunks;
- поиск по нескольким типам источников;
- ranking и reranking.

---

## 157. RAG ACL future model

В MVP секретные данные не индексируются.

Для будущего необходимо решить:

- private Session;
- закрытые задачи;
- CRM ACL;
- department-level access;
- user-level access;
- metadata filters;
- reindex при смене ACL.

---

## 158. Artifact processing

Не выбраны конкретные библиотеки для:

- PDF extraction;
- DOCX extraction;
- MIME detection;
- token counting;
- chunking.

Не определены:

- malware scanning;
- encrypted PDF;
- corrupted files;
- password-protected DOCX;
- extraction retry;
- quarantine.

---

## 159. Session deletion

Нужно определить точную реализацию удаления:

- Temporal Workflow termination;
- Temporal history retention;
- удаление Search Attributes;
- Qdrant consistency;
- MinIO shared artifacts;
- audit anonymization;
- recovery window.

---

## 160. Retention

Автоматическая business retention отсутствует.

Позднее необходимо определить:

- Session retention;
- RunEvent retention;
- AuditEvent retention;
- Artifact retention;
- Qdrant retention;
- Kafka retention;
- Temporal retention;
- backup retention;
- deleted secret retention.

---

## 161. Continue-As-New

Не определены thresholds:

- количество Temporal events;
- размер history;
- период;
- количество Run;
- перенос pending Approval;
- перенос message queue.

---

## 162. Observability

Не определены:

- logging library;
- log schema;
- metrics;
- Prometheus names;
- OpenTelemetry exporters;
- alerting;
- dashboards;
- SLO;
- trace sampling;
- correlation propagation.

---

## 163. Нагрузка и SLA

Пока отсутствуют:

- количество Project;
- активные Session;
- Run per minute;
- Kafka throughput;
- размер DB;
- model concurrency;
- MCP concurrency;
- latency SLO;
- availability SLO;
- polling interval;
- maximum active waiting workflows.

---

## 164. Process supervision

В MVP всё работает в одном Python process.

Необходимо определить:

- supervision background tasks;
- поведение при падении Kafka consumer;
- поведение при падении Temporal worker;
- порядок shutdown;
- readiness delay;
- restart policy;
- event loop blocking protection.

---

## 165. Database concurrency — архитектурная база зафиксирована

Используются unique constraints, conditional updates, `ON CONFLICT`, monotonic sequence allocation и idempotency keys.

Зафиксировано:

- CREATED и QUEUED считаются active Run statuses;
- partial unique index обеспечивает не более одного active Run на Session;
- `sessions.active_run_id` является materialized pointer;
- Message и RunEvent sequence уникальны и монотонны, gaps разрешены;
- Approval resolution финален;
- quota settlement выполняется без reservation;
- outbox claiming отсутствует, поскольку Python outbox publisher не используется.

Точные DDL/atomic statements будут определены вместе с вопросом 139.

---

## 166. Debezium readiness — закрыто на уровне паттерна

Используется стандартный Debezium PostgreSQL Connector с `pgoutput`, filtered publication, explicit `table.include.list`, heartbeat и RegexRouter. Raw CDC публикуется только для явно включённых business tables.

Базовый deployment template:

```json
{
  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "topic.creation.default.partitions": "1",
  "transforms.AddPrefix.type": "org.apache.kafka.connect.transforms.RegexRouter",
  "slot.name": "export__business_logic__0",
  "database.query.timeout.ms": "0",
  "publication.name": "export__business_logic__0__publication",
  "retriable.restart.connector.wait.ms": "30000",
  "transforms": "AddPrefix",
  "slot.max.retries": "60",
  "transforms.AddPrefix.replacement": "$1.debezium.cdc.$2.0",
  "topic.creation.default.min.insync.replicas": "1",
  "slot.retry.delay.ms": "60000",
  "topic.prefix": "cyberstudio",
  "heartbeat.action.query": "INSERT INTO public.debezium_heartbeat (id, heartbeat_ts) VALUES (1, NOW()) ON CONFLICT(id) DO UPDATE SET heartbeat_ts=EXCLUDED.heartbeat_ts;",
  "transforms.AddPrefix.regex": "(.*).public.(.*)",
  "topic.creation.default.replication.factor": "-1",
  "publication.autocreate.mode": "filtered",
  "topic.creation.default.compression.type": "lz4",
  "database.user": "user",
  "database.dbname": "business-logic",
  "topic.creation.default.cleanup.policy": "compact",
  "database.server.name": "business-logic",
  "heartbeat.interval.ms": "10000",
  "plugin.name": "pgoutput",
  "database.port": "5432",
  "errors.max.retries": "-1",
  "database.hostname": "postgres",
  "database.password": "******",
  "name": "business-logic.export.business_logic.0",
  "table.include.list": "public.events,public.event_stops,public.processes,public.tasks,public.process_templates,public.debezium_heartbeat",
  "snapshot.mode": "when_needed"
}
```

Для agent-core значения name/database/slot/publication/prefix/credentials/table list определяются deployment configuration. Password передаётся через bootstrap secrets.

Не используются Outbox Event Router, Python outbox publisher и direct PostgreSQL+Kafka dual-write.

---

## 167. Kafka topics

Не определены точные:

- logical topic names;
- version suffixes;
- Avro schemas;
- compatibility mode;
- consumer groups;
- DLQ topics;
- retry topics;
- retention;
- partition count.

---

## 168. Error code registry

Необходимо создать единый список:

- API codes;
- Run errors;
- AgentInvocation errors;
- Tool errors;
- MCP errors;
- Workflow validation errors;
- Artifact errors;
- Budget errors;
- Auth errors.

---

## 169. Политика архивирования

Нужно определить:

- восстановление archived Agent;
- восстановление MCP;
- повторное включение Workflow;
- поведение automation rule;
- очистку secrets;
- физическое удаление после archive.

---

## 170. Тестирование

Предоставленный implementation skill запрещает запуск тестов в рамках своей процедуры.

Отдельно необходимо определить:

- unit tests;
- integration tests;
- Temporal tests;
- Kafka contract tests;
- MCP mock server;
- model adapter tests;
- approval tests;
- cancellation tests;
- load tests;
- evaluation dataset агентов.

---

## 171. Python stack и версии

Архитектурные библиотеки определены концептуально, но не зафиксированы версии:

- Python;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- PostgreSQL driver;
- Temporal SDK;
- OpenAI Agents SDK;
- aiokafka-based broker;
- Qdrant client;
- MinIO client;
- JSON Schema validator;
- JSON Pointer implementation или собственный ограниченный resolver;
- encryption library.

Версии должны быть взяты из фактического backend repository и его dependency files.

---

## 172. Фактический `AGENTS.md`

Перед реализацией необходимо изучить `<backend>/AGENTS.md`.

Если его правила противоречат текущему контракту, противоречие должно быть вынесено на согласование, а не разрешено молча.

---

# Итог версии 1.3-draft

Версия 1.3-draft фиксирует:

- бизнес-назначение;
- бизнес-сценарии;
- мультитенантность;
- роли;
- координатора и работников;
- Temporal-managed delegation;
- Session и Run;
- Workflow/DAG;
- Approval;
- MCP;
- модели;
- бюджеты;
- RAG;
- Artifacts;
- Kafka;
- безопасность;
- tracing;
- API conventions;
- PostgreSQL;
- deployment;
- backend coding regulations.

Следующие версии должны не переписывать систему целиком, а последовательно закрывать открытые вопросы и добавлять точные схемы реализации.