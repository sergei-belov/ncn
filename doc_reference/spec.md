# QAi Platform - Project Specification

## What Platform Does

QAi is an intelligent platform for automating web application testing using Large Language Model (LLM) capabilities. The platform enables QA engineers and developers to quickly create and run automated tests without manual code writing.

Key functions:
- Creates visual action graphs representing user scenarios with Vue Flow
- Automatically generates abstract Playwright code from action graphs
- Separates editable pipeline drafts from immutable published pipeline versions
- Publishes immutable test-case versions from the current draft state
- Generates draft test cases and step refinements with AI-assisted preview flows
- Stores a project-level command-step Graph of tested-application pages, DOM states, href candidates, URL normalization rules, request diffs, and removable stale command branches
- Executes tests and provides detailed reports with screenshots
- Manages projects, variables, and secrets for test configuration
- Integrates with CI/CD pipelines for scalable testing

The platform focuses on reducing manual testing costs, accelerating automation development, and improving product quality through AI-supported automation.

## Main User Experience

The user experience centers around creating and managing automated tests through a visual interface:

1. **Project Creation**: Users start by creating projects linked to specific web applications and then enter the project workspace through the projects list and project overview screens.

2. **Project Configuration**: Inside a project, users manage reusable variables and secrets on the dedicated Variables screen so pipeline steps can reference shared placeholders such as `{{BASE_URL}}`.

3. **Project Graph Modeling**: Users can open a dedicated Graph section for the project, enter a start URL, inspect pages/screens, manage deterministic URL normalization, view DOM states and command traces, delete stale command branches, and use the graph builder agent to extend the navigable information model of the tested application. Backend initialization stores the start as a command step; frontend views may present the produced state and node as the visual start.

4. **Pipeline Design**: Through the Pipelines screen and the visual Pipeline Detail editor powered by Vue Flow, users create and maintain graph-based draft scenarios with steps, assertions, links, variable references, start steps, branching links, and pre/post pipeline dependencies.

5. **Test Case Versioning**: Users publish immutable pipeline versions from the current draft, inspect version history, compare version metadata, and choose the active version that future launches should use.

6. **AI-assisted Generation**: Users can ask QAi to generate or refine one draft pipeline from a free-form description, from a current step context, or from existing draft steps. AI generation sidebars can insert project variable placeholders into the user's prompt or description through a searchable frontend picker before submission. Generation is asynchronous, produces a preview first, and lets the user accept, edit, or reject the result before any live draft is changed.

7. **Test Generation**: The LLM interprets user descriptions, HTML context, step metadata, and agent tools to generate normalized pipeline preview structures that can later be transformed into executable Playwright tests.

8. **Execution and History**: Runs are initiated from pipeline-related entry points or from the project-wide Runs screen. At launch time, the system resolves the concrete published pipeline version for every selected pipeline, queues Playwright execution, and persists that resolution in run history.

9. **Results Analysis**: Users review run history, execution statuses, per-pipeline results, and related pipeline-version context to understand what was launched, which exact published test-case version was used, and what requires follow-up.

The platform is especially valuable for teams wanting quick UI test coverage without extensive automation resources, offering a solution that adapts to product changes using AI capabilities.

## Test Case Lifecycle

QAi treats a pipeline as a **test case with two layers**:

1. **Draft pipeline**
   - editable working state
   - used in the visual editor
   - may change frequently during authoring

2. **Published pipeline version**
   - immutable snapshot created from the current draft
   - used for controlled launches and historical traceability
   - can be reviewed later exactly as it was published

### Lifecycle rules
- Only the **draft** is editable.
- A **published version** is immutable and cannot be changed in place.
- Creating a new published version always serializes the current draft into a new snapshot.
- Each pipeline may have many published versions.
- Exactly one published version may be marked as the **active version** for launch by default.
- Runs must reference the concrete published version used for execution and history.
- If a pipeline has no published version yet, it cannot be launched as a controlled test case.

### Variable handling rule for versions
- The published version snapshot stores pipeline structure together with a **variable reference manifest**.
- Secret and non-secret variable **values are not duplicated** into the version snapshot by default.
- Runtime resolution uses the current project variable set unless a future execution step introduces value pinning.

## AI Generation Lifecycle

QAi treats AI-assisted generation as a **session-based preview workflow** and not as a direct mutation of live domain tables.

### Session layers
1. **Generation session**
   - tracks one asynchronous generation request
   - belongs to one project
   - may optionally target one pipeline or one step
   - may produce multiple previews over time

2. **Generation preview**
   - normalized candidate result produced by the agent runtime
   - editable by the user before accept
   - may represent a new pipeline draft, a pipeline patch, a step patch, or an append-after-step patch

