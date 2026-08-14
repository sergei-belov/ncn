from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class ProjectStatesDb(
    BaseDatabaseGeneric[
        sqlalchemy.ProjectState,
        UUID,
        pydantic.ProjectStateDTO,
        pydantic.ProjectStateCreateDTO,
        pydantic.ProjectStateUpdateFieldsDTO,
    ]
):
    """Provide persistence operations and aggregate queries for project states."""

    database = Services.database
    _table = sqlalchemy.ProjectState
    _id = UUID
    _model = pydantic.ProjectStateDTO
    _model_create = pydantic.ProjectStateCreateDTO
    _model_update = pydantic.ProjectStateUpdateFieldsDTO

    async def list_with_counts(self, session: AsyncSession, project_id: UUID) -> list[sa.Row]:
        """List project states with their work-item counts.

        Args:
            session: Active database session.
            project_id: Project whose states are requested.

        Returns:
            State rows ordered by position and enriched with item counts.
        """
        query = (
            sa.select(
                self._table,
                sa.func.count(sqlalchemy.WorkItem.id).label("work_items_count"),
            )
            .outerjoin(sqlalchemy.WorkItem, sqlalchemy.WorkItem.state_id == self._table.id)
            .where(self._table.project_id == project_id)
            .group_by(self._table.id)
            .order_by(self._table.position.asc(), self._table.id.asc())
        )
        return (await session.execute(query)).fetchall()

    async def set_positions(
        self, session: AsyncSession, project_id: UUID, ordered_ids: list[UUID]
    ) -> None:
        """Replace state positions with the supplied ordering.

        Args:
            session: Active database session.
            project_id: Project whose states are reordered.
            ordered_ids: State identifiers in their desired order.

        Side Effects:
            Temporarily negates existing positions before assigning contiguous
            zero-based positions and incrementing state versions.
        """
        await session.execute(
            sa.update(self._table)
            .where(self._table.project_id == project_id)
            .values(position=-(self._table.position + 1))
        )
        for position, state_id in enumerate(ordered_ids):
            await session.execute(
                sa.update(self._table)
                .where(self._table.id == state_id, self._table.project_id == project_id)
                .values(position=position, version=self._table.version + 1)
            )

    async def clear_default(self, session: AsyncSession, project_id: UUID, except_id: UUID) -> None:
        """Clear the default flag from every state except one.

        Args:
            session: Active database session.
            project_id: Project whose default state is updated.
            except_id: State that may retain its default flag.
        """
        await session.execute(
            sa.update(self._table)
            .where(
                self._table.project_id == project_id,
                self._table.id != except_id,
                self._table.is_default.is_(True),
            )
            .values(is_default=False, version=self._table.version + 1)
        )
