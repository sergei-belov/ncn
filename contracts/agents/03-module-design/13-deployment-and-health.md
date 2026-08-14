# Deployment и health

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3372-3414 -->
<!-- SOURCE-CONTENT-START -->
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

