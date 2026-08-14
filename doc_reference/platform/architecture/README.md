# Architecture Documentation

This directory contains cross-cutting architecture documents that describe flows spanning several subsystems.

## Available Documents
- [ai_generation.md](ai_generation.md) - Step 06 architecture for AI-assisted test-case generation, including Kafka topics, LangGraph worker flow, API contracts, preview lifecycle, and database responsibilities.
- [project_graph.md](project_graph.md) - Step 07 architecture for the project-level Graph module, including URL normalization, command-step graph topology, observed states, href candidates, request diffs, recovery, and graph builder agent boundaries.

## Usage Rules
- Keep architecture documents aligned with `../../spec.md`.
- Use these documents for subsystem boundaries, async flows, message schemas, and component responsibilities.
- Keep UI-only behavior in `../ui/pages/...` and table details in `../tables/...`.
