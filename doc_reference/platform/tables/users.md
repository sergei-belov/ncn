# Users Table

## Description
The `users` table stores information about application users who can access the QAi platform. This table manages user accounts with authentication details.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | Unique identifier for each user |
| email | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | - | User's email address used for login |
| name | VARCHAR(100) | NOT NULL | - | User's display name |
| password | VARCHAR | NULLABLE | - | Hashed password for authentication |
| created_at | TIMESTAMP | NOT NULL | NOW() | Timestamp when the user account was created |

## Relationships
- **One-to-Many**: A user can be associated with multiple projects through the `project_users` table

## Purpose
This table serves as the foundation for user authentication and authorization within the QAi platform, allowing the system to manage user accounts and control access to projects and resources.