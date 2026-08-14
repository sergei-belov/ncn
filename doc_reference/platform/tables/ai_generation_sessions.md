# AI Generation Sessions Table

## Description
The `ai_generation_sessions` table stores one asynchronous AI-assisted generation request. A session belongs to a project and optionally targets one pipeline or one step. It tracks lifecycle state, source input, options, the latest active preview, shortened progress information for UI polling, and the final apply result once the user accepts a preview.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for the generation session |
| project_id | UUID | NOT NULL, FK `projects.id`, INDEX | - | Owning project |
| pipeline_id | UUID | NULLABLE, FK `pipelines.id`, INDEX | - | Optional pipeline target for pipeline-level refinement |
| step_id | UUID | NULLABLE, FK `steps.id`, INDEX | - | Optional step target for step-level generation |
| created_by_user_id | UUID | NOT NULL, FK `users.id`, INDEX | - | User who started the session |
| mode | VARCHAR(50) | NOT NULL, INDEX | - | Generation mode such as `description_to_pipeline`, `patch_pipeline_draft`, `patch_step`, `append_after_step` |
| target_scope | VARCHAR(20) | NOT NULL | - | High-level scope such as `project`, `pipeline`, `step` |
| status | VARCHAR(30) | NOT NULL, INDEX | `created` | Current lifecycle status |
| input_payload | JSONB | NOT NULL | `'{}'` | Original user request payload |
| options_payload | JSONB | NOT NULL | `'{}'` | Generation options and internal switches |
| latest_preview_id | UUID | NULLABLE, FK `ai_generation_previews.id` | - | Latest active preview visible to the user |
| short_trace_payload | JSONB | NULLABLE | - | Small UI-friendly summary of progress and warnings |
| error_payload | JSONB | NULLABLE | - | Error information for failed sessions |
| accepted_result_payload | JSONB | NULLABLE | - | Summary of created/updated draft entities after accept |
| started_at | TIMESTAMP | NULLABLE | - | Time when worker processing actually started |
| finished_at | TIMESTAMP | NULLABLE | - | Time when the session reached a terminal state |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last session update timestamp |

## Relationships
- **Many-to-One**: Each generation session belongs to one project through `project_id`
- **Many-to-One**: A session may reference one pipeline draft through `pipeline_id`
- **Many-to-One**: A session may reference one step through `step_id`
- **Many-to-One**: A session is created by one user through `created_by_user_id`
- **One-to-Many**: A session has many trace records in `ai_generation_messages`
- **One-to-Many**: A session may have many previews in `ai_generation_previews`
- **Many-to-One**: `latest_preview_id` points to the preview currently shown in the UI

## Purpose
This table is the orchestration root for Step 06. It gives the backend, worker, and UI one stable record to track while generation runs asynchronously through Kafka and LangGraph.

It intentionally stores only orchestration-level state, not the full generated graph. Generated graph content lives in `ai_generation_previews`, while detailed reasoning and tool traces live in `ai_generation_messages`.

## Notes
- A session may produce many previews over time, but only one preview is the latest active preview.
- Accept updates `accepted_result_payload` and does not auto-publish a pipeline version.
- Deleting a pipeline draft later should not destroy the historical session record if the project-level audit policy requires retention; final FK delete behavior should be chosen to match retention policy.
- Common indexes: `(project_id, created_at DESC)`, `(status, updated_at DESC)`, `(pipeline_id, created_at DESC)`, `(step_id, created_at DESC)`.
