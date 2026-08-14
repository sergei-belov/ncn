# Память, модели и наблюдаемость

<!-- SOURCE: NCN_Contract_v2.0.md:458-565 -->
<!-- SOURCE-CONTENT-START -->
# Часть VII. Память, RAG и артефакты

## 24. Источники контекста

Контекст агента формируется backend и может включать:

- текущий пользовательский запрос;
- ограниченную историю Session;
- summary предыдущего контекста;
- результаты уже выполненных nodes;
- выбранные Project facts;
- RAG results;
- metadata связанных артефактов.

Модель не получает произвольный полный дамп Project.

## 25. RAG MVP

MVP должен поддерживать:

- ingestion разрешённых Project документов и выбранной доменной информации;
- chunking и embeddings;
- project-scoped retrieval;
- metadata filters как минимум по Project и типу источника;
- ссылки результата на source identifiers;
- удаление или переиндексацию производных chunks при изменении источника.

Векторный индекс является производным. Первичный текст и metadata сохраняются вне Qdrant.

Секреты, credentials и данные, для которых нельзя гарантировать корректную ACL-фильтрацию, не индексируются.

Точный ranking, reranking, chunk size и библиотека ingestion определяются на этапе проектирования и оценки качества.

## 26. Артефакты

Артефакт имеет Project ownership, metadata в PostgreSQL и content в object storage.

Минимально поддерживаются загрузка, чтение разрешённым агентом, извлечение текста и создание производного результата.

Лимиты размера, MIME allowlist и базовая защита от повреждённых файлов должны быть определены до production release. Malware scanning может быть отложен только для закрытого тестового MVP.

---

# Часть VIII. Модели, результаты и наблюдаемость

## 27. Model abstraction

Агенты ссылаются на логический model identifier из Model Registry, а не на provider SDK напрямую.

Model gateway/adapter нормализует:

- messages/input;
- structured output;
- tool call representation;
- usage;
- provider errors;
- timeout и cancellation.

Конкретный provider может быть заменён без изменения orchestration contract.

## 28. Structured output

Все машинно обрабатываемые решения координатора и работников должны иметь JSON Schema/Pydantic validation.

При невалидном ответе допускаются validation feedback и не более двух repair attempts. После этого node завершается контролируемой ошибкой.

Свободный текст допустим как часть результата, но не заменяет структурированные поля, необходимые backend.

## 29. Result envelope

Worker result должен различать как минимум:

- успешный результат;
- частичный результат;
- невозможность выполнения;
- необходимость уточнения;
- предложенные действия;
- ссылки на источники/артефакты.

Run result должен различать:

- итоговый пользовательский текст;
- terminal status;
- completed и failed parts;
- совершённые side effects;
- unresolved approvals/reconciliation items;
- usage summary.

Точная схема определяется при проектировании API, но указанная семантика обязательна.

## 30. События, tracing и audit

Система должна сохранять достаточную информацию для ответа на вопросы:

- кто инициировал Run;
- какая конфигурация использовалась;
- какие агенты и tools были вызваны;
- какие permissions и approvals применились;
- какие side effects были выполнены;
- почему Run завершился данным статусом;
- сколько ресурсов было использовано.

Logs и traces не должны содержать secrets или неограниченные raw prompts/responses.

Audit event должен быть отделён от пользовательского progress event.

---

