# Cross-service backend flows

## Service flow references

| Logical service | Covered flows | Reference |
| --- | --- | --- |
| `authz` | Session gate, workspace/project membership, service restrictions, and named decisions | [Authz flows](services/authz/flows.md) |
| `pms` | Project creation, board reads, cards, states, epics, agents, and archive behavior | [PMS flows](services/pms/flows.md) |

## Shared request lifecycle

1. Correlation middleware accepts a bounded inbound ID or creates a UUID.
2. The authz bearer dependency decodes token claims and normalizes the email.
3. `get_user` loads the persistent user or provisions one with its email as the initial name, rejects disabled users, and applies the process-local rate limit.
4. Nested PMS project routes additionally load the routed project and matching `project_users` record. Project list/create only derive the workspace scope from the route and do not read `workspace_users`.
5. The router validates query/body data and delegates to the owning service manager.
6. The manager revalidates scope, role capability, archive state, versions, and references.
7. Repositories operate in one async database session/transaction.
8. The session commits on clean exit or rolls back on exception.

Project membership is intentionally checked both in the dependency boundary and PMS manager layer. Authz management endpoints use the current-user dependency and apply their own workspace/project administration guards.

## Failure and observability flow

- Pydantic query errors become 400 when malformed query input is detected; other validation failures become 422.
- `PmsError` preserves domain status, code, details, field errors, and current conflict state for both logical services.
- Unauthorized requests receive `WWW-Authenticate: Bearer` on 401.
- Successful PMS operations emit structured `ncn_pms.events` log lines.
- Authz operations emit `ncn_authz.events` records and Prometheus counters.
- Unexpected failures return a generic 500 without leaking exception content.

These records are process logs/metrics only; there is no durable audit table or event outbox.

## Related documentation

- [Backend service index](README.md)
- [Runtime and architecture](runtime.md)
- [API conventions](api.md)
- [Database](../database/README.md)
- [Frontend](../frontend/README.md)
