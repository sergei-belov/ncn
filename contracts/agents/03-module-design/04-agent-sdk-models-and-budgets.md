# Agent SDK, модели и бюджеты

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:1664-2041 -->
<!-- SOURCE-CONTENT-START -->
# Часть VII. OpenAI Agents SDK

## 52. Основные SDK-примитивы

Используются максимально:

```text
Agent
Runner
Runner.run_streamed
RunConfig
ModelSettings
RunContextWrapper
RunState
function_tool
MCPServerStreamableHttp
```

Native handoff не используется.

---

## 53. Runner

Используется:

```python
Runner.run_streamed(...)
```

Streaming применяется для внутренних semantic events.

Raw token delta не сохраняются и не передаются frontend.

Frontend использует polling.

---

## 54. SDK Session

Встроенное Session storage SDK не используется.

Каждый Invocation получает явно собранный input.

---

## 55. Runtime context

```text
AgentRuntimeContext
├── space_id
├── project_id
├── session_id
├── run_id
├── agent_id
├── agent_version_id
├── invocation_id
├── initiated_by_user_id
├── permissions_snapshot
├── delegation_packet
├── trace_id
└── correlation_id
```

Credentials в context не передаются.

---

## 56. SDK RunState

При interruption:

1. создаётся `RunState`;
2. сериализуется;
3. шифруется;
4. сохраняется в PostgreSQL;
5. Child Workflow ожидает Signal;
6. применяется approve/reject/input;
7. Runner продолжается с RunState.

RunState:

- не показывается пользователю;
- не передаётся в Kafka;
- не индексируется;
- удаляется после Invocation;
- удаляется при удалении Session.

---

## 57. Tool calls

Модель может выполнить несколько tool calls внутри Invocation.

В MVP все tool calls выполняются последовательно.

Параллельность существует только между WorkerInvocation:

```text
max_parallel_workers = 2
```

---

## 58. Structured output

Для пользовательских JSON Schema используется:

1. schema в runtime instructions;
2. безопасный JSON parser;
3. валидация через `jsonschema`;
4. Pydantic `TypeAdapter`, где применимо;
5. помещение результата в envelope.

Pipeline:

```text
primary generation
→ repair 1
→ repair 2
→ fallback model
→ fallback repair
→ INVALID_OUTPUT
```

---

## 59. Tool error для модели

Модель получает только безопасный ответ:

```json
{
  "code": "MCP_UNAVAILABLE",
  "detail": "Tool is temporarily unavailable",
  "retryable": true
}
```

Stack trace и внутренние детали не передаются.

---

## 60. SDK tracing

Экспорт в OpenAI tracing backend отключён.

Используются:

- streamed events;
- Runner hooks;
- внутренний trace processor;
- RunEvent;
- AuditEvent.

Hidden reasoning не сохраняется.

---

# Часть VIII. Модели и бюджеты

## 61. Model Registry

Используется одна сущность:

```text
ModelDefinition
```

Отдельное версионирование ModelDefinition не используется. Если требуется другая функциональная конфигурация модели, создаётся новая ModelDefinition с новым UUID.

```text
ModelDefinition
├── id
├── display_name
├── provider_type
├── api_compatibility
├── base_url
├── configured_model_name
├── resolved_model_name
├── resolved_at
├── credential_secret_id
├── capabilities
├── context_window
├── max_output_tokens
├── supports_tools
├── supports_structured_output
├── supports_streaming
├── supports_cancellation
├── supports_vision
├── supports_responses_api
├── supports_embeddings
├── embedding_dimension
├── verification_status
├── health_status
├── enabled
├── created_at
└── updated_at
```

После первого использования ModelDefinition её функциональные поля считаются immutable. Для изменения provider, endpoint, model name, capabilities, limits, adapter mode или embedding dimension создаётся новая ModelDefinition.

Разрешено изменять operational metadata, health state, enabled state и ссылку на ротируемый credential.

Provider alias может быть указан в `configured_model_name`, но при verification сохраняется фактически разрешённый `resolved_model_name`. Изменение результата разрешения alias считается configuration drift и требует новой ModelDefinition.

