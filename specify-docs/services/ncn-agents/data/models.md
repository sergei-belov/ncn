# ncn-agents Models

## Applicability and Ownership

Applicable. MODEL-AGT-001 and current mutable config are **Present**; snapshot and execution models are **Planned design**. Agents owns execution semantics/constraints, memory metadata/derived index control and records. Persisted actor/project-role authorization is an external `ncn-authz` reference; PMS business entities, external tool-provider state and object bytes also remain external.

## Model Inventory

| ID | Model | Kind | Owner | Purpose | Interfaces | Persistence |
|---|---|---|---|---|---|---|
| MODEL-AGT-001 | AgentConfiguration | Domain/DTO | Agents | Mutable coordinator/worker definition/status | API-AGT-001/002 | TABLE-AGT-001 transitional; TABLE-AGT-002 Planned |
| MODEL-AGT-002 | AgentConfigSnapshot | Immutable domain/snapshot | Agents | Effective Run configuration | API-AGT-003 | TABLE-AGT-004 Planned |
| MODEL-AGT-003 | Session/Message | Domain/DTO | Agents | Ordered conversation/system context | API-AGT-003 | TABLE-AGT-003 Planned |
| MODEL-AGT-004 | Run | Domain/DTO | Agents | Durable attempt/state/result linkage | API-AGT-003/004 | TABLE-AGT-005 Planned |
| MODEL-AGT-005 | RunPlan/Revision/Node | Domain/command | Agents | Validated execution graph and revisions | API-AGT-004 | TABLE-AGT-006 Planned |
| MODEL-AGT-006 | AgentInvocation | Domain/result | Agents | Coordinator/worker call evidence | API-AGT-004 | TABLE-AGT-007 Planned |
| MODEL-AGT-007 | ToolExecution | Domain/result | Agents | Tool attempt/effect/reconciliation | API-AGT-004/006 | TABLE-AGT-008 Planned |
| MODEL-AGT-008 | Approval | Domain/command | Agents execution and permission policy | Durable human decision | API-AGT-005 | TABLE-AGT-009 Planned |
| MODEL-AGT-009 | UsageRecord/ArtifactMetadata | Domain/reference | Agents | Cost/resource and run-produced artifacts | API-AGT-006 | TABLE-AGT-010/011 Planned |
| MODEL-AGT-010 | RunEvent/ResultEnvelope/AuditReference | Internal event/read | Agents | Progress, terminal semantics, reconstructability | API-AGT-004/006 | TABLE-AGT-012 plus audit store Planned |

## MODEL-AGT-001/002: Agent Configuration and Snapshot

### Semantics

Mutable project-scoped config defines coordinator/worker intent; snapshot is immutable effective configuration bound to one Run and includes instructions, model/parameters, tool versions/allowlist, permission/approval policy reference, memory configuration and project constraints.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| IDs/project/kind | UUID/enum | Required | Stable scope; coordinator/worker | Internal | Identity/topology |
| name/description/instructions | strings | Required | Current limits 80/240/4000; trimmed | Instructions restricted | Human/model behavior |
| model/memory/max steps/approval | IDs/enums/int | Required | Allowed registry/policies; positive limit | Restricted | Runtime selection/limits |
| tool names/version refs | list/references | Default empty | Allowed/discovered schema | Restricted | Capability |
| status/version/timestamps | enum/int/time | Active default/version positive | Coordinator active; live name unique | Internal | Lifecycle/concurrency |
| snapshot payload/hash/schema | structured/hash/version | Snapshot required/immutable | Complete effective config and provenance | Restricted | Reproducibility |

### Identity and Relationships

One active coordinator/project; many workers; each Run references one coordinator snapshot and any invoked worker snapshots/config versions. Project is external PMS reference.

### State and Invariants

Workers active/disabled/archived; coordinator always active. Snapshot never changes and Run cannot resolve mutable config after start for semantic behavior.

### Serialization and Versioning

Config API is `snake_case`; snapshot has explicit schema version/hash and normalized enums. Secret plaintext is never serialized; only secret-version references.

### Mappings

Present API/table map MODEL-AGT-001. Planned TABLE-AGT-002/004 separate mutable versions/snapshots. API-AGT-003 creates snapshot transactionally.

## MODEL-AGT-003/004: Session, Message, and Run

### Semantics

Session is ordered user/system context; Message is an immutable content entry with visibility; Run is one durable attempt with snapshot, state, plan, execution records, usage and terminal result.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| session/run/message IDs + project | UUID | Required | Stable/replay-safe; same project | Restricted | Identity/scope |
| initiator/participants/kind | persisted User UUID/service refs/enums | Required | API-AUTHZ-003 actor or scoped service | Personal/internal | Origin/visibility |
| message order/content parts/mentions | int/structured | Required | Monotonic; size/type limits Open | Confidential | Conversation input/output |
| Run status/wait reason/version/times | enums/int/time | Required | One terminal transition | Internal | Lifecycle |
| snapshot/plan/result/usage refs | UUIDs | Required as lifecycle advances | Same Run/project | Restricted | Execution evidence |
| client command/workflow/causation IDs | UUID/strings | Required where applicable | Scoped unique/stable on replay | Internal | Duplicate safety, workflow identity and async diagnosis |

### Identity and Relationships

Session has Messages and Runs; one active mutating Run. Run has one root Temporal workflow and many revisions/nodes/invocations/tools/approvals/events/usage/artifacts.

