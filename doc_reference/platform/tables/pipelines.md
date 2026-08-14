# Pipelines Table

## Description
The `pipelines` table stores the mutable draft head for each test case inside a project. It contains authoring metadata, operational status fields used by the list/editor UI, and the project relationship for the editable graph. Published immutable snapshots are stored separately in [`pipeline_versions.md`](pipeline_versions.md).

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for each pipeline draft |
| code | VARCHAR(20) | NOT NULL, UNIQUE, INDEX | - | Stable human-readable test-case code such as `TC-001` |
| name | VARCHAR(100) | NOT NULL | - | Draft name shown in the pipelines list and editor |
| description | TEXT | NULLABLE | - | Optional draft description |
| priority | VARCHAR(20) | NOT NULL | `medium` | Priority enum used by list filters and badges |
| tags | ARRAY(VARCHAR(50)) | NOT NULL | `{}` | Project-scoped tags for grouping and filtering pipelines |
| status | VARCHAR(20) | NOT NULL | `pending` | Current draft status used in the pipeline inventory UI |
| actuality | VARCHAR(20) | NOT NULL | `actual` | Whether the test case is current or requires changes |
| project_id | UUID | FOREIGN KEY (projects.id) ON DELETE CASCADE, INDEX | - | Reference to the owning project |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp for the pipeline record |
| updated_at | TIMESTAMP | NULLABLE | NOW() | Last draft metadata update timestamp |
| last_run_at | TIMESTAMP | NULLABLE | - | Timestamp of the most recent run registered for this pipeline family |
| last_run_status | VARCHAR(20) | NULLABLE | - | Last known run result summary for list badges and filters |

## Relationships
- **Many-to-One**: Each pipeline belongs to one project through `project_id`
- **One-to-Many**: Each pipeline draft contains multiple steps through the `steps` table
- **Self-referencing**: Pipelines connect to other pipelines through `pre_pipelines` and `post_pipelines`
- **One-to-Many**: A pipeline draft can have many immutable published snapshots in `pipeline_versions`
- **Many-to-Many**: Runs target pipelines through the `run_pipelines` junction table

## Purpose
This table is the editable authoring surface for a test case. Users change the draft here through the pipeline editor, while step 04 introduces a separate publish flow that serializes the current draft into immutable version snapshots. That split keeps authoring fast while giving the platform a stable execution target, rollback path, and publish history.

Because published versions and runs are historical artifacts, deletion of the live draft must not cascade into `pipeline_versions` or `run_pipelines`. History is preserved through immutable version snapshots and version-aware run links.
