# Run Assertion Results Table

## Description
The `run_assertion_results` table stores persisted execution output for assertions evaluated during a run step. Each row belongs to one run and one step result, and captures the assertion status, payloads, errors, and execution timestamps used by the run results view.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for each assertion result record |
| run_id | UUID | FOREIGN KEY (runs.id) ON DELETE CASCADE, INDEX | - | Reference to the parent run |
| run_step_result_id | UUID | FOREIGN KEY (run_step_results.id) ON DELETE CASCADE, INDEX, part of UNIQUE(run_step_result_id, assertion_id) | - | Reference to the parent step result |
| assertion_id | UUID | NOT NULL, INDEX, part of UNIQUE(run_step_result_id, assertion_id) | - | Identifier of the assertion inside the published snapshot |
| assertion_name | VARCHAR(100) | NOT NULL | - | Assertion name copied for stable result display |
| status | VARCHAR(50) | NOT NULL, INDEX | `queued` | Assertion execution state: `queued`, `running`, `passed`, `failed`, or `skipped` |
| input | JSONB | NOT NULL | `{}` | Structured input payload used for assertion execution |
| output | JSONB | NOT NULL | `{}` | Structured output payload produced by assertion execution |
| error | JSONB | NULLABLE | - | Structured error payload captured when the assertion fails |
| started_at | TIMESTAMP | NULLABLE | - | Timestamp when assertion execution started |
| finished_at | TIMESTAMP | NULLABLE | - | Timestamp when assertion execution finished |
| created_at | TIMESTAMP | NOT NULL | NOW() | Timestamp when the assertion result row was created |

## Relationships
- **Many-to-One**: Belongs to a run via `run_id`
- **Many-to-One**: Belongs to a step result via `run_step_result_id`

## Purpose
This table is the assertion-level result store for real Playwright execution. It lets the run results endpoint nest assertion outcomes under each step result while preserving the assertion identifier and display name from the published snapshot.

The `assertion_id` value is stored as the snapshot assertion identifier. The result row is deleted when the parent run or step result is deleted, but it does not depend on the mutable live assertion record.
