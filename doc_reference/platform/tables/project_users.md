# Project Users Table

## Description
The `project_users` table manages the many-to-many relationship between users and projects, defining user roles and permissions within each project.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier for each project-user association |
| project_id | UUID | FOREIGN KEY (projects.id) ON DELETE CASCADE, INDEX | - | Reference to the project |
| user_id | UUID | FOREIGN KEY (users.id) ON DELETE CASCADE, INDEX | - | Reference to the user |
| role | VARCHAR(20) | NOT NULL | - | User's role within the project (e.g., owner, admin, user) |

## Relationships
- **Many-to-One**: References the `projects` table via `project_id`
- **Many-to-One**: References the `users` table via `user_id`

## Purpose
This table enables role-based access control, allowing different users to have varying levels of access and permissions within specific projects.