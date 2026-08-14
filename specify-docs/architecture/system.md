# NCN Current System Architecture

## Context

The current development system is a Vue SPA plus a FastAPI/PostgreSQL backend that exposes common authentication/authorization, PMS, and agent-configuration resources. The living logical boundary contains three services: `ncn-authz` owns common User/ProjectUser actor and role policy; `ncn-pms` owns project work; `ncn-agents` owns agent configuration and the in-development durable agent runtime. The current code is physically shared, so service names express ownership and evolution boundaries, not verified independent deployments.

Users act through the browser. Agents act on project data only through permission-checked PMS APIs/MCP tools. Future GitLab, procurement, analytics and other integrations are deferred external capabilities; they are not current services in this specification.

## Service Boundaries

| Service | Responsibility | Owns | Exposes | Depends on | Status |
|---|---|---|---|---|---|
| `ncn-authz` | Common identity-to-actor and project authorization | User, ProjectUser, normalized identity resolution, role-to-service-action policy, access identity | Present current-user/local-auth HTTP and common dependency; independent policy API Open | OIDC-verifying edge/local auth, PostgreSQL, PMS project reference | Common layer Present; independent deployment Open |
| `ncn-pms` | Projects and daily project work | Projects, stages, board/preferences, work items, epics and ordering | Present `/api/v1/workspaces/{workspace_slug}/projects...`; future PMS tool/events as needed | `ncn-authz`, PostgreSQL, frontend | Present core slice |
| `ncn-agents` | Agent configuration and coordinated execution | Coordinator/workers, snapshots, Sessions, Messages, Runs, plans, invocations, tools, approvals, usage, run artifacts metadata | Present agent config API; Planned Session/Run/control API | `ncn-authz`, PMS project/tool API, PostgreSQL, Temporal/model/Qdrant/object storage for execution | Configuration Present; execution in development |

## Cross-Service Flows

| Flow | Trigger | Ordered participants | State/authority changes | Failure/recovery | Observability |
|---|---|---|---|---|---|
| Common actor resolution | Protected action | Edge/local auth → `ncn-authz` → consumer | Resolve User; for project scope resolve ProjectUser role/action | Reauthenticate/provision on identity failure; access change on denial | Persisted user UUID, scope, role/action/decision |
| Browser PMS operation | User action | Vue → authz actor → PMS API | Authz role decision; PMS business validation/owner transaction | Stable validation/deny/conflict; UI rollback/refetch | User UUID, operation/resource/version/error |
| Agent configuration | Admin action | Vue → authz actor → agent API → PMS project reference validation | Authz role decision; Agents configuration transaction/version | Protected coordinator, stale rollback/refetch | User UUID, config version/status/audit |
| Coordinated Run | User Message | Vue → agents/Temporal → model/memory/tool → PMS API when needed | Agents stores snapshot/Run; PMS alone commits project effect | Durable retry/wait/cancel; idempotency; reconciliation | Session/Run/node/tool/correlation/usage/audit |

## Data and Consistency Boundaries

Authz PostgreSQL `users`/`project_users` are authoritative for persisted actor and project role. PMS rows are authoritative for project work. Agent PostgreSQL rows are authoritative for configuration/execution product state; Temporal will retain workflow progress, Qdrant only derived vectors, and MinIO/S3 artifact bytes. The current `pms_agents` table is physically coupled to PMS but logically belongs to `ncn-agents`; extraction is Open. Frontend query cache and browser mock data are derived/demo state.

There is no distributed database transaction. Current shared project bootstrap can atomically create project and creator ProjectUser; independent extraction must replace that coupling with an accepted consistency protocol. Agent-to-PMS mutation uses the owner API/MCP command with current authz decision, scope, JSON expected version and duplicate-safety classification. The agent Run records the attempted/actual effect but never becomes the PMS or authz source of truth.

## Shared Infrastructure and Integrations

### Technology Stack

#### Approved Shared Infrastructure

**Confirmed:** the following table is the approved NCN platform baseline. It assigns one shared technology to each infrastructure concern; introducing a competing component requires an explicit architecture decision. Selection in this baseline does not by itself prove that a component is deployed or used by the current shared-runtime development slice.

| Concern | Technology | Platform role |
|---|---|---|
| Ingress | Traefik | Reverse proxy, TLS termination, and routing for UI, APIs, and webhooks |
| Browser authentication | oauth2-proxy | Central OIDC/OAuth2 and SSO edge flow |
| Transactional storage | PostgreSQL | System metadata, domain tables, outbox, and event-backed projections |
| Cache and coordination | Redis | Cache, short-lived locks, rate limits, and ephemeral runtime state |
| Event bus | Kafka | Durable domain events, telemetry, fan-out, reindex events, and data streams |
| Workflow engine | Temporal | Stateful workflows, retries, deadlines, dependencies, approvals, and cancellation |
| Local model serving | Ollama | Self-hosted LLM and embedding inference |
| Vector search | Qdrant | The single vector store for RAG, semantic search, and memory recall |
| Object storage | MinIO/S3 | Documents, attachments, binary artifacts, and signed links |
| Notifications | Novu | Channel orchestration, templates, and delivery policies |
| Metrics | Prometheus | Platform, service, and SLO metrics |
| Logs | Loki | Centralized searchable runtime logs |
| Dashboards | Grafana | Dashboards, alerting, and metrics/log correlation |

