# Pre-Pipelines Table

## Description
The `pre_pipelines` table defines dependencies between pipelines by specifying which pipelines should run before others as prerequisites. This creates ordered execution chains where certain pipelines must run before the main pipeline.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier for each relationship |
| pipeline_id | UUID | FOREIGN KEY (pipelines.id) ON DELETE CASCADE, INDEX | - | ID of the pipeline that requires a prerequisite |
| linked_pipeline_id | UUID | FOREIGN KEY (pipelines.id) ON DELETE CASCADE, INDEX | - | ID of the pipeline that acts as a prerequisite |

## Relationships
- **Many-to-One**: References the `pipelines` table twice - once for the main pipeline and once for the prerequisite pipeline

## Purpose
This table enables complex workflow orchestration by allowing pipelines to have prerequisite dependencies, ensuring that setup or preparation steps run before dependent pipelines execute.

## UI API Mapping
The Pipeline Detail redactor exposes records from this table through the `connected-pipelines` API with `type: pre`.

# Post-Pipelines Table

## Description
The `post_pipelines` table defines cleanup or follow-up actions by specifying which pipelines should run after others complete. This creates ordered execution chains where certain pipelines execute after the main pipeline finishes.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier for each relationship |
| pipeline_id | UUID | FOREIGN KEY (pipelines.id) ON DELETE CASCADE, INDEX | - | ID of the pipeline after which another pipeline should run |
| linked_pipeline_id | UUID | FOREIGN KEY (pipelines.id) ON DELETE CASCADE, INDEX | - | ID of the pipeline that runs as a follow-up action |

## Relationships
- **Many-to-One**: References the `pipelines` table twice - once for the main pipeline and once for the follow-up pipeline

## Purpose
This table enables complex workflow orchestration by allowing pipelines to have follow-up actions, ensuring that cleanup or verification steps run after the main pipeline completes.

## UI API Mapping
The Pipeline Detail redactor exposes records from this table through the `connected-pipelines` API with `type: post`.
