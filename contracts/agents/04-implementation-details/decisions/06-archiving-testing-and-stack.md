# Архивирование, тестирование и стек

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3896-3957 -->
<!-- SOURCE-CONTENT-START -->
## 169. Политика архивирования

Нужно определить:

- восстановление archived Agent;
- восстановление MCP;
- повторное включение Workflow;
- поведение automation rule;
- очистку secrets;
- физическое удаление после archive.

---

## 170. Тестирование

Предоставленный implementation skill запрещает запуск тестов в рамках своей процедуры.

Отдельно необходимо определить:

- unit tests;
- integration tests;
- Temporal tests;
- Kafka contract tests;
- MCP mock server;
- model adapter tests;
- approval tests;
- cancellation tests;
- load tests;
- evaluation dataset агентов.

---

## 171. Python stack и версии

Архитектурные библиотеки определены концептуально, но не зафиксированы версии:

- Python;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- PostgreSQL driver;
- Temporal SDK;
- OpenAI Agents SDK;
- aiokafka-based broker;
- Qdrant client;
- MinIO client;
- JSON Schema validator;
- JSON Pointer implementation или собственный ограниченный resolver;
- encryption library.

Версии должны быть взяты из фактического backend repository и его dependency files.

---

## 172. Фактический `AGENTS.md`

Перед реализацией необходимо изучить `backend/AGENTS.md`.

Если его правила противоречат текущему контракту, противоречие должно быть вынесено на согласование, а не разрешено молча.

---
