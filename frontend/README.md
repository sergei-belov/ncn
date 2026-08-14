# Project Management MVP — Clean Architecture

Готовый frontend для управления проектами по мотивам Plane. В MVP входят только проекты, эпики, карточки и Kanban-доска. По умолчанию приложение работает автономно на демонстрационном API в `localStorage`; переключение на реальный backend выполняется одной переменной окружения.

## Реализовано

- список, поиск, создание, редактирование, архивация и восстановление проектов;
- адаптивная Kanban-доска с настраиваемыми колонками состояний и компактными сворачиваемыми статусами;
- drag-and-drop карточек между колонками и внутри колонки с точной вставкой между соседними карточками, оптимистичным обновлением и откатом при ошибке;
- быстрое создание карточки, отдельный диалог перемещения и детальная карточка;
- название, rich-text описание, статус, приоритет, исполнители, эпик, даты и удаление карточки;
- список, создание, редактирование и удаление эпиков;
- управление составом эпика и рассчитанный backend-прогресс;
- создание, редактирование, перестановка и безопасное удаление состояний с миграцией карточек;
- список ассистентов проекта с обязательным координатором, создание и настройка специализированных работников;
- включение, отключение и архивирование работников с защитой системной роли координатора;
- проектная навигация с разделами «Агент» и «Управление» и обзором будущих сессий;
- route-aware sheet на desktop и отдельные страницы карточки/эпика при прямой ссылке или на mobile;
- фильтры доски по тексту, приоритету, эпику и исполнителю;
- права `admin` / `member` / `viewer`, read-only режим архивного проекта;
- светлая и тёмная темы, loading/empty/error/disabled-состояния, toast-уведомления;
- русскоязычный UI, адаптивная навигация desktop/mobile.

## Стек

- Vue 3.5, TypeScript 6, Vite 8, Vue Router 5;
- TanStack Vue Query 5 как единственный владелец server state;
- Tailwind CSS 4;
- shadcn-vue-подход: локальные UI-компоненты и токены, Reka UI для доступных Dialog/Sheet;
- vee-validate + Zod;
- Pragmatic Drag and Drop с hitbox и auto-scroll;
- Tiptap 3 для rich-text (лениво загружается только с маршрутом карточки);
- Lucide Vue, VueUse, vue-sonner, date-fns;
- Vitest, Vue Test Utils, Playwright, ESLint.

## Быстрый запуск

Требования: Node.js `>=22.12`, pnpm `11.x`.

```bash
pnpm install
cp .env.example .env.local
pnpm dev
```

Откройте [http://localhost:4173](http://localhost:4173). Начальный маршрут — `/demo/projects`.

Демо-данные сохраняются в `localStorage`. Команда «Сбросить демо» в боковой панели возвращает исходный набор проектов, карточек, эпиков и ассистентов.

## Команды

```bash
pnpm dev          # development server
pnpm build        # typecheck + production build
pnpm preview      # preview production build
pnpm lint         # ESLint
pnpm test         # unit + integration
pnpm test:e2e     # Playwright: desktop + Pixel 7
```

Перед первым E2E-запуском установите Chromium:

```bash
pnpm exec playwright install chromium
```

## Режимы API

```dotenv
VITE_API_MODE=mock
VITE_API_BASE_URL=/api/v1
VITE_WORKSPACE_SLUG=demo
VITE_APP_ENV=local
```

- `mock` — готовый in-browser backend с задержкой, версиями сущностей, конфликтами и сохранением в `localStorage`;
- `http` — resource-oriented REST-адаптеры в `src/entities/*/api/http.ts`.

Оба режима реализуют одинаковые resource ports для проектов, доски, карточек, эпиков, состояний и агентов. App-level provider выбирает transport, поэтому UI от него не зависит. HTTP-ответы валидируются Zod-схемами до попадания в query cache. Wire DTO используют `snake_case`, доменные модели — `camelCase`.

### Ожидания от backend

Базовый ресурс: `/workspaces/{workspaceSlug}/projects`.

| Область | Основные endpoints |
|---|---|
| Projects | `GET/POST /projects`, `GET/PATCH /projects/{id}`, `POST /archive`, `POST /restore` |
| Board | `GET /projects/{id}/board` |
| Work items | `POST /work-items`, `GET/PATCH/DELETE /work-items/{id}`, `POST /work-items/{id}/move` |
| Epics | `GET/POST /epics`, `GET/PATCH/DELETE /epics/{id}`, `POST /epics/{id}/work-items/batch` |
| States | `GET/POST /states`, `PATCH/DELETE /states/{id}`, `POST /states/reorder` |
| Agents | `GET/POST /agents`, `GET/PATCH /agents/{id}`, `POST /agents/{id}/enable`, `POST /agents/{id}/disable`, `POST /agents/{id}/archive` |

Изменяющие запросы отправляют `Idempotency-Key`; операции над версионируемыми сущностями — `If-Match: "{version}"`. Перемещение карточки содержит `board_version` и `client_mutation_id`. Ожидаемый envelope для одиночной сущности — `{ "data": ... }`; wire-контракты находятся рядом с владельцами в `src/entities/*/api/wire.ts`.

Если фактический backend отличается от контракта, менять нужно только HTTP-адаптеры и wire-mappers, не компоненты и query consumers.

## Структура

```text
src/
  app/       bootstrap, router, providers, global styles and demo adapters
  pages/     thin route-level entry points
  widgets/   Kanban, shells, project navigation and detail compositions
  features/  user actions, forms, validation and mutation orchestration
  entities/  domain models, resource ports, wire mapping, queries and cache logic
  shared/    generic transport, configuration, routes, utilities and UI kit
tests/       unit and mock API integration tests
e2e/         desktop/mobile smoke scenarios
```

Слои зависят только вниз: `app -> pages -> widgets -> features -> entities -> shared`. TanStack Vue Query управляет server state, optimistic snapshots и invalidation; route query содержит воспроизводимые фильтры доски. Все route-level компоненты загружаются динамически.

## Проверки поставки

Для clean-миграции выполняются:

- `vue-tsc --noEmit` — успешно;
- `eslint .` — успешно, без предупреждений;
- `vitest run` — 9 suites, 23 unit/integration tests, успешно;
- `vite build` — успешно;
- `playwright test --list` — 10 desktop/mobile smoke-проверок успешно обнаружены и скомпилированы.
- `playwright test` — 9 проверок успешно выполнены; точная mouse-DnD геометрия на mobile-проекте намеренно пропущена и проверяется в Chromium desktop.

Фактический browser-run Playwright требует локально установленного Chromium.

## Границы MVP

В приложение намеренно не включены workspace administration, inbox, cycles/sprints, modules вне трактовки «эпик», views, pages/wiki, analytics, notifications, comments, attachments, time tracking и интеграции. Раздел сессий пока показывает только контрактный обзор: создание диалогов, сообщения и выполнение Run остаются следующим этапом. Авторизация предполагается внешней: backend возвращает роль и рассчитанные permissions проекта.
