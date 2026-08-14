# Контекст, память и RAG

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2042-2240 -->
<!-- SOURCE-CONTENT-START -->
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

