# Форматы результатов

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3415-3470 -->
<!-- SOURCE-CONTENT-START -->
# Часть XXI. Форматы результатов

## 136. WorkerResultEnvelope

```json
{
  "status": "completed",
  "summary": "Краткий результат",
  "data": {},
  "artifacts": [],
  "proposed_actions": [],
  "performed_actions": [],
  "warnings": [],
  "errors": [],
  "requires_follow_up": false
}
```

Статусы:

```text
completed
partial
failed
cancelled
waiting_for_approval
blocked
```

---

## 137. RunResultEnvelope

```json
{
  "status": "completed",
  "message_id": "UUID",
  "summary": "...",
  "data": {},
  "artifacts": [],
  "warnings": [],
  "completed_at": "UTC+00:00"
}
```

Статусы:

```text
completed
partially_completed
failed
cancelled
```

---

