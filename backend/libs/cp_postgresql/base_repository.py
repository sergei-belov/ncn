import logging
from functools import wraps
from typing import (
    Any,
    Sequence,
)

import sqlalchemy as sa
from pydantic import (
    BaseModel,
    TypeAdapter,
)

from libs.cp_common.models.enum import SortOrder
from libs.cp_postgresql.models.pydantic.filters import (
    BaseFilter,
    FilterProtocol,
)
from libs.cp_postgresql.models.sqlalchemy import SQLAlchemyBase


class BaseDatabase:
    """Provide reusable SQLAlchemy query-building helpers."""

    logger: logging.Logger

    def __init__(self):
        """Initialize the repository logger."""

        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def set_search_by_column(query: sa.Select, search: str, column: sa.Column) -> sa.Select:
        """
        Setting 'search' variable value as searching by getting SQLAlchemy 'column'.

        Args:
            query: collected user select(...).where(...).
            search: what should be searched for by the selected 'column' in the database.
            column: SQLAlchemy column for searching 'search' inside.
        Returns:
            sa.Select: updated select(...).where(...).where(column.icontains(search)).
        """

        search = search.strip().lower()
        if len(search) != 0:
            query = query.where(column.icontains(search))
        return query

    @staticmethod
    def set_search_by_columns(query: sa.Select, search: str, columns: list[sa.Column]) -> sa.Select:
        """
        Setting 'search' variable value as searching by getting SQLAlchemy 'column'.

        Args:
            query: collected user select(...).where(...).
            search: what should be searched for by the selected 'column' in the database.
            columns: SQLAlchemy columns for searching 'search' inside.
        Returns:
            sa.Select: updated select(...).where(...).where(or_(column.icontains(search), ...)).
        """

        search = search.strip().lower()

        if not search or not columns:
            return query

        conditions = [column.icontains(search) for column in columns]
        query = query.where(sa.or_(*conditions))

        return query

    @staticmethod
    def set_offset_limit(query: sa.Select, offset: int, limit: int) -> sa.Select:
        """
        Setting 'offset' and 'limit' for collected user select(...).where(...).

        Args:
            query: collected user select(...).where(...).
            offset: used to skip rows before returning a result of the query.
            limit: number of rows returned by the query.
        Returns:
            sa.Select: updated select(...).where(...).offset(offset).limit(limit).
        """

        return query.offset(offset).limit(limit)

    @staticmethod
    def set_order_by(query: sa.Select, sort_by: str, sort_order: SortOrder) -> sa.Select:
        """
        Setting 'order_by' with 'asc' and 'desc' options for collected user select(...).where(...).

        Args:
            query: collected user select(...).where(...).
            sort_by: sorting column in database.
            sort_order: option to sort rows in 'sort_order.ASC' or in 'sort_order.DESC' order.
        Returns:
            sa.Select: updated select(...).where(...).order_by("column asc").
        """

        sort_by = sort_by.strip().lower()
        sort_order = sort_order.strip().lower()
        query = query.order_by(sa.text(f"{sort_by} {sort_order}"))
        return query

    def apply_filters(
        self,
        query: sa.Select | sa.Subquery,
        filters: list[BaseFilter],
        filter_columns: dict,
    ) -> sa.Select:
        """Apply typed filters to their configured SQLAlchemy columns.

        Args:
            query: Query to filter.
            filters: Filter models to apply in order.
            filter_columns: Mapping from public filter fields to columns.

        Returns:
            The filtered query.
        """
        for filter_ in filters:
            column = filter_columns[filter_.field]
            query = self._apply_filter(query=query, column=column, filter=filter_)
        return query

    @staticmethod
    def _apply_filter(query: sa.Select | sa.Subquery, column: sa.Column, filter: FilterProtocol) -> sa.Select:
        """Delegate one query transformation to a filter implementation."""

        query = filter.q(query=query, column=column)
        return query


def sqlalchemy_to_pydantic(func):
    """
    Decorator for converting SQLAlchemy model to Pydantic model that
    specified in __annotation__ attribute covering method.
    It check return type of method and convert to specified type.
    """

    def _as_dict(row: sa.Row) -> dict[str, Any]:
        """
        Function convert sa.Row to linear dictionary view.
        For example, client can request SQLAlchemy User model (id, name) and his tasks count.
        (User(id, name), 10) is one row of query. This method convert this view to dictionary:
        {"id": 1, "name": "Big Brother", "tasks_count": 10}.

        PS. You need to specify key 'tasks_count' when make select(count(...).label('tasks_count')).where(...)
        """
        dict_ = {}
        for k, v in row._asdict().items():
            if issubclass(type(v), SQLAlchemyBase):
                dict_.update(v.to_dict())
            elif v is not None:
                dict_[k] = v
        return dict_

    @wraps(func)
    async def inner(*args, **kwargs) -> list[BaseModel] | BaseModel | None | Sequence[sa.Row]:
        """Execute the wrapped query and validate annotated Pydantic output."""

        result = await func(*args, **kwargs)
        is_sqlalchemy_response = any(isinstance(result, cls) for cls in (sa.ChunkedIteratorResult, sa.CursorResult))
        if "return" not in func.__annotations__ or not is_sqlalchemy_response:
            return result
        result = result.fetchall()

        return_class = func.__annotations__["return"]
        is_list = hasattr(return_class, "__origin__") and isinstance([], return_class.__origin__)

        if len(result) == 0:
            return [] if is_list else None

        result = [_as_dict(r) for r in result]
        return TypeAdapter(return_class).validate_python(result if is_list else result[0])

    return inner