3. **Accepted draft changes**
   - applied by backend domain managers only after explicit user acceptance
   - create or update draft entities in `pipelines`, `steps`, `steps_links`, and `assertions`

### AI generation rules
- AI generation always starts with a **preview**.
- The agent **must not** mutate live draft tables directly.
- A session may have many previews, but only one preview is the current `latest active preview`.
- If the user regenerates within the same session, the old active preview becomes `superseded` and the new preview becomes `active`.
- Accept creates or updates **draft data only**; it does not auto-publish a pipeline version.
- On the first implementation stage, one generation session may produce **one pipeline maximum**.
- Step-level generation may only:
  - patch the target step, or
  - append new steps after the target step.
- Step-level generation may **not** change previous steps.
- When appending after a step, the first generated link from the target step is created automatically.
- The agent may use existing step HTML snapshots or trigger a pipeline run/Playwright path to obtain HTML context.
- The UI shows a shortened trace; the database keeps the full trace.
- Variable insertion in AI sidebars is a frontend-only input composition feature: selected variables are inserted as placeholders such as `{{BASE_URL}}` into the existing prompt or description text, without changing the AI generation API contracts.

## Project Graph Lifecycle

QAi treats the project Graph as a **navigable information model** of the tested application, not as an executable test-case graph.

### Graph layers
1. **Project graph**
   - one graph root per project
   - owns nodes, states, command steps, command-step request diffs, route normalization data, and graph builder sessions
   - may be empty until the user initializes the start command from a start URL
   - stores the canonical start command step; the start state and start node are derived from that command's observed result

2. **Graph node**
   - represents a page, route, or screen
   - stores raw URL, normalized route template, full route regex pattern, route params, and canvas metadata
   - may exist without states when created manually

3. **Graph command step**
   - stores one validated browser command
   - links to the previous command step through `before_step_id`
   - is the source of truth for command graph topology
   - may be the canonical graph start when `project_graphs.start_command_step_id` points to it
   - supports branches and leaves naturally
   - may be deleted as a command subtree together with descendant commands, produced states, request diffs, and orphaned nodes

4. **Graph state**
   - stores the observed browser result of one command step through `command_step_id`
   - belongs to one node through `node_id`
   - stores cleaned HTML, cleaned HTML hash, and href candidates observed in that DOM snapshot
   - is deleted when its producing command step is deleted

5. **Graph command step request**
   - stores network request diffs for one command step
   - never stores cumulative browser request history
   - is deleted when its owning command step is deleted

6. **Graph builder session**
   - stores only the current state cursor through `current_state_id`
   - derives the current command step from `graph_states.command_step_id`

### Graph rules
- Each project has exactly one graph.
- Each initialized graph has exactly one canonical start command step.
- Backend graph start is `project_graphs.start_command_step_id`, not a node ID or state ID.
- The frontend may display a start state: `graph_states.command_step_id = project_graphs.start_command_step_id`.
- The start node is derived from that start state through `graph_states.node_id`.
- Node identity is matched by full route regex pattern, not only by placeholder template.
- URL normalization is deterministic and backend-owned.
- Command graph topology is `graph_command_steps.before_step_id`, not sequence, timestamps, state IDs, or node IDs.
- A state is produced by one command step: `graph_states.command_step_id`.
- A node groups observed states: `graph_states.node_id`.
- Hrefs are stored on states as candidate navigation; confirmed navigation requires a normal command step such as `page.goto(resolved_href)` or a validated href click.
- Requests are stored as diffs on command steps, not as cumulative state data.
- State edges, node edges, leaves, paths, and request summaries are API/service projections from command steps, states, nodes, and request diffs.
- Client-initiated session cursor changes happen through agent-session creation or the agent-session PATCH endpoint, not through graph-agent message creation payloads.
- Deleting a graph command step deletes that command and every descendant command step whose ancestry passes through it via `before_step_id`.
- Command deletion deletes request diffs for deleted commands and states produced by deleted commands; graph nodes are deleted only when no remaining state in the same project graph references them after the cascade.
- If the deleted command subtree contains `project_graphs.start_command_step_id`, the start pointer is cleared and the frontend has no derived start state or visual start node until the graph is initialized again.
- Agent session cursors pointing to deleted states are cleared; message creation must not continue from a deleted state context.
- The graph builder agent may mutate graph data only by executing validated command steps and creating observed states.
- Uploaded Playwright codegen can guide the agent but must not be executed as trusted arbitrary code.

## Documentation Structure

