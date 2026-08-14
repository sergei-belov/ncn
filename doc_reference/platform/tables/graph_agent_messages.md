# Graph Agent Messages Table

## Description
The `graph_agent_messages` table stores ordered chat-like messages for a graph builder agent session. It captures user instructions, assistant responses, system messages, and tool events.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for the graph agent message |
| session_id | UUID | NOT NULL, FK `graph_agent_sessions.id`, INDEX | - | Parent graph agent session |
| seq | INTEGER | NOT NULL | - | Monotonic sequence number unique inside one session |
| role | TEXT | NOT NULL | - | Message role: `user`, `assistant`, `system`, or `tool` |
| content | TEXT | NOT NULL | - | Message text or compact tool event description |
| metadata | JSONB | NOT NULL | `'{}'` | Structured message metadata |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |

## Relationships
- **Many-to-One**: Each message belongs to one graph agent session through `session_id`

## Purpose
This table supports the Graph page agent panel and preserves a durable interaction log for graph-building activity. The `seq` cursor supports reliable incremental polling while the session is active.

## Notes
- Recommended uniqueness rule: `(session_id, seq)`.
- Agent messages are graph-building records, not AI-generation preview records.
