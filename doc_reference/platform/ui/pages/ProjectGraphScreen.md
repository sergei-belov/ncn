# Project Graph Screen

## Location
URL: `/qai/projects/:project_id/graph`

## Purpose
The Project Graph screen visualizes the explored application as a command graph. It shows URL nodes, observed browser states, command steps, request diffs, href candidates, and graph-builder agent sessions.

The screen is used to inspect and extend the discovered application map. It does not replace the pipeline editor and does not launch project runs.

## Features
- Initialize a project graph from a start URL by creating a backend start command step
- Display route nodes grouped by normalized URL and route regex pattern
- Display executed command topology derived from `graph_command_steps.before_step_id`
- Display observed states produced by command steps through `graph_states.command_step_id`
- Show executed node transitions derived from command steps and their produced states
- Show href candidate transitions from `graph_states.hrefs`
- Inspect command code, status, detail, request diff, parent command, and child commands
- Delete stale command branches and cascade their produced states, request diffs, orphaned nodes, and descendant commands
- Inspect state HTML snapshot metadata, hrefs, producing command step, incoming commands, and outgoing commands
- Explore href candidates by creating normal command steps with `source = href_goto` or `source = href_click`
- Start and continue graph-builder agent sessions from the current state cursor
- Change an active graph-builder session cursor through the agent-session PATCH endpoint
- Poll graph-builder messages incrementally
- Cancel an active graph-builder session
- Edit node metadata, position, and URL normalization settings

## Links to Other Screens
- [Project Navigation Screen](project_navigation.md) (URL: `/qai/projects/:project_id/*`) - left sidebar entry point into the graph section
- [Project Detail Screen](ProjectDetailScreen.md) (URL: `/qai/projects/:project_id`) - project overview and section navigation
- [Pipelines Screen](PipelinesScreen.md) (URL: `/qai/projects/:project_id/pipelines`) - versioned test-case inventory that may use discovered graph knowledge later
- [Project Runs Screen](ProjectRunsScreen.md) (URL: `/qai/projects/:project_id/runs`) - project run history, separate from graph exploration

## Design Description
The page lives inside the shared project layout and uses a graph-inspection workspace.

- **Header Area**: page title, graph status summary, derived start state information, and actions for initializing the graph or starting an agent session
- **Graph Canvas**:
  - route node cards grouped by URL normalization
  - executed node transitions derived from command steps and states
  - href candidate transitions displayed as secondary/dashed hints
  - current session cursor highlighted by the state currently selected in the active agent session
- **Toolbar**:
  - search by URL, normalized URL, route regex, command code, or href text
  - toggles for executed transitions, href candidates, command leaves, and state expansion
  - source and status filters for command steps
- **Node Panel**:
  - selected node metadata
  - route normalization and route params
  - states under the selected node
  - executed incoming/outgoing node transitions derived from command steps
  - href candidates discovered from states under the node
- **State Panel**:
  - selected state metadata
  - producing command step
  - cleaned HTML hash and preview
  - href candidates observed in the state
  - incoming and outgoing command steps
  - request diffs for the producing command and outgoing commands
- **Command Step Panel**:
  - command source, status, detail, code, parent command, child commands, produced state, request diff, and delete action
  - recovery diagnostics from metadata when the command was produced by replay
- **Href Panel**:
  - href candidates from the selected state or node
  - actions to explore a href through `page.goto(resolved_href)` or validated anchor click
- **Agent Session Panel**:
  - graph-builder sessions, current state cursor, browser storage presence, message log, and cancel action

UI Guidelines:
- Treat command steps as the graph source of truth
- Never infer topology from insertion order or message order
- Display href candidates separately from confirmed executed transitions
- Display failed command steps in traces, but do not treat them as confirmed reachability
- Display recovery command steps as replay traces with diagnostics, not as user-explored canonical paths
- Confirm command deletion before sending it because deleting a command removes its descendant command branch and produced states
- Show request counts as per-command diffs, never as cumulative browser-session totals
- The current agent cursor is always `graph_agent_sessions.current_state_id`
- The current command for a session is derived through `current_state.command_step_id`

