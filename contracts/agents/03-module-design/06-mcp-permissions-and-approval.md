# MCP, permissions и Approval

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2241-2492 -->
<!-- SOURCE-CONTENT-START -->
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

