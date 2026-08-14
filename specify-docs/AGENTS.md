# NCN Specification Operating Context

NCN is a project-management platform with an internal coordinator-and-worker agent runtime. This documentation is a draft living contract for three current logical services: common authorization in `ncn-authz`, project work in `ncn-pms`, and agent configuration/execution in `ncn-agents`.

## Required Reading

Read `docs/README.md`, `docs/spec.md`, and `docs/project-map.md`, then the selected service's `README.md`, `spec.md`, and affected contract documents.

## Authority

Apply the user's current request first, then accepted project and service specifications/decisions, then explicitly verified implementation evidence, then `contracts/**`, then `docs_old/**`, then labeled assumptions. Surface conflicts rather than merging them silently.

## Service Ownership

- Keep each capability, feature, and authoritative data set assigned to one service.
- Update consumer contracts without copying owner state or behavior.
- Keep project documents focused on cross-service truth.
- Treat `ncn-authz` as the logical owner of common User, ProjectUser, role-policy, and authorized actor semantics even while its implementation is physically shared.
- Treat `ncn-pms` as the sole project-work system of record.
- Keep `ncn-agents` execution-domain neutral: it acts on project work only through PMS APIs/MCP tools.
- Do not create a service contract for a future capability until active development and evidence establish its boundary.

## Evidence Boundary

Do not inspect implementation code, tests, `frontend/**`, or `backend/**` unless the user explicitly requests documentation verification against implementation. Never mark planned paths, APIs, models, tables, or events Present without permitted evidence.

The 2026-08-13 rewrite was explicitly authorized to inspect backend and frontend for missing information. Its verified paths and boundaries are recorded in `docs/project-map.md`.

## Maintenance

- Register every current service and active/in-development feature at project level.
- Update affected service specs, scenarios, designs, UI/UX, interfaces, models, tables, and decisions together.
- Update `docs/project-map.md` when ownership, paths, entry points, features, or documents change.
- Use **Confirmed**, **Assumed**, and **Open** for certainty; use **Present**, **Planned**, **External**, and **Unknown** for implementation/path status.
- Keep GitLab, procurement, analytics, and other future MCP integrations under Deferred/Open until their development starts.
- Run the specification validator after changes.

## Validation

From the repository root:

```bash
python3 .agents/skills/specify-project/scripts/validate_spec.py docs
```
