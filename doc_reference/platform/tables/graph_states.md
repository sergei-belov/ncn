# Graph States Table

## Description
The `graph_states` table stores the observed browser result of a command step. A state belongs to one normalized node and is produced by exactly one command step.

State rows are execution-state instances. They are not deduplicated by hash as primary identity. `cleaned_html_hash` is retained for comparison, grouping, recovery validation, and UI similarity detection.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique graph state identifier |
| project_graph_id | UUID | NOT NULL, FK `project_graphs.id`, INDEX | - | Owning project graph |
| node_id | UUID | NOT NULL, FK `graph_nodes.id`, INDEX | - | Node/route where this state was observed |
| command_step_id | UUID | NOT NULL, UNIQUE, FK `graph_command_steps.id`, INDEX | - | Command step that produced this observed state |
| name | TEXT | NULLABLE | - | Optional user-visible state name |
| description | TEXT | NULLABLE | - | Editable state description |
| cleaned_html_compressed | BYTEA | NOT NULL | - | Compressed cleaned HTML snapshot |
| cleaned_html_hash | TEXT | NOT NULL, INDEX | - | Hash of cleaned DOM for comparison and recovery validation |
| html_cleaner_version | TEXT | NOT NULL | - | Cleaner version that produced the stored HTML |
| hrefs | JSONB | NOT NULL | `'[]'` | Normalized href observations from this state; used for candidate node edges and href exploration commands |
| source | TEXT | NOT NULL | - | Observation source: `positioning`, `agent`, `manual`, `href_goto`, `href_click`, `recovery`, or `system` |
| metadata | JSONB | NOT NULL | `'{}'` | Additional observation metadata such as title, visible element summary, viewport, page errors, and observation timing |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |
| created_by_user_id | UUID | NULLABLE, FK `users.id` | - | User who initiated the producing command when applicable |
| updated_by_user_id | UUID | NULLABLE, FK `users.id` | - | User who last edited state metadata |

## Relationships
- **Many-to-One**: Each state belongs to one project graph through `project_graph_id`.
- **Many-to-One**: Each state belongs to one graph node through `node_id`.
- **One-to-One**: Each state is produced by one command step through `command_step_id`.
- **One-to-Many**: A graph builder session points to its current state through `graph_agent_sessions.current_state_id`.

## Href Payload
`hrefs` stores candidate navigation information observed in this state. A recommended item shape is:

```json
{
  "raw": "../select-project/ru",
  "resolved_url": "https://dev.cyberstudio.online/cyberstudio/select-project/ru",
  "normalized_url": "/cyberstudio/select-project/ru",
  "route_regex_pattern": "^/cyberstudio/select\-project/ru$",
  "text": "Select project",
  "selector": "a[href='../select-project/ru']",
  "discoverable": true
}
```

Href-derived edges are candidate edges only. To confirm reachability, the backend creates a normal command step with `source = href_goto` or `source = href_click` and captures the resulting state.

## State Graph Derivation
A state transition is derived from command steps and states:

```text
step.before_step_id -> step.id
source_state.command_step_id = step.before_step_id
target_state.command_step_id = step.id
```

The state table does not own actions or requests. Outgoing commands, incoming commands, and request summaries are query projections over `graph_command_steps` and `graph_command_step_requests`.

## Notes
- Do not reuse a state row only because `cleaned_html_hash` matches. Same hash means equivalent snapshot; same state id means exact execution result.
- `command_step_id` is required for observed states. A manually described state should still be created through a manual/system command step.
- Hrefs are stored on states because candidate navigation depends on the DOM snapshot that exposed the links.
- A state is deleted when its producing command step is deleted as part of a command-subtree cascade.
- Any agent session cursor that points to a deleted state must be cleared to `null`.
