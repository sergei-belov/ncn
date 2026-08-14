# Backend service reference

The backend is one deployable `ncn-pms` FastAPI application organized into two logical services. These boundaries describe ownership of routes, policy, domain behavior, and data; they are not separate runtime processes.

| Logical service | Short description | Platform role | Documentation |
| --- | --- | --- | --- |
| `authz` | Authentication, persistent identity, memberships, service restrictions, and named authorization decisions. | Establishes who the actor is and what workspace, project, or service scope the actor may use. | [Overview](services/authz/README.md) · [API](services/authz/api.md) · [Flows](services/authz/flows.md) |
| `pms` | Projects, agents, workflow states, work items, epics, boards, and preferences. | Owns project-management behavior and applies authz-derived project capabilities to every domain operation. | [Overview](services/pms/README.md) · [API](services/pms/api.md) · [Flows](services/pms/flows.md) |

## Shared references

| Reference | Role |
| --- | --- |
| [Runtime and architecture](runtime.md) | Shared stack, layers, registered runtime services, cross-cutting behavior, and operational gaps. |
| [API conventions](api.md) | Common authentication, types, envelopes, errors, concurrency rules, and operational endpoints. |
| [Cross-service flows](flows.md) | Shared request, transaction, failure, and observability sequences. |
| [Database](../database/README.md) | Table-level schema reference used by both logical services. |
