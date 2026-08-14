# Kafka и автоматизации

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2564-2643 -->
<!-- SOURCE-CONTENT-START -->
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