## Components Used
- `ProjectSidebar.vue` - persistent project navigation
- `AppHeader.vue` - global header and breadcrumbs
- `ProjectGraphView.vue` - main graph screen container
- `GraphToolbar.vue` - graph search, filters, and display toggles
- `GraphCanvas.vue` - route graph visualization with executed and candidate transitions
- `GraphNodePanel.vue` - selected node metadata, states, and normalization controls
- `GraphStatePanel.vue` - selected state snapshot, hrefs, and command context
- `GraphCommandStepPanel.vue` - selected command step details and request diff
- `GraphHrefPanel.vue` - href candidates and exploration actions
- `GraphAgentPanel.vue` - graph-builder session messages and controls
- `GraphNormalizationEditor.vue` - route normalization editor
- `StatusBadge.vue` - shared lifecycle state visualization

## System Flow

### System Interactions:
1. **Initial Load**:
   - User opens `/qai/projects/:project_id/graph`
   - `GET /api/qai/v1/projects/:project_id/graph` loads graph summary, backend start command metadata, and derived start state/node metadata
   - `GET /api/qai/v1/projects/:project_id/graph/topology` loads derived topology for the canvas
   - If the graph is not initialized, the page shows an initialization empty state

2. **Graph Initialization Flow**:
   - User enters the application start URL
   - `POST /api/qai/v1/projects/:project_id/graph/init` creates the graph if needed, creates a root command step for the start URL, executes it, and observes the resulting state
   - Backend derives the start node from the produced state's `node_id`
   - The topology reloads and the produced start state/node is shown on the canvas

3. **Node Selection Flow**:
   - User selects a node on the canvas
   - `GET /api/qai/v1/projects/:project_id/graph/nodes/:node_id` loads node details, route params, states, and href candidates
   - The node panel shows editable metadata and normalization controls

4. **Node Normalization Flow**:
   - User edits normalized URL, route regex pattern, route params, or normalization settings
   - `PATCH /api/qai/v1/projects/:project_id/graph/nodes/:node_id/normalization` validates and applies the route normalization
   - The topology reloads so route grouping and href candidate matching use the updated pattern

5. **State Selection Flow**:
   - User selects a state under a node or from an expanded graph view
   - `GET /api/qai/v1/projects/:project_id/graph/states/:state_id` loads the full state snapshot
   - The state panel shows the producing command step, HTML preview, hrefs, incoming commands, outgoing commands, and related request diffs

6. **Command Step Selection Flow**:
   - User selects a command edge or command row
   - `GET /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id` loads command detail
   - The command panel shows parent command, child commands, produced state, request diff, status, detail, and metadata

7. **Command Step Deletion Flow**:
   - User chooses delete from a selected command step
   - UI confirmation explains that the selected command, descendant commands, their produced states, request diffs, and orphaned nodes will be removed
   - `DELETE /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id` deletes the selected command subtree
   - Backend clears `project_graphs.start_command_step_id` when the deleted subtree contains the canonical start command
   - Backend clears graph-agent session cursors that pointed to deleted states
   - The topology, open panels, and graph summary reload after deletion

8. **Href Exploration Flow**:
   - User selects a href candidate from a state or node
   - User chooses `goto` or `click` exploration strategy
   - `POST /api/qai/v1/projects/:project_id/graph/hrefs/explore` creates a normal command step with `source = href_goto` or `source = href_click`
   - Backend executes the command, observes the resulting state, records request diffs, updates the session cursor, and the topology reloads

9. **Agent Session Start Flow**:
   - User starts a graph-builder session from the selected state or from the derived graph start state
   - `POST /api/qai/v1/projects/:project_id/graph/agent-sessions` creates a session with `current_state_id`
   - The agent session panel opens and shows the current state cursor

