import json
from typing import (
    Any,
    ClassVar,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)
from sqlalchemy import Row

from libs.cp_postgresql.models.sqlalchemy.base import SQLAlchemyBase


__all__ = ["OrmModel"]


class OrmModel(BaseModel):
    """ORM model with SQLAlchemy (both ORM and Core) query result mapping to Pydantic model via `.model_validate()`."""

    model_config = ConfigDict(
        from_attributes=True,
        revalidate_instances="subclass-instances",
        protected_namespaces=(),
    )

    _json_serialization_fields: ClassVar[set[str]] = set()

    @model_validator(mode="before")
    @classmethod
    def load_object(cls, obj: SQLAlchemyBase | Row | BaseModel | dict) -> dict[str, Any]:
        """Prepare object for valid Pydantic attributes mapping via `.model_validate()`.

        Args:
            obj (SQLAlchemyBase | Row | BaseModel | dict): object to load in Pydantic model.
                1. SQLAlchemyBase - if object is SqlAlchemy ORM model
                2. Row - if object is SqlAlchemy Core query result
                3. BaseModel - if model is created from another Pydantic model.
                4. Dict - if model is created in a usual way via attributes.

        Returns:
            dict[str, Any]: prepared dict to load into Pydantic model
        """
        parsed: dict[str, Any] = {}
        if isinstance(obj, dict):
            parsed = obj
        elif isinstance(obj, BaseModel):
            parsed = obj.model_dump()
        elif isinstance(obj, SQLAlchemyBase):
            parsed.update(obj.__dict__)
        else:
            for field, value in obj._asdict().items():
                if isinstance(value, SQLAlchemyBase):
                    parsed.update(value.__dict__)
                else:
                    parsed[field] = value

        for field in cls._json_serialization_fields:
            if field in parsed and isinstance(parsed[field], str):
                parsed[field] = json.loads(parsed[field])
        return parsed
