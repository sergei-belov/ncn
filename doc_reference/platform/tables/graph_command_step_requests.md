# Graph Command Step Requests Table

## Description
The `graph_command_step_requests` table stores network request diffs captured while executing one command step. It is command telemetry, not graph topology.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique request row identifier |
| command_step_id | UUID | NOT NULL, FK `graph_command_steps.id`, INDEX | - | Command step that caused or observed this request |
| order_index | INTEGER | NOT NULL | - | Request order inside the command step diff |
| method | TEXT | NOT NULL | - | HTTP method |
| url | TEXT | NOT NULL | - | Request URL |
| status_code | INTEGER | NULLABLE | - | Response status code when available |
| resource_type | TEXT | NULLABLE | - | Browser resource type, for example `document`, `xhr`, `fetch`, `script`, or `stylesheet` |
| metadata | JSONB | NOT NULL | `'{}'` | Extra request/response metadata such as timing, failure text, initiator, headers summary, or redirect chain |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |

## Relationships
- **Many-to-One**: Each request diff row belongs to one command step through `command_step_id`.

## Rules
- Persist only requests observed since the previous request cursor for the command being executed.
- Never persist the cumulative browser request log into a state.
- State-level request summaries are calculated by joining states to their producing command steps and adjacent command steps.
- Delete request diff rows when their owning command step is deleted by a command-subtree cascade.
