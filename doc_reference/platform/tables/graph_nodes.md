# Graph Nodes Table

## Description
The `graph_nodes` table stores normalized tested-application pages, routes, or screens. A node groups states by URL normalization and route regex identity.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique graph node identifier |
| project_graph_id | UUID | NOT NULL, FK `project_graphs.id`, INDEX | - | Owning project graph |
| raw_url | TEXT | NOT NULL | - | Original URL used to create or observe the node |
| normalized_url | TEXT | NOT NULL | - | Human-readable normalized route template |
| route_regex_pattern | TEXT | NOT NULL | - | Full regex used for backend URL matching |
| url_path | TEXT | NOT NULL | - | URL path without query string |
| url_query | JSONB | NOT NULL | `'{}'` | Normalized query parameters retained for identity/display |
| title | TEXT | NULLABLE | - | Optional node title |
| description | TEXT | NULLABLE | - | Optional node description |
| source | TEXT | NOT NULL | - | Node source: `manual`, `agent`, `href`, `system`, or `import` |
| normalization_settings | JSONB | NOT NULL | `'{}'` | Settings and auto-detected route params used to normalize the URL |
| position_x | FLOAT | NULLABLE | - | Optional canvas X position |
| position_y | FLOAT | NULLABLE | - | Optional canvas Y position |
| metadata | JSONB | NOT NULL | `'{}'` | Additional node metadata |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |
| created_by_user_id | UUID | NULLABLE, FK `users.id` | - | User who created the node when applicable |
| updated_by_user_id | UUID | NULLABLE, FK `users.id` | - | User who last updated node metadata |

## Relationships
- **Many-to-One**: Each node belongs to one project graph.
- **One-to-Many**: A node has route params in `graph_node_route_params`.
- **One-to-Many**: A node has observed states in `graph_states`.

## Identity Rule
Node identity is based on `project_graph_id + route_regex_pattern`. Matching by regex prevents duplicate nodes for dynamic routes such as:

```text
/projects/123/users/456/settings
/projects/789/users/111/settings
```

when both match the same route pattern.

## Node Edges
Node edges are not stored as a source table. They are derived from command steps and states:

```text
step.before_step_id -> step.id
source_state.command_step_id = step.before_step_id
target_state.command_step_id = step.id
source_node = source_state.node_id
target_node = target_state.node_id
```

Candidate node edges can also be calculated from `graph_states.hrefs`, but only executed command steps confirm canonical reachability.

## Deletion Rules
Command deletion can remove nodes only after produced states are deleted. A node is deleted when all of its states were removed by the command-subtree cascade and no remaining `graph_states` row in the same project graph references it.

Nodes with remaining states are kept, even when one command branch that reached the node was deleted. Parent commands and sibling branches continue to derive node edges through their remaining states.