Пользователь Project выбирает только модель, которая одновременно:

```text
enabled platform model
AND allowed for Space
AND healthy or degraded
AND verification_status = verified
```

Собственные пользовательские model credentials не поддерживаются.

### ModelPriceVersion

Цена хранится независимо от ModelDefinition:

```text
ModelPriceVersion
├── id
├── model_definition_id
├── currency
├── input_per_million
├── cached_input_per_million
├── output_per_million
├── effective_from
├── effective_to
└── created_at
```

ModelPriceVersion immutable. Изменение цены создаёт новую запись и не требует новой ModelDefinition.

---

## 62. Model adapter

Все модели рассматриваются как provider-neutral OpenAI-compatible endpoints. Понятие `local model` в доменной модели не используется.

```text
supports_responses_api = true
→ Responses-compatible adapter

supports_responses_api = false
→ Chat Completions-compatible adapter

supports_embeddings = true
→ Embeddings-compatible adapter
```

Ollama, vLLM, SGLang и другие совместимые endpoints подключаются через `base_url`, model name и optional credential secret.

---

## 63. Model gateway

Отдельный HTTP model gateway в MVP не создаётся.

Внутри agent-core существуют:

```text
ModelRegistryRepository
ModelClientFactory
ModelInvocationService
ModelCapabilityVerificationService
ModelHealthService
ModelUsageRecorder
```

---

## 64. Model credentials и deployment configuration

Model credentials относятся к platform scope.

`ModelDefinition` хранит только `credential_secret_id`, nullable для endpoints без authentication.

Credential:

- не возвращается через API;
- не сохраняется в AgentVersion;
- не попадает в trace;
- не передаётся в Temporal input;
- расшифровывается непосредственно перед model call.

Допускается in-memory cache с TTL не более пяти минут.

Deployment может bootstrap model endpoints и model-role defaults из отдельных environment variable groups. Environment variables не являются runtime source of truth после успешной инициализации и не должны логироваться.

Логические model roles:

```text
coordinator_model_id
worker_model_id
structured_output_fallback_model_id
summary_model_id
embedding_model_id
```

---

## 65. Fallback

Fallback model задаётся через `structured_output_fallback_model_id` и используется только после нескольких невалидных structured outputs.

Fallback не используется для timeout, rate limit, недоступности primary, provider error или budget limit.

---

## 66. ModelUsageRecord

```text
id
project_id
session_id
run_id
agent_invocation_id
agent_id
agent_version_id
model_id
model_price_version_id
provider_request_id
input_tokens
output_tokens
cached_input_tokens
reasoning_tokens
request_count
latency_ms
estimated_cost
status
created_at
```

Prompt и output в usage table не сохраняются.

Расчёт стоимости выполняется по ModelPriceVersion, активной на момент начала model call. Если endpoint имеет нулевую цену, usage всё равно сохраняется.

---

## 67. Бюджеты и квоты

Поддерживаются дневная и недельная Project cost quota, token budgets Run/Invocation, output token limit, tool-call limit и invocation limit.

Monetary amounts хранятся в фиксированной минимальной единице без floating-point arithmetic.

Используется post-factum settlement без предварительного reservation.

Перед model call проверяется уже зафиксированный usage. Если quota уже исчерпана, новый model call не начинается и Run получает `BUDGET_BLOCKED`.

После ответа фактическое usage атомарно добавляется в quota ledger. Параллельные Run могут совместно превысить лимит; отрицательный остаток допускается и сохраняется как overdraft. Уже начатый model call не отменяется.

Используются:

```text
project_quota_policies
project_quota_buckets
quota_ledger
```

`quota_reservations` не используется.

Settlement идемпотентен по `ModelUsageRecord.id` и, при наличии, `provider_request_id`.

Иерархия limits:

```text
platform default / maximum
→ Space override / maximum
→ Project override
```

`Project limit ≤ Space maximum ≤ platform maximum`. Отсутствие Project override означает наследование, а не unlimited.

# Часть IX. Контекст, память и RAG

