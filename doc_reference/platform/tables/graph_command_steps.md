# Graph Command Steps Table

## Description
The `graph_command_steps` table is the source of truth for Project Graph reachability. Each row stores one validated browser command and links it to the previous command step through `before_step_id`.

The command graph is explicit and branch-safe:

```text
previous command step --before_step_id--> current command step
```

States and nodes are not duplicated inside command steps. The state produced by a command is stored in `graph_states.command_step_id`, and the node is reached through that state.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique command step identifier |
| project_graph_id | UUID | NOT NULL, FK `project_graphs.id`, INDEX | - | Owning project graph |
| source | TEXT | NOT NULL, INDEX | - | Command source: `positioning`, `agent`, `codegen_guided_agent`, `manual`, `href_goto`, `href_click`, `recovery`, `assertion`, or `system` |
| code | TEXT | NOT NULL | - | Validated direct Playwright expression, for example `page.goto(...)` or `page.get_by_role(...).click()` |
| before_step_id | UUID | NULLABLE, FK `graph_command_steps.id`, INDEX | - | Previous command step in the command graph; `null` for root commands such as the canonical start command or positioning traces |
| status | TEXT | NOT NULL, INDEX | `pending` | Execution status: `pending`, `completed`, `failed`, `cancelled`, or `skipped` |
| detail | TEXT | NULLABLE | - | Human-readable status detail, failure explanation, stale recovery explanation, or cancellation reason |
| metadata | JSONB | NOT NULL | `'{}'` | Structured metadata such as terminal method, selector hint, masked input summary, replay origin, expected recovery hash, trace ids, timing, token/tool data |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |
| created_by_user_id | UUID | NULLABLE, FK `users.id` | - | User that initiated the command when applicable |

## Relationships
- **Many-to-One**: Each command step belongs to one project graph through `project_graph_id`.
- **Self-reference**: `before_step_id` links a command to the command that produced its source state.
- **One-to-One / One-to-Zero**: A completed command step normally produces one `graph_states` row through `graph_states.command_step_id`. Failed commands may produce no state if no reliable observation is available.
- **One-to-Many**: A command step owns request diff rows through `graph_command_step_requests.command_step_id`.
- **Delete cascade root**: Deleting a command step deletes that command and all descendant command steps whose `before_step_id` ancestry passes through it.

## Command Graph Invariant
Command steps are graph vertices linked by `before_step_id`; they are not linked by chronological order.

```text
Step A
  ├─ Step B
  └─ Step C
      └─ Step D
```

In this example both `Step B.before_step_id = Step A.id` and `Step C.before_step_id = Step A.id` are valid branches. A leaf is any command step that has no child row where `before_step_id = command_steps.id`.

## Start Command Rule
The backend graph start is a command step, not a node or standalone state.

```text
project_graphs.start_command_step_id -> graph_command_steps.id
graph_states.command_step_id = project_graphs.start_command_step_id -> frontend start state
frontend start state.node_id -> visual start node
```

Graph initialization normally creates a root command with `before_step_id = null`, for example a validated `page.goto(raw_url)` positioning command. The produced state and its node are derived display data.

## State and Node Derivation
A state edge is derived by joining command steps to states:

```text
current_step = Step B
previous_step = Step B.before_step_id
source_state = graph_states where command_step_id = previous_step
target_state = graph_states where command_step_id = Step B.id
```

A node edge is derived through those states:

```text
source_node = source_state.node_id
target_node = target_state.node_id
```

No duplicated before/after state or node columns and no sequence-based topology are required.

## Execution Rules
- Create the command step before executing the command with `status = pending`.
- Execute exactly one validated Playwright command per command step.
- Capture request diff with the browser request cursor.
- Observe the browser after execution.
- Create one `graph_states` row linked to the command step when the observation is reliable.
- Set `status = completed` when command execution and observation succeed.
- Set `status = failed` and `detail` when command execution fails.
- If a command fails before any reliable after-state can be observed, do not create a state for the failed step and do not move the session cursor.

## Deletion Rules
- Delete command steps as a subtree, not as an isolated row.
- The deleted command set includes the selected command step and every descendant command step reachable through `before_step_id`.
- Delete `graph_command_step_requests` rows for every deleted command step.
- Delete `graph_states` rows whose `command_step_id` is in the deleted command set.
- Delete `graph_nodes` rows that have no remaining `graph_states` after the state delete.
- Keep parent commands and sibling command branches that are outside the deleted command set.
- If the deleted command set contains `project_graphs.start_command_step_id`, clear that start pointer.
- Clear any `graph_agent_sessions.current_state_id` that points to a deleted state.

## Source Semantics
- `positioning`: opens the requested start/current URL; useful for graph initialization and session setup but not a canonical user action.
- `agent`: command produced by the graph builder agent.
- `codegen_guided_agent`: command produced by agent using uploaded codegen guidance.
- `manual`: command created by explicit user action.
- `href_goto`: href exploration using `page.goto(resolved_href)`.
- `href_click`: href exploration using a validated anchor click command.
- `recovery`: replay of a known command path; metadata stores `replayed_from_step_id` and expected target information.
- `assertion`: validation command; useful in trace but not a navigation action.
- `system`: backend-owned command not directly authored by the user or agent.

## Notes
- `code` must be a validated direct Playwright expression, not arbitrary Python.
- `source` is the only phase/source discriminator; do not add a separate phase column unless the model later requires it.
- Chronological trace information belongs in `metadata` and must not define graph topology.
- Recovery path search traverses `before_step_id` children, then verifies produced states/nodes during replay.
