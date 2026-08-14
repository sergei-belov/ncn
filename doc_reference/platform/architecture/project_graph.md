# Project Graph Architecture

## Purpose
The Project Graph is a project-level information model of the tested web application. It records browser command exploration, observed DOM states, normalized URL nodes, request diffs, href candidates, and graph-builder conversation history.

The graph is not a test-case pipeline and does not launch project runs. It helps QAi understand reachable pages and UI states so future test generation and authoring can use real application context.

## Core Architecture

```text
project_graphs
  ├─ start_command_step_id -> graph_command_steps.id
  ├─ graph_nodes
  │    └─ graph_states
  │         └─ command_step_id -> graph_command_steps.id
  ├─ graph_command_steps
  │    ├─ before_step_id -> graph_command_steps.id
  │    └─ graph_command_step_requests
  └─ graph_agent_sessions
       ├─ graph_agent_messages
       └─ graph_agent_artifacts
```

## Source of Truth
`graph_command_steps` is the only reachability source of truth.

```text
command_steps.before_step_id = command graph topology
states.command_step_id = observed browser result
states.node_id = URL/route grouping
sessions.current_state_id = browser/agent cursor
project_graphs.start_command_step_id = canonical backend graph start
```

There are no separate source-of-truth tables for action lists, state request summaries, or graph edges. These are calculated by projection services.

## Start Semantics
The Project Graph starts from a command step at the backend level. It does not start from a graph node or a standalone state.

Initialization from a start URL creates a root command step with `before_step_id = null`, usually a validated `page.goto(raw_url)` positioning command. The backend executes the command, observes the resulting browser state, creates or reuses the normalized node for the observed URL, creates the state linked to that command, and stores the command id in `project_graphs.start_command_step_id`.

Frontend views may present the start as a state because that is the useful browser context for users:

```text
start command = project_graphs.start_command_step_id
start state = graph_states where command_step_id = start command
start node = start_state.node_id
```

Any session that begins from the graph start should resolve the start state through the start command. It must not use a node id as the backend topology root.

## Session Cursor API Semantics
`graph_agent_sessions.current_state_id` is the browser/agent cursor for a session. Client-initiated cursor changes use agent-session endpoints:

```text
POST /api/qai/v1/projects/:project_id/graph/agent-sessions
PATCH /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id
```

The graph-agent message endpoint stores a user instruction and queues work. It must not accept `current_state_id` and must not move the session cursor as part of message creation.

Validated graph execution may still advance `current_state_id` after a command produces a new observed state.

## Command Step Model
A command step stores only the command graph identity and execution status:

```text
id
project_graph_id
source
code
before_step_id
status
detail
metadata
```

`before_step_id` is nullable for root command steps, including the canonical start command and non-canonical positioning traces. Branches and leaves are natural:

```text
Step A
  ├─ Step B
  └─ Step C
      └─ Step D
```

A leaf is a command step with no child command step where `before_step_id = leaf.id`.

## Command Deletion Semantics
Deleting a command step removes a command subtree from the Project Graph. The deleted command set contains the selected command step and every descendant command step reachable by following `before_step_id` children.

The cascade removes:

```text
selected command step
descendant command steps where before_step_id chains through the selected step
graph_command_step_requests for deleted command steps
graph_states where command_step_id is in the deleted command set
graph_nodes that have no remaining graph_states after the state delete
```

Parent commands and sibling branches remain. A graph node remains when at least one non-deleted state still points to it, because nodes group states and do not own commands.

If the deleted command set includes `project_graphs.start_command_step_id`, the manager must clear `project_graphs.start_command_step_id`. The graph then has no canonical backend start until it is initialized again, and the frontend must not display a derived start state or visual start node.

Any `graph_agent_sessions.current_state_id` that points to a deleted state must be set to `null`. New agent messages must not continue from a state that was removed by command deletion.

## State Model
A state is the browser result of one command step:

```text
state.command_step_id -> command_steps.id
state.node_id -> graph_nodes.id
```

State rows are execution-state instances. They are not reused as primary graph identity only because `cleaned_html_hash` matches. The hash is used for comparison and recovery validation.

`graph_states.hrefs` stores href candidates observed in that DOM snapshot. Hrefs can create candidate node edges in the UI, but confirmed reachability requires executing a normal command step with `source = href_goto` or `source = href_click`.

## Node Model
A node represents a normalized application route or screen. Node identity is `project_graph_id + route_regex_pattern`. Nodes group states; they do not own commands.

## Execution Primitive
All graph-building browser operations use one command-recording primitive:

```text
execute_command_step(project_graph_id, session_id?, code, source)
```

Flow:

