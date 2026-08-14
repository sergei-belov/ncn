# Data and State Model

## Applicability

Applicable. `ncn-authz` persists Users and workspace/project/service access relationships in PostgreSQL. The MVP does not add an SSO identity-link table, a durable authorization-audit table, command receipts, or persisted decision records. This document plans schema work only; it does not claim that migrations exist.

## Ownership

`ncn-authz` owns DATA-001..004 and all writes to those rows. `ncn-pms` owns workspace/project business records; authz stores their opaque identifiers solely as access scope references. Consumer services receive decisions through API-002 and never copy memberships as authoritative state.

## NCN Model Basis

| NCN concept | Treatment | Reason |
| --- | --- | --- |
| Current `users` | Preserve as DATA-001 with existing NCN UUIDs and local-password compatibility | Existing identity references remain stable |
| Workspace scope | Add DATA-002 without copying workspace business state | `ncn-pms` owns workspaces while authz owns access |
| Current `project_users` | Preserve and evolve as DATA-003 | Existing project access is migration truth |
| Project-service restriction | Add DATA-004 as a narrowing overlay | Supports explicit service access without generalized ACLs |
| OIDC identity input | Use verified normalized email and optional display name only for DATA-001 resolution | SSO identifies a User but never changes access |
| PMS workspace/project records | Store only opaque scope identifiers | Preserves domain ownership |

## Entity Inventory

| ID | Entity / table | Owner | Purpose | Sensitivity |
| --- | --- | --- | --- | --- |
| DATA-001 | User / `users` | `ncn-authz` | Stable application actor and optional local-development credential | Personal/security-sensitive |
| DATA-002 | WorkspaceUser / `workspace_users` | `ncn-authz` | User role in an externally owned workspace | Security-sensitive |
| DATA-003 | ProjectUser / `project_users` | `ncn-authz` | User role in an externally owned project | Security-sensitive |
| DATA-004 | ServiceUser / `service_users` | `ncn-authz` | Optional role restriction for a service inside a project | Security-sensitive |

Authorization decisions are request/response values, not a DATA entity. Security events are structured operational logs, not an authz-owned durable domain table in the MVP.

## Entities and Fields

### DATA-001: User

| Field | Type | Required/default | Constraint | Meaning |
| --- | --- | --- | --- | --- |
| `id` | UUID | Required/generated | Primary key; preserve existing UUID | Stable actor ID |
| `email` | case-insensitive varchar | Required | Unique on canonical normalized value | MVP SSO and local identity key |
| `name` | varchar | Required | Trimmed, bounded | Display name |
| `password_hash` | varchar | Nullable | Null for SSO-only User | Development/test local credential |
| `is_active` | boolean | Required/default true | Disabled denies all access | Account state |
| `created_at`, `updated_at` | timestamptz | Required | Server-managed | Lifecycle metadata |

Email normalization is one documented function used by SSO resolution, local registration, lookup, uniqueness validation, and backfill. Case or surrounding whitespace cannot produce another User. The accepted OIDC identity input is required `email`, required `email_verified=true`, and optional `name`; no other identity-carrier field is persisted or used by this feature.

### DATA-002: WorkspaceUser

| Field | Type | Required/default | Constraint | Meaning |
| --- | --- | --- | --- | --- |
| `id` | UUID | Required/generated | Primary key | Membership ID |
| `workspace_id` | opaque UUID/string | Required | Indexed; references PMS contract, not a cross-service FK | Scope |
| `user_id` | UUID | Required | FK DATA-001 | Member |
| `role` | enum | Required | `owner|admin|member` | Workspace role |
| `version` | integer | Required/default 1 | Increments on each mutation | Optimistic concurrency |
| `created_at`, `updated_at` | timestamptz | Required | Server-managed | Lifecycle metadata |

Unique `(workspace_id, user_id)`. An active workspace must retain at least one owner once workspace access is established. Owner transfer semantics remain Open; ordinary mutation cannot remove the last owner.

### DATA-003: ProjectUser

