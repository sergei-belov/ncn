# Session, Run и план исполнения

<!-- SOURCE: NCN_Contract_v2.0.md:211-317 -->
<!-- SOURCE-CONTENT-START -->
# Часть IV. Session, Run и план исполнения

## 9. Session

Session является пользовательским или системным контекстом общения, содержащим Messages и Runs.

В MVP требуется поддержать:

- последовательное добавление Messages;
- один активный mutating Run на Session;
- чтение истории с project-level access control;
- явное завершение Session;
- сохранение связи итогового ответа с Run.

Параллельные read-only сценарии могут быть добавлены позднее и не должны усложнять первый релиз.

## 10. Run

Run является одной попыткой достижения цели.

Run содержит:

- входной envelope;
- snapshot конфигурации;
- текущий статус;
- план и его revisions;
- agent invocations;
- tool executions;
- approvals;
- события;
- usage;
- итоговый result envelope.

Минимальные terminal statuses:

- `COMPLETED`;
- `PARTIALLY_COMPLETED`;
- `FAILED`;
- `CANCELLED`.

Внутренние промежуточные статусы определяются реализацией, но API должно различать активное выполнение, ожидание пользователя и terminal state.

## 11. Единый RunPlan

Любой Run исполняется через единое представление `RunPlan`, независимо от того, был ли план создан координатором или в будущем загружен из Workflow template.

Минимальные типы plan nodes:

- coordinator reasoning/decision;
- worker invocation;
- tool call;
- approval boundary;
- finalization.

Side effects разрешены только через явно исполняемые plan nodes. Модель не может выполнить внешний side effect скрыто внутри reasoning step.

## 12. Plan revisions

Первоначальный план и каждое изменение являются immutable revision.

Координатор может менять только ещё не начатую часть плана на safe boundary.

Запрещено изменять:

- завершённые nodes;
- выполняющиеся nodes;
- зафиксированные tool call arguments;
- совершённые side effects;
- выданные решения Approval.

Backend валидирует каждую revision до исполнения.

## 13. Ветвление и mapping

Семантическое ветвление выполняет координатор через strict structured output.

CEL в MVP не используется.

Для передачи данных между nodes применяются:

- ограниченный перечень source scopes;
- RFC 6901 JSON Pointer для чтения и записи;
- явная schema validation;
- отсутствие expressions, filters и неявного type coercion.

## 14. Параллельность и ограничения

MVP поддерживает:

- последовательное выполнение;
- параллельный запуск ограниченного числа независимых worker nodes;
- join только по правилу `all`.

Значения лимитов являются deployment/configuration parameters, но должны существовать с первого релиза:

- максимальное число plan nodes;
- максимальное число plan revisions;
- максимальная глубина/число worker invocations;
- максимальная параллельность;
- максимальное число tool calls;
- максимальная продолжительность Run;
- token и monetary limits.

Backend отклоняет или завершает исполнение при превышении hard limit.

---

