# Runtime и эксплуатация

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3734-3815 -->
<!-- SOURCE-CONTENT-START -->
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