| Field | Type | Required/default | Constraint | Meaning |
| --- | --- | --- | --- | --- |
| `id` | UUID | Required/generated or preserved | Primary key | Membership ID |
| `project_id` | UUID | Required | Unique with `user_id`; external PMS scope | Project scope |
| `workspace_id` | opaque UUID/string | Required | Indexed; must agree with PMS validation | Parent access scope |
| `user_id` | UUID | Required | FK DATA-001 | Member |
| `role` | enum | Required | `admin|member|viewer` | Project capability ceiling |
| `source` | enum | Required/default `manual` | `manual|bootstrap` | Lifecycle provenance |
| `version` | integer | Required/default 1 | Increments on mutation | Optimistic concurrency |
| `created_at`, `updated_at` | timestamptz | Required | Server-managed | Lifecycle metadata |

Unique `(project_id, user_id)`. Existing NCN ProjectUser identifiers and valid roles are preserved. A project with established access must retain an effective admin. Only API-005 creates `source=bootstrap`; ordinary access administration creates `source=manual` and may subsequently manage a bootstrap row subject to normal guards.

### DATA-004: ServiceUser

| Field | Type | Required/default | Constraint | Meaning |
| --- | --- | --- | --- | --- |
| `id` | UUID | Required/generated | Primary key | Restriction ID |
| `project_user_id` | UUID | Required | FK DATA-003; cascade on authz-owned parent removal | Parent membership |
| `service_id` | bounded identifier | Required | Unique with `project_user_id`; allowlisted | Service scope |
| `role` | enum | Required | `admin|member|viewer`; cannot exceed parent role | Explicit restriction |
| `version` | integer | Required/default 1 | Increments on mutation | Optimistic concurrency |
| `created_at`, `updated_at` | timestamptz | Required | Server-managed | Lifecycle metadata |

Absence means the project role applies to the service. A row exists only when an explicit equal-or-weaker restriction is needed. Removing it restores inheritance. Removing DATA-003 removes its DATA-004 children in the same authz transaction.

## Relationships and Constraints

`User 1 → many WorkspaceUser` and `User 1 → many ProjectUser`. `ProjectUser 1 → zero or many ServiceUser`. Workspace and project IDs are external references validated through the PMS owner contract rather than cross-database foreign keys.

The role strength orders are `workspace owner > admin > member` and `project/service admin > member > viewer`. A service role must be equal to or weaker than its parent ProjectUser role. Check constraints enforce role values; unique constraints enforce one relation at each scope; manager transactions enforce last-owner/admin and actor-ceiling invariants.

There is deliberately no relationship from OIDC identity input to DATA-002..004. Roles change only through API-003/004/006 or API-005 creator bootstrap.

## State Transitions

| Entity | From | Trigger | Guard | To |
| --- | --- | --- | --- | --- |
| DATA-001 | Absent | First verified SSO session | Normalized verified email is valid and unique | Active User |
| DATA-001 | Active | Later SSO session | Same normalized email | Active User with safe profile refresh |
| DATA-001 | Active | Administrative disable | Authorized external/operator process | Disabled User; memberships retained but ineffective |
| DATA-002 | Absent | Workspace access grant | Actor scope/ceiling, User active, PMS scope valid | Active membership |
| DATA-002 | Active | Role change/revoke | Expected version and last-owner guard | Updated or absent |
| DATA-003 | Absent | Manual grant or project bootstrap | Actor/workload authority, User active, PMS scope valid | Active membership |
| DATA-003 | Active | Role change/revoke | Expected version and last-admin guard | Updated or absent |
| DATA-004 | Absent | Add restriction | Parent exists; role does not exceed parent; service valid | Explicit restriction |
| DATA-004 | Active | Change/remove | Expected version and ceiling guard | Updated or absent/inherited |

Email change to a value that does not resolve uniquely is not an automatic transition in the MVP. The request fails safely and uses the deferred account-recovery process.

## Consistency and Transactions

- First SSO provisioning is a single insert-or-resolve transaction protected by the canonical-email unique constraint. Concurrent first logins converge to one User or return a stable collision error.
- Each workspace/project/service mutation locks or version-checks the target and, where required, counts privileged rows in the same transaction.
- A parent-role demotion that would invalidate service restrictions either adjusts/removes those restrictions in the same explicitly requested transaction or returns a conflict; silent broadening is forbidden.
- API-005 uses `PUT` semantics and unique `(project_id, user_id)` state. Repeating an identical creator bootstrap returns the same canonical membership; a different creator conflicts.
- No command-receipt table is required. After an ambiguous response, a caller reads canonical state before deciding whether to retry.
- PMS/authz operations are not a distributed database transaction. PMS must use the accepted non-visible provisioning state or compensation contract.

