# Current Data Ownership Map

## Ownership Inventory

| Data/capability | System of record | Write owner | Consumers | Access contract | Projection/cache/search | Sensitivity |
|---|---|---|---|---|---|---|
| Persisted users, project-user roles, authorized actor/permission projection | Shared PostgreSQL / `ncn-authz` | `ncn-authz` logical common layer | All backend services/frontends | [Authz interface](../services/ncn-authz/interfaces/api.md) | Request-scoped projection; no authz cache specified | Personal/security/restricted credential hash |
| Projects, stages, board/preferences, cards, epics | PostgreSQL / `ncn-pms` | `ncn-pms` | Frontend, future agent tools | [PMS API](../services/ncn-pms/interfaces/api.md) | TanStack Query; mock `localStorage` demo | Internal/member/content-sensitive |
| Agent mutable configuration/status | Current `public.pms_agents`; target logical owner `ncn-agents` | `ncn-agents` semantics in shared backend | Frontend, future Runs | [Agents API](../services/ncn-agents/interfaces/api.md) | TanStack Query | Restricted instructions/tool metadata |
| Sessions, Messages, Runs, snapshots, plans, invocations, tools, approvals, usage, Run events/results | Planned PostgreSQL / `ncn-agents` | `ncn-agents` | Frontend/operators | [Planned Run API](../services/ncn-agents/interfaces/api.md) | Temporal workflow progress; UI projections | Confidential/restricted |
| Agent artifacts | Planned PostgreSQL metadata + MinIO/S3 bytes | `ncn-agents` for Run artifact metadata | Agent/UI/memory module | Agent artifact API | Derived text/chunks | Potentially confidential |
| Agent memory/RAG | Planned primary source refs/metadata in PostgreSQL; vectors in Qdrant | `ncn-agents` memory module for derived index | Coordinator/workers | Internal memory contract | Qdrant rebuildable | Inherits source classification |

## Cross-Service Data Rules

- Authz is the sole logical owner of User/ProjectUser identity and role semantics. Consumers preserve `user.id` and never copy role truth or accept token/client permission grants.
- PMS is the sole writer and system of record for project work. Agent Run/effect records may reference a PMS resource/version but never replace it.
- Agents owns agent configuration/execution state even while `pms_agents` is physically colocated and named. The extraction/migration must preserve IDs, versions and project scope.
- Frontend query cache and browser mock storage are projections/demo data, not production truth.
- Temporal owns workflow progress only. Qdrant is rebuildable; MinIO/S3 bytes require authoritative metadata/checksum/lifecycle.
- Every scoped record/command includes project identity; domain IDs used for replay/duplicate safety remain stable; secrets, bearer contents and password hashes are never indexed or logged.

Physical details are owned by the two service `data/` contracts.
