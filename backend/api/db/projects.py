from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import pydantic, sqlalchemy


class ProjectsDb(
    BaseDatabaseGeneric[
        sqlalchemy.Project,
        UUID,
        pydantic.ProjectDTO,
        pydantic.ProjectCreateDTO,
        pydantic.ProjectUpdateFieldsDTO,
    ]
):
    """Provide persistence operations and listing queries for projects."""

    database = Services.database
    _table = sqlalchemy.Project
    _id = UUID
    _model = pydantic.ProjectDTO
    _model_create = pydantic.ProjectCreateDTO
    _model_update = pydantic.ProjectUpdateFieldsDTO

    async def list_visible(
        self,
        session: AsyncSession,
        workspace_slug: str,
        actor_id: UUID,
        archived: bool,
        mine: bool,
        search: str | None,
        sort: str,
        offset: int,
        limit: int,
    ) -> tuple[list[sa.Row], int]:
        """List projects visible to a workspace actor.

        Args:
            session: Active database session.
            workspace_slug: Workspace containing the projects.
            actor_id: Actor whose membership grants visibility.
            archived: Whether to list archived rather than active projects.
            mine: Whether to restrict results to actor-created projects.
            search: Optional name or identifier search text.
            sort: Requested sort expression.
            offset: Number of matching projects to skip.
            limit: Maximum number of projects to return.

        Returns:
            A pair containing enriched project rows and the total match count.
        """
        member = sqlalchemy.ProjectUser
        conditions = [
            self._table.workspace_slug == workspace_slug,
            self._table.archived_at.is_not(None) if archived else self._table.archived_at.is_(None),
            member.user_id == actor_id,
        ]
        if mine:
            conditions.append(self._table.created_by == actor_id)
        if search:
            pattern = f"%{search.strip()}%"
            conditions.append(
                sa.or_(self._table.name.ilike(pattern), self._table.identifier.ilike(pattern))
            )
        active_work_items_count = (
            sa.select(sa.func.count())
            .select_from(sqlalchemy.WorkItem)
            .where(sqlalchemy.WorkItem.project_id == self._table.id)
            .correlate(self._table)
            .scalar_subquery()
        )
        epics_count = (
            sa.select(sa.func.count())
            .select_from(sqlalchemy.Epic)
            .where(sqlalchemy.Epic.project_id == self._table.id)
            .correlate(self._table)
            .scalar_subquery()
        )
        base = (
            sa.select(
                self._table,
                member.role.label("member_role"),
                active_work_items_count.label("active_work_items_count"),
                epics_count.label("epics_count"),
            )
            .select_from(self._table)
            .join(
                member,
                sa.and_(
                    member.project_id == self._table.id,
                    member.user_id == actor_id,
                ),
            )
            .where(*conditions)
        )
        sort_column = self._table.created_at if "created_at" in sort else sa.func.lower(self._table.name)
        order = sort_column.desc() if sort.startswith("-") else sort_column.asc()
        query = base.order_by(order, self._table.id.asc()).offset(offset).limit(limit)
        count_query = sa.select(sa.func.count()).select_from(base.with_only_columns(self._table.id).subquery())
        rows = (await session.execute(query)).fetchall()
        total = int((await session.execute(count_query)).scalar() or 0)
        return rows, total

    async def increment_board_version(self, session: AsyncSession, project_id: UUID) -> int:
        """Atomically increment and return a project's board version.

        Args:
            session: Active database session.
            project_id: Project whose board version is incremented.

        Returns:
            The updated board version.
        """
        result = await session.execute(
            sa.update(self._table)
            .where(self._table.id == project_id)
            .values(board_version=self._table.board_version + 1, updated_at=sa.func.now())
            .returning(self._table.board_version)
        )
        return int(result.scalar_one())

    async def allocate_sequence(self, session: AsyncSession, project_id: UUID, field: str) -> int:
        """Atomically allocate the current value of a project sequence field.

        Args:
            session: Active database session.
            project_id: Project that owns the sequence.
            field: Sequence column to increment.

        Returns:
            The sequence value reserved for the caller.
        """
        column = getattr(self._table, field)
        result = await session.execute(
            sa.update(self._table)
            .where(self._table.id == project_id)
            .values({field: column + 1})
            .returning(column)
        )
        return int(result.scalar_one()) - 1
