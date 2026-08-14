# Specification Operating Context

<!-- TEMPLATE: State the project purpose, specification maturity, and applicable instruction precedence. -->

## Required Reading

Read `docs/README.md`, `docs/spec.md`, and `docs/project-map.md`, then the selected service's `README.md`, `spec.md`, and affected contract documents.

## Authority

Apply the user's current request first, then accepted project and service specifications/decisions, then explicitly verified implementation evidence, then older documentation, then labeled assumptions. Surface conflicts.

## Service Ownership

- Keep each capability, feature, and authoritative data set assigned to one service.
- Update consumer service contracts without copying owner state or behavior.
- Keep project documents focused on cross-service truth.

## Evidence Boundary

Do not inspect implementation code, tests, `frontend/**`, or `backend/**` unless the user explicitly requests verification of documentation against implementation. Never mark planned paths, APIs, models, or tables present without permitted evidence.

## Maintenance

- Register every service and feature at project level.
- Update affected service specs, scenarios, designs, UI/UX, interfaces, models, tables, and decisions together.
- Update `docs/project-map.md` when ownership, paths, entry points, features, or documents change.
- Run the specification validator after changes.

## Validation

<!-- TEMPLATE: Record the repository-relative validate_spec.py command. -->
