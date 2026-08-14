# Database Tables Summary

This directory contains documentation for the currently documented database tables in the QAi platform.

## Core Tables
- [users.md](users.md) - Application users with authentication details
- [projects.md](projects.md) - Top-level containers for test automation
- [project_users.md](project_users.md) - Many-to-many relationship between users and projects with roles
- [variables.md](variables.md) - Project-level variables and secrets used by drafts, versions, and generation prompts

## Pipeline and Flow Tables
- [pipelines.md](pipelines.md) - Mutable draft heads for test cases
- [pipeline_versions.md](pipeline_versions.md) - Immutable published snapshots of pipeline drafts
- [pre_post_pipelines.md](pre_post_pipelines.md) - Pipeline dependencies
- [steps.md](steps.md) - Individual test actions, validations, and their relationships

## Run Tables
- [runs.md](runs.md) - Project-wide run history records with status, execution mode, and targeting metadata
- [run_pipelines.md](run_pipelines.md) - Junction table linking recorded runs to selected pipelines, concrete pipeline versions, and per-pipeline execution state
- [run_step_results.md](run_step_results.md) - Step-level execution results for each selected run pipeline
- [run_assertion_results.md](run_assertion_results.md) - Assertion-level execution results nested under run step results

## AI Generation Tables
- [ai_generation_sessions.md](ai_generation_sessions.md) - Asynchronous AI-generation lifecycle and target refs
- [ai_generation_messages.md](ai_generation_messages.md) - Full trace of planner/agent/validator/tool messages with cursor-based ordering
- [ai_generation_previews.md](ai_generation_previews.md) - Editable preview artifacts produced before accept

## Project Graph Tables
- [project_graphs.md](project_graphs.md) - One graph root per project and start-command pointer
- [graph_nodes.md](graph_nodes.md) - Normalized tested-application pages, routes, and screens
- [graph_node_route_params.md](graph_node_route_params.md) - Editable URL route parameter rules for graph nodes
- [graph_states.md](graph_states.md) - Observed browser states produced by command steps, including href candidates
- [graph_command_steps.md](graph_command_steps.md) - Minimal command graph source of truth linked by `before_step_id`
- [graph_command_step_requests.md](graph_command_step_requests.md) - Network request diffs captured per command step
- [graph_agent_sessions.md](graph_agent_sessions.md) - Graph builder agent sessions with current-state cursor
- [graph_agent_messages.md](graph_agent_messages.md) - Ordered graph builder agent messages
- [graph_agent_artifacts.md](graph_agent_artifacts.md) - Large graph builder inputs such as Playwright codegen guidance

## Project Graph Invariant

The Project Graph is command-step based:

```text
graph_command_steps.before_step_id = command graph topology
graph_states.command_step_id = observed result of one command step
graph_states.node_id = URL/route grouping
project_graphs.start_command_step_id = canonical backend graph start
```

The model does not store source-of-truth action, request-summary, state-edge, node-edge, or start-node tables. State edges, node edges, leaves, paths, request summaries, href candidate edges, and visual start state/node data are service/API projections from the tables above.
