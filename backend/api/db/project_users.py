from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class ProjectUsersDb(
    BaseDatabaseGeneric[
        sqlalchemy.ProjectUser,
        UUID,
        pydantic.ProjectUserDTO,
        pydantic.ProjectUserCreateDTO,
        pydantic.ProjectUserUpdateFieldsDTO,
    ]
):
    """Project authorization relation repository."""

    database = Services.database
    _table = sqlalchemy.ProjectUser
    _id = UUID
    _model = pydantic.ProjectUserDTO
    _model_create = pydantic.ProjectUserCreateDTO
    _model_update = pydantic.ProjectUserUpdateFieldsDTO

    async def get_members_with_details(
        self,
        project_ids: list[UUID],
        session: AsyncSession,
    ) -> list[pydantic.ProjectUserDetailsDTO]:
        """Return authorization relations joined with their user display data."""

        if not project_ids:
            return []
        query = (
            sa.select(
                self._table.id,
                self._table.project_id,
                self._table.user_id,
                self._table.role,
                sqlalchemy.User.name.label("display_name"),
                sa.null().label("avatar_url"),
                sa.true().label("is_active"),
            )
            .join(sqlalchemy.User, sqlalchemy.User.id == self._table.user_id)
            .where(self._table.project_id.in_(project_ids))
            .order_by(sa.func.lower(sqlalchemy.User.name), self._table.user_id)
        )
        rows = (await session.execute(query)).fetchall()
        return [pydantic.ProjectUserDetailsDTO.model_validate(row) for row in rows]
