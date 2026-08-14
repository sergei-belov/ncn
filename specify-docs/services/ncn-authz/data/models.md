# ncn-authz Models

## Applicability and Ownership

Applicable. User, ProjectUser, persisted-user DTOs, joined authorization projection, and actor DTO are **Present** in the shared backend by authorized verification on 2026-08-14. `ncn-authz` owns their logical meaning for all services. Provider account/token models and consumer-domain entities remain external.

## Model Inventory

| ID | Model | Kind | Owner | Purpose | Interfaces | Persistence |
|---|---|---|---|---|---|---|
| MODEL-AUTHZ-001 | User | Domain/DTO | `ncn-authz` | Persisted application identity and optional local credential hash | API-AUTHZ-001/002/003 | TABLE-AUTHZ-001 |
| MODEL-AUTHZ-002 | ProjectUser | Domain/DTO | `ncn-authz` | One user's role in one project | API-AUTHZ-003 | TABLE-AUTHZ-002 |
| MODEL-AUTHZ-003 | UserAccess/AuthorizedUser | Joined read DTO | `ncn-authz` | Resolve identity plus project relation/scope/role | API-AUTHZ-003 | Derived from TABLE-AUTHZ-001/002 plus external Project |
| MODEL-AUTHZ-004 | Actor/PermissionSet | Transient policy/read model | `ncn-authz` | Carry persisted actor and role-derived service actions to consumers | API-AUTHZ-003 | Not persisted |

## MODEL-AUTHZ-001: User

### Semantics

Authoritative NCN application identity. It links a normalized email to a stable UUID and display name. Local users may have a password hash; provider-only users may not. Authentication-provider account lifecycle is external.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| `id` | UUID | Required/generated | Primary/stable | Internal | Actor identity used by all services |
| `email` | string | Required | Normalize trim/lowercase; max 100; unique | Personal | Authentication-to-application link |
| `name` | string | Required | Trim; 1–100 | Personal | Display identity |
| `password` | string | Nullable/default null | Bcrypt hash only; never public | Restricted | Local credential verifier |
| `created_at` | UTC datetime | Required/server default | Immutable creation time | Internal | Lifecycle/audit |

### Identity and Relationships

One User has zero or more ProjectUser relations. Consumer resources reference `user.id` for actor/creator/assignee/audit meaning but do not copy User authority. Email identifies the current provider/local link and must be collision-free after normalization.

### State and Invariants

Current model has no explicit active/disabled state; external disable/reconciliation behavior is Open. Password may transition null → hash or hash → new hash only under an authorized credential flow. Public variants always omit password.

### Serialization and Versioning

Wire uses `snake_case`, UUID, UTC ISO 8601. Public User is `id,email,name,created_at`; internal DTO may carry password hash. Additive public fields require privacy review.

### Mappings

API-AUTHZ-001/002 use public/internal variants. API-AUTHZ-003 resolves the internal DTO then emits MODEL-AUTHZ-004.

## MODEL-AUTHZ-002: ProjectUser

### Semantics

Authoritative current membership and role for one User in one external PMS Project. It is the only project-role input to common authorization.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| `id` | UUID | Required/generated | Primary/stable | Internal | Relation identity |
| `project_id` | UUID | Required | External Project reference; indexed | Internal | Authorization scope |
| `user_id` | UUID | Required | User reference; indexed | Personal/internal | Authorized actor |
| `role` | enum | Required | `admin|member|viewer` | Security/internal | Common policy input |

### Identity and Relationships

Exactly zero or one ProjectUser exists for a project/user pair. Many relations may reference a User or Project. Display name/avatar/active flags are derived from User or future identity status, not duplicated authority in this relation.

### State and Invariants

Create grants the stored role; update changes effective actions on the next request; delete revokes project access on the next request. Project creator receives admin atomically with project bootstrap. Other administration is Open.

### Serialization and Versioning

Role values are stable compatibility semantics. Clients may receive role and derived permissions but may not submit them as authority outside a future authorized membership-management contract.

### Mappings

API-AUTHZ-003 and MODEL-AUTHZ-003/004; TABLE-AUTHZ-002. PMS project list/member summaries consume projections only.

## MODEL-AUTHZ-003/004: Authorized User, Actor, and Permission Set

### Semantics

UserAccess is an internal nullable join projection used to distinguish missing User from missing membership. AuthorizedUser is its non-null project variant. Actor carries persisted User UUID, workspace, display name, and optional avatar to consumer managers. PermissionSet is a role/service/action projection, not stored authority.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| User fields | MODEL-AUTHZ-001 | Required | Persisted source | Personal/internal | Actor identity |
| `project_user_id` | UUID | Nullable in access; required authorized | Exact relation | Internal | Membership proof |
| `project_id` | UUID | Nullable/required | Exact path project | Internal | Scope |
| `workspace_slug` | string | Nullable/required | Exact path/project workspace | Internal | Tenant path scope |
| `project_role` | enum | Nullable/required | Valid stored role | Security/internal | Policy input |
| actor display fields | UUID/string/optional URL | Required/optional | No password/email needed by manager actor | Personal/internal | Consumer context |
| permission flags | booleans by service action | Derived | Common matrix only | Internal | UI/manager projection |

### Identity and Relationships

Transient models point to authoritative User/ProjectUser and external Project. They are request-scoped and never persisted or accepted from clients as permission proof.

### State and Invariants

AuthorizedUser cannot exist with null relation/project/workspace/role. Actor UUID always equals User UUID. PermissionSet is recalculated from current role on each authorization.

### Serialization and Versioning

Internal DTOs use `snake_case`. Consumer-facing permission fields are additive only when a named service action is accepted; removing/changing meaning requires compatibility handling.

### Mappings

API-AUTHZ-003 feeds consumer managers and response permission projections. No table maps directly to MODEL-AUTHZ-004.

## Traceability

MODEL-AUTHZ-001..004 → AUTHZ-REQ-001..010 → SCN-001..003 → API-AUTHZ-001..003 → TABLE-AUTHZ-001/002 → DEC-AUTHZ-001/004 → FEAT-004.
