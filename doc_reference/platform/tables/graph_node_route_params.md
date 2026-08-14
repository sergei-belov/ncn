# Graph Node Route Params Table

## Description
The `graph_node_route_params` table stores editable parameter metadata for dynamic URL segments of a graph node. These records support deterministic URL normalization and let users fix parameter names or segment regex rules.

## Schema

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid4() | Unique identifier for the route parameter |
| node_id | UUID | NOT NULL, FK `graph_nodes.id`, INDEX | - | Owning graph node |
| segment_index | INTEGER | NOT NULL | - | Zero-based path segment index |
| raw_segment | TEXT | NOT NULL | - | Concrete URL segment before normalization |
| parameter_name | TEXT | NOT NULL | - | Display parameter name such as `project_id` |
| regex_pattern | TEXT | NOT NULL | - | Segment-level regex such as `[0-9]+` |
| detected_type | TEXT | NULLABLE | - | Detected kind: `integer`, `uuid`, or `custom` |
| is_auto_detected | BOOLEAN | NOT NULL | true | Whether the parameter was detected automatically |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |

## Relationships
- **Many-to-One**: Each route parameter belongs to one graph node through `node_id`

## Purpose
The table stores user-editable parameter metadata used to compose `graph_nodes.route_regex_pattern`. It keeps normalization explainable in the UI while preserving backend-owned route matching.

## Notes
- The final node identity still lives in `graph_nodes.route_regex_pattern`.
- Recommended built-in segment regexes are `[0-9]+` for integers and `[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}` for UUIDs.
- The common uniqueness rule is `(node_id, segment_index)`.
