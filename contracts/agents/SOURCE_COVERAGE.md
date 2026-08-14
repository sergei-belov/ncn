# Карта покрытия исходных документов

Каждый файл разбиения содержит служебный комментарий `SOURCE` и маркер `SOURCE-CONTENT-START`. Всё после маркера является дословным фрагментом указанного исходника. Дополнительный заголовок до маркера нужен только для автономной навигации по файлу.

## Контракт v1.3-draft

Исходник: `Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md`, строки 1–3983.

| Строки | Разделы | Файл |
| ---: | --- | --- |
| 1–186 | статус, 1–4 | `01-business/01-product-and-agent-roles.md` |
| 187–409 | 5–11 | `01-business/02-business-scenarios.md` |
| 410–675 | 12–15 | `01-business/03-capabilities-and-domain-model.md` |
| 676–1015 | части III–IV, 16–25 | `03-module-design/01-agent-orchestration-and-run-plan.md` |
| 1016–1417 | часть V, 26–44 | `03-module-design/02-session-and-run.md` |
| 1418–1518 | часть VI, 45–49 | `03-module-design/03-temporal-runtime.md` |
| 1519–1663 | 50–51 | `04-implementation-details/01-retry-and-timeout-policies.md` |
| 1664–2041 | части VII–VIII, 52–67 | `03-module-design/04-agent-sdk-models-and-budgets.md` |
| 2042–2240 | часть IX, 68–76 | `03-module-design/05-context-memory-and-rag.md` |
| 2241–2492 | части X–XI, 77–88 | `03-module-design/06-mcp-permissions-and-approval.md` |
| 2493–2563 | часть XII, 89–91 | `03-module-design/07-errors-and-idempotency.md` |
| 2564–2643 | часть XIII, 92–96 | `03-module-design/08-kafka-and-automations.md` |
| 2644–2749 | часть XIV, 97–100 | `03-module-design/09-security-and-secrets.md` |
| 2750–2809 | часть XV, 101–103 | `03-module-design/10-artifact-storage.md` |
| 2810–2890 | часть XVI, 104–106 | `03-module-design/11-tracing-and-audit.md` |
| 2891–3105 | части XVII–XVIII, 107–118 | `03-module-design/12-api-and-data.md` |
| 3106–3371 | часть XIX, 119–132 | `04-implementation-details/02-backend-regulations.md` |
| 3372–3414 | часть XX, 133–135 | `03-module-design/13-deployment-and-health.md` |
| 3415–3470 | часть XXI, 136–137 | `03-module-design/14-result-envelopes.md` |
| 3471–3544 | часть XXII, 138–141 | `04-implementation-details/decisions/01-scope-data-and-api.md` |
| 3545–3631 | 142–154 | `04-implementation-details/decisions/02-closed-architecture-decisions.md` |
| 3632–3733 | 155–160 | `04-implementation-details/decisions/03-memory-artifacts-and-lifecycle.md` |
| 3734–3815 | 161–165 | `04-implementation-details/decisions/04-runtime-and-operations.md` |
| 3816–3895 | 166–168 | `04-implementation-details/decisions/05-cdc-kafka-and-errors.md` |
| 3896–3957 | 169–172 | `04-implementation-details/decisions/06-archiving-testing-and-stack.md` |
| 3958–3983 | итог v1.3-draft | `04-implementation-details/decisions/07-v1.3-summary.md` |

Диапазоны непрерывны, не пересекаются и покрывают строки 1–3983.

## Архитектурный контракт v2.0

Исходник: `NCN_Contract_v2.0.md`, строки 1–812.

| Строки | Части | Файл |
| ---: | --- | --- |
| 1–22 | статус | `02-invariants/00-contract-status.md` |
| 23–105 | I | `02-invariants/01-product-boundaries.md` |
| 106–210 | II–III | `02-invariants/02-components-and-agent-model.md` |
| 211–317 | IV | `02-invariants/03-session-run-and-plan.md` |
| 318–457 | V–VI | `02-invariants/04-durable-tools-and-security.md` |
| 458–565 | VII–VIII | `02-invariants/05-memory-models-and-observability.md` |
| 566–658 | IX–X | `02-invariants/06-data-deployment-and-readiness.md` |
| 659–745 | XI | `02-invariants/07-decisions-before-development.md` |
| 746–812 | XII–XIII и итог | `02-invariants/08-design-boundary-and-change-rules.md` |

Диапазоны непрерывны, не пересекаются и покрывают строки 1–812.

## Результат проверки полноты

Проверка выполнена 2026-08-06 после создания структуры:

- 35 из 35 перенесённых фрагментов дословно совпадают с исходными диапазонами по SHA-256;
- v1.3-draft покрыт непрерывно от строки 1 до строки 3983;
- все нумерованные разделы v1.3-draft от 1 до 172 присутствуют ровно по одному разу и идут без пропусков;
- v2.0 покрыт непрерывно от строки 1 до строки 812;
- все нумерованные разделы v2.0 от 0 до 43 присутствуют ровно по одному разу и идут без пропусков;
- ссылки из `architecture/README.md` разрешаются;
- незакрытых Markdown code fences нет.