10. **Agent Session Cursor Update Flow**:
   - User selects a different graph state while an active graph-builder session exists
   - `PATCH /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id` updates `current_state_id`
   - The agent session panel refreshes the current state cursor
   - This endpoint is the client API for moving or clearing the session cursor after creation

11. **Agent Instruction Flow**:
   - User sends an instruction to the graph-builder agent
   - If the UI needs to change the active cursor first, it calls `PATCH /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id` before sending the instruction
   - `POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/messages` stores only the user message content and queues worker execution
   - The worker splits executable browser work into command steps
   - Each command step is executed one by one, request diffs are captured, and a new state is created for the observed result
   - Session cursor moves by updating `graph_agent_sessions.current_state_id`
   - The UI polls messages and reloads topology when new graph data is available

12. **Recovery Flow**:
   - When a session needs to reach a known state or node, backend searches command paths through `graph_command_steps.before_step_id`
   - Recovery replay creates command steps with `source = recovery`
   - Replay diagnostics are stored in command metadata and summarized in `detail`
   - Recovery steps remain visible in the trace, while confirmed user-explored reachability remains derived from normal command sources

13. **Cancel Flow**:
   - User cancels an active graph-builder session
   - `POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/cancel` marks the session as cancelled
   - The worker stops accepting additional work for the cancelled session

### API Interactions:
- Page opened -> `GET /api/qai/v1/projects/:project_id/graph`
- Topology loaded -> `GET /api/qai/v1/projects/:project_id/graph/topology`
- Graph initialized -> `POST /api/qai/v1/projects/:project_id/graph/init`
- Nodes listed -> `GET /api/qai/v1/projects/:project_id/graph/nodes`
- Node selected -> `GET /api/qai/v1/projects/:project_id/graph/nodes/:node_id`
- Node metadata updated -> `PATCH /api/qai/v1/projects/:project_id/graph/nodes/:node_id`
- Node normalization updated -> `PATCH /api/qai/v1/projects/:project_id/graph/nodes/:node_id/normalization`
- State selected -> `GET /api/qai/v1/projects/:project_id/graph/states/:state_id`
- Command steps filtered -> `GET /api/qai/v1/projects/:project_id/graph/command-steps`
- Command step selected -> `GET /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id`
- Command step branch deleted -> `DELETE /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id`
- Href candidate explored -> `POST /api/qai/v1/projects/:project_id/graph/hrefs/explore`
- Agent session created -> `POST /api/qai/v1/projects/:project_id/graph/agent-sessions`
- Agent session opened -> `GET /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id`
- Agent session cursor changed -> `PATCH /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id`
- Agent message sent -> `POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/messages`
- Agent messages polled -> `GET /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/messages`
- Agent session cancelled -> `POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/cancel`

### Data Flow:
- `graph_command_steps.before_step_id` is the only persisted command topology link
- `project_graphs.start_command_step_id` stores the backend graph start command
- The frontend start state is derived by finding the state whose `command_step_id` equals `start_command_step_id`
- `graph_states.command_step_id` identifies the command that produced a state
- `graph_states.node_id` groups observed states by URL/route node
- Executed state and node transitions are derived by joining a command step with its parent command step and their produced states
- Deleting a command removes the selected command subtree, produced states, request diffs, and nodes that become orphaned after the state delete
- Deleting the canonical start command clears `project_graphs.start_command_step_id`, so derived start state and visual start node become `null`
- Agent session cursors that point to deleted states are cleared to `null`
- Href candidate transitions are derived from `graph_states.hrefs`; they become executed transitions only after href exploration creates and executes a normal command step
- Request data is stored as command-scoped diffs in `graph_command_step_requests`
- Agent sessions use `current_state_id` as the only browser cursor
- The current command step for a session is derived from the current state's `command_step_id`
- Recovery uses command paths and records replay attempts as command steps with `source = recovery`

