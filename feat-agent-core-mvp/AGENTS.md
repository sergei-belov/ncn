# Agent Core MVP Planning Context

This folder is the authoritative implementation plan for the first sessionless `ncn-agents` vertical slice. It defines one project coordinator configuration, direct Runs, a bounded agent loop, Temporal durability, and read-only system MCP access. The plan is a draft for implementation review; no runtime code exists in this folder.

Repository instruction precedence remains: root `AGENTS.md`, then the nearest instructions for any implementation subtree (notably `backend/AGENTS.md`), then this feature package for feature behavior. The user's current explicit request overrides older broader plans.

## Required Reading Order

Before implementing or changing this feature, read:

1. `README.md` for navigation and document authority.
2. `feature.md` for scope, requirements, invariants, and acceptance.
3. `scenarios.md` for observable behavior and recovery.
4. `delivery/plan.md` for slice boundaries and validation.
5. Only the technical, UI/UX, API, data, and decision sections linked by the selected slice.
6. Root `AGENTS.md` and the nearest implementation `AGENTS.md` before changing files outside this folder.

## Authority

Apply the user's current explicit request first, then `contracts/agents/02-invariants/`, then verified repository behavior, then this feature's recorded decisions, then the v1.3-derived module and implementation details. Surface conflicts instead of silently blending them.

The v2 contract calls Sessions, workers, approval, memory, and other features part of its full MVP. This package deliberately defines an earlier vertical slice. Do not claim this feature alone satisfies the full v2 readiness criteria.

## Scope

- Treat `feature.md` as the source of truth for feature behavior.
- Keep the external Run contract sessionless: do not add `session_id`, Message ingestion, conversational history, follow-up input, or wait-for-input behavior.
- Keep one non-delegating project coordinator. Do not add workers, handoffs, child agent workflows, dynamic DAGs, or RunPlan revisions.
- Permit only allowlisted read-only tools from one deployment-provisioned system MCP. Do not add mutating tools, Approval, user MCP credentials, or direct domain-database access.
- Keep PostgreSQL as product state authority and Temporal as durable execution authority.
- Keep model and MCP network operations in Temporal Activities. Do not hide an MCP call inside replayable workflow code or a retryable model Activity.
- Keep scenarios in `scenarios.md`, technical design in `design/technical.md`, machine interfaces in `interfaces/api.md`, and state contracts in `data/model.md`.
- Do not treat planned paths or symbols as present implementation.

## Change Propagation

- Update scenarios, design, interface, data, acceptance, and delivery links when requirements change.
- Update authorization, API errors, audit, and tests when actor permissions change.
- Update retry, idempotency, replay, cancellation, compatibility, rollout, and observability together when execution behavior changes.
- If a mutating tool enters scope, stop and revise Approval, idempotency, reconciliation, data, scenarios, and delivery contracts before implementation.
- If Sessions enter scope, create or revise a separate feature contract rather than smuggling Session semantics into this one.
- Keep `README.md` navigation complete whenever documents are added, removed, or renamed.

## Implementation Handoff

Use the repository `backend-plan-develop` workflow for backend implementation. Preserve the logical `ncn-agents` ownership boundary even if the first deployable is physically co-located with existing Python infrastructure. Do not place agent-owned business state in `ncn-pms` tables or access PMS tables directly; use owner interfaces.

## Validation

Run from the repository root:

```bash
python3 .agents/skills/specify-plan/scripts/validate_feature.py feat-agent-core-mvp
```
