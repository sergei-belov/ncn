# ncn-pms Event Interfaces

## Applicability

**Not applicable to the current development slice.** The Present frontend uses HTTP resource APIs, and the first `ncn-agents` happy path can call PMS through a permission-checked API/MCP tool. No current asynchronous consumer or Kafka event implementation was verified.

## Event Inventory

No current events are registered.

## Deferred Event Boundary

If an actively developed consumer later needs asynchronous project changes, define producer trigger, exact consumer, minimal schema, project/aggregate ordering, event and causation IDs, transaction/outbox, at-least-once deduplication, compatibility, retention/replay, privacy, DLQ and owner reconciliation before registering the event. Event identifiers are domain lifecycle metadata and do not create synchronous HTTP tracking metadata. An event remains a PMS fact and never transfers write ownership.

## Traceability

Current project REQ-001/004 use [the PMS HTTP contract](api.md). Event work is triggered only by a confirmed current feature/consumer.