## API Endpoints Used
- `GET /api/qai/v1/projects/:project_id/graph` - get graph summary
- `POST /api/qai/v1/projects/:project_id/graph/init` - initialize graph and backend start command
- `PATCH /api/qai/v1/projects/:project_id/graph` - update graph metadata
- `GET /api/qai/v1/projects/:project_id/graph/topology` - get derived graph topology
- `GET /api/qai/v1/projects/:project_id/graph/nodes` - list route nodes
- `GET /api/qai/v1/projects/:project_id/graph/nodes/:node_id` - get node detail
- `PATCH /api/qai/v1/projects/:project_id/graph/nodes/:node_id` - update node metadata or position
- `PATCH /api/qai/v1/projects/:project_id/graph/nodes/:node_id/normalization` - update node route normalization
- `GET /api/qai/v1/projects/:project_id/graph/states/:state_id` - get state detail
- `GET /api/qai/v1/projects/:project_id/graph/command-steps` - list command steps
- `GET /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id` - get command step detail
- `DELETE /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id` - delete a command subtree and its produced graph data
- `POST /api/qai/v1/projects/:project_id/graph/hrefs/explore` - execute a href candidate as a command step
- `POST /api/qai/v1/projects/:project_id/graph/agent-sessions` - create graph-builder agent session
- `GET /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id` - get graph-builder session
- `PATCH /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id` - change graph-builder session cursor
- `POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/messages` - send graph-builder instruction
- `GET /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/messages` - poll graph-builder messages
- `POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/cancel` - cancel graph-builder session

