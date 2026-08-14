# Graph Agent Artifacts Table

## Description
The `graph_agent_artifacts` table stores optional large inputs or artifacts attached to a graph builder agent session. The main Step 07 artifact is Playwright codegen guidance.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for the graph agent artifact |
| session_id | UUID | NOT NULL, FK `graph_agent_sessions.id`, INDEX | - | Parent graph agent session |
| artifact_type | TEXT | NOT NULL | - | Artifact type: `playwright_codegen`, `html_snapshot`, `trace`, or `other` |
| content_compressed | BYTEA | NULLABLE | - | Optional compressed artifact content |
| content_hash | TEXT | NULLABLE | - | Optional hash for deduplication or integrity checks |
| metadata | JSONB | NOT NULL | `'{}'` | Additional artifact metadata |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |

## Relationships
- **Many-to-One**: Each artifact belongs to one graph agent session through `session_id`

## Purpose
Artifacts let the graph builder agent receive larger context such as pasted or uploaded Playwright codegen without executing it directly. The artifact is guidance for agent navigation and graph mutation, not a pipeline or test script.

## Notes
- Uploaded Playwright codegen must not be executed directly by the platform.
- Codegen guidance must not create pipelines or test cases in Step 07.
