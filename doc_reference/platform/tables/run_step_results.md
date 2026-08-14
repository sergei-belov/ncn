# Run Step Results Table

## Description
The `run_step_results` table stores persisted execution output for each step executed inside a run pipeline target. Each row belongs to one project run, one selected run pipeline, and the published pipeline version that supplied the immutable step snapshot.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for each step result record |
| run_id | UUID | FOREIGN KEY (runs.id) ON DELETE CASCADE, INDEX | - | Reference to the parent run |
| run_pipeline_id | UUID | FOREIGN KEY (run_pipelines.id) ON DELETE CASCADE, INDEX, part of UNIQUE(run_pipeline_id, step_id) | - | Reference to the selected pipeline execution inside the run |
| pipeline_version_id | UUID | FOREIGN KEY (pipeline_versions.id) ON DELETE RESTRICT, INDEX | - | Reference to the published pipeline version that supplied this step |
| step_id | UUID | NOT NULL, INDEX, part of UNIQUE(run_pipeline_id, step_id) | - | Identifier of the step inside the published snapshot |
| step_name | VARCHAR(100) | NOT NULL | - | Step name copied for stable result display |
| step_index | INTEGER | NOT NULL | - | Execution order index for the step within the run pipeline |
| status | VARCHAR(50) | NOT NULL, INDEX | `queued` | Step execution state: `queued`, `running`, `passed`, `failed`, or `skipped` |
| input | JSONB | NOT NULL | `{}` | Structured input payload used for step execution |
| output | JSONB | NOT NULL | `{}` | Structured output payload produced by step execution |
| logs | JSONB | NOT NULL | `[]` | Ordered structured log entries captured while executing the step |
| error | JSONB | NULLABLE | - | Structured error payload captured when the step fails |
| started_at | TIMESTAMP | NULLABLE | - | Timestamp when step execution started |
| finished_at | TIMESTAMP | NULLABLE | - | Timestamp when step execution finished |
| created_at | TIMESTAMP | NOT NULL | NOW() | Timestamp when the step result row was created |

## Relationships
- **Many-to-One**: Belongs to a run via `run_id`
- **Many-to-One**: Belongs to a run pipeline target via `run_pipeline_id`
- **Many-to-One**: Belongs to a published pipeline version via `pipeline_version_id`
- **One-to-Many**: Can have multiple assertion result rows in `run_assertion_results`

## Purpose
This table is the step-level result store for real Playwright execution. It lets the run results endpoint return execution order, status, timing, input/output payloads, logs, and errors for every step under a selected published pipeline version.

The `step_id` value is stored as the identifier from the published snapshot, not as a cascading live draft dependency. This keeps historical execution output readable even if the mutable draft step changes or the live pipeline draft is later removed.
