# Step 06 — AI-assisted Test Case Generation

## Goal
Introduce AI-assisted creation and refinement of test cases based on the dev mechanics from `/backend/api/dev/test.py`, but move that logic into a production-oriented backend architecture with Kafka, LangGraph, reusable LLM services, preview-first UX, and explicit audit storage.

## Product Result
QAi gains a core “smart” capability: generation of one draft pipeline from a description, and refinement of the current draft or a selected step through agent-assisted preview flows.

## Final Scope Decisions
- Generation always creates a **preview first**.
- The user can **accept**, **edit**, **reject**, or **regenerate**.
- Accept creates or updates **draft data only**.
- One session may have multiple previews, but only one latest active preview.
- Regenerate marks the old preview as `superseded` and the new one as `active`.
- First implementation stage is limited to **one generated pipeline per session**.
- Step-level generation may only patch the target step or append steps after it.
- Previous steps are read-only context and may not be changed.
- For `append_after_step`, the link from the target step to the first generated step is created automatically.
- The UI shows a shortened trace; the DB stores the full trace.
- `messages` endpoint uses `after_seq`, not offset.
- Preview editing includes `suggested_variables`.

## Backend Architecture Decisions

### Session-first orchestration
A generation request creates `ai_generation_sessions`, not draft rows in `pipelines`.

### Thin Kafka envelope
Kafka task payload contains routing and ownership ids only:
- `session_id`
- `project_id`
- `pipeline_id`
- `step_id`
- `mode`
- `requested_by_user_id`

The worker loads the rest of the context from DB and tools.

### LangGraph chain
Subagents:
1. Planner
2. QAi Agent
3. QAi Validator

### Backend-owned apply
Only backend managers write into `pipelines`, `steps`, `steps_links`, and `assertions` after explicit accept.

## New Database Tables
- `ai_generation_sessions`
- `ai_generation_messages`
- `ai_generation_previews`

## New Kafka Topics
- `qai.ai.cmd.generation-request.v1`
- `qai.ai.fct.generation-progress.v1`
- `qai.ai.fct.generation-result.v1`

## API Surface
- `POST /api/qai/v1/projects/{project_id}/ai/generations`
- `GET /api/qai/v1/projects/{project_id}/ai/generations/{session_id}`
- `GET /api/qai/v1/projects/{project_id}/ai/generations/{session_id}/messages`
- `GET /api/qai/v1/projects/{project_id}/ai/generations/{session_id}/previews/{preview_id}`
- `PATCH /api/qai/v1/projects/{project_id}/ai/generations/{session_id}/previews/{preview_id}`
- `POST /api/qai/v1/projects/{project_id}/ai/generations/{session_id}/accept`
- `POST /api/qai/v1/projects/{project_id}/ai/generations/{session_id}/reject`

## Frontend Scope
- Pipelines screen gets project-level AI generation entry and preview review sidebar
- Pipeline Detail screen gets:
  - draft-level AI refinement action
  - step-level patch action
  - step-level append-after-step action
- Preview must always be shown before save
- Shortened trace is polled from the messages endpoint while generation is active

## Documentation Updates Included
- `docs/spec.md`
- `docs/platform/README.md`
- `docs/platform/intro.md`
- `docs/platform/defenitions.md`
- `docs/platform/architecture/README.md`
- `docs/platform/architecture/ai_generation.md`
- `docs/platform/tables/README.md`
- `docs/platform/tables/ai_generation_sessions.md`
- `docs/platform/tables/ai_generation_messages.md`
- `docs/platform/tables/ai_generation_previews.md`
- `docs/platform/ui/README.md`
- `docs/platform/ui/pages/PipelinesScreen.md`
- `docs/platform/ui/pages/PipelineDetailScreen.md`
- `docs/templates/page.md`
- `docs/templates/table.md`

## Notes for Implementation
- The backend should extract reusable generation logic from `/backend/api/dev/test.py` and move it into managers/services.
- Agent MUST write prompts one by one for test case generation, for each subagent.
- `/backend/api/services/llm` should be upgraded to support structured generation, retries, timeouts, prompt versioning, and model profiles.
- Validation must support partial preview fallback when the model returns an incomplete but still reviewable response.
- Secret values must not be exposed to the generation worker or appear in preview payloads.
