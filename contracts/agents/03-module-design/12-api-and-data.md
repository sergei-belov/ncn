# API и данные

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2891-3105 -->
<!-- SOURCE-CONTENT-START -->
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

