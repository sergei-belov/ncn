# Clean Frontend Architecture Guide

This file applies to `frontend_clean/**`. Preserve the product behavior documented in `README.md` while following the stricter architecture below.

## Architecture

Use pragmatic Feature-Sliced Design with the dependency direction:

```text
app -> pages -> widgets -> features -> entities -> shared
```

- `app`: bootstrap, router, app providers, global styles, and domain-aware demo adapters.
- `pages`: thin route entry points that compose widgets and features.
- `widgets`: substantial reusable page compositions such as the project board and detail panels.
- `features`: user actions, forms, validation, and mutation orchestration.
- `entities`: domain models, resource API ports/adapters, wire schemas/mappers, queries, cache helpers, and entity UI.
- `shared`: business-neutral transport, configuration, route constants, focused utilities, and UI primitives.

Every slice exposes an `index.ts` public API. Import a slice through that API outside the slice. Explicit entity cross-APIs under `@x` are allowed only for aggregate schemas such as the board. Never import pages from pages, widgets from sibling widget internals, or anything in a lower layer from `app`.

## State Ownership

- TanStack Vue Query is the only server-state owner. Do not add Pinia mirrors or duplicate entity stores.
- Update query caches through pure entity helpers, then invalidate after mutations.
- Optimistic board movement must cancel matching queries, snapshot all affected variants, update immutably, rollback every snapshot on failure, and refetch after settlement.
- Keep route-reproducible filters in Vue Router query parameters.
- Keep dialog/form/sheet state local and display preferences in `useStorage`.

## API and Domain Rules

- Resource ports live with their owning entity: project, board, work item, epic, and workflow state.
- HTTP implementations and wire mapping stay in entity API segments.
- The app-level provider selects HTTP or demo implementations using `VITE_API_MODE`.
- The persistent demo database and combined mock adapter live in `app/mocks`, not `shared`.
- `shared/api` contains only generic fetch/envelope/error utilities.
- Validate HTTP responses with Zod. Keep wire DTOs `snake_case` and domain models `camelCase`.

## UI and Product Contract

Use Vue 3 `<script setup lang="ts">`, Tailwind CSS, and the local `shared/ui` kit. Components receive data and emit intent; entity UI must not navigate directly. Preserve all project, board, work-item, epic, state-management, permission, archived read-only, responsive, theme, loading/error/empty, toast, and mock-reset behavior described in `README.md`.

Keep route components lazy-loaded. Preserve route-aware desktop sheets and full direct-link/mobile pages. Drag-and-drop must retain the explicit move dialog and accessibility announcement.

## Checks

Run from `frontend_clean/`:

```bash
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm test:e2e -- --list
```

Audit imports after structural changes:

```bash
rg -n '@/app|@/pages|@/widgets|@/features|@/entities' src
```
