# Durable execution, MCP и безопасность

<!-- SOURCE: NCN_Contract_v2.0.md:318-457 -->
<!-- SOURCE-CONTENT-START -->
# Часть V. Durable execution и идемпотентность

## 15. Temporal contract

Один Run соответствует одному корневому Temporal Workflow.

Workflow code должен быть детерминированным. Внешние операции выполняются через Activities.

В Activities выносятся:

- model calls;
- MCP calls;
- PostgreSQL operations, не являющиеся безопасными локальными workflow calculations;
- Qdrant operations;
- object storage operations;
- extraction и embeddings.

Ожидание Approval, пользовательского ответа и cancellation реализуется как durable wait/signal, а не polling loop внутри процесса API.

## 16. Retry contract

Retry определяется классом операции, а не единым глобальным правилом.

Обязательные принципы:

- model/read operations могут повторяться при transient errors;
- mutating tool call повторяется только при наличии idempotency contract;
- non-idempotent external write автоматически не повторяется после неопределённого результата;
- validation errors не retry;
- structured output может пройти validation и не более двух repair attempts;
- исчерпание retries приводит к контролируемому node/Run result, а не к бесконечному исполнению.

Точные интервалы и timeout values задаются конфигурацией реализации.

## 17. Идемпотентность MCP

Каждый mutating MCP tool обязан объявить одну из характеристик:

- идемпотентен по природе;
- поддерживает idempotency key;
- не поддерживает безопасный retry.

Для операций с idempotency key `agent-core` формирует стабильный ключ, связанный как минимум с Run, plan node и логической попыткой операции.

MCP обязан сохранять и проверять ключ в своей доменной границе либо обеспечить эквивалентную дедупликацию.

При timeout с неизвестным исходом система не должна слепо повторять non-idempotent операцию. Такой node переходит в состояние, требующее reconciliation, ручного решения или безопасной проверки результата.

---

# Часть VI. MCP, permissions и безопасность

## 18. Tool discovery

`agent-core` получает список tools и schemas от MCP, валидирует и сохраняет snapshot, используемый конкретной конфигурацией агента или Run.

Изменение MCP schema не должно молча менять активный Run.

Перед tool call backend проверяет:

- доступность MCP и tool;
- принадлежность Project;
- Agent permissions;
- Project constraints;
- risk/approval policy;
- schema arguments;
- idempotency requirements;
- лимиты Run.

## 19. Системные MCP

Для внутренних системных MCP применяется доверенная граница:

1. `agent-core` получает service access token по `client_credentials`;
2. OAuth2 Proxy проверяет workload token и audience конкретного MCP;
3. `agent-core` является единственной точкой agent-level authorization;
4. MCP доверяет execution context от `agent-core`, но самостоятельно проверяет request schema, idempotency и доменные инварианты.

Per-tool-call delegation JWT не используется.

Компрометация `agent-core` рассматривается как компрометация доступных ему системных MCP и должна учитываться в deployment hardening.

## 20. Пользовательские MCP

В MVP разрешены API key и Basic Auth.

OAuth flow, callback, token refresh и revoke не реализуются.

Credentials:

- никогда не передаются модели;
- никогда не записываются в prompts, Run events или logs в plaintext;
- расшифровываются только непосредственно перед Invocation;
- не возвращаются через read API.

## 21. Permissions

Permissions являются deterministic backend policy.

Модель может предложить действие, но не принимает окончательное решение о доступе.

Policy должна учитывать:

- user role;
- Project membership;
- agent configuration;
- tool/action;
- resource scope;
- Project constraints;
- текущий Run state.

Project isolation является обязательным инвариантом всех repository и service operations.

## 22. Approval

Approval отделён от permission:

- permission отвечает, допустимо ли действие в принципе;
- Approval отвечает, требуется ли подтверждение человека для конкретного допустимого действия.

Approval создаётся автоматически по policy перед side effect.

Approval payload должен содержать достаточное описание действия и его аргументов. После изменения существенных аргументов прежнее решение Approval недействительно.

MVP поддерживает решение `approve` или `reject`. Маршрутизация approver определяется Project policy и проверяется backend.

После restart процесс должен продолжить ожидание или исполнение без потери решения.

## 23. Secrets

Bootstrap secrets передаются через environment/mounted secrets; в Kubernetes допускаются Kubernetes Secrets.

Динамические Project secrets хранятся в PostgreSQL только в зашифрованных immutable `SecretVersion`.

Master key не хранится в той же базе. Должна поддерживаться ротация master key без раскрытия plaintext через API.

Vault/KMS может быть добавлен позднее без изменения модели SecretVersion.

---

