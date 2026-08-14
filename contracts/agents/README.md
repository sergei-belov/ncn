# Архитектура мультиагентного ядра NCN

Этот каталог разделяет архитектурную документацию на четыре уровня: бизнес-контекст, архитектурные инварианты, проектирование модулей и детали реализации.

## Статус и приоритет документов

1. [`02-invariants/`](02-invariants/) — нормативный слой версии 2.0. Он отвечает на вопрос: «какие свойства системы нельзя нарушить?»
2. [`03-module-design/`](03-module-design/) — детальный дизайн подсистем, извлечённый из v1.3-draft.
3. [`04-implementation-details/`](04-implementation-details/) — конкретные параметры, backend-регламент и реестр решений v1.3-draft.
4. [`01-business/`](01-business/) — бизнес-назначение, роли, сценарии и функциональная область продукта.

Если деталь v1.3 противоречит инварианту v2.0, приоритет имеет v2.0. Такое расхождение требует обновления соответствующего module design document, а не молчаливого изменения инварианта.

Исходные документы сохранены в корне репозитория без изменений:

- [`Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md`](../Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md);
- [`NCN_Contract_v2.0.md`](../NCN_Contract_v2.0.md).

Точная карта переноса приведена в [`SOURCE_COVERAGE.md`](SOURCE_COVERAGE.md).

## 1. Бизнес-описание

- [`01-product-and-agent-roles.md`](01-business/01-product-and-agent-roles.md) — назначение продукта, координатор, работники и связь агентов с задачами.
- [`02-business-scenarios.md`](01-business/02-business-scenarios.md) — закупка, deadline, ручной диалог, прямое обращение к работнику, уточнение, документы и остановка.
- [`03-capabilities-and-domain-model.md`](01-business/03-capabilities-and-domain-model.md) — функции платформы, мультитенантность, роли и сущности исполнения.

## 2. Архитектурные инварианты

- [`00-contract-status.md`](02-invariants/00-contract-status.md) — назначение и статус контракта.
- [`01-product-boundaries.md`](02-invariants/01-product-boundaries.md) — продуктовая граница и состав MVP.
- [`02-components-and-agent-model.md`](02-invariants/02-components-and-agent-model.md) — компоненты, координатор, работники и snapshot конфигурации.
- [`03-session-run-and-plan.md`](02-invariants/03-session-run-and-plan.md) — Session, Run, единый план, revisions и ограничения.
- [`04-durable-tools-and-security.md`](02-invariants/04-durable-tools-and-security.md) — Temporal, retry, идемпотентность, MCP, permissions, Approval и secrets.
- [`05-memory-models-and-observability.md`](02-invariants/05-memory-models-and-observability.md) — RAG, артефакты, модели, результаты, tracing и audit.
- [`06-data-deployment-and-readiness.md`](02-invariants/06-data-deployment-and-readiness.md) — идентификаторы, транзакции, API, deployment и критерии готовности.
- [`07-decisions-before-development.md`](02-invariants/07-decisions-before-development.md) — границы, обязательные к закрытию до реализации.
- [`08-design-boundary-and-change-rules.md`](02-invariants/08-design-boundary-and-change-rules.md) — решения уровня module design и правила изменения контракта.

## 3. Проектирование модулей

- [`01-agent-orchestration-and-run-plan.md`](03-module-design/01-agent-orchestration-and-run-plan.md)
- [`02-session-and-run.md`](03-module-design/02-session-and-run.md)
- [`03-temporal-runtime.md`](03-module-design/03-temporal-runtime.md)
- [`04-agent-sdk-models-and-budgets.md`](03-module-design/04-agent-sdk-models-and-budgets.md)
- [`05-context-memory-and-rag.md`](03-module-design/05-context-memory-and-rag.md)
- [`06-mcp-permissions-and-approval.md`](03-module-design/06-mcp-permissions-and-approval.md)
- [`07-errors-and-idempotency.md`](03-module-design/07-errors-and-idempotency.md)
- [`08-kafka-and-automations.md`](03-module-design/08-kafka-and-automations.md)
- [`09-security-and-secrets.md`](03-module-design/09-security-and-secrets.md)
- [`10-artifact-storage.md`](03-module-design/10-artifact-storage.md)
- [`11-tracing-and-audit.md`](03-module-design/11-tracing-and-audit.md)
- [`12-api-and-data.md`](03-module-design/12-api-and-data.md)
- [`13-deployment-and-health.md`](03-module-design/13-deployment-and-health.md)
- [`14-result-envelopes.md`](03-module-design/14-result-envelopes.md)

## 4. Детали реализации и реестр решений

- [`01-retry-and-timeout-policies.md`](04-implementation-details/01-retry-and-timeout-policies.md) — численные retry/timeout policies.
- [`02-backend-regulations.md`](04-implementation-details/02-backend-regulations.md) — слои, Router, Manager, Repository, DTO, stream models и registration hubs.
- [`decisions/01-scope-data-and-api.md`](04-implementation-details/decisions/01-scope-data-and-api.md)
- [`decisions/02-closed-architecture-decisions.md`](04-implementation-details/decisions/02-closed-architecture-decisions.md)
- [`decisions/03-memory-artifacts-and-lifecycle.md`](04-implementation-details/decisions/03-memory-artifacts-and-lifecycle.md)
- [`decisions/04-runtime-and-operations.md`](04-implementation-details/decisions/04-runtime-and-operations.md)
- [`decisions/05-cdc-kafka-and-errors.md`](04-implementation-details/decisions/05-cdc-kafka-and-errors.md)
- [`decisions/06-archiving-testing-and-stack.md`](04-implementation-details/decisions/06-archiving-testing-and-stack.md)
- [`decisions/07-v1.3-summary.md`](04-implementation-details/decisions/07-v1.3-summary.md)

## Правило дальнейшего ведения

- Изменение обязательного свойства системы вносится в `02-invariants/` и требует новой версии контракта.
- Уточнение устройства отдельной подсистемы вносится в `03-module-design/`.
- Конкретные схемы, параметры, библиотеки и coding conventions относятся к `04-implementation-details/`.
- Бизнес-сценарии и продуктовые возможности поддерживаются в `01-business/` и не должны содержать скрытые технические инварианты.
