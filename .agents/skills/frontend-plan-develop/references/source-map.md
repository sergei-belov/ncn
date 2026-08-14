# Frontend Source Map

Use live repository files as the source of truth. Inspect only the examples relevant to the requested change, then prefer the nearest analogous slice over copying a generic pattern blindly.

## Architecture and Tooling

- `AGENTS.md`: repository-wide ownership and change rules.
- `frontend/AGENTS.md`: frontend architecture, state ownership, API invariants, UI contract, and required checks.
- `frontend/README.md`: current product behavior, API modes, backend expectations, and MVP boundaries.
- `frontend/eslint.config.ts`: enforced dependency direction and Vue/TypeScript style.
- `frontend/tsconfig.app.json`: strict TypeScript settings and `@/*` alias.
- `frontend/package.json`: supported dependencies and validation commands.
- `frontend/components.json`: local shadcn-vue-style UI aliases and icon choice.

## Component Reuse

Start every reuse search with:

```bash
rg --files frontend/src/shared/ui frontend/src/widgets
sed -n '1,240p' frontend/src/shared/ui/index.ts
find frontend/src/widgets -maxdepth 3 -name index.ts -print
```

Search by behavior and markup before inventing a name:

```bash
rg -n 'App(Dialog|Sheet|Button|Input|Select|EmptyState|Skeleton)|defineModel|defineEmits|aria-live' frontend/src
```

Use these representative patterns:

- `frontend/src/shared/ui/AppButton.vue`: variants, loading state, typed props, and token-based classes.
- `frontend/src/shared/ui/AppDialog.vue`: accessible Reka UI composition and `defineModel`.
- `frontend/src/shared/ui/AppFormField.vue`: label, hint, and validation error presentation.
- `frontend/src/shared/ui/index.ts`: shared UI public API.
- `frontend/src/entities/project/ui/ProjectCard.vue`: passive entity UI that emits intent.
- `frontend/src/widgets/project-board/ui/ProjectBoardView.vue`: substantial widget composition, route-backed filters, local display preferences, permissions, and UI states.

## Slice Patterns

- Entity model/API/query: `frontend/src/entities/project/`.
- Wire validation and mapping: `frontend/src/entities/project/api/wire.ts`.
- Resource port and provider use: `frontend/src/entities/project/api/port.ts`.
- Query keys and server-state reads: `frontend/src/entities/project/api/queries.ts`.
- Feature form and validation: `frontend/src/features/project-create/`.
- Mutation orchestration: `frontend/src/features/project-create/use-project-mutations.ts`.
- Optimistic cache workflow: `frontend/src/features/work-item-move/use-move-work-item.ts` and `frontend/src/entities/board/model/cache.ts`.
- Widget public API: `frontend/src/widgets/project-board/index.ts`.
- Thin page: `frontend/src/pages/board/BoardPage.vue`.
- Lazy route wiring: `frontend/src/app/router/routes.ts`.
- HTTP/demo provider selection: `frontend/src/app/providers/project-management-api.ts`.

## Test Patterns

- Pure domain/cache tests: `frontend/tests/unit/board-cache.spec.ts`, `order.spec.ts`, and `mapping.spec.ts`.
- Form schema tests: `frontend/tests/unit/schemas.spec.ts`.
- Demo resource integration tests: `frontend/tests/integration/mock-project-api.spec.ts`.
- User flow smoke tests: `frontend/e2e/smoke.spec.ts`.

Find the closest test before adding a new test file:

```bash
rg -n 'describe\(|test\(' frontend/tests frontend/e2e
```

## Boundary Audit

After adding or moving slices, inspect public APIs and deep imports:

```bash
find frontend/src -name index.ts -print | sort
rg -n 'from "@/(app|pages|widgets|features|entities)/[^";]+/' frontend/src
```

Interpret results in context: imports through `@/<layer>/<slice>` are public API imports; imports that reach into another slice's internal `api`, `model`, or `ui` segment require correction unless they use an approved entity `@x` cross-API.