Shared infrastructure remains domain-neutral. Its use does not create a current service contract or transfer authoritative business data away from its owning service. PostgreSQL remains the transactional source of truth; Redis caches, Qdrant indexes, dashboards, and other projections are rebuildable. Temporal holds the state of a particular workflow or agent Run, while Kafka carries durable events and streams shared across workflows or services.

#### Current Development Adoption

| Concern | Current development contract | Status |
|---|---|---|
| Browser/UI | Vue 3, TypeScript, Vite, TanStack Vue Query | Present |
| HTTP backend | FastAPI layered routers/managers/repositories | Present |
| Common authorization | Shared User/ProjectUser repositories, actor dependencies and role policy | Present; independent deployment Open |
| Edge routing and browser authentication | Traefik and oauth2-proxy from the approved baseline | Unknown; deployment not verified |
| Transactional state | PostgreSQL | Present mappings; runtime deployment not reverified |
| Cache and coordination | Redis from the approved baseline | Unknown; no current use was verified |
| Agent workflow | Temporal, one root workflow per Run | Planned/in development |
| Models/embeddings | Provider-neutral adapter with local Ollama | Planned/in development |
| Memory | Project-scoped RAG metadata plus rebuildable Qdrant index inside agent capability | Planned/in development |
| Artifacts | PostgreSQL metadata plus MinIO/S3 bytes | Planned/in development |
| Tools | Internal PMS API/MCP first; external MCP integrations deferred | Planned/in development |
| Event distribution | Kafka is the approved event bus, but requires a confirmed current asynchronous consumer | Deferred for the first Run happy path |
| Notifications | Novu from the approved baseline | Unknown; no current notification flow is specified |
| Observability platform | Prometheus, Loki, and Grafana from the approved baseline | Unknown; deployment and production thresholds are not verified |

#### Baseline Exclusions

**Confirmed:** the baseline does not include a separate tracing stack, CI/CD service, Git service, Vault-class secrets manager, Matrix/Synapse, or a dedicated SMTP relay. Adding one requires a documented need and an explicit architecture decision. Exclusion of a dedicated component does not remove the related security, delivery, operability, or correlation requirements elsewhere in this specification.

## Security and Trust Boundaries

The OIDC edge verifies external identity or local auth verifies its own token. `ncn-authz` resolves the persisted User and current ProjectUser role/action; every consumer requires that common actor and applies its own domain/project-state checks. Authentication claims/configuration never grant application permissions. In agent execution, permission is deterministic backend policy and Approval is a separate human gate for a permitted risky action. Model input/output and tool responses are untrusted and schema validated. Credentials are referenced by encrypted immutable versions and never exposed to APIs, model context, logs or Qdrant. Rich text/files are untrusted content.

## Failure Isolation and Recovery

Authz failures deny before consumer work; invalid roles/data block readiness rather than default access. PMS transactions use validation, JSON expected versions where defined, and client-generated resource/command identities. UI optimistic changes roll back/refetch. Agent Run uses deterministic Temporal workflow and I/O Activities; retry varies by operation class; unsafe unknown outcome is not blindly repeated. Durable waits handle approval/input/cancel. PostgreSQL and object storage require backup/restore; Qdrant/cache is rebuildable.

## Observability and Operations

Synchronous logs and access evidence use the persisted User UUID, scope, role/action, operation/resource/version, and safe outcome. Agent execution propagates its domain Session/Run/node/tool/event and causation IDs through durable workflows and owner calls. Measure API latency/error/conflict, auth failures/denials/rate limits, Run states/age, workflow/activity retry, model/tool latency, approvals, cancellation, tokens/cost and reconciliation. Logs/audit omit secrets, bearer/password data, unrestricted prompts/private reasoning and file contents. Production thresholds/RPO/RTO are Open.

## Runtime and Deployment Shape

Present verification found one Vue app and one FastAPI codebase containing authz, PMS, and agent-configuration domains. The agent design adds an API component and Temporal worker, potentially in the same initial deployment with modular boundaries. Independent service deployment is not claimed. Extraction must preserve `/api/v1`, persisted User UUIDs, ProjectUser roles, JSON domain/version fields, project scope and frontend behavior.

## Architecture Decisions

Use [project decisions](../decisions/README.md) and the two service decision files. Add a future service only when development starts and its evidence/owner contract is accepted.
