# Feature Planning Context

This file applies to the whole `feat-ncn-authz-service/` package. It preserves the feature contract for future planning, review, and implementation agents. More specific repository instructions still apply to implementation subtrees.

## Required Reading Order

1. `README.md` for status, scope snapshot, navigation, and vocabulary.
2. `feature.md` for authoritative requirements, invariants, acceptance, assumptions, and Open questions.
3. `scenarios.md` for observable behavior and recovery.
4. Task-specific design/interface/data documents.
5. `decisions.md` before changing a boundary or rejected alternative.
6. `delivery/plan.md` before implementation or rollout work.

For backend work also read `backend/AGENTS.md` and use the applicable backend workflow. For frontend work also read `frontend/AGENTS.md` and use the applicable frontend workflow. This package itself remains documentation-only under `specify-plan`.

## Authority

Within this package, `feature.md` owns requirements and acceptance; `scenarios.md` owns behavior; `design/technical.md` owns component/flow design; `design/ui-ux.md` owns frontend experience; `interfaces/api.md` owns machine interfaces; `data/model.md` owns data/state; `decisions.md` owns consequential choices; and `delivery/plan.md` owns slices/rollout.

When sources conflict, follow the user's current explicit request, accepted project contracts/decisions, verified repository behavior, older notes, then labeled assumptions. Never average contradictory contracts.

## Evidence Sources

- Repository root `AGENTS.md` and `docs/services/ncn-authz/**` for NCN ownership and architecture.
- Current `backend/**` User, ProjectUser, authentication, authorization, and consumer behavior for compatibility evidence.
- Current `frontend/**` route/settings/member/shared-UI patterns for potential reuse.
- Current repository service documentation and contracts for workspace/project ownership, role names, SSO ingress, and frontend routing.

## Scope

- `ncn-authz` owns DATA-001 User, DATA-002 WorkspaceUser, DATA-003 ProjectUser, DATA-004 ServiceUser, and named authorization evaluation.
- SSO supplies only allowlisted OIDC identity claims: required verified email and optional display name. These claims identify/provision DATA-001 and never define access.
- Roles/access change only through direct browser management APIs or PMS creator bootstrap.
- The frontend calls API-001/003/004/006 directly through Traefik/oauth2-proxy.
- API-002/005 are internal workload-authenticated interfaces; API-007 is local development/test compatibility only.
- PMS owns workspace/project business objects; authz stores opaque access scope references only.
- MVP excludes UserIdentity, SSO-derived access rules, durable authz audit, command receipts, persisted decisions, custom roles, and general ACLs.

## Change Propagation

- Requirement/invariant change → scenarios, acceptance, APIs, data, decisions, and delivery.
- Actor/permission change → scenario permissions, UI visibility/states, API authorization/errors, data guards, concurrency tests, and telemetry.
- Identity change → trust carrier, API-001/007, DATA-001, security/privacy, migration, DEC-003, and SLICE-002.
- Workspace/project/service role change → API-002/003/004/006, DATA-002..004, UX-002..004, last-owner/admin and ceiling guards, matrix tests, and SLICE-003/004.
- Ownership/routing change → technical dependencies, APIs, DEC-001/006, rollout, root service docs, and this README.
- Retry/failure change → scenario recovery, API concurrency semantics, transactions, UI canonical reload, logs/metrics, and rollback.
- Any stable ID/document inventory change → README routes and all traceability tables.

## Implementation Handoff

Resolve blocking Open questions for the target slice before code. Re-inventory implementation paths at slice start; a path marked Planned is not proof of existing code. Preserve one write authority and existing IDs/valid roles. Do not create migrations or edit runtime code while operating under this documentation skill.

Implementation must not add omitted MVP entities as incidental infrastructure. A need for identity links, SSO-derived access, immutable audit, receipts, decision persistence, new broker/workflow/cache, or an aggregation service requires an explicit contract/decision update first.

## Validation

Run:

```bash
python3 .agents/skills/specify-plan/scripts/validate_feature.py feat-ncn-authz-service
```

Then search for template/TODO markers, stale identifiers, positive `ncn-portal-api` dependencies, OIDC input beyond the allowlisted identity claims, omitted DATA entities, and implementation claims that lack evidence. The package is ready only when validation passes and enabled slices have their blocking Open contracts resolved.
