# Feature Planning System

## Contents

- [Document model](#document-model)
- [Document authority](#document-authority)
- [Contract coverage](#contract-coverage)
- [Stable identifiers and traceability](#stable-identifiers-and-traceability)
- [Applicability rules](#applicability-rules)
- [Consistency and change propagation](#consistency-and-change-propagation)
- [Delivery slicing](#delivery-slicing)

## Document model

Create exactly this required baseline, allowing additional linked documents only when they materially improve the plan:

```text
feat-{feature-slug}/
├── AGENTS.md
├── README.md
├── feature.md
├── scenarios.md
├── decisions.md
├── design/
│   ├── technical.md
│   └── ui-ux.md
├── interfaces/
│   └── api.md
├── data/
│   └── model.md
└── delivery/
    └── plan.md
```

Use lowercase ASCII kebab-case for `{feature-slug}`. Keep feature-package navigation self-contained with relative links inside the folder. Cite project-level paths as evidence without copying their full contracts or creating local Markdown links that escape the feature folder.

## Document authority

| Concern | Authoritative document |
|---|---|
| Navigation, reading routes, package status | `README.md` |
| Feature scope, requirements, invariants, acceptance | `feature.md` |
| User behavior, alternatives, edge cases, recovery | `scenarios.md` |
| Component design, flows, ownership, operations | `design/technical.md` |
| UI structure, interactions, states, accessibility | `design/ui-ux.md` |
| HTTP/API and other machine-facing contracts | `interfaces/api.md` |
| Data ownership, schema, lifecycle, consistency | `data/model.md` |
| Decisions, alternatives, consequences | `decisions.md` |
| Implementation slices, validation, rollout | `delivery/plan.md` |
| Future-agent operating context | `AGENTS.md` |

Keep active truth in these documents. Treat external notes and old proposals as evidence, not as authority. When sources conflict, apply this order:

1. the user's current explicit request;
2. an accepted project contract or decision record;
3. verified current repository behavior;
4. older plans and planning notes;
5. labeled assumptions.

## Contract coverage

### Feature contract

Define the problem, actors, outcomes, measures, in-scope behavior, non-goals, deferred work, functional requirements, invariants, state lifecycle, dependencies, security/privacy boundaries, failure/recovery behavior, observability, acceptance criteria, assumptions, and open questions.

Separate required behavior from proposed implementation. A requirement states an observable obligation; the technical design states how the system should satisfy it.

### User scenarios

Give every material scenario a stable `SCN-NNN` heading. Cover:

- actor and goal;
- preconditions and permissions;
- trigger;
- ordered happy path;
- alternate, empty, boundary, duplicate, concurrent, stale, and partial states that apply;
- validation and dependency failures;
- retry, cancellation, rollback, and user recovery;
- accessibility and input-method considerations;
- observable result and linked acceptance criteria.

Use a scenario inventory to connect scenarios to `REQ-NNN`, UX surfaces, API operations, and delivery slices.

### Technical design

Document verified current behavior separately from proposed design. Define component responsibilities, synchronous and asynchronous flows, state ownership, transactional boundaries, dependencies, trust boundaries, failure isolation, observability, operational controls, performance constraints, deployment effects, compatibility, and rollout.

Use repository-native architecture and shared infrastructure. Do not introduce a new framework, broker, workflow engine, data store, or runtime merely to make the feature plan look complete.

### UI/UX design

Define experience goals, information architecture, navigation, user flows, screen or surface inventory, interaction rules, content, confirmation, and all applicable states: initial, loading, empty, populated, validation error, dependency error, partial, offline or degraded, disabled, permission denied, and success.

Specify keyboard behavior, focus order, semantics, contrast, motion, screen-reader feedback, localization, responsive behavior, and platform differences when applicable. Describe behavior and intent; use wireframes only when spatial relationships are otherwise ambiguous.

### API and interface contract

For each operation, define a stable identifier, owner, consumer, protocol, entry point, authentication, authorization, input schema, optional/null/default semantics, validation, output schema, status behavior, stable errors, idempotency, concurrency, ordering, pagination or streaming, timeouts, rate or size limits, compatibility, deprecation, audit, and examples where useful.

The file may also index events, jobs, webhooks, CLI, or file interfaces when they are part of the feature. Put a large non-HTTP contract in an additional linked document rather than overloading the API document.

### Data and state model

Define authoritative ownership, entity identifiers, fields, types, required/null/default semantics, relationships, uniqueness and other constraints, lifecycle, state transitions, transaction boundaries, consistency, retention, deletion, sensitivity, encryption expectations, access patterns, indexing, migration, backfill, rollback, and audit rules.

Do not claim a migration exists. Describe migration work as planned until verified.

### Decisions

Record only consequential choices. Each `DEC-NNN` entry includes status, context, drivers, decision, alternatives, consequences, reversal conditions, and affected contracts. Keep unresolved choices in the open-decision queue and explain what evidence or owner resolves them.

### Delivery plan

Define dependency-ordered `SLICE-NNN` sections. Each slice includes an observable outcome, prerequisites, in-scope behavior by layer, non-goals, affected contracts, verified or planned implementation surfaces, automated and manual validation, acceptance criteria, rollout, rollback, observability, and documentation updates.

## Stable identifiers and traceability

Use these identifier families:

| Prefix | Meaning | Authoritative location |
|---|---|---|
| `OUT-NNN` | Outcome | `feature.md` |
| `REQ-NNN` | Functional requirement | `feature.md` |
| `INV-NNN` | Invariant | `feature.md` |
| `NFR-NNN` | Quality requirement | `feature.md` |
| `SCN-NNN` | User or system scenario | `scenarios.md` |
| `UX-NNN` | UI surface or interaction contract | `design/ui-ux.md` |
| `API-NNN` | API or machine-interface operation | `interfaces/api.md` |
| `DATA-NNN` | Entity or state contract | `data/model.md` |
| `DEC-NNN` | Consequential decision | `decisions.md` |
| `SLICE-NNN` | Delivery slice | `delivery/plan.md` |

Use IDs only for real entries, never for placeholder rows. Link or cite identifiers from dependent documents. Every in-scope `REQ-NNN` must map to at least one `SCN-NNN`, acceptance criterion, and `SLICE-NNN`; add UX, API, data, and decision links when applicable.

## Applicability rules

All baseline files are mandatory. When a concern does not apply:

1. Keep the file and all required headings.
2. Put `Not applicable` under `## Applicability` or the closest relevant section.
3. State the evidence and reason.
4. State the delivery consequence, such as “no frontend surface changes” or “no external API change.”
5. Keep traceability links to the feature and delivery plan.

Do not invent an API, user interface, database entity, or architecture component to avoid an explicit non-applicability statement.

## Consistency and change propagation

| Change | Also inspect |
|---|---|
| Scope, requirement, invariant | scenarios, design, acceptance, delivery |
| Actor or permission | scenarios, UI states, API authorization, audit |
| User flow or UI state | feature rules, API errors, data state, tests |
| API payload or error | scenarios, UI handling, data mapping, compatibility |
| Entity or state lifecycle | feature, scenarios, API, migration, delivery |
| Component boundary | ownership, APIs/events, data, decisions, rollout |
| Failure or retry rule | scenarios, API idempotency, consistency, observability |
| Implementation path | technical design, delivery, AGENTS context |
| Document inventory | README routes and links |

Reject contradictions instead of averaging them. Record unresolved conflicts as **Open** and name the decision owner or resolution trigger.

## Delivery slicing

Prefer thin vertical slices over layer-only phases. A useful slice demonstrates one observable behavior across the layers needed for that behavior, includes its validation and telemetry, and leaves compatibility intact.

Order slices by dependency and risk:

1. settle blocking contracts or create a safe enabling seam;
2. deliver the smallest end-to-end happy path;
3. add permissions, edge cases, recovery, and accessibility;
4. complete migration, compatibility, operational, and rollout work;
5. remove temporary compatibility paths only after evidence supports cleanup.

Avoid “build backend,” “build frontend,” and “test everything” as isolated slices when they cannot independently satisfy an acceptance criterion.
