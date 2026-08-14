# Step 07 — Project Graph: Minimal Event-Sourced Command Graph

## Goal
Refactor the Project Graph backend, database model, and UI documentation to use a compact event-sourced command graph.

The command graph is stored in `graph_command_steps.before_step_id`. Observed browser states point back to the command step that produced them. Nodes group states by URL/route. Sessions point only to the current state.

The backend graph start is also command-based: `project_graphs.start_command_step_id` points to the canonical root command that initializes exploration. Frontend views may show the state produced by that command as the start state and its node as the visual start node.

## Non-Goals
- Do not create test cases from the graph in this step.
- Do not execute project runs from graph nodes or states.
- Do not keep old graph action/request/edge source tables.
- Do not execute uploaded Playwright codegen as trusted code.

## Core Tables

```text
project_graphs
graph_nodes
graph_node_route_params
graph_states
graph_command_steps
graph_command_step_requests
graph_agent_sessions
graph_agent_messages
graph_agent_artifacts
```

Edges, action lists, and request summaries are service/API projections, not source-of-truth graph tables.

## Command Step Contract
Required fields:

```text
id
project_graph_id
source
code
before_step_id nullable
status
detail nullable
metadata
created_at
updated_at
created_by_user_id nullable
```

Rules:
- `before_step_id` links commands into a directed graph.
- `project_graphs.start_command_step_id` identifies the canonical graph start command.
- `source` is the only phase/source discriminator.
- `status` is the main execution status field.
- `detail` stores human-readable failure/cancellation/stale-recovery information.
- `metadata` stores optional structured details such as selector hints, masked input summaries, replay source, expected recovery hash, trace ids, and timings.
- Do not duplicate before/after state or node context inside `graph_command_steps`; derive it from states linked to command steps.

## State Contract
A state is produced by one command step.

Required fields:

```text
id
project_graph_id
node_id
command_step_id
name
description
cleaned_html_compressed
cleaned_html_hash
html_cleaner_version
hrefs
source
metadata
created_at
updated_at
created_by_user_id nullable
updated_by_user_id nullable
```

Rules:
- `command_step_id` is required and unique.
- State rows are execution-state instances; do not deduplicate primary state identity by hash.
- Same `cleaned_html_hash` means equivalent UI snapshot, not the same execution result.
- `hrefs` stores candidate navigation discovered in that DOM snapshot.

## Session Contract
A graph agent session stores only the current state cursor:

```text
id
project_graph_id
current_state_id nullable
status
mode
browser_storage_state_payload
metadata
created_at
updated_at
created_by_user_id nullable
```

`current_command_step_id` is not stored. It is derived:

```text
session.current_state_id -> graph_states.command_step_id
```

## Execution Semantics
Every executable browser operation must use the same command-recording primitive:

```text
execute_command_step(project_graph_id, session_id?, code, source)
```

Flow:

```text
1. Load session.current_state_id when a session is present.
2. Derive before_step_id from current_state.command_step_id, or use null for graph initialization/root positioning.
3. Create command step with status = pending.
4. Execute one validated Playwright command.
5. Capture request diff from the request cursor.
6. Observe current URL, cleaned HTML, title, visible elements, hrefs, and errors.
7. Get or create graph node from observed URL.
8. Create graph state linked to command_step_id.
9. Persist request diff rows.
10. Update command step status/detail/metadata.
11. Atomically update session.current_state_id when a session is present.
12. For graph initialization, set project_graphs.start_command_step_id to the created command step.
```

Graph initialization uses the same command semantics with no prior current state:

```text
1. Create root command step with before_step_id = null.
2. Execute the start URL command, normally page.goto(raw_url).
3. Observe and persist the produced state and node.
4. Set project_graphs.start_command_step_id to the root command step id.
```

## Batch Commands
If the agent returns multiple commands, split them into separate command steps:

```text
Step A -> fill login -> State A1
Step B -> fill password -> State A2
Step C -> click login -> State B0
```

Never attach a whole batch to the final browser state.

## Redirects
Redirects are normal command outcomes.

```text
AuthState -- click Login command step --> SelectProjectState
```

Node edge is derived from the states:

```text
AuthNode -> SelectProjectNode
```

## Href Exploration
Href discovery stores href candidates on `graph_states.hrefs`. To confirm a href, execute a normal command step:

```python
page.goto(resolved_href)
```

or a validated anchor click:

```python
page.locator("a[href='...']").click()
```

Use `source = href_goto` or `source = href_click`.

## Requests
Requests are stored only as diffs in `graph_command_step_requests`:

```text
cursor_before = request_cursor
execute command
requests_diff = requests_since(cursor_before)
```

Do not persist cumulative browser requests to states.

## Derived Projections
No projection edge tables are required.

State edge:

```text
step.before_step_id -> step.id
source_state.command_step_id = step.before_step_id
target_state.command_step_id = step.id
```

Node edge:

```text
source_node = source_state.node_id
target_node = target_state.node_id
```

Command leaves:

```text
steps where no child step has before_step_id = step.id
```

Href candidate edge:

```text
source_node = state.node_id
target_url = state.hrefs[].resolved_url / normalized_url / route_regex_pattern
```

## Command Deletion
Project Graph supports deleting stale command branches.

Deleting a command step deletes:

```text
selected command step
descendant command steps reachable through before_step_id
graph_command_step_requests for deleted commands
graph_states produced by deleted commands
graph_nodes left with no remaining states after the state delete
```

Parent commands and sibling command branches remain. If the deleted command branch contains `project_graphs.start_command_step_id`, clear the start pointer so the graph no longer has a derived start state or visual start node. Clear any `graph_agent_sessions.current_state_id` values that point to deleted states.

## Recovery
Recovery path search traverses command steps by `before_step_id`.

For state recovery:

```text
current_step = current_state.command_step_id
target_step = target_state.command_step_id
find path current_step -> target_step using child steps
```

Replay each command with:

```text
source = recovery
metadata.replayed_from_step_id = original_step.id
metadata.expected_state_id = original target state
metadata.expected_cleaned_html_hash = original target hash
metadata.expected_node_id = original target node
```

After each replay, validate actual state/node/hash. Stop on divergence and write `detail` on the recovery command step.

## API/UI Requirements
- Topology APIs derive command edges, state edges, node edges, href candidate edges, leaves, and paths from the core tables.
- State panel shows incoming/outgoing command steps by joining through `command_step_id`.
- Request panels show command-step request diffs.
- Href panel shows candidate navigation and can trigger `href_goto` or `href_click` command steps.
- Command step panel can delete a command subtree and reload derived topology after the cascade.
- No UI should depend on stored navigation-edge or state-relation-edge rows.

## Implementation Phases
1. Drop old graph action/request/edge tables from the target model.
2. Create minimal command-step and state schema.
3. Refactor manager around `execute_command_step`.
4. Capture requests by cursor diff.
5. Store hrefs on states.
6. Build topology/recovery projections from command steps.
7. Update UI to use derived command/state/node edges.
