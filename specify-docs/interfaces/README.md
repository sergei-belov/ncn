# Current Interface Map

## Shared Conventions

- Present HTTP APIs use `/api/v1`, JSON `snake_case`, UUID identifiers, UTC timestamps and workspace/project scope.
- Protected requests receive the persisted actor and role/action decision from `ncn-authz`; consumers recheck domain and archive state.
- Successful resources use `data` and optional `meta`; errors use stable code/message and optional field errors, with no synchronous tracking value.
- Synchronous APIs use standard bearer identity and path/query/JSON fields only. Expected entity/board versions and client-generated domain/command IDs in JSON provide concurrency and duplicate safety where defined.
- Authorized HTTP logs/rate tracking use persisted `user.id`. Async agent flows use Session/Run/node/tool/event and causation IDs defined by their domain contracts.
- Cursor/size bounds prevent unbounded lists. Additive changes are compatible; breaking semantics require a new version and overlap.
- No current service uses another service's table as a supported interface.

## Interaction Inventory

| Producer/owner | Consumer | Kind | Purpose | Contract | Compatibility | Failure/recovery |
|---|---|---|---|---|---|---|
| `ncn-authz` | All backend services/frontend current-user flow | HTTP/common dependency | Resolve persisted actor and project role/action | [Authz interface](../services/ncn-authz/interfaces/api.md) | Present shared layer; extraction must preserve actor/errors | Reauthenticate/provision on identity failure; authorized data change on denial |
| `ncn-pms` | Vue frontend | HTTP resource API | Project/board/stage/work-item/epic operations | [PMS API](../services/ncn-pms/interfaces/api.md) | Present `/api/v1` | Validation/deny/conflict; optimistic rollback/refetch |
| `ncn-agents` | Vue frontend | HTTP resource API | Agent configuration/status | [Agents API](../services/ncn-agents/interfaces/api.md) | Present `/api/v1` | Validation/deny/protected/stale; cache rollback/refetch |
| `ncn-agents` | Vue frontend | Planned HTTP/progress interface | Session/Message/Run/Approval/control | [Agents API](../services/ncn-agents/interfaces/api.md) | Versioned design | Durable state, reconnect/read, cancellation/recovery |
| `ncn-pms` | `ncn-agents` | Planned owner API/MCP tool | Read/mutate project work during Run | [PMS API](../services/ncn-pms/interfaces/api.md) | Must preserve authz and owner semantics | Reauthorize; classify duplicate safety; reconcile unknown outcome |

Kafka event interfaces are not a current project-level dependency. Service event files explicitly state current applicability and defer cross-service topics until a confirmed consumer exists.