## Retention, Deletion, and Privacy

Users are disabled rather than hard-deleted until product/legal retention and downstream actor-reference rules are approved. Memberships and service restrictions may be deleted when revoked; structured logs provide platform-level operational evidence for the configured Loki retention period but are not an immutable business audit ledger.

Database roles use least privilege, backups are encrypted and restore-tested, transport is encrypted, and non-production copies mask personal data. Password hashes are null for SSO-only Users and follow the local-credential retirement policy. Tokens, passwords, password hashes, and full OIDC payloads are excluded from logs and metrics.

## Access Patterns and Indexing

| Access pattern | Lookup | Planned support |
| --- | --- | --- |
| Resolve SSO User | Canonical normalized email | Unique canonical-email index |
| Current User scopes | `user_id` | WorkspaceUser/ProjectUser indexes by User |
| Workspace member list/check | `workspace_id`, optional cursor/user | Unique scope-user key plus pagination index |
| Project member list/check | `project_id`, optional cursor/user | Existing/expanded unique scope-user key plus pagination index |
| Service decision | `project_id + user_id + service_id` | Project membership lookup plus unique parent-service key |
| Last owner/admin guard | Scope + privileged role | Scope/role indexes used inside mutation transaction |
| Migration/parity | IDs, roles, source, scope | Deterministic inventory and reconciliation queries |

Expected volumes and query plans are **Open** until inventory. Partitioning or a second authorization store is not planned without measured need.

## Migration and Backfill

1. Inventory current `users` and `project_users`: counts, UUIDs, normalized-email collisions, null/invalid roles, duplicate project memberships, and projects without admins.
2. Resolve all collisions and invalid rows through an approved repair report before enforcing new constraints.
3. Add expand-only compatible fields/tables for normalized email, workspace membership, project version/source/workspace reference, and service restriction. No migration is claimed by this plan.
4. Preserve current User and ProjectUser UUIDs; backfill valid ProjectUser source as `manual` unless creator-bootstrap provenance is demonstrably known.
5. Put old and new reads behind compatibility adapters while one write authority remains active.
6. Run structural reconciliation and sampled decision shadow parity before reader cutover.
7. Retain rollback compatibility through the observation window; remove legacy paths only in an explicitly approved cleanup change.

Rollback before cleanup switches readers/writers back to the compatible previous path without rewriting IDs or roles. Additive rows remain available for diagnosis until a later reviewed cleanup.

## Audit and Observability

No durable authz audit entity is included in the MVP. Successful and rejected identity, decision, and access-mutation operations emit structured logs with timestamp, correlation ID, User UUID when resolved, authenticated actor/consumer, safe scope IDs, action, before/after role where applicable, result/reason, entity version, latency, and active/shadow mode.

Metrics aggregate outcomes without email or raw identity attributes. Alerts cover identity collision, invalid/duplicate bindings, last-owner/admin violations, service-role elevation attempts, authorization unavailability, parity mismatch, and bootstrap drift. If immutable compliance audit becomes required, it must be specified as a separate decision and data lifecycle rather than inferred from these logs.

## Traceability

| Data | Requirements / invariants | Scenarios / APIs | Decisions / slices |
| --- | --- | --- | --- |
| DATA-001 | REQ-001/002/008; INV-002/008 | SCN-001/005; API-001/007 | DEC-003/004; SLICE-001/002/005 |
| DATA-002 | REQ-003/004/006; INV-003/005/006 | SCN-002/003/005; API-002/006 | DEC-001/002/005; SLICE-003/004 |
| DATA-003 | REQ-003/005/006/008/009; INV-003/005/006 | SCN-002/004/005/006; API-002/003/005 | DEC-001/002/004/005; SLICE-001/003/004/005 |
| DATA-004 | REQ-003/005/006; INV-004 | SCN-002/004/005; API-002/004 | DEC-001/002/005; SLICE-003/004 |
