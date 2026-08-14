# Feature Planning Context

<!-- TEMPLATE: Replace with a concise feature purpose, current plan maturity, and applicable repository instruction precedence. -->

## Required Reading Order

Before implementing or changing this feature, read:

1. `README.md` for navigation and document authority.
2. `feature.md` for scope, requirements, invariants, and acceptance.
3. `scenarios.md` for observable behavior and recovery.
4. `delivery/plan.md` for slice boundaries and validation.
5. Only the technical, UI/UX, API, data, and decision sections linked by the selected slice.

## Authority

Apply the user's current explicit request first, then accepted project contracts and decisions, then verified repository behavior, then this active feature package, then older planning notes. Record conflicts as open decisions; do not silently blend them.

## Scope

- Treat `feature.md` as the source of truth for feature behavior.
- Keep scenarios in `scenarios.md`, technical design in `design/technical.md`, UX behavior in `design/ui-ux.md`, machine interfaces in `interfaces/api.md`, and state contracts in `data/model.md`.
- Keep delivery-only scope, sequencing, validation, rollout, and rollback in `delivery/plan.md`.
- Do not treat planned paths or symbols as present implementation.

## Change Propagation

- Update scenarios, design, interface, data, acceptance, and delivery links when requirements change.
- Update authorization, UI states, API errors, audit, and tests when actor permissions change.
- Update compatibility, migration, rollout, rollback, and observability when data or interface contracts change.
- Keep `README.md` navigation complete whenever documents are added, removed, or renamed.

## Validation

<!-- TEMPLATE: Replace with the repository-relative command that runs validate_feature.py for this feature folder. -->
