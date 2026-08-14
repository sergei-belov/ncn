# Данные, deployment и готовность MVP

<!-- SOURCE: NCN_Contract_v2.0.md:566-658 -->
<!-- SOURCE-CONTENT-START -->
# Часть IX. Данные и API

## 31. Стабильные идентификаторы

Все externally addressable сущности используют UUID или эквивалентный глобально уникальный backend identifier.

Внутри plan revision допускается локальный стабильный node key. Backend связывает его с UUID сохранённой сущности.

Идентификаторы, влияющие на retry/deduplication, не должны генерироваться заново при replay Temporal Workflow.

## 32. Транзакционные инварианты

Обязательны:

- атомарное создание Run и его initial state;
- атомарное применение решения Approval;
- защита от повторного terminal transition;
- unique constraint или эквивалент для idempotency command;
- optimistic/pessimistic concurrency control там, где возможны competing updates;
- запись audit metadata в той же бизнес-транзакции либо через надёжный производный механизм.

## 33. API principles

API первого релиза должно покрывать:

- управление конфигурацией координатора;
- CRUD работников;
- подключение и проверку MCP;
- создание Session;
- отправку Message и запуск Run;
- получение Run state и events;
- cancellation;
- получение и решение Approval;
- загрузку и получение артефактов;
- базовое управление memory ingestion.

Точные endpoints, DTO, pagination и error codes определяются в модульных design specs до реализации соответствующего endpoint.

Long-running операции возвращают идентификатор Run/operation и не удерживают HTTP request до завершения.

---

# Часть X. Deployment и расширяемость

## 34. MVP deployment

Минимальный deployment включает:

- `agent-core` API;
- Temporal worker;
- PostgreSQL;
- Temporal service;
- Qdrant;
- MinIO/S3-compatible storage;
- Keycloak/OAuth2 Proxy для системных MCP при наличии таких MCP;
- один или несколько MCP servers.

Kafka и Debezium не являются обязательными для первого пользовательского happy path. Они добавляются, когда появляется подтверждённый asynchronous integration consumer или automation pipeline. Их отсутствие в первом срезе не должно менять PostgreSQL-first contract.

## 35. Расширяемость

Следующие элементы должны быть заменяемыми через interfaces/adapters:

- model provider;
- embedding provider;
- vector store;
- object storage;
- MCP transport/auth strategy;
- event publisher;
- document extractors.

Не требуется преждевременно создавать универсальную plugin framework. Достаточно явных портов на фактических границах внешних систем.

## 36. Критерии готовности MVP

MVP считается архитектурно завершённым, если:

1. happy path проходит end-to-end;
2. Run переживает restart API/worker;
3. изменение конфигурации агента не меняет активный Run;
4. worker не может вызвать неразрешённый tool;
5. mutating tool call защищён idempotency contract или не retry;
6. Approval корректно приостанавливает и возобновляет Run;
7. cross-project access блокируется;
8. structured outputs валидируются;
9. cancellation приводит к контролируемому terminal state;
10. audit позволяет восстановить последовательность действий;
11. secrets отсутствуют в API responses, logs и model context;
12. RAG возвращает только Project-scoped источники;
13. ограничения предотвращают бесконечный план и бесконтрольные расходы.

---