```
docs/
├── platform/                  # Platform documentation
│   ├── README.md              # Platform overview (in Russian)
│   ├── intro.md               # Introduction to the platform (in Russian)
│   ├── defenitions.md         # Key definitions and terminology (in Russian)
│   ├── architecture/          # Cross-cutting architecture documentation
│   ├── ui/                    # UI screen documentation
│   │   ├── general/           # General components - navbar, user button ets
│   │   ├── pages/             # Pages documentation
│   │   └── README.md          # UI structure and overall description
│   └── tables/                # Database schema documentation
├── templates/                 # Documentation templates
│   ├── page.md                # Template for UI screen documentation and system design
│   └── table.md               # Template for database schema documentation
```

## Docs Templates

Documentation templates are provided to maintain consistency across the project:

- **Page Template**: Standard structure for documenting user interface pages ([page.md](templates/page.md))
- **Table Template**: Standard structure for documenting database tables ([table.md](templates/table.md))

These templates ensure consistent formatting and comprehensive coverage of all necessary information for both UI pages and database schema documentation.

## System Description Style

The platform follows a client-server architecture with REST API endpoints and asynchronous Kafka-backed workers where necessary.

**API Endpoint Style**:
- Base path: `/api/qai/v1/`
- Resource-oriented URLs following CRUD patterns
- Standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- JSON request/response bodies
- Consistent data structures with pagination support
- UUID-based identifiers

**Key Resources**:
- Projects: Main containers for test configurations
- Project Graphs: Command-step informational models of tested-application pages, states, href candidates, URL normalization rules, and request diffs
- Pipelines: Mutable draft heads for test cases inside a project
- Pipeline Versions: Immutable published snapshots used for controlled launches and history
- Runs: Project-wide launch history with resolved pipeline-version context and Playwright execution lifecycle
- AI Generation Sessions: Asynchronous generation requests with progress, preview, and accept/reject lifecycle
- Steps / Links / Assertions: Structural elements of the authored draft and of the published snapshot; step graphs support start steps, branching outgoing links, and one incoming link per non-start step

**Request/Response Patterns**:
- Paginated list responses with metadata
- Detailed resource objects for single item requests
- Standardized error responses
- Authentication headers for secure access
- Polling-friendly cursor patterns for growing message logs

**Data Modeling**:
- Hierarchical structure (Projects contain Pipelines)
- Project Graph uses one graph per project, one backend start command step, normalized node identity by full route regex pattern, command steps linked by `before_step_id` as source of truth, states as observed command results, and command-subtree deletion for stale exploration data
- Pipelines use a draft-plus-version model: one editable draft, many immutable published versions
- Published versions serialize metadata, steps, links, assertions, dependencies, and variable references
- AI generation uses a session-plus-preview model: one session, many previews, one latest active preview
- Runs resolve and persist the concrete published pipeline version used at launch time and queue Playwright execution
- Step schemas store test case descriptions, generated execution artifacts, status, and editor metadata
- Rich metadata tracking (created_at, stats, relationships, active version, session status, preview status)

## System Design

### Database Tables

The platform uses a well-structured relational database with the following documented key entities. Detailed documentation for these tables can be found in the [platform/tables](platform/tables/) directory:

