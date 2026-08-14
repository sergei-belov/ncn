# Database Methods Reference

Use this when adding or changing `backend/api/db/*.py` repositories or manager code that calls repositories.

This reference embeds the generic repository behavior needed for backend implementation.

## Generic Repository Shape

```python
class WidgetsDb(
    BaseDatabaseGeneric[
        sqlalchemy.Widget,
        UUID,
        pydantic.WidgetDTO,
        pydantic.WidgetCreateDTO,
        pydantic.WidgetUpdateFieldsDTO,
    ]
):
    database = Services.database

    _table = sqlalchemy.Widget
    _id = UUID
    _model = pydantic.WidgetDTO
    _model_create = pydantic.WidgetCreateDTO
    _model_update = pydantic.WidgetUpdateFieldsDTO
```

Set the five generic attributes and register the instance in `backend/api/db/db.py`.

## Prefer Generic Methods

Use these from managers before adding repository-specific helpers:

- `create(model, session=None, return_query=False, mode="python")`
- `bulk_create(models, session=None, return_query=False, mode="python")`
- `get(id=None, session=None, return_query=False, **filters)`
- `get_by_ids(ids, session=None, return_query=False, **filters)`
- `get_list(session=None, return_query=False, **filters)`
- `get_paginated_list(queries, search_column=None, session=None, filters_=None, filter_columns=None, return_query=False, **raw_filters)`
- `get_count(search=None, search_column=None, filters_=None, filter_columns=None, session=None, return_query=False, **raw_filters)`
- `update(id, data, updated_by_id=None, session=None, return_query=False, mode="python", **filters)`
- `bulk_update(ids, data, session=None, updated_by_id=None, return_query=False, mode="python", **filters)`
- `upsert(data, update_fields=None, session=None, conflict_fields=None, return_query=False, mode="python", on_conflict="update")`
- `bulk_upsert(data, conflict_fields=None, update_fields=None, session=None, return_query=False, mode="python", on_conflict="update")`
- `delete(id, session=None, return_query=False, **filters)`
- `delete_many(ids, session=None, return_query=False, **filters)`
- `delete_list(session=None, return_query=False, **filters)`

`truncate(session=None, return_query=False)` exists, but use it only for an explicitly requested whole-table cleanup pattern and follow neighboring code.

Filter kwargs must match real SQLAlchemy table fields. Scalar values become equality checks; list values become `IN` filters. Unknown filter fields raise `ValueError`.

## Manager Call Examples

Simple lookup with authorization/project scope:

```python
async with Services.database.session() as session:
    widget = await Database.widgets.get(
        id=widget_id,
        project_id=user.project_id,
        session=session,
    )
```

Paginated list and count with matching filters:

```python
async with Services.database.session() as session:
    total_count = await Database.widgets.get_count(
        search=queries.search,
        search_column=sqlalchemy.Widget.name,
        project_id=user.project_id,
        session=session,
    )
    widgets = await Database.widgets.get_paginated_list(
        queries=queries,
        search_column=sqlalchemy.Widget.name,
        project_id=user.project_id,
        session=session,
    )
```

PATCH/update with sparse fields:

```python
update_dto = pydantic.WidgetUpdateFieldsDTO(**data.model_dump(exclude_unset=True))
updated = await Database.widgets.update(
    id=widget_id,
    data=update_dto,
    updated_by_id=user.user_id,
    project_id=user.project_id,
    session=session,
)
```

Upsert by a natural key:

```python
widget = await Database.widgets.upsert(
    data=widget_dto,
    conflict_fields={"external_id"},
    update_fields={"name", "description", "updated_at"},
    session=session,
)
```

Use `return_query=True` only when composing a larger SQL query or CTE; otherwise let the repository execute and validate models.

## Custom Repository Methods

Add a custom method only for a query shape the generic API cannot express cleanly, such as:

- joins across multiple tables
- aggregations or grouped results
- tuple filters or CTE-heavy logic
- custom result DTOs assembled from several tables
- special ordering or result shaping that belongs in SQL

Example custom query with joins, tuple filters, early empty-input handling, optional execution, and DTO result shaping:

```python
async def get_by_external_tags(
    self,
    external_tags: list[tuple[UUID, str]],
    session: AsyncSession | None = None,
    return_query: bool = False,
) -> list[pydantic.BaseTagExternalUnitDTO] | sa.CTE:
    if not external_tags:
        return []

    unique_external_tags = list(dict.fromkeys(external_tags))
    source_tag_pairs = [(str(source_id), tag_name) for source_id, tag_name in unique_external_tags]

    query = (
        sa.select(
            sqlalchemy.SourceTag.source_id.label("source_id"),
            sqlalchemy.SourceTag.name.label("tag_name"),
            sqlalchemy.BaseTag,
        )
        .select_from(sqlalchemy.SourceTag)
        .join(sqlalchemy.TagMapping, sqlalchemy.TagMapping.source_tag_id == sqlalchemy.SourceTag.id)
        .join(sqlalchemy.BaseTag, sqlalchemy.BaseTag.id == sqlalchemy.TagMapping.base_tag_id)
        .where(sa.tuple_(sqlalchemy.SourceTag.source_id, sqlalchemy.SourceTag.name).in_(source_tag_pairs))
    )

    if return_query:
        return query.cte()

    if session:
        result = await session.execute(query)
    else:
        async with self.database.session() as session:
            result = await session.execute(query)

    return [
        pydantic.BaseTagExternalUnitDTO(
            source_id=row.source_id,
            tag_name=row.tag_name,
            base_tag=pydantic.BaseTagDTO.model_validate(row[2]),
        )
        for row in result.fetchall()
    ]
```

For custom methods:

- accept `session: AsyncSession | None = None` unless the surrounding code always owns the session
- support `return_query: bool = False` when the method may be composed
- return `[]` early for empty list inputs
- deduplicate input pairs when building tuple filters
- validate returned rows into DTOs explicitly
- keep business decisions and authorization in managers
