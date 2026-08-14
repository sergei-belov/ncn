# AI Generation Messages Table

## Description
The `ai_generation_messages` table stores the full ordered trace of one generation session. It captures user-visible progress items and deeper planner/agent/validator/tool messages for audit and debugging.

The key design requirement is reliable incremental polling for the UI. Because the message log grows while the user watches it, the table uses a session-local `seq_no` cursor instead of offset-based pagination.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for the message row |
| session_id | UUID | NOT NULL, FK `ai_generation_sessions.id`, INDEX | - | Parent generation session |
| seq_no | BIGINT | NOT NULL | - | Monotonic sequence number unique inside one session |
| agent_role | VARCHAR(30) | NOT NULL | - | Origin role such as `user`, `planner`, `qai_agent`, `validator`, `tool`, `system` |
| stage | VARCHAR(30) | NOT NULL | - | Lifecycle stage such as `input`, `planning`, `execution`, `validation`, `result`, `error` |
| message_type | VARCHAR(20) | NOT NULL | - | Payload kind: `text`, `json`, `event` |
| is_visible_in_ui | BOOLEAN | NOT NULL | `false` | Whether the message belongs to the shortened UI trace |
| summary_text | TEXT | NULLABLE | - | Short human-readable summary used by the UI trace |
| content_text | TEXT | NULLABLE | - | Full text payload when applicable |
| content_json | JSONB | NULLABLE | - | Structured payload for tool events and machine-readable traces |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |

## Relationships
- **Many-to-One**: Each message belongs to one generation session through `session_id`

## Purpose
This table gives QAi a durable generation trace that serves two audiences:

1. **Product UI**
   - shortened trace only
   - incremental polling by `after_seq`
   - safe append-only rendering

2. **Engineering / audit**
   - full planner / agent / validator / tool history
   - debugging of generation quality and failures

## Notes
- Add a unique constraint on `(session_id, seq_no)`.
- Recommended indexes:
  - `(session_id, seq_no)`
  - `(session_id, is_visible_in_ui, seq_no)`
- The messages endpoint should use:
  - `after_seq`
  - `limit`
  - `view=ui|full`
- Offset-based pagination should not be used for the live trace endpoint.
