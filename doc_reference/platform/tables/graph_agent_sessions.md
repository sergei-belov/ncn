# Graph Agent Sessions Table

## Description
The `graph_agent_sessions` table stores interactive graph builder sessions. A session is a browser/agent cursor over the command graph and points only to the current observed state.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique graph agent session identifier |
| project_graph_id | UUID | NOT NULL, FK `project_graphs.id`, INDEX | - | Owning project graph |
| current_state_id | UUID | NULLABLE, FK `graph_states.id`, INDEX | - | Current browser state cursor for the session |
| status | TEXT | NOT NULL, INDEX | `active` | Session status: `active`, `cancelled`, `failed`, or `completed` |
| mode | TEXT | NOT NULL | `agent` | Session mode: `agent`, `manual`, or `codegen_guided` |
| browser_storage_state_payload | JSONB | NULLABLE | - | Playwright browser storage state for session continuity |
| metadata | JSONB | NOT NULL | `'{}'` | Runtime metadata such as requested start state, last observation summary, or UI options |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |
| created_by_user_id | UUID | NULLABLE, FK `users.id` | - | User who created the session |

## Relationships
- **Many-to-One**: Each session belongs to one project graph through `project_graph_id`.
- **Many-to-One**: `current_state_id` points to the current browser state.
- **One-to-Many**: A session owns chat/tool messages through `graph_agent_messages.session_id`.
- **One-to-Many**: A session owns large guidance artifacts through `graph_agent_artifacts.session_id`.

## Cursor Rule
The session does not store `current_command_step_id`. It is derived from the current state:

```text
session.current_state_id
  -> graph_states.command_step_id
  -> current command step
```

When executing the next command, the new command step uses that current command step as `before_step_id`.

If command deletion removes the state referenced by `current_state_id`, the cursor must be set to `null`. A session with a cleared cursor must choose a new current state before it can continue from graph context.

## Atomic Update Rule
When moving a session after command execution, update the cursor with an optimistic guard:

```sql
UPDATE graph_agent_sessions
SET current_state_id = :new_state_id
WHERE id = :session_id
  AND current_state_id = :old_state_id;
```

If no row is updated, another worker moved the session and the result must not silently become current.
