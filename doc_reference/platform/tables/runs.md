# Runs Table

## Description
The `runs` table stores project-wide run history records for pipeline launches, tag-based launches, and mixed launch targets. Each row represents one queued or executed run with lifecycle status, targeting metadata, execution mode, and audit timestamps that the Runs API uses for listing, filtering, detail retrieval, and execution result lookup.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for each run record |
| project_id | UUID | FOREIGN KEY (projects.id) ON DELETE CASCADE, INDEX | - | Reference to the project that owns the run |
| title | VARCHAR(120) | NOT NULL | - | Human-readable run title shown in the runs history UI |
| status | VARCHAR(50) | NOT NULL, INDEX | `queued` | Lifecycle state such as `queued`, `running`, `completed`, `failed`, or `canceled` |
| target_type | VARCHAR(50) | NOT NULL | - | How the run target was selected: `pipelines`, `tags`, or `mixed` |
| execution_mode | VARCHAR(50) | NOT NULL | `record_only` | Execution mode such as `record_only` or `playwright`; normal run creation now stores `playwright` |
| tags | ARRAY(VARCHAR) | NOT NULL | `{}` | Tag selectors attached to the run for filtering and future suite-style launches |
| requested_by_user_id | UUID | FOREIGN KEY (users.id) ON DELETE CASCADE, INDEX | - | Reference to the user who created the run |
| message | VARCHAR(500) | NULLABLE | - | Optional informational message returned to the UI after the run is queued |
| started_at | TIMESTAMP | NULLABLE | - | Execution start timestamp, if the run has started |
| finished_at | TIMESTAMP | NULLABLE | - | Execution finish timestamp, if the run has ended |
| created_at | TIMESTAMP | NOT NULL, INDEX | NOW() | Timestamp when the run record was created |

## Relationships
- **Many-to-One**: Belongs to a project via `project_id`
- **Many-to-One**: Belongs to a user via `requested_by_user_id`
- **One-to-Many**: Can have multiple linked pipeline records in `run_pipelines`
- **One-to-Many**: Can have multiple step result records in `run_step_results`
- **One-to-Many**: Can have multiple assertion result records in `run_assertion_results`
- **Many-to-Many**: Connects to `pipelines` through the `run_pipelines` junction table

## Purpose
This table is the central history store for project launches. The backend queries it by `project_id`, title search, status, tag overlap, sorting, and pagination in `backend/api/db/runs.py`, while the `run_pipelines` table carries the selected pipeline set and per-pipeline execution state for each run. Together they allow the project runs screen to show one history feed regardless of whether a launch came from a single pipeline, multiple pipelines, or tag-based targeting.

In the versioned test-case model introduced by step 04, each run is linked to concrete published pipeline versions through `run_pipelines.pipeline_version_id`. The top-level `runs` row remains the container for lifecycle state, execution mode, queue message, and audit timestamps, while version-specific target links live in the run-to-pipeline junction records. The optional live `pipeline_id` reference may be nulled later without affecting historical run resolution.

Run creation now writes `execution_mode: playwright` and the message `Playwright execution queued.` before scheduling background execution. The legacy `record_only` value remains part of the documented enum for historical rows and compatibility.
