# Backend-регламент

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3106-3371 -->
<!-- SOURCE-CONTENT-START -->
## 119. Порядок источников

```text
1. backend/AGENTS.md
2. контракт задачи
3. database-methods.md
4. kafka-streaming.md
5. ближайший рабочий модуль
6. template
```

Ближайший рабочий код имеет приоритет над универсальным template.

---

## 120. Слои

```text
models/sqlalchemy
models/pydantic/dto
models/pydantic/api
models/pydantic/stream
models/enum
api/db
api/managers
api/router
api/stream
```

---

## 121. Router

Router:

- тонкий;
- объявляет endpoint;
- принимает dependencies;
- вызывает Manager;
- не содержит business logic;
- не содержит SQL;
- не вызывает MCP и LLM.

Итоговый path формируется:

```text
/api/{service}/v1
+
/projects/{project_id}/...
```

---

## 122. Manager

Manager отвечает за:

- authorization;
- project scope;
- business validation;
- orchestration repositories;
- DB transaction;
- Kafka production;
- DTO;
- API response;
- перевод ошибок.

---

## 123. Repository

Repository наследуется от:

```text
BaseDatabaseGeneric
```

Обязательные generic attributes:

```text
database
_table
_id
_model
_model_create
_model_update
```

---

## 124. Generic methods

```text
create
bulk_create
get
get_by_ids
get_list
get_paginated_list
get_count
update
bulk_update
upsert
bulk_upsert
delete
delete_many
delete_list
```

Не создаются thin wrappers для простых filters.

Custom methods — только для:

- join;
- aggregation;
- CTE;
- tuple filter;
- сложной сортировки;
- custom DTO.

---

## 125. DTO

```text
ResourceDTO
ResourceCreateDTO
ResourceUpdateFieldsDTO
```

Используются:

```text
OrmModel
UUIDModel
NoneValidationMixin
```

---

## 126. API models

```text
ResourceAPI
ResourceListItemAPI
GetResourceResponse
GetResourceListQueries
GetResourceListResponse
PostResourceRequest
PostResourceResponse
PutResourceRequest
PutResourceResponse
PatchResourceRequest
PatchResourceResponse
```

Фактический состав зависит от домена.

---

## 127. SQLAlchemy

Модели наследуются от:

```text
SQLAlchemyBase
```

Поля DTO, API и SQLAlchemy должны совпадать по:

- имени;
- типу;
- nullable;
- семантике.

---

## 128. Kafka models

Stream model:

```python
class TriggerEventStream(OrmModel):
    ...

    class Meta:
        topic = "..."
```

Topic берётся только через:

```text
Model.Meta.topic
```

KafkaBroker сам выполняет Avro и Schema Registry operations.

---

## 129. Listener

```python
@Services.broker.listen(...)
```

Listener:

- имеет точную Pydantic-аннотацию;
- может принимать batch;
- только логирует получение;
- вызывает Manager.

---

## 130. Producer

```python
await Services.broker.produce(
    topic=Model.Meta.topic,
    message=Model(...),
)
```

При batch выполняется один flush после цикла.

---

## 131. Registration hubs

Обязательная регистрация:

```text
models/pydantic/__init__.py
models/pydantic/stream/__init__.py
models/sqlalchemy/__init__.py
models/enum/__init__.py
api/db/db.py
api/managers/managers.py
api/router/router.py
api/stream/__init__.py
```

---

## 132. Ограничения skill реализации

Skill не должен:

- создавать Alembic migrations;
- редактировать migrations;
- запускать код;
- запускать тесты;
- запускать сервер;
- запускать formatter;
- запускать linter;
- выполнять compile checks.

В handoff указываются:

- требуемые migrations;
- непройденные runtime checks;
- непройденные tests;
- внешние зависимости.

---
