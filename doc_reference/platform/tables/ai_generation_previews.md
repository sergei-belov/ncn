# AI Generation Previews Table

## Description
The `ai_generation_previews` table stores normalized candidate results produced by the AI-generation worker. A preview is the reviewable artifact shown to the user before anything is applied to live draft tables.

A preview may describe creation of a new draft pipeline, a patch of the current draft pipeline, a patch of one step, or an append-after-step graph fragment.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for the preview |
| session_id | UUID | NOT NULL, FK `ai_generation_sessions.id`, INDEX | - | Parent generation session |
| preview_kind | VARCHAR(40) | NOT NULL | - | Preview type such as `pipeline_draft_create`, `pipeline_draft_patch`, `step_patch`, `step_tail_patch` |
| status | VARCHAR(20) | NOT NULL, INDEX | `draft` | Preview lifecycle state |
| normalized_payload | JSONB | NOT NULL | `'{}'` | Generated graph payload used for review and apply |
| validation_report | JSONB | NOT NULL | `'{}'` | Validation warnings, fallback flags, and quality notes |
| ui_summary_payload | JSONB | NULLABLE | - | Optional compact summary optimized for preview cards |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |

## Relationships
- **Many-to-One**: Each preview belongs to one generation session through `session_id`
- **Many-to-One**: One session may reference one preview as `latest_preview_id`

## Purpose
The preview table is the safety boundary between AI output and the editable draft model. It allows QAi to:

- show generation results before save
- let the user edit generated content
- regenerate within the same session without losing old attempts
- apply only the selected preview into live draft tables

## Notes
- Only one preview per session should be `active` at a time.
- On regenerate, the previous active preview becomes `superseded`.
- Accepted previews remain immutable audit artifacts even though the resulting live draft may later change again.
- `normalized_payload` should include pipeline metadata, `steps`, `steps_links`, `assertions`, and `suggested_variables`.
- Secret values must never appear in `normalized_payload`.