### Shared API Models
```txt
type PaginationMeta = {
  total_count: int
  offset: int
  limit: int
}

type GraphCommandSource = enum(positioning, agent, codegen_guided_agent, manual, href_goto, href_click, recovery, assertion, system)
type GraphCommandStatus = enum(pending, completed, failed, cancelled, skipped)
type GraphAgentSessionStatus = enum(active, cancelled, failed)
type GraphAgentSessionMode = enum(interactive, codegen_guided)

type GraphNodeSource = enum(manual, agent, href, system)
type GraphStateSource = enum(agent, manual, recovery, positioning, href)

type GraphRouteParam = {
  id: uuid
  node_id: uuid
  name: str
  pattern: str
  segment_index: int
  source: enum(auto, manual)
}

type GraphNode = {
  id: uuid
  project_graph_id: uuid
  raw_url: str
  normalized_url: str
  route_regex_pattern: str
  url_path: str
  url_query: json
  title: null | str
  description: null | str
  source: GraphNodeSource
  normalization_settings: json
  position_x: null | float
  position_y: null | float
  metadata: json
  created_at: datetime
  updated_at: datetime
}

type GraphNodeListItem = GraphNode & {
  states_count: int
  executed_incoming_count: int
  executed_outgoing_count: int
  href_candidate_outgoing_count: int
}

type GraphStateHref = {
  raw: str
  resolved_url: str
  normalized_url?: str
  route_regex_pattern?: str
  text?: str
  selector?: str
  discoverable: bool
}

type GraphState = {
  id: uuid
  project_graph_id: uuid
  node_id: uuid
  command_step_id: uuid
  name: null | str
  description: null | str
  cleaned_html_hash: str
  html_cleaner_version: str
  hrefs: GraphStateHref[]
  source: GraphStateSource
  metadata: json
  created_at: datetime
  updated_at: datetime
}

type GraphCommandStep = {
  id: uuid
  project_graph_id: uuid
  source: GraphCommandSource
  code: str
  before_step_id: null | uuid
  status: GraphCommandStatus
  detail: null | str
  metadata: json
  created_at: datetime
  updated_at: datetime
}

type GraphCommandStepRequest = {
  id: uuid
  command_step_id: uuid
  order_index: int
  method: str
  url: str
  status_code: null | int
  resource_type: null | str
  metadata: json
  created_at: datetime
}

type CommandEdge = {
  source_step_id: null | uuid
  target_step_id: uuid
}

type StateEdge = {
  source_state_id: uuid
  target_state_id: uuid
  command_step_id: uuid
}

type NodeEdge = {
  source_node_id: uuid
  target_node_id: uuid
  command_step_id: uuid
}

type HrefCandidateEdge = {
  source_state_id: uuid
  source_node_id: uuid
  target_node_id: null | uuid
  href: GraphStateHref
}

type ProjectGraphSummary = {
  id: uuid
  project_id: uuid
  start_command_step_id: null | uuid
  start_state_id: null | uuid
  name: null | str
  description: null | str
  start_command_step: null | GraphCommandStep
  start_state: null | GraphState
  visual_start_node: null | GraphNode
  nodes_count: int
  states_count: int
  command_steps_count: int
  href_candidates_count: int
  created_at: datetime
  updated_at: datetime
}

type ProjectGraphTopologyResponse = {
  graph: ProjectGraphSummary
  project_graph_id: uuid
  start_command_step_id: null | uuid
  start_state_id: null | uuid
  nodes: GraphNodeListItem[]
  states: GraphState[]
  command_steps: GraphCommandStep[]
  command_edges: CommandEdge[]
  state_edges: StateEdge[]
  executed_node_edges: NodeEdge[]
  href_candidate_edges: HrefCandidateEdge[]
  leaf_command_step_ids: uuid[]
}

type GraphNodeDetail = GraphNode & {
  route_params: GraphRouteParam[]
  states: GraphState[]
  executed_incoming_edges: NodeEdge[]
  executed_outgoing_edges: NodeEdge[]
  href_candidate_edges: HrefCandidateEdge[]
}

type GraphStateDetail = GraphState & {
  cleaned_html: str
  node: GraphNode
  producing_command_step: GraphCommandStep
  incoming_command_steps: GraphCommandStep[]
  outgoing_command_steps: GraphCommandStep[]
  producing_request_diff: GraphCommandStepRequest[]
  outgoing_request_diffs: GraphCommandStepRequest[]
}

type GraphCommandStepDetail = GraphCommandStep & {
  parent_command_step: null | GraphCommandStep
  child_command_steps: GraphCommandStep[]
  produced_state: null | GraphState
  request_diff: GraphCommandStepRequest[]
}

type DeleteGraphCommandStepResponse = {
  deleted_command_step_ids: uuid[]
  deleted_state_ids: uuid[]
  deleted_node_ids: uuid[]
  cleared_session_ids: uuid[]
  start_command_step_deleted: bool
  graph: ProjectGraphSummary
}

type GraphAgentSession = {
  id: uuid
  project_graph_id: uuid
  current_state_id: null | uuid
  status: GraphAgentSessionStatus
  mode: GraphAgentSessionMode
  browser_storage_state_present: bool
  metadata: json
  created_at: datetime
  updated_at: datetime
}

type GraphAgentMessage = {
  id: uuid
  session_id: uuid
  seq: int
  role: enum(user, assistant, system, tool)
  content: str
  metadata: json
  created_at: datetime
}
```

### GET /api/qai/v1/projects/:project_id/graph
**Response Model:**
```txt
ProjectGraphSummary
```

### POST /api/qai/v1/projects/:project_id/graph/init
**Request Body Model:**
```txt
type InitProjectGraphRequest = {
  raw_url: str
  title?: null | str
  description?: null | str
  normalization_settings?: json
  position?: {
    x: float
    y: float
  }
}
```

**Response Model:**
```txt
ProjectGraphSummary
```

