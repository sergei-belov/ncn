# ncn-authz Database Tables

## Applicability and Database Status

Applicable. PostgreSQL SQLAlchemy mappings for `public.users` and `public.project_users` are **Present** in the shared backend by authorized verification on 2026-08-14. No migration execution was performed and checked-in schema provisioning is not claimed. Logical owner is `ncn-authz`; physical storage is currently shared.

## Table Inventory

| ID | Schema.table | Purpose | Authoritative/derived | Lifecycle | Models |
|---|---|---|---|---|---|
| TABLE-AUTHZ-001 | `public.users` | Stable application identity and optional local password hash | Authoritative | Register/provision; update credential/name; disable/delete policy Open | MODEL-AUTHZ-001/003 |
| TABLE-AUTHZ-002 | `public.project_users` | Project-to-user membership and role | Authoritative | Creator bootstrap/add; role update; revoke/delete; cascade current mapping | MODEL-AUTHZ-002/003/004 |

## TABLE-AUTHZ-001: users

### Ownership and Purpose

`ncn-authz` is the logical sole owner. The common layer reads/writes the current shared table; consumers receive User/Actor interfaces and must not create copies. The table links external/local email identity to stable NCN actor UUID.

### Columns

| Column | Database type | Null/default | Key/constraint | Sensitivity | Meaning |
|---|---|---|---|---|---|
| `id` | UUID | Required/generated | Primary key | Internal | Stable actor |
| `email` | varchar(100) | Required | Unique and indexed Present; lowercase normalization enforced by application, stronger DB rule Planned | Personal | Identity link |
| `name` | varchar(100) | Required | API trim/length | Personal | Display name |
| `password` | varchar/text | Nullable | Hash-only application invariant | Restricted | Local credential hash |
| `created_at` | timestamp | Required/server now | Creation time | Internal | Lifecycle evidence |

### Relationships and Constraints

ProjectUser references User with current cascade delete. Email uniqueness is physical; normalization collision prevention must be verified before adding a lowercase expression constraint/index. Public serializers exclude password. A future active/provider-subject model requires an explicit schema decision.

### Access Patterns and Indexes

| Query/access pattern | Filter/order | Expected volume | Index/partition | Verification |
|---|---|---|---|---|
| Resolve identity | Exact normalized email | One row/request | Present unique email index | Query plan/load test |
| Read current user | Primary UUID/email | One row | Primary/unique | Contract test |
| Local registration | Normalized email conflict | Low | Unique email | Concurrent duplicate test |

### Transactions and Concurrency

Local registration inserts one User under unique email; concurrent duplicate returns a stable conflict. Credential update must be atomic. Identity lookup is read-only. No consumer mutation is included in the authorization transaction except current shared project bootstrap coordination.

### Lifecycle, Retention, and Privacy

Provision/register creates. Name/password update rules exist; disable/delete/provider-link retention are Open. Encrypt at rest via platform controls, mask non-production data, restrict hash access, and never log/export hashes. User deletion must consider access/audit and consumer references before cascade.

### Schema Evolution

Planned migration must inventory normalized collisions, backfill/verify lowercase values, create constraints/indexes, preserve UUIDs, and support rollback. It must not claim provider synchronization that does not exist.

### Backup, Restore, and Data Quality

Back up with shared PostgreSQL and test restore before extraction. Check non-empty normalized unique email, non-empty name, hash format where present, no public/hash leakage, and relation referential integrity.

## TABLE-AUTHZ-002: project_users

### Ownership and Purpose

`ncn-authz` owns the relation and role semantics for all services. Current physical code reads it directly through the common layer and creates creator membership in the shared project transaction. Consumers must not own an alternative membership table.

### Columns

| Column | Database type | Null/default | Key/constraint | Sensitivity | Meaning |
|---|---|---|---|---|---|
| `id` | UUID | Required/generated | Primary key | Internal | Relation identity |
| `project_id` | UUID | Required | Current FK to `pms_projects.id`, cascade, indexed | Internal | Project scope |
| `user_id` | UUID | Required | FK to `users.id`, cascade, indexed | Personal/internal | Actor scope |
| `role` | varchar(16) | Required | DTO enum Present; DB check for allowed roles Planned | Security/internal | Common policy input |

### Relationships and Constraints

Unique `(project_id,user_id)` is Present. Current deferrable FKs cascade with Project/User. Role must be exactly admin/member/viewer; until a DB check is verified, the application must deny invalid values. Independent service extraction cannot retain a cross-service physical project FK without an accepted shared-schema decision.

### Access Patterns and Indexes

| Query/access pattern | Filter/order | Expected volume | Index/partition | Verification |
|---|---|---|---|---|
| Authorize project request | project + user | One row/request | Individual indexes plus unique pair | Query plan/load test |
| List visible projects | user + workspace/project join | Project count/user | User index and project join | Pagination/load test |
| List members | project joined to User | Members/project Open | Project index | Explain/load test |
| Validate assignees | project + set of users | Up to consumer limit | Project/user indexes | Contract test |

### Transactions and Concurrency

Project bootstrap creates the creator admin relation in the same current shared transaction. Duplicate grant is rejected by the unique pair. Role update/revoke takes effect on the next canonical authorization read. Membership administration concurrency/version/audit remains Open because no management API is specified.

### Lifecycle, Retention, and Privacy

Create/grant, role change, and revoke/delete are the logical lifecycle; only creator bootstrap is currently specified. Current cascade removes relation with project/user. Retention and access-decision history are Open. Restrict member enumeration and mask non-production User links.

### Schema Evolution

Migration must create/backfill User rows before relations, map any legacy member rows, resolve orphan/duplicate/invalid roles, verify counts and role matrix, then switch readers. Keep rollback until canonical authorization comparison passes. All such work is Planned until verified.

### Backup, Restore, and Data Quality

Validate unique project/user, existing references, allowed role, creator admin relation, no orphan consumer assignments, and authorization sample parity after restore. Alert on invalid role, duplicate relation, missing creator membership, or join failures.

## Cross-Table Rules

Use stable UUIDs, normalized identity, explicit role enum, owner-only writes, transactional creator bootstrap, least disclosure, tested backup/restore, and no plaintext credentials. Authorized consumer state references User UUID without copying User/ProjectUser truth.

## Traceability

TABLE-AUTHZ-001/002 → MODEL-AUTHZ-001..004 → AUTHZ-REQ-001..010 / AUTHZ-INV-001..006 → SCN-001..003 → API-AUTHZ-001..003 → DEC-AUTHZ-001..004 → FEAT-004.
