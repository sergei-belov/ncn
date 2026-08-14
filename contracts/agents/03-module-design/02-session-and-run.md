# Session и Run

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:1016-1417 -->
<!-- SOURCE-CONTENT-START -->
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

