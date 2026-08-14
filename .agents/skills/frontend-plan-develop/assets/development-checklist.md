# <Feature or Fix Title> — Frontend Development Checklist

## Context

- Task slug: `<task-slug>`
- Change type: `feature | fix | refactor`
- Request/specification: `<source>`
- Affected routes/slices: `<list>`
- Status: `planned | in progress | blocked | complete`

## Acceptance Criteria

- [ ] `<observable behavior or invariant>`
- [ ] `<observable behavior or invariant>`

## Architecture and Reuse

- [ ] Read `AGENTS.md`, `frontend/AGENTS.md`, relevant `frontend/README.md` sections, and named specifications/contracts.
- [ ] Assign each change to the correct FSD layer and confirm dependency direction.
- [ ] Inspect `shared/ui`, widget public APIs, and nearby consumers for reuse candidates.
- [ ] Record reuse candidates and the decision: `<components and rationale>`.
- [ ] List required public API, route, query/cache, provider, or mock updates: `<updates>`.

## Implementation

- [ ] `<implementation step>`
- [ ] `<implementation step>`
- [ ] Preserve permissions, archived read-only behavior, and API concurrency/idempotency contracts where applicable.
- [ ] Cover loading, error, empty, disabled, responsive, theme, toast, and accessibility behavior where applicable.
- [ ] Export new or changed slice APIs through `index.ts` and remove cross-slice deep imports.

## Tests

- [ ] Add or update focused unit/integration tests: `<tests>`.
- [ ] Decide whether E2E coverage is required and add or update it when needed: `<coverage or concrete not-applicable reason>`.

## Validation Results

- [ ] `cd frontend && pnpm typecheck` — `<result>`
- [ ] `cd frontend && pnpm lint` — `<result>`
- [ ] `cd frontend && pnpm test` — `<result>`
- [ ] `cd frontend && pnpm build` — `<result>`
- [ ] `cd frontend && pnpm test:e2e -- --list` — `<result>`
- [ ] Decide whether an import-boundary audit is required and run it when needed — `<result or concrete not-applicable reason>`
- [ ] Decide whether full browser E2E is required and run it when needed — `<result or concrete not-applicable reason>`

## Final Review

- [ ] Review changed files/diff for duplicated UI, missing states, missing exports, deep imports, and generated artifacts.
- [ ] Confirm every acceptance criterion is met.
- [ ] Document remaining limitations or follow-up work: `<none or details>`.
