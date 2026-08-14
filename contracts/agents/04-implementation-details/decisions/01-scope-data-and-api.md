# Решения по scope, данным и API

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3471-3544 -->
<!-- SOURCE-CONTENT-START -->
# Часть XXII. Открытые вопросы

Открытые вопросы не отменяют утверждённые решения. Они должны быть закрыты в следующих версиях контракта до реализации соответствующего участка.

## 138. Первый объём реализации

Необходимо определить первый вертикальный срез:

- только Agents CRUD;
- Agents + Model Registry;
- Agents + MCP;
- Sessions + Runs;
- полный минимальный happy path;
- automation-triggered сценарий.

---

## 139. Точные PostgreSQL-таблицы

Необходимо зафиксировать:

- полный перечень таблиц;
- поля;
- типы;
- nullable;
- indexes;
- unique constraints;
- внутренние foreign keys;
- JSONB schemas;
- ownership модулей.

---

## 140. Точные API-контракты

Для каждого service namespace необходимо определить:

- endpoints;
- request DTO;
- response DTO;
- PUT support;
- PATCH support;
- archive/disable commands;
- status codes;
- HTTPExceptionResponse models;
- pagination filters;
- sorting;
- search fields.

---

## 141. Регламент pagination

Известно, что используются:

```text
ViewListQueries
ViewList
MetaList
offset
limit
```

Требуется изучить фактические базовые модели репозитория и зафиксировать:

- точные поля;
- default limit;
- maximum limit;
- sort syntax;
- filter syntax;
- search semantics.

---