- **users**: Stores application user accounts with authentication details ([users.md](platform/tables/users.md))
- **projects**: Top-level containers for organizing test automation efforts ([projects.md](platform/tables/projects.md))
- **project_users**: Manages user-to-project relationships with role assignments ([project_users.md](platform/tables/project_users.md))
- **variables**: Stores project-level variables and secrets for test configuration ([variables.md](platform/tables/variables.md))
- **project_graphs**: Stores one project-level graph root and start-command pointer per project ([project_graphs.md](platform/tables/project_graphs.md))
- **graph_nodes**: Stores normalized tested-application pages/screens with route regex identity ([graph_nodes.md](platform/tables/graph_nodes.md))
- **graph_node_route_params**: Stores editable dynamic route parameter rules for graph nodes ([graph_node_route_params.md](platform/tables/graph_node_route_params.md))
- **graph_states**: Stores observed browser states produced by command steps, including href candidates ([graph_states.md](platform/tables/graph_states.md))
- **graph_command_steps**: Stores the minimal command graph source of truth linked by `before_step_id` ([graph_command_steps.md](platform/tables/graph_command_steps.md))
- **graph_command_step_requests**: Stores network request diffs per command step ([graph_command_step_requests.md](platform/tables/graph_command_step_requests.md))
- **graph_agent_sessions**: Stores graph builder agent sessions and current graph context ([graph_agent_sessions.md](platform/tables/graph_agent_sessions.md))
- **graph_agent_messages**: Stores ordered graph builder agent chat/tool messages ([graph_agent_messages.md](platform/tables/graph_agent_messages.md))
- **graph_agent_artifacts**: Stores graph builder artifacts such as Playwright codegen guidance ([graph_agent_artifacts.md](platform/tables/graph_agent_artifacts.md))
- **pipelines**: Mutable draft heads and test-case metadata containers ([pipelines.md](platform/tables/pipelines.md))
- **pipeline_versions**: Immutable published snapshots of pipelines used for controlled launches, rollback, and history ([pipeline_versions.md](platform/tables/pipeline_versions.md))
- **steps**: Individual test actions with generated code and execution status ([steps.md](platform/tables/steps.md))
- **assertions**: Validation checks associated with each test step ([steps.md](platform/tables/steps.md))
- **steps_links**: Defines execution flow between steps in a directed graph ([steps.md](platform/tables/steps.md))
- **pre_pipelines/post_pipelines**: Handle draft pipeline dependencies and execution order ([pre_post_pipelines.md](platform/tables/pre_post_pipelines.md))
- **runs**: Stores project-wide run history, lifecycle state, targeting metadata, execution mode, and audit timestamps ([runs.md](platform/tables/runs.md))
- **run_pipelines**: Links each recorded run to selected pipelines and the concrete published versions resolved at launch time, including per-pipeline execution state ([run_pipelines.md](platform/tables/run_pipelines.md))
- **run_step_results**: Stores step-level Playwright execution output for run result inspection ([run_step_results.md](platform/tables/run_step_results.md))
- **run_assertion_results**: Stores assertion-level Playwright execution output nested under step results ([run_assertion_results.md](platform/tables/run_assertion_results.md))
- **ai_generation_sessions**: Tracks asynchronous AI-generation requests, targets, statuses, and acceptance results ([ai_generation_sessions.md](platform/tables/ai_generation_sessions.md))
- **ai_generation_messages**: Stores full planner/agent/validator/tool traces with cursor-friendly ordering ([ai_generation_messages.md](platform/tables/ai_generation_messages.md))
- **ai_generation_previews**: Stores editable preview artifacts before they are accepted into live draft tables ([ai_generation_previews.md](platform/tables/ai_generation_previews.md))

### Pages and User Interface Components

The platform's user interface is organized around the currently documented page files in [platform/ui/pages](platform/ui/pages/). The list below reflects the actual screen documents that exist in the repository today:

- **Projects List Screen** (URL: `/qai/projects`): Main dashboard showing all accessible projects with statistics ([ProjectsListScreen.md](platform/ui/pages/ProjectsListScreen.md))
- **Project Navigation Screen** (URL: `/qai/projects/:project_id/*`): Shared navigation shell with global breadcrumbs and the persistent project sidebar ([project_navigation.md](platform/ui/pages/project_navigation.md))
- **Project Detail Screen** (URL: `/qai/projects/:project_id`): Project overview screen with metadata, statistics, and entry points into project sections ([ProjectDetailScreen.md](platform/ui/pages/ProjectDetailScreen.md))
- **Project Variables Screen** (URL: `/qai/projects/:project_id/variables`): Project-level variables and secrets management for reusable placeholders ([ProjectVariablesScreen.md](platform/ui/pages/ProjectVariablesScreen.md))
- **Project Runs Screen** (URL: `/qai/projects/:project_id/runs`): Project-wide run history and run creation screen ([ProjectRunsScreen.md](platform/ui/pages/ProjectRunsScreen.md))
- **Project Graph Screen** (URL: `/qai/projects/:project_id/graph`): Project-level command-step navigable information model for pages, states, href candidates, URL normalization, and graph builder sessions ([ProjectGraphScreen.md](platform/ui/pages/ProjectGraphScreen.md))
- **Pipelines Screen** (URL: `/qai/projects/:project_id/pipelines`): Pipeline list, publish state, and AI-assisted generation entry screen for a selected project ([PipelinesScreen.md](platform/ui/pages/PipelinesScreen.md))
- **Pipeline Detail Screen** (URL: `/qai/projects/:project_id/pipelines/:pipeline_id`): Vue Flow redactor for step graphs, assertions, pre/post dependencies, draft publishing, version history, and step-level AI assistance ([PipelineDetailScreen.md](platform/ui/pages/PipelineDetailScreen.md))

### Architecture Notes

Cross-cutting architecture documentation is stored in [platform/architecture](platform/architecture/):

- [README.md](platform/architecture/README.md) - overview of architecture documents
- [ai_generation.md](platform/architecture/ai_generation.md) - Step 06 architecture for Kafka, LangGraph, preview flow, and API contracts
- [project_graph.md](platform/architecture/project_graph.md) - Step 07 architecture for project graph data, URL normalization, command graph topology, observed states, href candidates, request diffs, recovery, and graph builder agent boundaries
