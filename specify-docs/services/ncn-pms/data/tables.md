# ncn-pms Database Tables

## Applicability and Database Status

Applicable. PostgreSQL SQLAlchemy mappings below are **Present** by authorized inspection on 2026-08-13. Table names use the current shared backend schema. No migration execution was performed. Authz `users`/`project_users` and agent `pms_agents` are intentionally not PMS-owned; their current physical colocation does not change logical ownership.

## Table Inventory

| ID | Schema.table | Purpose | Authoritative/derived | Lifecycle | Models |
|---|---|---|---|---|---|
| TABLE-PMS-001 | `public.pms_projects` | Project root, board/sequence versions | Authoritative | Create; archive/restore; retained | MODEL-PMS-001/005 |
| TABLE-PMS-003 | `public.pms_states` | Ordered workflow stages | Authoritative | Create/update/reorder/delete guarded | MODEL-PMS-002 |
| TABLE-PMS-004 | `public.pms_work_items` | Cards and ordering | Authoritative | Create/update/move/delete/retain history Open | MODEL-PMS-003 |
| TABLE-PMS-005 | `public.pms_work_item_assignees` | Card-user links | Authoritative relation | Replace with card assignment; cascade card | MODEL-PMS-003 |
| TABLE-PMS-006 | `public.pms_epics` | Epics and derived-work root | Authoritative | Create/update/delete; detach cards | MODEL-PMS-004 |
| TABLE-PMS-007 | `public.pms_epic_assignees` | Epic-user links | Authoritative relation | Replace; cascade epic | MODEL-PMS-004 |
| TABLE-PMS-008 | `public.pms_board_preferences` | Per-user display/collapse | Authoritative preference | Upsert; delete with project/user policy | MODEL-PMS-005 |

## PMS-Owned Present Schema and External Authz Reference

### Ownership and Purpose

`ncn-pms` is the sole writer of its owned tables. `ncn-authz` owns `users`/`project_users`; `ncn-agents` owns agent state. Present code runs in a shared backend. The frontend and other services must not treat PMS tables as supported direct interfaces.

### Columns

| Table | Key columns | Required/null/default | Key/constraint | Sensitivity | Meaning |
|---|---|---|---|---|---|
| `pms_projects` | base `id`; workspace/name/identifier; description/icon/color/access; default state; archive; board/sequence counters; creator/times/version | Description/default/archive nullable; counters/version default 1 | unique workspace+identifier; positive versions | Internal | Project aggregate root |
| `pms_states` | base `id`; project/name/color/group/position/default/version | Required; default false; version 1 | FK project cascade; unique project+position/name(CI); partial unique default | Internal | Workflow |
| `pms_work_items` | base `id`; project/sequence/title/HTML/state/priority/epic/dates/rank/creator/times/version | Epic/dates nullable; description empty; priority none | FKs; unique project+sequence and project+state+rank; date check | Potentially confidential | Card |
| `pms_work_item_assignees` | base `id`; work_item/user | Required | FK card cascade; unique card+user | Personal | Assignment |
| `pms_epics` | base `id`; project/sequence/title/HTML/state/priority/dates/rank/creator/times/version | Dates nullable; description empty; priority none | FKs; unique project+sequence/rank; date check | Potentially confidential | Epic |
| `pms_epic_assignees` | base `id`; epic/user | Required | FK epic cascade; unique epic+user | Personal | Assignment |
| `pms_board_preferences` | base `id`; project/user/display JSONB/collapsed UUID[]/version | Defaults show fields/empty collapse/version 1 | FK project cascade; unique project+user | Internal | User preference |

### Relationships and Constraints

All PMS child project FKs cascade except stage references from cards/epics restrict deletion; card epic FK sets null. Manager transaction must prove referenced states/epics belong to the same project, while user membership/assignment eligibility is validated through the common authz relation. Default-state pointer resolution/creation order is transactionally managed. UUID base columns and inherited audit fields follow shared backend base mapping.

### Access Patterns and Indexes

| Query/access pattern | Filter/order | Expected volume | Index/partition | Verification |
|---|---|---|---|---|
| Project list | workspace, archive, identifier/sort | Open | workspace/archive indexes; unique workspace+identifier Present | Query plan/load test before production |
| Board/stage list | project, position | Stages low; cards potentially high | project+position unique; card project/state/rank unique | Present constraints; explain/load test Open |
| Work search/filter | project, state, epic, due, creator, rank | Open | indexes on project/state/epic/due/creator plus rank unique | Present mapping; search index adequacy Open |
| Assignment/member lookup | project/resource/user | Open | PMS assignment indexes plus external authz project/user index | PMS query and authz contract tests |
| Preference lookup | project+user | One row/user/project | unique project+user | Present mapping |

### Transactions and Concurrency

Project bootstrap, stage default switch/reorder/delete-transfer, card create/move/delete, epic membership/delete, sequence allocation and board-version changes are atomic. Optimistic versions prevent lost updates; movement locks/validates affected ordering. Client IDs/mutation IDs need a durable uniqueness/deduplication record where the current resource ID alone is insufficient.

### Lifecycle, Retention, and Privacy

Project archive is logical and read-only. Physical deletion, work-history retention, member deactivation, rich-text retention, and legal-hold rules are Open. Cascades must not bypass audit/retention policy. Encrypt at rest via platform controls; restrict member/content access and mask non-production copies.

### Schema Evolution

All extraction or schema changes are Planned until migration evidence exists. Use expand/backfill/verify/switch/contract, preserve UUID/version/scope, support rollback before destructive cleanup, and keep API compatibility. Authz User/ProjectUser migration is owned by its table contract; moving `pms_agents` to agents ownership requires a separate cross-service decision.

### Backup, Restore, and Data Quality

Back up authoritative PostgreSQL with tested restore. Validate unique default/position/rank, project-consistent references, positive versions/counters, date order, non-orphan assignees, board-version monotonicity, and aggregate counts/progress. Alert on violations and reconcile derived projections after restore.

## Cross-Table Rules

Use UUID identities, UTC timestamps, project scope, owner-only writes, optimistic versions, explicit FKs, and atomic invariant changes. Do not place writable agent/PLM/procurement state in PMS tables.

## Traceability

PMS-owned TABLE-PMS-001/003..008 plus external TABLE-AUTHZ-001/002 → MODEL-PMS-001..005 → PMS-INV-001..009 → SCN-001..003 → API-PMS-001..007 and API-AUTHZ-003 → DEC-PMS-001/002/004.