Validation notes:
- The graph can be initialized only once while `start_command_step_id` is empty.
- The backend creates a root command step with `before_step_id = null` for the start URL, normally equivalent to `page.goto(raw_url)`.
- The backend observes the resulting state, normalizes the observed URL into a node, and sets `project_graphs.start_command_step_id`.
- `start_state_id` and `visual_start_node` in response models are derived values for frontend display.

### PATCH /api/qai/v1/projects/:project_id/graph
**Request Body Model:**
```txt
type PatchProjectGraphRequest = {
  name?: null | str
  description?: null | str
}
```

**Response Model:**
```txt
ProjectGraphSummary
```

### GET /api/qai/v1/projects/:project_id/graph/topology
**Request Query Parameters:**
- `include_states` (`null | bool`): include state records in the response
- `include_command_steps` (`null | bool`): include command step records in the response
- `expanded_node_ids` (`uuid[]`, optional): limit expanded state data to selected nodes
- `show_href_candidates` (`null | bool`): include href candidate edges
- `source` (`null | GraphCommandSource`): filter command-derived projections by source
- `status` (`null | GraphCommandStatus`): filter command-derived projections by command status

**Response Model:**
```txt
ProjectGraphTopologyResponse
```

Projection notes:
- Command edges are derived directly from `GraphCommandStep.before_step_id`.
- State edges are derived by matching command steps to their produced states.
- Executed node edges are derived from state edges where source and target states belong to different nodes.
- Href candidate edges are derived from `GraphState.hrefs`.

### GET /api/qai/v1/projects/:project_id/graph/nodes
**Request Query Parameters:**
- `search` (`null | str`): search by title, description, raw URL, normalized URL, or route regex pattern
- `source` (`null | GraphNodeSource`): filter by node source

**Response Model:**
```txt
type GraphNodesResponse = {
  data: GraphNodeListItem[]
}
```

### GET /api/qai/v1/projects/:project_id/graph/nodes/:node_id
**Response Model:**
```txt
GraphNodeDetail
```

### PATCH /api/qai/v1/projects/:project_id/graph/nodes/:node_id
**Request Body Model:**
```txt
type PatchGraphNodeRequest = {
  title?: null | str
  description?: null | str
  raw_url?: str
  normalization_settings?: json
  position?: null | {
    x: float
    y: float
  }
  position_x?: null | float
  position_y?: null | float
  metadata?: json
}
```

**Response Model:**
```txt
GraphNodeDetail
```

### PATCH /api/qai/v1/projects/:project_id/graph/nodes/:node_id/normalization
**Request Body Model:**
```txt
type PatchGraphNodeNormalizationRequest = {
  normalized_url: str
  route_regex_pattern: str
  route_params: {
    name: str
    pattern: str
    segment_index: int
    source: enum(auto, manual)
  }[]
  normalization_settings?: json
}
```

**Response Model:**
```txt
GraphNodeDetail
```

Validation notes:
- Route regex must be unique inside the project graph.
- The updated route regex must not ambiguously match another node's raw URL.

### GET /api/qai/v1/projects/:project_id/graph/states/:state_id
**Response Model:**
```txt
GraphStateDetail
```

### GET /api/qai/v1/projects/:project_id/graph/command-steps
**Request Query Parameters:**
- `before_step_id` (`null | uuid`): load direct child command steps
- `source` (`null | GraphCommandSource`): filter by command source
- `status` (`null | GraphCommandStatus`): filter by status
- `node_id` (`null | uuid`): filter by produced state's node
- `state_id` (`null | uuid`): filter by produced state or adjacent state context
- `leaf_only` (`null | bool`): return only command steps with no child command steps
- `search` (`null | str`): search by command code or detail
- `limit` (`null | int`): page size
- `offset` (`null | int`): pagination offset

**Response Model:**
```txt
type GraphCommandStepsResponse = {
  data: (GraphCommandStep & {
    produced_state: null | GraphState
    child_command_steps_count: int
    requests_count: int
  })[]
  meta: PaginationMeta
}
```

### GET /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id
**Response Model:**
```txt
GraphCommandStepDetail
```

