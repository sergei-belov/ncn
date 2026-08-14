from datetime import timedelta
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from api.services import Services
from libs.cp_postgresql import BaseDatabaseGeneric
from models import enum, pydantic, sqlalchemy


RANK_STEP = 1024
RANK_WIDTH = 32


def format_rank(value: int) -> str:
    """Format an integer as a fixed-width lexical rank.

    Args:
        value: Numeric rank to format.

    Returns:
        The zero-padded rank string.
    """
    return str(value).zfill(RANK_WIDTH)


class WorkItemsDb(
    BaseDatabaseGeneric[
        sqlalchemy.WorkItem,
        UUID,
        pydantic.WorkItemDTO,
        pydantic.WorkItemCreateDTO,
        pydantic.WorkItemUpdateFieldsDTO,
    ]
):
    """Provide persistence operations and ordered queries for work items."""

    database = Services.database
    _table = sqlalchemy.WorkItem
    _id = UUID
    _model = pydantic.WorkItemDTO
    _model_create = pydantic.WorkItemCreateDTO
    _model_update = pydantic.WorkItemUpdateFieldsDTO

    def _filters(
        self,
        project_id: UUID,
        search: str | None,
        state_id: UUID | None,
        priorities: list[enum.Priority],
        assignee_ids: list[UUID],
        epic_id: UUID | str | None,
        due_status: enum.DueStatus | None,
        created_by: UUID | None,
    ) -> list:
        """Build SQLAlchemy predicates for work-item list queries.

        Args:
            project_id: Project that owns the work items.
            search: Optional title or display-identifier search text.
            state_id: Optional state identifier.
            priorities: Priority values to include.
            assignee_ids: Assignee identifiers to include.
            epic_id: Epic identifier, ``"none"`` for unassigned items, or
                ``None`` for no epic filter.
            due_status: Optional derived due-date status.
            created_by: Optional creator identifier.

        Returns:
            SQLAlchemy predicates representing the requested filters.
        """
        filters = [self._table.project_id == project_id]
        if search:
            pattern = f"%{search.strip()}%"
            project_identifier = (
                sa.select(sqlalchemy.Project.identifier)
                .where(sqlalchemy.Project.id == project_id)
                .scalar_subquery()
            )
            identifier = sa.func.concat(project_identifier, "-", self._table.sequence_id)
            filters.append(sa.or_(self._table.title.ilike(pattern), identifier.ilike(pattern)))
        if state_id:
            filters.append(self._table.state_id == state_id)
        if priorities:
            filters.append(self._table.priority.in_([value.value for value in priorities]))
        if assignee_ids:
            filters.append(
                sa.exists().where(
                    sqlalchemy.WorkItemAssignee.work_item_id == self._table.id,
                    sqlalchemy.WorkItemAssignee.user_id.in_(assignee_ids),
                )
            )
        if epic_id == "none":
            filters.append(self._table.epic_id.is_(None))
        elif epic_id:
            filters.append(self._table.epic_id == epic_id)
        if due_status == enum.DueStatus.OVERDUE:
            filters.extend([self._table.due_date.is_not(None), self._table.due_date < sa.func.current_date()])
        elif due_status == enum.DueStatus.DUE_SOON:
            filters.extend([
                self._table.due_date >= sa.func.current_date(),
                self._table.due_date <= sa.func.current_date() + timedelta(days=7),
            ])
        elif due_status == enum.DueStatus.NO_DUE_DATE:
            filters.append(self._table.due_date.is_(None))
        if created_by:
            filters.append(self._table.created_by == created_by)
        return filters

    async def list_filtered(
        self,
        session: AsyncSession,
        project_id: UUID,
        search: str | None = None,
        state_id: UUID | None = None,
        priorities: list[enum.Priority] | None = None,
        assignee_ids: list[UUID] | None = None,
        epic_id: UUID | str | None = None,
        due_status: enum.DueStatus | None = None,
        created_by: UUID | None = None,
        sort: str = "rank",
        offset: int = 0,
        limit: int = 30,
    ) -> tuple[list[pydantic.WorkItemDTO], int]:
        """List filtered work items with a total match count.

        Args:
            session: Active database session.
            project_id: Project that owns the work items.
            search: Optional title or display-identifier search text.
            state_id: Optional state identifier.
            priorities: Optional priorities to include.
            assignee_ids: Optional assignees to include.
            epic_id: Optional epic filter or ``"none"`` for unassigned items.
            due_status: Optional due-date status filter.
            created_by: Optional creator identifier.
            sort: Requested sort expression.
            offset: Number of matching rows to skip.
            limit: Maximum number of rows to return.

        Returns:
            A pair containing work-item DTOs and the total match count.
        """
        filters = self._filters(
            project_id, search, state_id, priorities or [], assignee_ids or [], epic_id, due_status, created_by
        )
        if sort == "due_date":
            order = self._table.due_date.asc().nulls_last()
        elif "created_at" in sort:
            order = self._table.created_at.desc() if sort.startswith("-") else self._table.created_at.asc()
        else:
            order = self._table.rank.asc()
        query = sa.select(self._table).where(*filters).order_by(order, self._table.id.asc()).offset(offset).limit(limit)
        count_query = sa.select(sa.func.count()).select_from(self._table).where(*filters)
        rows = (await session.execute(query)).fetchall()
        total = int((await session.execute(count_query)).scalar() or 0)
        return [self._model.model_validate(row) for row in rows], total

    async def list_board_columns(
        self,
        session: AsyncSession,
        project_id: UUID,
        search: str | None = None,
        priorities: list[enum.Priority] | None = None,
        assignee_ids: list[UUID] | None = None,
        epic_id: UUID | str | None = None,
        due_status: enum.DueStatus | None = None,
        per_column: int = 30,
    ) -> dict[UUID, tuple[list[pydantic.WorkItemDTO], int]]:
        """Load a bounded work-item slice for every board state.

        Args:
            session: Active database session.
            project_id: Project whose board is loaded.
            search: Optional title or display-identifier search text.
            priorities: Optional priorities to include.
            assignee_ids: Optional assignees to include.
            epic_id: Optional epic filter or ``"none"`` for unassigned items.
            due_status: Optional due-date status filter.
            per_column: Maximum number of items returned for each state.

        Returns:
            A mapping from state identifiers to visible item DTOs and the full
            item count for that state.
        """
        filters = self._filters(
            project_id,
            search,
            None,
            priorities or [],
            assignee_ids or [],
            epic_id,
            due_status,
            None,
        )
        row_number = sa.func.row_number().over(
            partition_by=self._table.state_id,
            order_by=(self._table.rank.asc(), self._table.id.asc()),
        )
        state_count = sa.func.count().over(partition_by=self._table.state_id)
        ranked = (
            sa.select(
                self._table,
                row_number.label("row_number"),
                state_count.label("state_count"),
            )
            .where(*filters)
            .cte("ranked_board_work_items")
        )
        query = (
            sa.select(ranked)
            .where(ranked.c.row_number <= per_column)
            .order_by(ranked.c.state_id.asc(), ranked.c.rank.asc(), ranked.c.id.asc())
        )
        rows = (await session.execute(query)).fetchall()
        columns: dict[UUID, tuple[list[pydantic.WorkItemDTO], int]] = {}
        for row in rows:
            item = self._model.model_validate(row)
            items, _ = columns.setdefault(item.state_id, ([], int(row.state_count)))
            items.append(item)
        return columns

    async def allocate_rank(
        self,
        session: AsyncSession,
        project_id: UUID,
        state_id: UUID,
        before_id: UUID | None,
        after_id: UUID | None,
        exclude_id: UUID | None = None,
    ) -> tuple[str, UUID | None, UUID | None]:
        """Allocate a rank between optional neighboring work items.

        Args:
            session: Active database session.
            project_id: Project that owns the target state.
            state_id: State receiving the work item.
            before_id: Optional item that must follow the allocated rank.
            after_id: Optional item that must precede the allocated rank.
            exclude_id: Optional moving item omitted from neighbor discovery.

        Returns:
            The allocated rank and the resolved previous and next item IDs.

        Raises:
            ValueError: If an anchor is missing or both anchors are not adjacent.

        Side Effects:
            Rebalances existing ranks when no numeric gap remains between the
            selected neighbors.
        """
        query = (
            sa.select(self._table.id, self._table.rank)
            .where(self._table.project_id == project_id, self._table.state_id == state_id)
            .order_by(self._table.rank.asc(), self._table.id.asc())
        )
        rows = [(row.id, row.rank) for row in (await session.execute(query)).fetchall() if row.id != exclude_id]
        ids = [row[0] for row in rows]
        if before_id and before_id not in ids:
            raise ValueError("before anchor not found")
        if after_id and after_id not in ids:
            raise ValueError("after anchor not found")
        if before_id and after_id and ids.index(after_id) + 1 != ids.index(before_id):
            raise ValueError("anchors are not adjacent")

        insert_index = len(rows)
        if before_id:
            insert_index = ids.index(before_id)
        elif after_id:
            insert_index = ids.index(after_id) + 1
        previous_id = rows[insert_index - 1][0] if insert_index > 0 else None
        next_id = rows[insert_index][0] if insert_index < len(rows) else None
        previous_rank = int(rows[insert_index - 1][1]) if insert_index > 0 else 0
        next_rank = int(rows[insert_index][1]) if insert_index < len(rows) else previous_rank + RANK_STEP * 2
        if next_rank - previous_rank <= 1:
            for position, (item_id, _) in enumerate(rows, start=1):
                await session.execute(
                    sa.update(self._table)
                    .where(self._table.id == item_id)
                    .values(rank=format_rank(position * RANK_STEP))
                )
            previous_rank = insert_index * RANK_STEP
            next_rank = (insert_index + 1) * RANK_STEP if insert_index < len(rows) else previous_rank + RANK_STEP * 2
        return format_rank((previous_rank + next_rank) // 2), previous_id, next_id

    async def set_epic(
        self,
        session: AsyncSession,
        project_id: UUID,
        work_item_ids: list[UUID],
        epic_id: UUID | None,
    ) -> list[pydantic.WorkItemDTO]:
        """Assign or remove an epic for a collection of work items.

        Args:
            session: Active database session.
            project_id: Project expected to own the work items.
            work_item_ids: Work items to update.
            epic_id: Epic to assign, or ``None`` to remove the assignment.

        Returns:
            DTOs for the work items updated within the project.
        """
        if not work_item_ids:
            return []
        result = await session.execute(
            sa.update(self._table)
            .where(
                self._table.id.in_(work_item_ids),
                self._table.project_id == project_id,
            )
            .values(
                epic_id=epic_id,
                version=self._table.version + 1,
                updated_at=sa.func.now(),
            )
            .returning(self._table)
        )
        return [self._model.model_validate(row) for row in result.fetchall()]


class WorkItemAssigneesDb(
    BaseDatabaseGeneric[
        sqlalchemy.WorkItemAssignee,
        UUID,
        pydantic.WorkItemAssigneeDTO,
        pydantic.WorkItemAssigneeCreateDTO,
        pydantic.WorkItemAssigneeUpdateFieldsDTO,
    ]
):
    """Provide persistence operations for work-item assignee relations."""

    database = Services.database
    _table = sqlalchemy.WorkItemAssignee
    _id = UUID
    _model = pydantic.WorkItemAssigneeDTO
    _model_create = pydantic.WorkItemAssigneeCreateDTO
    _model_update = pydantic.WorkItemAssigneeUpdateFieldsDTO
