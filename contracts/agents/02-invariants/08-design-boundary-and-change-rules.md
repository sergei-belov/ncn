# Граница проектирования и правила изменения контракта

<!-- SOURCE: NCN_Contract_v2.0.md:746-812 -->
<!-- SOURCE-CONTENT-START -->
# Часть XII. Решения, переносимые в проектирование

Следующие вопросы не должны блокировать старт разработки и оформляются в отдельных module design documents:

- точные PostgreSQL tables, columns, indexes и JSONB schemas;
- полный endpoint registry и DTO;
- pagination syntax;
- полный error code registry;
- названия Kafka topics и Debezium connector settings;
- конкретные extraction/chunking libraries;
- детальные retry intervals и timeout numbers;
- архивирование всех конфигурационных сущностей;
- физическое удаление и retention;
- расширенные Model Registry administration screens;
- сложные quotas и billing ledger;
- ProjectState generation;
- advanced RAG ranking/reranking;
- private/department/user ACL в RAG;
- сложные automation rules;
- Workflow template versioning UI;
- post-MVP service decomposition.

Любое решение из этого списка может быть принято командой реализации при условии, что оно не нарушает инварианты настоящего контракта.

---

# Часть XIII. Правило изменения контракта

Изменение считается архитектурным и требует новой версии контракта, если оно меняет хотя бы одно из следующего:

- границы ответственности `agent-core`, Temporal или MCP;
- topology coordinator/worker;
- Run durability или replay semantics;
- модель plan revisions;
- permission/Approval authority;
- project isolation;
- idempotency contract side effects;
- snapshot semantics;
- ownership первичных и производных данных;
- secret trust boundary;
- обязательные компоненты deployment.

Изменения таблиц, DTO, библиотек и внутренних классов не требуют новой версии контракта, если перечисленные инварианты сохраняются.

---

# Итог версии 2.0

Версия 2.0 заменяет перечень детальных предварительных решений версии 1.3 компактным MVP-контрактом.

Она фиксирует:

- единый `agent-core` с модульными границами;
- координатора и невложенных работников;
- durable Run в Temporal;
- PostgreSQL-first state;
- immutable configuration snapshot;
- единый RunPlan и immutable revisions;
- safe-boundary replanning;
- side effects только через plan nodes;
- централизованные permissions и policy-driven Approval;
- MCP как доменную границу;
- idempotency contract для mutation;
- минимальный Project-scoped RAG;
- provider-neutral model adapter;
- обязательные лимиты, audit и structured output validation;
- небольшой перечень границ, которые действительно необходимо закрыть до разработки.
