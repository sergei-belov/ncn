# NCN Frontend — UI and Pages Documentation

This section documents the implemented NCN frontend: its shared application shell, navigation levels, page structures, reusable components, visible states, and route-level behavior. The interface is a Russian-language Vue 3 project-management UI that runs with browser-backed mock adapters by default and can select HTTP adapters through configuration.

---

## Documentation structure

| Area | Contents |
| --- | --- |
| [General UI](general/README.md) | Workspace navbar, project sidebar, secondary settings navigation, shell nesting, responsive behavior, and shared page frames |
| [Pages](pages/README.md) | Every user-visible route with its definition, shell, page structure, behavior, states, permissions, and APIs |
| [Components and UI](components.md) | Shared primitives, widgets, entity components, feature components, accessibility behavior, and UI limitations |

## UI architecture

The frontend follows this dependency direction:

```text
app -> pages -> widgets -> features -> entities -> shared
```

- `app` owns bootstrap, routes, providers, global styles, and browser mock data.
- `pages` are route entries that compose the page UI.
- `widgets` own substantial page structures such as the application shell, project navigation, Kanban board, access view, and detail panels.
- `features` own user actions, forms, validation, dialogs, and mutation orchestration.
- `entities` own domain types, API ports/adapters, queries, cache helpers, and reusable entity cards.
- `shared` owns business-neutral transport, configuration, utilities, routes, and UI primitives.

All route components are lazy-loaded. `App.vue` renders the active route and a global top-right toaster; it does not add a persistent header or footer itself.

---

## General page structure

Protected routes are nested through `WorkspaceShell`. Project routes add `ProjectLayout`, and project settings pages add `SettingsTabs` inside their page content.

### Workspace pages

The project catalog and workspace-access page use the workspace shell only:

```text
┌────────────────────────────────────────────────────────────┐
│ Workspace navigation │ Main page                          │
│                      │                                    │
│ • Projects           │ • Page header                      │
│ • Workspace access   │ • Filters/actions                  │
│                      │ • Page-specific content            │
│ User / theme / reset │ • Dialogs and status states        │
└────────────────────────────────────────────────────────────┘
```

The desktop workspace navigation is a collapsible left sidebar. Below the `md` breakpoint it becomes a compact top navbar. `WorkspaceShell` resolves the authorization session before either layout is shown.

### Project pages

Project routes add a second, project-specific navigation level:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Workspace nav │ Project sidebar      │ Main project page                 │
│               │                      │                                   │
│ • Projects    │ Agent               │ • Page header                     │
│ • Access      │ • Assistants         │ • Page-specific controls          │
│               │ • Sessions           │ • Board, catalog, detail, or form │
│               │ Management          │ • Dialogs / sheets / status       │
│               │ • Board             │                                   │
│               │ • Epics             │                                   │
│               │ • Settings          │                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

The project sidebar is visible from the `lg` breakpoint. Below `lg`, `ProjectLayout` renders a sticky project header and grouped compact navigation above the page. Between `md` and `lg`, the workspace sidebar remains visible while project navigation uses its compact header.

### Project settings pages

Settings pages keep both outer navigation layers and add horizontal, tertiary page-local tabs:

```text
Workspace navigation
└── Project navigation
    └── Settings page
        ├── Page header
        ├── Secondary tabs: General · States · Access
        └── Form, workflow list, or access-management view
```

The Access tab is shown only to project administrators according to the resolved authz session. The project-level Settings entry is shown only when the loaded project exposes `canEditProject`.

### Route-aware detail pages

Work-item and epic routes have two presentations without changing their URL:

- navigation from the corresponding project view on desktop opens an `AppSheet` over the background page;
- direct links, reloads, and mobile navigation render the same detail content as a full page with back navigation.

### Standalone pages

The catch-all Not found page is outside both shells. It uses a centered recovery layout and links to the configured workspace project catalog. There is no authentication/login route in the current frontend router.

The application has no persistent footer.

---

## Navigation components

| UI level | Implementation | Responsibility |
| --- | --- | --- |
| Primary workspace navigation | [`WorkspaceShell`](general/navbar.md) | Session gate, workspace sidebar/mobile navbar, user identity, theme, demo reset, and desktop collapse |
| Secondary project navigation | [`ProjectLayout`](general/project-sidebar.md) | Nested project sidebar, project identity, grouped project routes, archive context, and project load failure |
| Settings tabs | [`SettingsTabs`](components.md#settingstabs) | Page-local navigation for General, States, and permission-gated Access settings; not part of the general shell |

## Page families

| Family | Routes | Canonical structure |
| --- | --- | --- |
| Workspace | Projects, Workspace access | `WorkspaceShell -> page` |
| Project | Board, Epics, Agents, Sessions | `WorkspaceShell -> ProjectLayout -> page` |
| Route-aware detail | Work item, Epic | Project shells plus desktop sheet or standalone page |
| Project configuration | Agent settings | Project shells plus configuration/danger sections |
| Project settings | General, States, Access | Project shells plus page header and `SettingsTabs` |
| Standalone | Not found | No shared shell |

See the [page catalog](pages/README.md) for exact routes and per-page structures.

## Shared UI behavior

- The workspace shell blocks protected content while resolving identity and access.
- Project permissions control edit, archive, state, agent, card, and epic actions.
- Archived projects are read-only except for restore and backend-supported personal board preferences.
- Pages provide loading skeletons or status views, empty states, retryable failures, disabled/read-only controls, toast feedback, and dark mode where relevant.
- Access administration additionally represents offline mode, permission loss, stale cached data, cursor pagination, and screen-reader announcements.
- The board provides drag-and-drop plus an explicit move dialog and live movement announcements.

## State and request flow

1. A page reads route parameters and reproducible query filters.
2. An entity query calls the injected resource port.
3. The selected mock or HTTP adapter returns a camelCase domain model.
4. TanStack Vue Query caches the result under entity-owned keys.
5. A feature mutation updates or invalidates relevant caches; board movement uses optimistic snapshots and rollback.
6. The UI renders canonical cached state and reports failures through `ApiError` and toasts.

Route query parameters own reproducible filters. Dialog, form, sheet, and local interaction state remain in components. Theme and selected display preferences use browser persistence.

## Stack

- Vue 3 with `<script setup lang="ts">`, Vue Router, and Vue I18n;
- TanStack Vue Query for server state;
- Tailwind CSS and local design tokens;
- Reka UI for accessible dialogs and sheets;
- vee-validate and Zod for forms;
- Pragmatic Drag and Drop for the Kanban board;
- Tiptap for work-item rich text;
- VueUse for theme, online status, debouncing, and browser persistence.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `VITE_API_MODE` | `mock` | Selects `mock` or `http` entity adapters |
| `VITE_API_BASE_URL` | `/api/v1` | Prefix used by the shared HTTP client |
| `VITE_WORKSPACE_SLUG` | `demo` | Workspace used by the root redirect and demo reset |
| `VITE_APP_ENV` | `local` | Runtime environment label |

Mock data is saved in `localStorage`. “Reset demo” replaces it with the seeded database. HTTP responses are parsed through Zod before they enter query caches. The current HTTP adapters are not aligned with every backend contract; see [HTTP integration status](../architecture.md#http-integration-status).

## Related documentation

- [General UI](general/README.md)
- [Page catalog](pages/README.md)
- [Components and UI](components.md)
- [PMS flows](../backend/services/pms/flows.md)
- [Authz flows](../backend/services/authz/flows.md)
