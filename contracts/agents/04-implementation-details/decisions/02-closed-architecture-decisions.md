# Закрытые архитектурные решения

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3545-3631 -->
<!-- SOURCE-CONTENT-START -->
## 142. `space_admin` — закрыто

`space_admin` является отдельной control-plane ролью, не наследует `project_admin`, не получает автоматического доступа к данным Project и не использует break-glass. Для data-plane доступа назначается обычная Project role.

---

## 143. Approval routing — закрыто

Зафиксированы fallback-цепочка approvers, one-of-many resolution, snapshot списка, повторная проверка membership и explicit reroute через `superseded` старого Approval.

---

## 144. Agent approval policy и ApprovalGrant — закрыто

Permission и Approval разделены. Постоянная AgentVersion policy управляется `project_admin` и может ослаблять Approval только для допустимых low/medium операций. Run-level ApprovalGrant строго ограничен scope.

---

## 145. Project approval mode — закрыто

Используется risk-based Project policy с overrides. `DENY` и `REQUIRE_APPROVAL` имеют приоритет.

---

## 146. Project quotas — закрыто

Зафиксированы monetary/token limits, post-factum settlement без reservation, допустимый concurrent overdraft, quota ledger и наследование platform → Space → Project.

---

## 147. Model Registry administration — закрыто на уровне архитектуры

Используются `platform_admin`, одна immutable-after-use ModelDefinition без ModelVersion, отдельная ModelPriceVersion, capability verification, health state и model allowlists.

---

## 148. Конкретные модели — закрыто на уровне ролей и embedding

Coordinator/worker/fallback/summary model IDs задаются deployment configuration. Для embedding предпочтительна Qwen3-Embedding-8B/4096, допустима Qwen3-Embedding-4B/2560.

---

## 149. MCP OAuth — исключено из MVP

OAuth пользовательских MCP, callback, PKCE, access/refresh tokens, discovery, refresh и revoke не реализуются. Поддерживаются API key и Basic Auth. Workload `client_credentials` системного MCP описан отдельно в разделе 98.

---

## 150. Machine-to-machine системного MCP — закрыто

Принят Keycloak service account `agent-core` + отдельная audience каждого MCP + OAuth2 Proxy. Agent-core является authorization authority для агентов; MCP сохраняет schema/domain/idempotency validation. Per-call delegation JWT, собственные ES256/JWKS и custom Keycloak grant не используются.

---

## 151. Secrets production path — закрыто для MVP

Bootstrap secrets передаются через `.env`/environment/mounted secret, для Kubernetes — Kubernetes Secrets. Dynamic Project secrets хранятся как encrypted SecretVersion в PostgreSQL с master-key rotation. Vault/KMS не являются обязательными компонентами.

---

## 152. CEL runtime — исключено из MVP

CEL, Python CEL library и `condition` nodes не используются. Семантическое ветвление выполняет координатор через `coordinator_decision` и strict structured output. Возврат CEL возможен post-MVP для детерминированного no-code конструктора правил.

---

## 153. Data mapping runtime — закрыто для MVP

Полноценный JSONPath не используется. Применяются ограниченные source scopes и RFC 6901 JSON Pointer для source/target paths, без filters, expressions и неявного type coercion.

---

## 154. Dynamic coordinator plan — частично закрыто

Зафиксировано:

- отдельный decision-agent не создаётся;
- координатор выбирает только разрешённые WorkflowVersion/plan snapshot переходы;
- решения возвращаются как strict structured output;
- backend валидирует references, permissions, Approval, limits и plan mutations;
- уже выполненные nodes и side effects immutable;
- CEL в dynamic plan отсутствует.

Точный JSON Schema DynamicPlanRevision, limits revisions и полный набор validation errors остаются для следующего уточнения.

---

