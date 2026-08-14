# Backend API conventions

Base path: `/api/v1`

This document defines conventions shared by the `authz` and `pms` APIs. Service documents own the route inventories and domain-specific contracts.

## Service API references

| Logical service | Route families | Reference |
| --- | --- | --- |
| `authz` | `/auth`, `/authorization`, workspace/project memberships, service restrictions, creator access | [Authz API](services/authz/api.md) |
| `pms` | `/workspaces/{workspace_slug}/projects` and nested agents, states, work items, board, preferences, and epics | [PMS API](services/pms/api.md) |

## Authentication

Domain and authorization routes require an OAuth2 bearer token. The backend resolves the token email to an active `users` row and applies a process-local per-user rate limit. Local registration and password login are usable only when `AUTH_FLOW=local`; otherwise those routes return `AUTH_ROUTE_DISABLED`.

## Naming and types

JSON uses `snake_case`. `UUID` values are strings in JSON, dates use `YYYY-MM-DD`, and datetimes are timezone-aware ISO 8601 values.

In these API documents:

- `field?: Type` means the field may be omitted;
- `field: null | Type` means explicit `null` is valid;
- `enum(a, b)` lists accepted string values.

Public models reject undeclared JSON fields. Routes with no query model also reject unknown query parameters.

## Success envelopes

Most PMS resources return:

```json
{
  "data": {},
  "meta": null
}
```

Cursor pages use `meta.next_cursor`, `meta.has_more`, and `meta.total_count`. Authz membership endpoints are an exception: individual memberships are returned directly, while lists use `{ "items": [...], "next_cursor": null }`.

## Errors and correlation

Every response includes `X-Correlation-ID`. A valid inbound `X-Correlation-ID` of 1–128 characters from `[A-Za-z0-9._:-]` is reused; otherwise the backend generates a UUID.

Errors use:

```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "The resource changed since it was read.",
    "correlation_id": "uuid",
    "field_errors": null,
    "details": null,
    "current": null
  }
}
```

Malformed query input returns `400 MALFORMED_REQUEST`. Other request-model failures return `422 VALIDATION_ERROR`. Domain conflicts usually return 409 and may include canonical `current` state.

## Concurrency and idempotency

The backend reads optimistic versions from JSON fields where shown in the service API references. It does not currently consume `If-Match` or `Idempotency-Key` headers.

Projects, states, work items, and epics require a client-generated UUID on create. Repeating a scoped create with that UUID can return the existing resource. State reorder and work-item move compare `board_version`; membership, service restriction, and agent commands compare an entity `expected_version`.

## Operational endpoints

| Path | Owner | Behavior |
| --- | --- | --- |
| `/healthcheck` | Shared service hub | Pings registered external services |
| `/metrics` | Prometheus instrumentator | Exposes request and custom authorization metrics |
| `/docs` | FastAPI | Swagger UI |
| `/openapi.json` | FastAPI | Generated OpenAPI schema |

## Related documentation

- [Backend service index](README.md)
- [Runtime and architecture](runtime.md)
- [Cross-service flows](flows.md)
- [Database](../database/README.md)
- [HTTP integration status](../architecture.md#http-integration-status)
