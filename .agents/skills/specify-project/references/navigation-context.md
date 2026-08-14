# Persistent Specification Navigation

Use `docs/project-map.md` as durable navigation memory, not as a source-code inventory.

## Required sections

### Snapshot

Record the last review date, specification status, evidence used, active services, and known implementation-verification boundary. Use `present`, `planned`, `external`, or `unknown`; `present` requires explicit verification evidence.

### Reading Routes

Provide routes to understand the project, change a service, add a feature, review architecture, review UI/UX, change an API/event, change models/tables, review security/operations, and validate the spec.

### Documentation Map

List project documents and each service README with purpose, authority, status, and owner.

### Service Ownership Map

Map every service to owned capabilities, authoritative data, exposed interfaces/events, dependencies, forbidden ownership, and status.

### Runtime Entry Points

List only documented or explicitly verified UI routes, APIs, events, jobs, workers, commands, and deployment units. Label their kind and evidence status. Do not inspect implementation merely to populate this table.

### Change Impact Map

Map each capability/feature to its owning service, affected services, scenarios, UI/UX, API/events, models/tables, decisions, implementation path status, tests status, and observability.

### Known Gaps

Record uncertain ownership, missing service contracts, stale docs, unverified paths, unresolved decisions, or absent acceptance evidence with a resolution trigger.

## Update protocol

Update the map whenever a service or feature is added/renamed/retired, ownership changes, a contract or document moves, an entry point changes, or explicit verification changes a path from planned/unknown to present.

After editing:

1. Verify all documentation links.
2. Ensure every service is registered and reachable.
3. Ensure every feature has one owner and is registered at service and project levels.
4. Ensure new documents are reachable from a README or area owner.
5. Confirm every `present` statement cites permitted evidence.
6. Update the snapshot and known gaps.

## Accuracy rules

- Never infer implementation from a proposal, feature spec, planning note, or directory name.
- Never read `frontend/**` or `backend/**` without an explicit documentation-verification request.
- Distinguish filesystem paths, UI routes, API routes, event topics, database objects, packages, and commands.
- Never record secrets, credentials, machine-specific paths, or transient artifacts.
- Keep useful uncertainty as `unknown`; do not convert uncertainty into invented detail.

## AGENTS handoff

Make `docs/AGENTS.md` direct future agents to `docs/README.md`, `docs/spec.md`, `docs/project-map.md`, the relevant project maps, then the selected service `README.md`, `spec.md`, and narrow contract files. Repeat the implementation-inspection boundary.
