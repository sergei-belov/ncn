# Run Pipelines Table

## Description
The `run_pipelines` table stores the junction records between a project run, the targeted pipeline family, and the exact published pipeline version used for that launch. It also carries the execution state for each selected pipeline inside a run, so a multi-pipeline run can show partial progress and per-pipeline failures.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for each run-to-pipeline link |
| run_id | UUID | FOREIGN KEY (runs.id) ON DELETE CASCADE, INDEX, part of UNIQUE(run_id, pipeline_version_id) | - | Reference to the parent run record |
| pipeline_id | UUID | NULLABLE, FOREIGN KEY (pipelines.id) ON DELETE SET NULL, INDEX | - | Optional reference to the live pipeline family, kept only while the draft still exists |
| pipeline_version_id | UUID | FOREIGN KEY (pipeline_versions.id) ON DELETE RESTRICT, INDEX, part of UNIQUE(run_id, pipeline_version_id) | - | Mandatory reference to the concrete published version resolved for this pipeline when the run was created |
| status | VARCHAR(50) | NOT NULL, INDEX | `queued` | Per-pipeline execution state: `queued`, `running`, `passed`, `failed`, or `skipped` |
| message | VARCHAR(500) | NULLABLE | - | Optional per-pipeline execution message returned to the UI |
| error | JSON | NULLABLE | - | Structured error payload captured for this pipeline execution |
| started_at | TIMESTAMP | NULLABLE | - | Timestamp when this pipeline execution started |
| finished_at | TIMESTAMP | NULLABLE | - | Timestamp when this pipeline execution finished |

## Relationships
- **Many-to-One**: Belongs to a run via `run_id`
- **Many-to-One**: May reference a live pipeline via `pipeline_id`, but that link may become `null`
- **Many-to-One**: Belongs to a published pipeline version via `pipeline_version_id`; this is the historical source of truth
- **One-to-Many**: Can have multiple step result rows in `run_step_results`
- **Many-to-Many**: Implements the logical many-to-many relationship between `runs` and `pipelines`, while preserving the exact launched version

## Purpose
This table is the explicit persistence layer for version-aware run history. When a run is created, the backend creates one link row per selected pipeline and stores:

- which run was created
- which pipeline family participated, if the live draft still exists
- which concrete `pipeline_version_id` was resolved at launch time
- the execution state, message, error payload, and timestamps for that pipeline target

That makes the relationship between a run and a published version durable in storage, so the runs UI can safely show stable history such as `TC-001 v3` even if a newer version becomes active later or the live pipeline draft is removed.

The top-level `runs.status` summarizes the overall run, while `run_pipelines.status` tracks the status of each selected published version. This distinction matters for multi-pipeline launches where one target may fail or be skipped while another target has already passed.
