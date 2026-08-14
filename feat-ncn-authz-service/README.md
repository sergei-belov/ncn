# Feature Plan: ncn-authz Workspace and Project Access Service

## Status

- Package: **Draft, implementation-ready after blocking Open contracts are resolved**
- Slug: `ncn-authz-service`
- Planning root: repository root
- Updated: 2026-08-14
- Validation: run the `specify-plan` validator after every contract change
- Implementation: not started by this package

`ncn-authz` manages application Users, workspace/project role assignments, optional project-service access restrictions, and authorization decisions. SSO provides only allowlisted OIDC identity claims: required verified email and optional display name. These claims identify or provision a User and never define access. `ncn-pms` retains workspace/project business ownership.

The NCN frontend calls browser-facing authz APIs directly through Traefik/oauth2-proxy. `ncn-portal-api` does not exist and is not a dependency. No identity-link, durable authz-audit, command-receipt, or persisted-decision table is part of the MVP.

## Scope Snapshot

| Included | Excluded / deferred |
| --- | --- |
| SSO User lookup/lazy creation from verified OIDC email | Any SSO-derived access rule |
| Local auth compatibility in development/test only | Issuer/subject identity linking and automatic email-change recovery |
| Workspace roles `owner|admin|member` | Workspace/project business records |
| Project roles `admin|member|viewer` | Durable compliance audit and command receipts in MVP |
| Optional narrowing project-service access | General ACLs, custom roles, default OIDC grants |
| Direct frontend session/access APIs | Frontend aggregation or domain API proxying |
| Internal named authorization checks and PMS bootstrap | Implementation or migrations in this planning package |
| Structured privacy-safe logs/metrics | Full OIDC payloads, tokens, passwords, or hashes in telemetry |

## Start Here

Read [feature.md](feature.md) first for authoritative scope, requirements, invariants, acceptance, assumptions, and Open questions. Continue with [scenarios.md](scenarios.md), then follow the route matching your task below.

## Reading Routes

| Task | Read in order |
| --- | --- |
| Product/scope review | `feature.md` → `scenarios.md` → `decisions.md` |
| Backend implementation | `feature.md` → `scenarios.md` → `design/technical.md` → `interfaces/api.md` → `data/model.md` → `delivery/plan.md` |
| Frontend implementation | `feature.md` → `scenarios.md` → `design/ui-ux.md` → `interfaces/api.md` → `delivery/plan.md` |
| Security/SSO review | `feature.md` security/Open questions → `decisions.md` DEC-002/003/006 → `design/technical.md` security → `interfaces/api.md` authentication |
| Migration/rollout | `data/model.md` → `decisions.md` DEC-004 → `delivery/plan.md` |
| Data-structure review | `decisions.md` DEC-001/002 → `data/model.md` → `design/technical.md` current state |
| Future agent handoff | `AGENTS.md` → this README → task-specific route |

## Document Map

| Document | Authority |
| --- | --- |
| [feature.md](feature.md) | Outcomes, scope, requirements, invariants, quality, acceptance, assumptions, Open questions |
| [scenarios.md](scenarios.md) | SSO User, authorization, workspace/project administration, failure, and bootstrap behavior |
| [design/technical.md](design/technical.md) | Current NCN context, components, flows, trust, ownership, operations, rollout |
| [design/ui-ux.md](design/ui-ux.md) | Direct frontend surfaces, states, interaction rules, accessibility, responsive behavior |
| [interfaces/api.md](interfaces/api.md) | Session, decision, workspace/project/service access, bootstrap, and local compatibility APIs |
| [data/model.md](data/model.md) | DATA-001..004 ownership, schema, relationships, lifecycle, migration, privacy |
| [decisions.md](decisions.md) | Consequential choices, rejected alternatives, consequences, reversal, Open decisions |
| [delivery/plan.md](delivery/plan.md) | Dependency-ordered slices, validation, rollout, rollback, completion gate |
| [AGENTS.md](AGENTS.md) | Persistent operating context and change-propagation rules |

## Evidence and Decision Vocabulary

- **Confirmed:** verified from the repository or the user's explicit correction.
- **Accepted constraint/direction:** must be followed unless the user/project changes it.
- **Assumed:** usable for planning but must be tested before the dependent slice.
- **Open:** unresolved; the named surface cannot ship when marked blocking.
- **Planned:** proposed implementation, not proof that code/config/migrations exist.

Authority order is the current user request, accepted project contract/decision, verified repository behavior, older notes, then labeled assumptions. The user's narrower MVP notes supersede earlier draft concepts for extra persistence.

## Maintenance Rules

- Keep stable IDs (`OUT`, `REQ`, `INV`, `NFR`, `SCN`, `UX`, `API`, `DATA`, `DEC`, `SLICE`) aligned across documents.
- Preserve domain ownership: authz stores access relationships; PMS owns workspace/project business state.
- SSO changes require checking the allowlisted OIDC identity claims, API trust, security, scenarios, data, and rollout; access remains database-managed.
- Role/permission changes require checking scenarios, API authorization/errors, UI states, data constraints, concurrency, logs, tests, and delivery.
- Keep direct browser authz routing explicit. Do not reintroduce `ncn-portal-api` without a new accepted architecture decision.
- Mark implementation surfaces and migrations Planned until inspected/created by the relevant development workflow.
- Run `.agents/skills/specify-plan/scripts/validate_feature.py feat-ncn-authz-service` after edits and resolve every error.
