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
        """Return project relations joined with safe user display data.

        Args:
            project_ids: Projects whose complete membership sets are needed.
            session: Active database session.

        Returns:
            Memberships ordered by user display name and identifier.
        """

        if not project_ids:
            return []
        query = (
            sa.select(
                self._table.id,
                self._table.project_id,
                self._table.workspace_id,
                self._table.user_id,
                self._table.role,
                self._table.source,
                self._table.version,
                self._table.created_at,
                self._table.updated_at,
                sqlalchemy.User.name.label("display_name"),
                sqlalchemy.User.email.label("email"),
                sa.null().label("avatar_url"),
                sqlalchemy.User.is_active.label("is_active"),
            )
            .join(sqlalchemy.User, sqlalchemy.User.id == self._table.user_id)
            .where(self._table.project_id.in_(project_ids))
            .order_by(sa.func.lower(sqlalchemy.User.name), self._table.user_id)
        )
        rows = (await session.execute(query)).fetchall()
        return [pydantic.ProjectUserDetailsDTO.model_validate(row) for row in rows]

    async def list_with_details(
        self,
        project_id: UUID,
        offset: int,
        limit: int,
        search: str | None,
        session: AsyncSession,
    ) -> tuple[list[pydantic.ProjectUserDetailsDTO], int]:
        """Return a stable page of project memberships joined to users.

        Args:
            project_id: Project whose members are listed.
            offset: Number of matching rows to skip.
            limit: Maximum rows to return.
            search: Optional case-insensitive user name or email fragment.
            session: Active database session.

        Returns:
            The joined membership page and total matching row count.
        """

        clause = self._table.project_id == project_id
        if search and search.strip():
            value = search.strip().casefold()
            clause = sa.and_(
                clause,
                sa.or_(
                    sa.func.lower(sqlalchemy.User.name).contains(value),
                    sa.func.lower(sqlalchemy.User.email).contains(value),
                ),
            )
        base = sa.select(self._table.id).select_from(self._table).join(
            sqlalchemy.User, sqlalchemy.User.id == self._table.user_id
        ).where(clause)
        count = await session.scalar(sa.select(sa.func.count()).select_from(base.subquery()))
        query = (
            sa.select(
                self._table.id,
                self._table.project_id,
                self._table.workspace_id,
                self._table.user_id,
                self._table.role,
                self._table.source,
                self._table.version,
                self._table.created_at,
                self._table.updated_at,
                sqlalchemy.User.name.label("display_name"),
                sqlalchemy.User.email.label("email"),
                sa.null().label("avatar_url"),
                sqlalchemy.User.is_active.label("is_active"),
            )
            .join(sqlalchemy.User, sqlalchemy.User.id == self._table.user_id)
            .where(clause)
            .order_by(self._table.created_at, self._table.id)
            .offset(offset)
            .limit(limit)
        )
        rows = (await session.execute(query)).fetchall()
        return [pydantic.ProjectUserDetailsDTO.model_validate(row) for row in rows], int(count or 0)
