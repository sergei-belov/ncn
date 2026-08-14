# Tracing и аудит

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2810-2890 -->
<!-- SOURCE-CONTENT-START -->
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

