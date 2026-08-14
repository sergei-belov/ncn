# Project Graphs Table

## Description
The `project_graphs` table stores one project-level graph root per project. The graph is an informational model of the tested application, built from command steps and observed states.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique project graph identifier |
| project_id | UUID | NOT NULL, UNIQUE, FK `projects.id` | - | Project that owns this graph |
| start_command_step_id | UUID | NULLABLE, FK `graph_command_steps.id` | - | Canonical command step that initializes graph exploration |
| name | TEXT | NULLABLE | - | Optional graph name |
| description | TEXT | NULLABLE | - | Optional graph description |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |
| created_by_user_id | UUID | NULLABLE, FK `users.id` | - | User who created the graph |
| updated_by_user_id | UUID | NULLABLE, FK `users.id` | - | User who last updated graph metadata |

## Relationships
- **One-to-One**: Each project has one project graph.
- **One-to-Many**: A graph owns nodes, states, command steps, command-step request diffs, agent sessions, messages, and artifacts.
- **Many-to-One**: `start_command_step_id` points to the canonical start command step after initialization.
- **Derived start state**: The frontend start state is the `graph_states` row where `command_step_id = project_graphs.start_command_step_id`.
- **Derived start node**: The visual start node is derived from that start state's `node_id`.

## Purpose
The graph root groups the command graph, route model, state observations, href candidates, and builder sessions for one project. It is separate from pipeline/test-case execution.

The graph does not start from a node or a standalone state at the backend level. Initialization creates a command step, usually a validated `page.goto(raw_url)` positioning command with `before_step_id = null`, observes the resulting state, and derives the displayed start state/node from that command result.

If command deletion removes the command step referenced by `start_command_step_id`, the start pointer is cleared. The graph remains attached to the project but has no canonical backend start, derived start state, or visual start node until initialization creates a new start command.
