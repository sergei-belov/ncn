# Решения до начала разработки

<!-- SOURCE: NCN_Contract_v2.0.md:659-745 -->
<!-- SOURCE-CONTENT-START -->
# Часть XI. Решения, обязательные до начала разработки

До начала реализации первого вертикального среза должны быть закрыты только следующие границы.

## 37. Продуктовая граница первого релиза

Нужно утвердить:

- один основной end-to-end use case;
- какие 1–2 системных MCP tools участвуют;
- требуется ли worker в обязательном acceptance scenario;
- какие типы документов входят в демонстрационный RAG;
- какой side effect требует Approval.

Без этого невозможно создать проверяемый acceptance test.

## 38. Контракт модели и provider

Нужно определить:

- модели координатора и работника для MVP;
- поддерживаемый structured output/tool calling;
- максимальный context window;
- timeout и fallback policy;
- способ предоставления credentials;
- допустимые расходы на один Run.

## 39. Минимальная permission/approval matrix

До кода необходимо перечислить используемые в acceptance scenario tools и для каждого определить:

- read или mutation;
- risk level;
- разрешённые роли/agents;
- нужен ли Approval;
- idempotency class.

Не требуется проектировать универсальный policy language.

## 40. Run concurrency semantics

Нужно утвердить:

- допускается ли новый пользовательский Message во время активного Run;
- присоединяется ли он к Run, ставится в очередь или создаёт новый Run;
- кто и как отменяет Run;
- что видит пользователь при `WAITING_FOR_APPROVAL` и `WAITING_FOR_INPUT`.

## 41. RAG corpus boundary

Нужно определить:

- какие источники индексируются в первом релизе;
- кто инициирует ingestion;
- какие изменения вызывают reindex/delete;
- минимальные metadata filters;
- какой уровень source citation обязателен.

## 42. Failure and reconciliation UX

Нужно определить пользовательское поведение для:

- timeout модели;
- недоступного MCP;
- невалидного structured output после repair;
- неизвестного результата внешнего side effect;
- отклонённого Approval;
- частично выполненного плана.

Это продуктовая семантика, а не только backend error handling.

## 43. Нефункциональные пороги

До production MVP необходимо установить измеримые значения:

- ожидаемая concurrent Run load;
- максимальная длительность Run;
- максимальный размер артефакта;
- p95 latency для создания Run и чтения состояния;
- допустимая потеря/задержка progress events;
- backup и restore objectives;
- минимальная log/audit retention.

Для начала разработки допускаются временные значения, явно оформленные как assumptions.

---

