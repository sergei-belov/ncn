# Ошибки и идемпотентность

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2493-2563 -->
<!-- SOURCE-CONTENT-START -->
## 89. Классификация ошибок

```text
TRANSIENT
RATE_LIMITED
AUTH_EXPIRED
INVALID_OUTPUT
BUSINESS_REJECT
PERMISSION_DENIED
VALIDATION_ERROR
SIDE_EFFECT_UNKNOWN
FATAL
```

---

## 90. Поведение

```text
TRANSIENT
→ retry

RATE_LIMITED
→ retry с Retry-After

AUTH_EXPIRED
→ refresh credentials и retry

INVALID_OUTPUT
→ repair/fallback

BUSINESS_REJECT
→ альтернативное решение координатора

PERMISSION_DENIED
→ без retry

VALIDATION_ERROR
→ исправление аргументов

SIDE_EFFECT_UNKNOWN
→ reconciliation

FATAL
→ завершение
```

---

## 91. Идемпотентность MCP

Для внутренних mutating tools обязателен:

```text
idempotency_key
```

Формат:

```text
project_id:run_id:node_id:attempt_group
```

Для пользовательских MCP поддержка не обязательна.

Без idempotency blind retry запрещён.

---

# Часть XIII. Kafka и автоматизации