### DELETE /api/qai/v1/projects/:project_id/graph/command-steps/:command_step_id
**Response Model:**
```txt
DeleteGraphCommandStepResponse
```

Deletion notes:
- The command step must belong to the selected project's graph.
- The deleted command set includes the selected command and every descendant command step reachable through `before_step_id`.
- Request diffs for deleted command steps are deleted.
- States produced by deleted command steps are deleted.
- Nodes are deleted only when no remaining state in the same project graph references them after the state delete.
- Parent commands and sibling command branches remain.
- If the deleted set contains `project_graphs.start_command_step_id`, the backend clears the start command pointer.
- Agent sessions whose `current_state_id` points to a deleted state are cleared to `current_state_id = null` and listed in `cleared_session_ids`.

### POST /api/qai/v1/projects/:project_id/graph/hrefs/explore
**Request Body Model:**
```txt
type ExploreGraphHrefRequest = {
  session_id: uuid
  state_id: uuid
  href: {
    raw?: str
    resolved_url?: str
    selector?: str
  }
  strategy: enum(goto, click)
}
```

**Response Model:**
```txt
type ExploreGraphHrefResponse = {
  command_step: GraphCommandStep
  state: null | GraphState
  session: GraphAgentSession
}
```

Notes:
- `strategy = goto` creates a command step with `source = href_goto` and code equivalent to `page.goto(resolved_href)`.
- `strategy = click` creates a command step with `source = href_click` and code equivalent to a validated anchor click.
- The command step's `before_step_id` is derived from `state_id -> command_step_id`.

### POST /api/qai/v1/projects/:project_id/graph/agent-sessions
**Request Body Model:**
```txt
type CreateGraphAgentSessionRequest = {
  current_state_id?: null | uuid
  mode?: GraphAgentSessionMode
  metadata?: json
}
```

**Response Model:**
```txt
GraphAgentSession
```

Notes:
- `current_state_id` is the only active session cursor.
- If omitted, backend resolves the start state from `project_graphs.start_command_step_id` and uses it as the session cursor before agent instructions are executed.
- The backend must not start a session from a node id; it always derives the active command through `current_state_id -> graph_states.command_step_id`.

### GET /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id
**Response Model:**
```txt
GraphAgentSession
```

### PATCH /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id
**Request Body Model:**
```txt
type PatchGraphAgentSessionRequest = {
  current_state_id?: null | uuid
}
```

**Response Model:**
```txt
GraphAgentSession
```

Notes:
- This endpoint is the client API for changing `current_state_id` after session creation.
- The session must be active.
- If `current_state_id` is a UUID, it must point to a state inside the same project graph.
- If `current_state_id` is `null`, the session cursor is cleared.
- Message creation must not change `current_state_id`; callers must patch the session first when the active cursor changes.

### POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/messages
**Request Body Model:**
```txt
type SendGraphAgentMessageRequest = {
  content: str
}
```

**Response Model:**
```txt
type SendGraphAgentMessageResponse = {
  session: GraphAgentSession
  message: GraphAgentMessage
}
```

Notes:
- This endpoint stores the user instruction and queues worker execution.
- This endpoint must not accept or mutate `current_state_id`.
- Worker execution must persist browser work command by command.

### GET /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/messages
**Request Query Parameters:**
- `after_seq` (`int`, optional): return only messages with `seq > after_seq`
- `limit` (`int`, optional): page size for incremental polling

**Response Model:**
```txt
type GraphAgentMessagesResponse = {
  session_id: uuid
  messages: GraphAgentMessage[]
  next_after_seq: int
  has_more: bool
}
```

### POST /api/qai/v1/projects/:project_id/graph/agent-sessions/:session_id/cancel
**Response Model:**
```txt
type CancelGraphAgentSessionResponse = {
  session: GraphAgentSession
  message: GraphAgentMessage
}
```
