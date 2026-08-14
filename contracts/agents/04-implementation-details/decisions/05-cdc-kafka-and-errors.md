# CDC, Kafka и ошибки

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3816-3895 -->
<!-- SOURCE-CONTENT-START -->
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

