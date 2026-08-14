---
name: frontend-plan-develop
description: Plan, implement, and validate Vue 3 and TypeScript frontend changes in this repository while following `frontend/AGENTS.md`, maintaining a task-specific Markdown development checklist, and maximizing reuse from `frontend/src/shared/ui` and `frontend/src/widgets` before creating components. Use when Codex needs to add, change, refactor, or fix UI, routes, pages, widgets, features, entity state or API code, forms, or tests under `frontend/**`.
---

# Frontend Planner & Developer

Implement frontend features and fixes through a checklist-driven workflow that preserves the repository's pragmatic Feature-Sliced Design, component contracts, server-state model, and product behavior.

## Required Start

1. Read `AGENTS.md`, `frontend/AGENTS.md`, and the relevant sections of `frontend/README.md`.
2. Read any specification or contract named by the user. Search `contracts/` and `docs/` when the request depends on existing product behavior.
3. Read `references/source-map.md` and inspect the nearest live files for every affected layer.
4. Derive a short kebab-case task slug from the request.
5. Create `docs/tasks/<task-slug>-frontend-checklist.md` from `assets/development-checklist.md` before editing any file under `frontend/**`. Create `docs/tasks/` if needed.
6. Customize the checklist with concrete acceptance criteria, affected slices, reuse candidates, tests, and validation commands. Never skip the checklist for a small feature or fix.
7. If the checklist already exists, preserve useful history, update its scope, and continue using it instead of replacing it.

Keep the checklist current during development. Mark an item complete only after the corresponding work or check succeeds. For a conditional item that does not apply, record the concrete reason and mark the applicability decision complete. Record blockers, skipped required checks, and exact failure reasons without marking them complete.

## Plan the Change

- Map the change onto `app -> pages -> widgets -> features -> entities -> shared` and preserve dependencies toward the right.
- Keep pages thin, widgets compositional, features action-oriented, entities domain-owned, and shared code business-neutral.
- List public API updates (`index.ts`), route changes, API contracts, query keys/cache effects, permissions, and required tests before coding.
- Preserve existing product behavior for loading, error, empty, disabled, archived read-only, permissions, responsive layout, theme, toasts, and direct-link navigation unless the request explicitly changes it.
- Add the resulting implementation steps to the Markdown checklist in dependency order.

## Reuse Before Creation

Before creating a component:

1. Run `rg --files frontend/src/shared/ui frontend/src/widgets`.
2. Inspect `frontend/src/shared/ui/index.ts` and the public `index.ts` of relevant widget slices.
3. Search for the required interaction and presentation patterns across existing consumers, not only for the proposed component name.
4. Record the components considered and the reuse decision in the checklist.

Use this precedence while respecting layer boundaries:

1. Reuse or compose primitives from `shared/ui` for business-neutral controls and presentation.
2. Reuse an existing widget for a substantial page composition when the importing layer may depend on widgets.
3. Reuse entity UI for passive domain representations and an existing feature for an established user action.
4. Extend an existing component with a small, cohesive prop, slot, or variant when doing so preserves its abstraction.
5. Create a component only when no suitable abstraction exists or extending one would combine unrelated responsibilities.

Never import upward to force reuse. If a lower layer needs reusable behavior currently trapped in a higher layer, extract the business-neutral part to `shared` or the domain-owned part to `entities`, then reuse it from both places.

## Place New Code

- Put generic visual primitives in `shared/ui` and export them from `shared/ui/index.ts`.
- Put generic transport, configuration, routes, or utilities in the matching `shared` segment; keep `shared` domain-neutral.
- Put domain types, resource ports/adapters, wire schemas/mappers, queries, cache helpers, and passive domain UI in the owning `entities/<entity>` slice.
- Put forms, validation, mutations, and user-action orchestration in `features/<feature>`.
- Put substantial reusable page compositions in `widgets/<widget>`.
- Put only route-level composition in `pages/<page>`.
- Put bootstrap, providers, router wiring, global styles, and demo adapters in `app`.
- Add or update a slice `index.ts`. Import other slices through their public APIs; use relative imports only within the same slice.
- Use explicit entity `@x` cross-APIs only for aggregate schemas that genuinely require them.

## Follow Project Code Style

- Use Vue 3 `<script setup lang="ts">` and strict TypeScript.
- Use type-only imports for types and follow the neighboring import grouping and formatting.
- Define typed props, emits, models, slots, and exposed methods. Keep component contracts narrow.
- Make components receive data and emit intent. Do not navigate from entity UI or hide mutation orchestration inside presentational components.
- Reuse Tailwind tokens, `cn`, and existing component variants. Preserve light/dark theming; do not introduce one-off visual systems.
- Use semantic HTML, labels, keyboard-accessible controls, focus treatment, and live announcements where interactions need them.
- Keep user-facing copy consistent with the existing Russian interface unless the request specifies otherwise.
- Follow the lint-enforced dependency boundaries in `frontend/eslint.config.ts`.

## Preserve State and API Contracts

- Use TanStack Vue Query as the only server-state owner. Do not mirror server entities in Pinia or ad hoc global stores.
- Keep dialog, form, and sheet state local; keep route-reproducible filters in router query parameters; use `useStorage` only for display preferences.
- Update query caches through pure entity helpers, then invalidate after mutations.
- For optimistic board moves, cancel matching queries, snapshot every affected variant, update immutably, roll back every snapshot on failure, and refetch after settlement.
- Keep resource ports and HTTP adapters with the owning entity. Keep generic transport in `shared/api` and demo persistence/adapters in `app/mocks`.
- Validate HTTP responses with Zod. Keep wire DTOs `snake_case` and domain models `camelCase`.
- Preserve idempotency keys, entity versions,  `board_version`, and `client_mutation_id` where applicable.

## Test and Validate

- Add or update the smallest meaningful tests for changed schemas, mappers, cache helpers, interactions, mock APIs, routes, and user-visible flows.
- Run focused tests during implementation when useful.
- Run all required checks from `frontend/` before completion:

```bash
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm test:e2e -- --list
```

- After structural changes, audit imports:

```bash
rg -n '@/app|@/pages|@/widgets|@/features|@/entities' src
```

- Run full browser E2E tests when the requested behavior changes a covered critical flow or when the user asks for them. Report an unavailable browser/runtime as a validation limitation, not as a passed check.
- Record each command and outcome in the checklist. Fix failures caused by the change. Clearly identify unrelated or environment-blocked failures.
- Review the final changed files or diff for stray deep imports, duplicated components, missing exports, missing states, and accidental generated artifacts.

## Completion

- Ensure every acceptance criterion and applicable checklist item is complete.
- Leave incomplete items unchecked and explain why; never claim full validation when a required check did not run or pass.
- Summarize the implementation, component reuse or creation decisions, validation results, and the checklist path in the final handoff.

## Resources

- Read `references/source-map.md` for live repository exemplars and discovery commands.
- Copy `assets/development-checklist.md` to `docs/tasks/<task-slug>-frontend-checklist.md` for every feature or fix.
