from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class WorkspaceUsersDb(
    BaseDatabaseGeneric[
        sqlalchemy.WorkspaceUser,
        UUID,
        pydantic.WorkspaceUserDTO,
        pydantic.WorkspaceUserCreateDTO,
        pydantic.WorkspaceUserUpdateFieldsDTO,
    ]
):
    """Workspace authorization relation repository."""

    database = Services.database
    _table = sqlalchemy.WorkspaceUser
    _id = UUID
    _model = pydantic.WorkspaceUserDTO
    _model_create = pydantic.WorkspaceUserCreateDTO
    _model_update = pydantic.WorkspaceUserUpdateFieldsDTO

    async def list_with_details(
        self,
        workspace_id: str,
        offset: int,
        limit: int,
        search: str | None,
        session: AsyncSession,
    ) -> tuple[list[pydantic.WorkspaceUserDetailsDTO], int]:
        """Return a stable page of workspace memberships joined to users.

        Args:
            workspace_id: Opaque workspace scope identifier.
            offset: Number of matching rows to skip.
            limit: Maximum rows to return.
            search: Optional case-insensitive user name or email fragment.
            session: Active database session.

        Returns:
            The joined membership page and total matching row count.
        """

        clause = self._table.workspace_id == workspace_id
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
                self._table.workspace_id,
                self._table.user_id,
                self._table.role,
                self._table.version,
                self._table.created_at,
                self._table.updated_at,
                sqlalchemy.User.email.label("email"),
                sqlalchemy.User.name.label("name"),
                sqlalchemy.User.is_active.label("is_active"),
            )
            .join(sqlalchemy.User, sqlalchemy.User.id == self._table.user_id)
            .where(clause)
            .order_by(self._table.created_at, self._table.id)
            .offset(offset)
            .limit(limit)
        )
        rows = (await session.execute(query)).fetchall()
        return [pydantic.WorkspaceUserDetailsDTO.model_validate(row) for row in rows], int(count or 0)
