# Database table reference

| Table documentation | Short description | Platform role |
| --- | --- | --- |
| [`users`](tables/users.md) | Persistent authenticated user and optional local credential. | Identity root for authentication, user resolution, membership, and rate limiting. |
| [`workspace_users`](tables/workspace_users.md) | User role in an externally owned workspace. | Workspace authorization boundary for management and named policy checks. |
| [`pms_projects`](tables/pms_projects.md) | Project metadata, counters, archive state, and concurrency versions. | Root aggregate for every PMS resource and project-scoped operation. |
| [`project_users`](tables/project_users.md) | User role and membership source in a project. | Project authorization boundary and source for member/assignee data. |
| [`service_users`](tables/service_users.md) | Optional per-service role restriction for a project member. | Narrows project permissions for service-scoped authorization. |
| [`pms_agents`](tables/pms_agents.md) | Coordinator or worker configuration and lifecycle state. | Defines the project agent topology and configuration exposed by agent APIs. |
| [`pms_states`](tables/pms_states.md) | Ordered workflow state and project default marker. | Defines Kanban columns, workflow semantics, defaults, and completion grouping. |
| [`pms_work_items`](tables/pms_work_items.md) | Ordered Kanban card with workflow, dates, and optional epic. | Primary unit of board work and card-level planning. |
| [`pms_work_item_assignees`](tables/pms_work_item_assignees.md) | User assignment to a work item. | Connects project members to cards and powers assignee responses and filters. |
| [`pms_epics`](tables/pms_epics.md) | Ordered planning epic with workflow, dates, and progress inputs. | Groups work items into higher-level delivery outcomes. |
| [`pms_epic_assignees`](tables/pms_epic_assignees.md) | User assignment to an epic. | Connects project members to epics and powers assignee responses and filters. |
| [`pms_board_preferences`](tables/pms_board_preferences.md) | Per-user display and collapsed-column settings for a project board. | Persists each user’s board presentation state. |
