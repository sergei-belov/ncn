from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class UsersDb(
    BaseDatabaseGeneric[
        sqlalchemy.User,
        UUID,
        pydantic.UserDTO,
        pydantic.UserCreateDTO,
        pydantic.UserUpdateFieldsDTO,
    ]
):
    """Application user repository."""

    database = Services.database
    _table = sqlalchemy.User
    _id = UUID
    _model = pydantic.UserDTO
    _model_create = pydantic.UserCreateDTO
    _model_update = pydantic.UserUpdateFieldsDTO

    async def get_extended_by_email(
        self,
        email: str,
        project_id: UUID,
        workspace_slug: str,
        session: AsyncSession,
    ) -> pydantic.UserAccessDataDTO | None:
        """Return a user with its project authorization relation."""

        query = (
            sa.select(
                self._table,
                sqlalchemy.ProjectUser.id.label("project_user_id"),
                sqlalchemy.Project.id.label("project_id"),
                sqlalchemy.Project.workspace_slug.label("workspace_slug"),
                sqlalchemy.ProjectUser.role.label("project_role"),
            )
            .select_from(self._table)
            .outerjoin(
                sqlalchemy.Project,
                sa.and_(
                    sqlalchemy.Project.id == project_id,
                    sqlalchemy.Project.workspace_slug == workspace_slug,
                ),
            )
            .outerjoin(
                sqlalchemy.ProjectUser,
                sa.and_(
                    sqlalchemy.ProjectUser.user_id == self._table.id,
                    sqlalchemy.ProjectUser.project_id == sqlalchemy.Project.id,
                ),
            )
            .where(sa.func.lower(self._table.email) == email.strip().casefold())
        )
        row = (await session.execute(query)).fetchone()
        if row is None:
            return None
        return pydantic.UserAccessDataDTO.model_validate(row)
