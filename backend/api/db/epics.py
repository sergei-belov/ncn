from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from api.db.work_items import format_rank
from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import enum, pydantic, sqlalchemy


class EpicsDb(
    BaseDatabaseGeneric[
        sqlalchemy.Epic,
        UUID,
        pydantic.EpicDTO,
        pydantic.EpicCreateDTO,
        pydantic.EpicUpdateFieldsDTO,
    ]
):
    """Provide persistence operations and aggregate queries for epics."""

    database = Services.database
    _table = sqlalchemy.Epic
    _id = UUID
    _model = pydantic.EpicDTO
    _model_create = pydantic.EpicCreateDTO
    _model_update = pydantic.EpicUpdateFieldsDTO

    async def next_rank(self, session: AsyncSession, project_id: UUID) -> str:
        """Allocate the next sparse rank at the end of a project's epic list.

        Args:
            session: Active database session.
            project_id: Project whose epic ranks are inspected.

        Returns:
            A zero-padded rank value greater than the current maximum.
        """
        value = (await session.execute(
            sa.select(sa.func.max(sa.cast(self._table.rank, sa.Numeric))).where(self._table.project_id == project_id)
        )).scalar()
        return format_rank(int(value or 0) + 1024)

    async def list_with_progress(
        self,
        session: AsyncSession,
        project_id: UUID,
        search: str | None = None,
        state_groups: list[enum.StateGroup] | None = None,
        priorities: list[enum.Priority] | None = None,
        assignee_ids: list[UUID] | None = None,
        status: enum.EpicStatus | None = None,
        sort: str = "rank",
        offset: int = 0,
        limit: int = 30,
    ) -> tuple[list[sa.Row], int]:
        """List filtered epics with work-item progress aggregates.

        Args:
            session: Active database session.
            project_id: Project that owns the epics.
            search: Optional title or display-identifier search text.
            state_groups: Optional state groups to include.
            priorities: Optional priorities to include.
            assignee_ids: Optional assignees used to filter epics.
            status: Optional active or completed status filter.
            sort: Requested sort expression.
            offset: Number of matching rows to skip.
            limit: Maximum number of rows to return.

        Returns:
            A pair containing the selected aggregate rows and total match count.
        """
        epic_state = aliased(sqlalchemy.ProjectState)
        work_item_state = aliased(sqlalchemy.ProjectState)
        completed = sa.func.count(sqlalchemy.WorkItem.id).filter(
            work_item_state.group == enum.StateGroup.COMPLETED.value
        )
        total = sa.func.count(sqlalchemy.WorkItem.id)
        progress = sa.case((total == 0, 0), else_=sa.cast(completed * 100 / total, sa.Integer))
        filters = [self._table.project_id == project_id]
        if search:
            pattern = f"%{search.strip()}%"
            identifier = sa.func.concat(sqlalchemy.Project.identifier, "-E", self._table.sequence_id)
            filters.append(sa.or_(self._table.title.ilike(pattern), identifier.ilike(pattern)))
        if state_groups:
            filters.append(epic_state.group.in_([value.value for value in state_groups]))
        if priorities:
            filters.append(self._table.priority.in_([value.value for value in priorities]))
        if assignee_ids:
            filters.append(sa.exists().where(
                sqlalchemy.EpicAssignee.epic_id == self._table.id,
                sqlalchemy.EpicAssignee.user_id.in_(assignee_ids),
            ))
        if status == enum.EpicStatus.COMPLETED:
            filters.append(epic_state.group == enum.StateGroup.COMPLETED.value)
        elif status == enum.EpicStatus.ACTIVE:
            filters.append(epic_state.group != enum.StateGroup.COMPLETED.value)
        base = (
            sa.select(
                self._table,
                total.label("work_items_count"),
                completed.label("completed_work_items_count"),
                progress.label("progress_percent"),
            )
            .join(sqlalchemy.Project, sqlalchemy.Project.id == self._table.project_id)
            .join(epic_state, epic_state.id == self._table.state_id)
            .outerjoin(sqlalchemy.WorkItem, sqlalchemy.WorkItem.epic_id == self._table.id)
            .outerjoin(work_item_state, work_item_state.id == sqlalchemy.WorkItem.state_id)
            .where(*filters)
            .group_by(self._table.id)
        )
        if sort == "-progress":
            order = progress.desc()
        elif sort == "due_date":
            order = self._table.due_date.asc().nulls_last()
        elif "created_at" in sort:
            order = self._table.created_at.desc() if sort.startswith("-") else self._table.created_at.asc()
        else:
            order = self._table.rank.asc()
        rows = (
            await session.execute(
                base.order_by(order, self._table.id.asc()).offset(offset).limit(limit)
            )
        ).fetchall()
        count_base = base.with_only_columns(self._table.id).order_by(None).subquery()
        count = int((await session.execute(sa.select(sa.func.count()).select_from(count_base))).scalar() or 0)
        return rows, count

    async def get_with_progress(
        self,
        session: AsyncSession,
        project_id: UUID,
        epic_id: UUID,
    ) -> sa.Row | None:
        """Return one epic with its work-item progress aggregates.

        Args:
            session: Active database session.
            project_id: Project expected to own the epic.
            epic_id: Epic to retrieve.

        Returns:
            The aggregate row when the epic exists in the project, otherwise
            ``None``.
        """
        work_item_state = aliased(sqlalchemy.ProjectState)
        completed = sa.func.count(sqlalchemy.WorkItem.id).filter(
            work_item_state.group == enum.StateGroup.COMPLETED.value
        )
        total = sa.func.count(sqlalchemy.WorkItem.id)
        progress = sa.case(
            (total == 0, 0),
            else_=sa.cast(completed * 100 / total, sa.Integer),
        )
        query = (
            sa.select(
                self._table,
                total.label("work_items_count"),
                completed.label("completed_work_items_count"),
                progress.label("progress_percent"),
            )
            .outerjoin(sqlalchemy.WorkItem, sqlalchemy.WorkItem.epic_id == self._table.id)
            .outerjoin(work_item_state, work_item_state.id == sqlalchemy.WorkItem.state_id)
            .where(
                self._table.id == epic_id,
                self._table.project_id == project_id,
            )
            .group_by(self._table.id)
        )
        return (await session.execute(query)).first()


class EpicAssigneesDb(
    BaseDatabaseGeneric[
        sqlalchemy.EpicAssignee,
        UUID,
        pydantic.EpicAssigneeDTO,
        pydantic.EpicAssigneeCreateDTO,
        pydantic.EpicAssigneeUpdateFieldsDTO,
    ]
):
    """Provide persistence operations for epic assignee relations."""

    database = Services.database
    _table = sqlalchemy.EpicAssignee
    _id = UUID
    _model = pydantic.EpicAssigneeDTO
    _model_create = pydantic.EpicAssigneeCreateDTO
    _model_update = pydantic.EpicAssigneeUpdateFieldsDTO
