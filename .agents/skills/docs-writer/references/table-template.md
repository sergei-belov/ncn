# Database Table Documentation Template

Adapt this structure to the project's database and conventions. Omit sections with no relevant information.

```md
# `[table_name]`

## Purpose

[One or two sentences describing what one row represents and why the table exists.]

## Schema

| Column | Type | Constraints | Default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | [type] | [primary key, nullability] | [verified default or —] | [meaning] |
| `[column]` | [type] | [constraints] | [default or —] | [meaning] |

## Relationships

- `[column]` -> `[table.column]`: [cardinality and delete/update behavior]

## Indexes and rules

- `[index or constraint]`: [purpose or invariant]

## Used by

- [Feature, service, event, or query that depends on the table]
```

Keep the document concise:

- Do not repeat the purpose after the schema.
- Prefer database-native type names and exact constraint names.
- Distinguish a missing default from `NULL`.
- Include indexes, triggers, partitioning, retention, or row-level security only when present and relevant.
- Verify every schema fact from an authoritative source; never infer constraints from column names.
