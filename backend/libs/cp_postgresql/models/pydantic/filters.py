from typing import (
    Any,
    Literal,
    Protocol,
)

import sqlalchemy as sa

from libs.cp_postgresql.models import enum
from libs.cp_postgresql.models.sqlalchemy import OrmModel


class FilterProtocol(Protocol):
    """Protocol implemented by filters that modify SQLAlchemy queries."""

    field: Any
    op: enum.FilterOperation
    value: Any

    def q(self, query: sa.Select, column: sa.Column) -> sa.Select:
        """Apply this filter to a query and column."""

        ...


class BaseFilter(OrmModel):
    """Base filter containing a field, operation, and comparison value."""

    field: Any
    op: enum.FilterOperation
    value: Any


class StringFilter(BaseFilter):
    """Case-insensitive substring filter for textual columns."""

    op: Literal[enum.FilterOperation.CONTAINS]

    def q(self, query: sa.Select, column: sa.Column) -> sa.Select:
        """Apply a case-insensitive contains predicate."""

        return query.where(column.icontains(self.value))


class DateFilter(BaseFilter):
    """Before-or-after comparison filter for date-like columns."""

    op: Literal[enum.FilterOperation.BEFORE, enum.FilterOperation.AFTER]

    def q(self, query: sa.Select, column: sa.Column) -> sa.Select:
        """Apply the selected date comparison predicate.

        Raises:
            ValueError: If the filter carries an unsupported operation.
        """
        if self.op == enum.FilterOperation.BEFORE:
            return query.where(column <= self.value)
        elif self.op == enum.FilterOperation.AFTER:
            return query.where(column >= self.value)
        else:
            raise ValueError(f"Operation {self.op} not allowed")


class ValueComparasionFilter(BaseFilter):
    """Equality or ordering filter applied in a WHERE clause."""

    op: Literal[enum.FilterOperation.IS, enum.FilterOperation.ISNOT, enum.FilterOperation.GTE, enum.FilterOperation.LTE]

    def q(self, query: sa.Select, column: sa.Column) -> sa.Select:
        """Apply the selected value comparison predicate.

        Raises:
            ValueError: If the filter carries an unsupported operation.
        """
        if self.op == enum.FilterOperation.IS:
            return query.where(column == self.value)
        if self.op == enum.FilterOperation.ISNOT:
            return query.where(column != self.value)
        elif self.op == enum.FilterOperation.GTE:
            return query.where(column >= self.value)
        elif self.op == enum.FilterOperation.LTE:
            return query.where(column <= self.value)
        else:
            raise ValueError(f"Operation {self.op} not allowed")


class ValueComparasionHavingFilter(BaseFilter):
    """Equality or ordering filter applied in a HAVING clause."""

    op: Literal[enum.FilterOperation.IS, enum.FilterOperation.GTE, enum.FilterOperation.LTE]

    def q(self, query: sa.Select, column: sa.Column) -> sa.Select:
        """Apply the selected aggregate comparison predicate.

        Raises:
            ValueError: If the filter carries an unsupported operation.
        """
        if self.op == enum.FilterOperation.IS:
            return query.having(column == self.value)
        elif self.op == enum.FilterOperation.GTE:
            return query.having(column >= self.value)
        elif self.op == enum.FilterOperation.LTE:
            return query.having(column <= self.value)
        else:
            raise ValueError(f"Operation {self.op} not allowed")
