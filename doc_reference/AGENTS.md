# QAi Platform Documentation Context

> Always read @spec.md as project reference

## Project Overview

QAi is an intelligent platform for automating web application testing using Large Language Model (LLM) capabilities. The platform enables QA engineers and developers to quickly create and run automated tests without manual code writing. At its core, the platform uses visual action graphs to represent user scenarios, which are then converted to executable Playwright tests using LLM technology.

### Key Features
- Visual flow designer for creating user scenario graphs
- Project Graph with event-sourced browser command steps for tested-application topology discovery
- LLM-powered code generation from action descriptions
- Automated test execution with screenshot captures
- Project management with variables and secrets
- Integration with CI/CD pipelines
- Comprehensive reporting with execution logs

### Tech Stack
- **Frontend**: Vue.js with Vue Flow for drag-and-drop visual graph editing with path `/qai/...`
- **Backend**: RESTful API based on FastAPI with endpoint structure `/api/qai/v1/`
- **Message Broker**: Apache Kafka for handling asynchronous tasks
- **Testing Framework**: Playwright for browser automation
- **AI/ML**: Large Language Model integration for code generation
- **Database**: PostgreSQL for storing projects, flows, and results
- **Infrastructure**: Container-based deployment

## Documentation Structure

```
docs/
├── QWEN.md                    # This file
├── spec.md                    # Main project specification file
├── platform/                  # Platform documentation
│   ├── README.md              # Platform overview (in Russian)
│   ├── intro.md               # Introduction to the platform (in Russian)
│   ├── defenitions.md         # Key definitions and terminology (in Russian)
│   ├── ui/                    # UI screen documentation
│   │   ├── general/           # General components - navbar, user button ets
│   │   ├── pages/             # Pages documentation
│   │   └── README.md          # UI structure and overall description
│   └── tables/                # Database schema documentation
```

## Core Concepts

### Projects
The basic unit for organizing test automation for specific web applications. Projects contain variables, secrets, action graphs, event-sourced project graph data, and execution reports.

### Project Graphs
Project-level information models of tested applications. Project Graph uses normalized nodes, observed DOM states, minimal command steps linked by `before_step_id`, href candidates, and per-command request diffs. Command steps are the source of truth; state/node edges are derived by API projection services.

### Action Graphs
Visual representation of user scenarios using drag-and-drop nodes. Each action includes checks and assertions to validate expected behaviors. The LLM interprets user descriptions to generate abstract Playwright code from these graphs.

### Actions and Assertions
Actions represent specific user steps, while assertions define the validation checks that ensure expected behaviors are met. Each action connects to screenshots taken during execution for visual verification.

### Abstract Code
Intermediate representation of test scenarios that can be transformed into executable Playwright code. This abstraction allows for flexible test generation and maintenance.

## Building and Running

This documentation set doesn't contain explicit build or run instructions as it's primarily a documentation repository. The actual QAi platform would be built and deployed separately, but this documentation serves as the central reference for understanding the system architecture, API endpoints, and database schema.

## Development Conventions

### API Design Patterns
- Base path: `/api/qai/v1/`
- Resource-oriented URLs following CRUD patterns
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response bodies
- Consistent data structures with pagination support
- UUID-based identifiers

### Data Modeling
- Hierarchical structure (Projects contain Flows and Pipelines)
- Step schemas store test case descriptions, generated execution artifacts, status, and editor metadata
- Rich metadata tracking (created_at, stats, relationships)
- Version-controlled flow definitions with change history
- Minimal Project Graph command steps linked by `before_step_id` with derived API projections

## For Future Development

When working with this documentation:
- Refer to `spec.md` for the main platform specification
- Read `platform/tables/` to check database structure
- Read `platform/ui/README.md` to check pages structure
- Only read `platform/ui/pages/` when specifically requested
- Follow the existing structure and terminology
- Maintain the separation between high-level concepts and detailed implementations

## Task cimplementation
- Accomplish task
- If new pages is added make changes to `spec.md` and to `platform/ui/README.md`

## Architectural Patterns

### Optimistic Update Pattern
For UI responsiveness, the platform uses optimistic updates with PATCH endpoints:

**When to use:**
- Drag-and-drop position changes (e.g., step nodes on Vue Flow canvas)
- Inline field edits that should feel instant
- Any UI update where perceived performance matters

**How it works:**
1. Update UI state immediately (optimistic)
2. Send minimal payload via PATCH in background
3. On error: rollback to server state by reloading data
4. On success: UI already reflects the change

**Example flow:**
```
User drags step node → UI updates position instantly → 
PATCH /steps/:id { meta: { position: { x, y } } } →
If error: reload steps to restore previous state
```

**Benefits:**
- Zero perceived latency for user actions
- Reduced payload (only changed fields via PATCH)
- Graceful error handling with automatic rollback

This documentation serves as a foundation for understanding the QAi platform architecture, enabling efficient collaboration between team members and providing AI agents with the necessary context to assist with platform development and maintenance.


## Project Graph Command Linkage

Project Graph topology is command-step based. `graph_command_steps.before_step_id` links commands into a directed graph with branches and leaves. `graph_states.command_step_id` stores the observed result of a command step. `graph_states.node_id` groups states by URL/route. Do not infer graph topology from sequence numbers, timestamps, state IDs, or node IDs.