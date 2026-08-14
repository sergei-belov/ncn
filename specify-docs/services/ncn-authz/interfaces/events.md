# ncn-authz Event Interfaces

## Applicability

**Not applicable to the current common-layer feature.** No authorization event producer, consumer, topic, outbox, or asynchronous access-decision flow is Present or required for synchronous authorization. All current decisions read canonical PostgreSQL state before consumer work. Consequence: no `EVT-AUTHZ-*` identifiers are registered.

## Event Inventory

No current events are registered.

## Deferred Event Boundary

An independently deployed service or access-audit consumer may later require identity/membership/policy change events. Before registration, define the exact producer/consumer, authoritative transaction and outbox, minimal non-sensitive payload, event/causation IDs, project/user key, ordering, at-least-once deduplication, schema version, retention/replay, privacy, failure repair, and canonical-state reconciliation. Events may invalidate derived caches but never replace a current authorization read unless a separate consistency decision is accepted.

## Traceability

FEAT-004 and AUTHZ-REQ-001..010 use [the synchronous/common interface](api.md). Event work begins only with an accepted current consumer and architecture decision.
