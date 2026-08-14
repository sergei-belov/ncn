# Projects Table

## Description
The `projects` table represents top-level containers for organizing test automation efforts within the QAi platform. Each project corresponds to a specific web application being tested.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier for each project |
| name | VARCHAR(100) | NOT NULL | - | Name of the project (3-100 characters) |
| description | TEXT | NULLABLE | - | Optional description providing context about the project |
| created_at | TIMESTAMP | NOT NULL | NOW() | Timestamp when the project was created |

## Relationships
- **One-to-Many**: A project can contain multiple pipelines through the `pipelines` table
- **Many-to-Many**: A project can be associated with multiple users through the `project_users` table
- **One-to-Many**: A project can have multiple steps through the `steps` table via pipelines

## Purpose
The projects table serves as the central organizational unit for test automation, grouping related pipelines, flows, and configurations for a specific web application under test.