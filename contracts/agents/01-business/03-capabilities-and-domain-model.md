# Функции платформы и доменная модель

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:410-675 -->
<!-- SOURCE-CONTENT-START -->
## 12. Основные функции платформы

### Управление координатором

- получение текущей конфигурации;
- полная замена пользовательской конфигурации через PUT;
- частичное обновление через PATCH;
- выбор модели;
- настройка инструкций;
- настройка memory policy;
- настройка limits;
- настройка Approval preferences;
- настройка доступных работников.

### Управление работниками

- создание;
- получение;
- получение списка;
- PUT;
- PATCH;
- архивирование;
- включение и отключение;
- выбор модели;
- настройка output schema;
- настройка permissions;
- подключение MCP tools;
- настройка memory policy;
- настройка limits;
- настройка approval policy.

### Управление MCP

- создание Project MCP configuration;
- Streamable HTTP transport;
- API key в настраиваемом header;
- Basic Auth;
- discovery tools;
- ручной refresh discovery;
- выбор разрешённых tools;
- повторное подтверждение изменённой schema;
- отключение;
- архивирование;
- управление Project credentials.

OAuth для пользовательских MCP не входит в MVP. Machine-to-machine `client_credentials` системного MCP является отдельным workload-механизмом и описан в разделе 98.

### Управление Workflow

- создание WorkflowDefinition;
- создание draft WorkflowVersion;
- PUT draft;
- PATCH draft;
- статическая валидация;
- публикация;
- deprecation;
- archive;
- привязка automation rule к опубликованной версии.

### Управление Session и Run

- создание Session;
- отправка Message;
- присоединение Message к активному Run;
- polling состояния;
- polling RunEvent;
- отмена;
- resume после budget block;
- закрытие Session;
- удаление Session и связанных данных.

### Управление Approval

- получение списка;
- получение конкретного Approval;
- approve;
- reject;
- редактирование аргументов;
- создание ограниченного ApprovalGrant;
- отзыв grant.

### Управление Artifact

- создание multipart upload;
- завершение upload;
- получение metadata;
- получение presigned URL;
- привязка к Session;
- извлечение текста;
- индексирование;
- удаление.

---

# Часть II. Организационная и доменная модель

## 13. Мультитенантность

Основная иерархия:

```text
Space
└── Project
    ├── Users
    ├── Sessions
    ├── Coordinator
    ├── Workers
    ├── MCP configurations
    ├── Workflows
    ├── Automation rules
    ├── Secrets
    ├── Artifacts
    └── Memory
```

Границей изоляции agent-core является Project.

По Project изолируются:

- агенты;
- версии агентов;
- Session;
- Run;
- Message;
- Workflow;
- MCP;
- MCP credentials;
- Approval;
- Artifact;
- Qdrant records;
- traces;
- budgets;
- project state;
- automation triggers.

`project_id` добавляется системой и не доверяется LLM-generated arguments.

---

## 14. Пользовательские роли

Базовые роли:

```text
platform_admin
space_admin
project_admin
project_member
```

### `platform_admin`

Управляет platform control plane:

- создаёт и изменяет ModelDefinition;
- подключает platform model credentials;
- устанавливает ModelPriceVersion;
- запускает capability verification и health checks моделей;
- включает и отключает модели;
- назначает platform model defaults;
- задаёт platform quota defaults и максимумы Space;
- просматривает глобальный model usage и platform audit.

`platform_admin` не получает автоматического доступа к Session, Message, Artifact, trace и MCP credentials конкретного Project. Для data-plane доступа требуется обычная роль соответствующего Project.

### `space_admin`

Управляет Space control plane:

- создаёт и архивирует Project;
- назначает и отзывает `project_admin`;
- задаёт Project quotas в пределах максимума Space;
- определяет список моделей, разрешённых в Space;
- просматривает агрегированное административное состояние Project;
- просматривает административный audit Space.

`space_admin` не наследует `project_admin` и не получает автоматического доступа к данным Project.

Break-glass механизм не вводится. Для доступа к данным конкретного Project `space_admin` должен получить обычную роль этого Project.

### `project_admin`

Может:

- выполнять все действия `project_member`;
- изменять координатора;
- создавать, изменять и архивировать работников;
- подключать MCP;
- выбирать MCP tools;
- создавать и ротировать Project secrets через безопасный API;
- отменять Run;
- удалять Session и историю;
- создавать и публиковать Workflow;
- управлять automation configuration;
- управлять Project approval policy;
- создавать AgentVersion с разрешённой approval policy;
- просматривать Project quotas и usage.

### `project_member`

Может:

- создавать Session;
- запускать агентов;
- отправлять Message;
- подтверждать действие, если включён в `allowed_approver_ids`;
- просматривать traces при наличии permission;
- просматривать доступные Session Project;
- скачивать доступные Artifacts.

---

## 15. Сущности исполнения

### Session

Долгоживущий проектный диалог.

В одной Session могут участвовать несколько пользователей.

Session может быть:

- пользовательской;
- системной, созданной automation rule.

### Message

Содержательный элемент timeline.

Message может быть создан:

- пользователем;
- координатором;
- работником;
- системой.

### Run

Durable-исполнение одного или нескольких входных сообщений или trigger event.

В одной Session одновременно существует не более одного активного Run.

### AgentInvocation

Один полноценный запуск координатора или работника.

### ToolCallExecution

Один вызов:

- function tool;
- MCP tool;
- memory tool;
- artifact tool;
- system tool.

### RunEvent

Append-only событие выполнения для polling frontend и диагностики.

### AuditEvent

Append-only security или administrative event.

---

