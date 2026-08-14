# Variables Table

## Description
The `variables` table stores project-level variables and secrets used across pipelines and step authoring flows. In the current prototype, each record belongs to exactly one project and is exposed through a typed API contract while still reusing the existing JSON column in the database.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier for each variable |
| name | VARCHAR(100) | NOT NULL | - | Project-scoped variable key such as `BASE_URL` or `LOGIN_USER` |
| description | TEXT | NULLABLE | - | Optional description shown in the UI |
| value | JSON / JSONB | NOT NULL | - | Typed payload envelope, for example `{ "type": "string", "value": "https://demo.example.com" }` |
| secret | BOOLEAN | NOT NULL | false | Compatibility flag used to mark masked/secret values |
| project_id | UUID | FOREIGN KEY (projects.id) ON DELETE CASCADE, INDEX | - | Reference to the owning project |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |

## Relationships
- **Many-to-One**: Each variable belongs to one project through `project_id`
- **One-to-Many (logical usage)**: Variables can be referenced by many pipeline steps through placeholder syntax such as `{{BASE_URL}}`

## Purpose
The table enables reusable test configuration at the project level. It supports four public prototype types: `string`, `number`, `integer`, and `secret`. The database schema is intentionally unchanged in this step; typed values are wrapped in the JSON payload so the API can evolve without introducing a migration during prototype stabilization.