```text
1. Load session.current_state_id when a session is present.
2. Resolve current_step_id from graph_states.command_step_id, or use null for graph initialization/root positioning.
3. Create graph_command_steps row with before_step_id = current_step_id and status = pending.
4. Execute one validated Playwright expression.
5. Capture network request diff since the previous cursor.
6. Observe browser URL, title, cleaned HTML, visible elements, hrefs, and errors.
7. Get or create graph node from observed URL.
8. Create graph state linked to the new command step.
9. Persist graph_command_step_requests for the request diff.
10. Update command step status/detail/metadata.
11. Atomically move session.current_state_id to the new state when a session is present.
12. For graph initialization, set project_graphs.start_command_step_id to the created command step.
```

The same primitive is used for agent commands, manual commands, href exploration, positioning, recovery replay, assertions, and system commands. Only `source` changes.

## Source Semantics
Recommended command sources:

```text
positioning
agent
codegen_guided_agent
manual
href_goto
href_click
recovery
assertion
system
```

Projection services can decide which sources are canonical for specific views. A common rule is:

```text
canonical exploration sources = agent, codegen_guided_agent, manual, href_goto, href_click, system
non-canonical trace sources = positioning, recovery, assertion
```

This rule belongs to projection/query services, not to additional database columns.

## Derived State Edges
A state transition is derived from one command step and its predecessor:

```text
step = command step B
previous_step = step.before_step_id
source_state = graph_states where command_step_id = previous_step
target_state = graph_states where command_step_id = step.id
edge = source_state -> target_state via step
```

No state edge table is required.

## Derived Node Edges
A node transition is derived through state edges:

```text
source_node = source_state.node_id
target_node = target_state.node_id
```

If nodes differ, this is an executed node transition. If nodes are the same, it is an intra-node state transition.

## Href Candidate Edges
Href candidate edges are derived from `graph_states.hrefs`:

```text
source_node = state.node_id
target URL = href.resolved_url / href.normalized_url / href.route_regex_pattern
```

Candidate edges are useful for exploration planning and UI hints. They are not canonical reachability until confirmed by an executed command step.

## Requests
Requests are command-scoped diffs in `graph_command_step_requests`.

The Playwright session may keep a cumulative request log internally, but persistence uses a cursor:

```text
cursor_before = requests_count()
execute command
requests_diff = requests_since(cursor_before)
```

States do not store cumulative requests.

## Recovery
Recovery uses the command graph, not URL-only edges or chronological order.

For target state recovery:

```text
1. Resolve current_step_id from session.current_state_id.
2. Resolve target_step_id from target_state.command_step_id.
3. Search the command graph from current_step_id to target_step_id using children where before_step_id = current step.
4. Replay each path command with source = recovery.
5. Store replay metadata: replayed_from_step_id, expected target hash/node/state.
6. Validate that the produced state matches expected node/hash/state.
7. Stop and mark detail if actual context diverges.
```

For target node recovery, use known states for that node as path targets and choose the shortest reachable command path.

Recovery replay is still recorded as command steps for traceability, but projection services should not treat `source = recovery` as canonical user/application reachability unless explicitly requested.

## Redirects
Redirects are normal command outcomes. Example:

```text
before: AuthState
command: click Login
after: SelectProjectState
```

This is one command step. The resulting node edge is derived through states:

```text
AuthNode -> SelectProjectNode via click Login step
```

No command is attached to the after state as its owner; the after state is only the result of the command.

## Failure Rules
- `status = failed` and `detail` describe failed command execution or stale recovery.
- If no reliable after-state exists, do not create a state for the failed command.
- If browser state changed before failure and a reliable observation exists, a state may be created and linked to the failed command, but the session cursor should move only when the manager trusts the observation.
- Failed commands are trace data. Projection services normally exclude them from canonical reachability.

## API Projection Responsibilities
The backend should expose projections without storing extra source-of-truth edge tables:

```text
CommandGraphProjectionManager
  get_command_steps()
  get_command_children(step_id)
  get_state_edges()
  get_node_edges()
  get_candidate_href_edges()
  get_leaves()
  find_path_to_state()
  find_path_to_node()
```

## Manager Boundaries
Recommended managers:

```text
GraphCommandStepManager
  - execute_command_step
  - create_pending_step
  - complete_step
  - fail_step
  - delete_command_subtree

GraphObservationManager
  - observe_browser_state
  - normalize_url_to_node
  - create_state_for_step
  - extract_hrefs
  - collect_request_diff

GraphProjectionManager
  - derive command/state/node edges
  - derive href candidate edges
  - find leaves and paths

GraphRecoveryManager
  - find command path to state/node
  - replay command steps with source = recovery
  - validate expected vs actual state
```

## Non-Goals
- The graph does not replace pipeline authoring.
- The graph does not execute project runs.
- The graph does not execute arbitrary uploaded code.
- The graph does not store redundant action/state-request/edge source tables.