### State and Invariants

Session can close. Run distinguishes queued/active/waiting/cancelling/terminal. Terminal states are COMPLETED/PARTIALLY_COMPLETED/FAILED/CANCELLED and apply once.

### Serialization and Versioning

Content parts/result/events have explicit schema versions and role-based redaction; no private reasoning. Event cursor is Run-local and stable.

### Mappings

API-AGT-003/004; TABLE-AGT-003/005/012.

## MODEL-AGT-005: RunPlan, Revision, and Node

### Semantics

Immutable revision of a validated bounded plan. Node kinds: coordinator decision, worker invocation, tool call, approval boundary, finalization. Data mapping uses allowed scopes and RFC 6901 JSON Pointer without expression runtime/coercion.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| run/revision/node identity | UUID/int/stable key | Required | Unique; stable across replay | Internal | Plan lineage |
| kind/dependencies/join | enum/list/enum | Required | DAG; bounded; join only `all` in MVP | Internal | Execution order |
| input/output schema/mapping | JSON Schema/pointers | Required by kind | Valid scopes/types | Restricted | Deterministic data flow |
| status/attempts/limits | enums/ints | Required | Guarded transitions/hard caps | Internal | Execution |
| tool/agent/approval refs | versioned refs | By kind | Snapshot/allowlist/policy compatible | Restricted | Capability |

### Identity and Relationships

Run has ordered immutable revisions; revision contains nodes. A superseding revision retains lineage and may replace only unstarted portion.

### State and Invariants

Completed/running nodes, arguments, effects and decisions cannot change. Side effects exist only as tool nodes. Cycles/nested workers/limit violations are rejected.

### Serialization and Versioning

Plan schema version is snapshot-bound. Workflow code must interpret historical versions through compatible handlers.

### Mappings

TABLE-AGT-006; MODEL-AGT-006/007/008; Run result/audit.

## MODEL-AGT-006/007/008: Invocation, Tool Execution, and Approval

### Semantics

Invocation records bounded model/agent work. ToolExecution records exact versioned tool request, common actor/action decision, execution policy, Approval, client command identity and effect/outcome. Approval records one human decision for an immutable material payload.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| run/node/attempt IDs | UUID/int | Required | Unique logical attempt | Internal | Traceability |
| agent/model/tool/schema versions | references | Required | Snapshot/discovery match | Restricted | Executed capability |
| structured input/output/result class | validated JSON | Required | JSON Schema; repair <=2 | Confidential | Machine result |
| authz decision/approval refs + payload hash | references/hash | Tool dependent | Current actor/action and material args exact | Security restricted | Authority |
| duplicate-safety class/client command ID/outcome/external ref | enums/UUID/string | Mutation dependent | Scoped stable command ID; unknown explicit | Restricted | Side-effect safety |
| decision/approver/expiry/version | enum/ref/time/int | Approval dependent | One eligible atomic decision | Personal/security | Human control |

### Identity and Relationships

Each record belongs to Run/node/project. PMS or a future tool provider is an external reference, not agent-owned business state. Approval points to the exact ToolExecution/node payload version.

### State and Invariants

Invocations terminate success/partial/blocked/failure. Tool may be planned/waiting/running/succeeded/failed/outcome_unknown/reconciled. Approval pending → approved/rejected/expired/invalidated once; changed args require a new approval.

### Serialization and Versioning

User views receive safe summaries; audit access is role-limited; credentials/raw private reasoning excluded. Schema/version references remain historical.

### Mappings

API-AGT-004..006; TABLE-AGT-007..009.

## MODEL-AGT-009/010: Usage, Artifacts, Events, and Result

### Semantics

Usage records provider-neutral tokens/cost/latency with price version. Artifact metadata links project/Run/object/source/derivatives. RunEvent is ordered user-safe progress; ResultEnvelope is immutable terminal summary; audit reference points to security/operational evidence.

### Fields

| Field | Type | Required/null/default | Validation/constraints | Sensitivity | Meaning |
|---|---|---|---|---|---|
| usage dimensions/value/price/version | enums/numbers/ref | Required | Non-negative; immutable | Commercial/internal | Budget/accounting |
| artifact ID/object key/MIME/size/checksum/state | mixed | Required | Size/MIME/checksum; project owner | Confidential | Binary metadata |
| event sequence/type/summary/time | int/enum/structured/time | Required | Monotonic/user-safe | Internal/restricted | Progress |
| result status/text/completed/failed/effects/unresolved/sources/usage | structured | Required terminal | Consistent with Run/executions | Confidential | User outcome |

### Identity and Relationships

Usage and artifacts link Run/node/invocation/tool. Object bytes are MinIO/S3; memory derivatives link source/version. Result links all terminal evidence without duplicating owner business state.

### State and Invariants

Budget is checked before/after chargeable work. Artifact lifecycle is explicit. Terminal result is written once and discloses all effects/unresolved items.

### Serialization and Versioning

Versioned envelopes; redact restricted content per caller. Results cite source/artifact IDs, not unsigned permanent object URLs.

### Mappings

API-AGT-004/006; TABLE-AGT-010..012 and object storage.

## Traceability

MODEL-AGT-001..010 → AGT-REQ-001..006 → SCN-001..003 → API-AGT → TABLE-AGT-001..012 → FEAT-002/003 acceptance.
