# Pipeline Versions Table

## Description
The `pipeline_versions` table stores immutable published snapshots of a pipeline draft. Each row captures the exact test-case structure that was published at a point in time so the platform can show version history, resolve the active version for launches, and support rollback without mutating the current draft. Once a version is referenced by run history, it becomes a durable historical artifact and must not be cascade-deleted with the live pipeline draft.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for each published version |
| pipeline_id | UUID | NULLABLE, FOREIGN KEY (pipelines.id) ON DELETE SET NULL, INDEX | - | Reference to the mutable pipeline draft that owns this version history while that draft still exists |
| version_number | INTEGER | NOT NULL, part of UNIQUE(pipeline_id, version_number) | - | Monotonic version number inside one pipeline history |
| is_active | BOOLEAN | NOT NULL | false | Marks which published version is currently used for launches |
| publish_note | TEXT | NULLABLE | - | Optional publish comment shown in version history |
| snapshot | JSONB | NOT NULL | - | Immutable snapshot of pipeline metadata, steps, links, assertions, dependencies, and variable reference metadata |
| snapshot_schema_version | INTEGER | NOT NULL | `1` | Version of the snapshot contract for forward-compatible deserialization |
| published_by_user_id | UUID | NULLABLE, FOREIGN KEY (users.id) ON DELETE SET NULL, INDEX | - | User who published the version |
| created_at | TIMESTAMP | NOT NULL | NOW() | Timestamp when the version was published |

## Relationships
- **Many-to-One**: Each version may reference one live pipeline through `pipeline_id`, but the link may become `null` after draft deletion
- **Many-to-One**: Each version may reference the publishing user through `published_by_user_id`
- **Logical One-to-One (active pointer)**: At most one version per pipeline should have `is_active = true`
- **One-to-Many**: One published version can be referenced by many `run_pipelines` launch-target records
- **One-to-Many**: One published version can be referenced by many `run_step_results` execution output records

## Purpose
This table is the publish-history layer for versioned test cases. The snapshot stores the immutable structure of the pipeline at publish time:

- pipeline metadata such as `code`, `name`, `priority`, and `tags`
- the step graph from `steps`, `steps_links`, and `assertions`
- prerequisite and follow-up pipeline relationships
- variable reference metadata without copying secret values

The active-version rule lets the platform answer two critical questions quickly:

- which version should be executed if the user clicks Run now
- which historical version should be shown or re-activated during rollback

The nullable `pipeline_id` link ensures that published history can outlive the live draft. If a pipeline is later removed from the active inventory, old version rows still remain available for run history resolution through their immutable snapshots and for step-level execution output through `run_step_results.pipeline_version_id`.

## Snapshot Content Rules
The `snapshot` JSONB field must serialize the publish-time state of the draft using a stable contract.

### Required snapshot sections
- `pipeline`:
  - draft metadata copied into the version snapshot, for example code, name, description, priority, tags, status, and other launch-relevant attributes
- `steps`:
  - ordered or indexed list of step definitions
  - step attributes required for rendering and execution preparation
- `steps_links`:
  - graph connections between steps
  - enough data to reconstruct the execution graph in read-only mode
- `assertions`:
  - assertion definitions attached to steps inside the snapshot
- `pre_pipelines` / `post_pipelines`:
  - pipeline dependencies captured at publish time
- `variables`:
  - variable reference manifest used by the snapshot
  - metadata needed for display and validation
  - no duplicated secret values

### Variable snapshot/reference rule
Published versions store a **reference manifest**, not a full copy of runtime variable values:
- secret values are never copied into the snapshot
- non-secret values are not pinned by default in this step
- the snapshot keeps enough metadata to show which variables the version depends on
- runtime execution resolves actual values from the current project variable set unless a later step adds value pinning

### Immutability rule
Once created, a `pipeline_versions` row must not be edited in place. Any draft change requires creation of a new version row.
