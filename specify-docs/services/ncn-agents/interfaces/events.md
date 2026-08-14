# ncn-agents Event Interfaces

## Applicability

**Not applicable to the current development slice as a cross-service Kafka contract.** Run progress, approval, tool effects and audit must first persist in `ncn-agents` and be available through the Run API. No current asynchronous consumer or Kafka producer was verified.

## Event Inventory

No current Kafka events are registered.

## Internal Run Event Contract

`RunEvent` is an agent-owned persisted/read model, not necessarily a Kafka event. It uses a stable Run-local sequence, event type, safe summary, timestamp, persisted actor UUID where applicable, and Run/node/tool IDs. It excludes private reasoning, secrets and unrestricted prompts/tool payloads. The frontend reconnects with a cursor and then reads canonical Run state.

## Deferred Event Boundary

If an actively developed notification, analytics or automation consumer later requires Kafka, define an exact current feature and consumer before registering topics. The contract must cover outbox trigger, minimal payload, Run ordering, event and causation IDs, at-least-once deduplication, compatibility, retention/replay, privacy, DLQ and API reconciliation.

## Traceability

Current AGT-REQ-003/006 and SCN-002 use [the Run API](api.md) and MODEL-AGT-010. Kafka remains deferred.
