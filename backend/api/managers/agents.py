from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.db import Database
from api.managers.common import AccessManager, PmsError, emit_event
from api.services import Services
from models import enum, pydantic
from models.pydantic.api import agent_api


COORDINATOR_NAME = "Координатор проекта"
COORDINATOR_DESCRIPTION = (
    "ИИ-менеджер проекта: анализирует состояние, строит план и делегирует работу "
    "ассистентам."
)
COORDINATOR_INSTRUCTIONS = (
    "Помогай команде достигать целей проекта, выявляй блокеры и риски, делегируй "
    "специализированные задачи подходящим ассистентам."
)


class AgentsManager:
    """Manage project agents and their lifecycle transitions."""

    @staticmethod
    def _response(agent: pydantic.AgentDTO) -> agent_api.AgentResponse:
        """Wrap an agent DTO in the standard API response."""

        return agent_api.AgentResponse(data=agent_api.Agent.model_validate(agent))

    @staticmethod
    async def _get_agent(
        session: AsyncSession,
        project_id: UUID,
        agent_id: UUID,
    ) -> pydantic.AgentDTO:
        """Load an agent that belongs to a project.

        Args:
            session: Active database session.
            project_id: Project expected to own the agent.
            agent_id: Agent to retrieve.

        Returns:
            The requested agent DTO.

        Raises:
            PmsError: If the agent does not exist in the project.
        """
        agent = await Database.agents.get(
            id=agent_id,
            project_id=project_id,
            session=session,
        )
        if not agent:
            raise PmsError(404, "AGENT_NOT_FOUND", "Agent not found.")
        return agent

    @staticmethod
    async def _require_unique_live_name(
        session: AsyncSession,
        project_id: UUID,
        name: str,
        current_agent_id: UUID | None = None,
    ) -> None:
        """Require a name to be unique among non-archived project agents.

        Args:
            session: Active database session.
            project_id: Project in which the name must be unique.
            name: Normalized agent name to validate.
            current_agent_id: Agent excluded while validating an update.

        Raises:
            PmsError: If another live agent already uses the name.
        """
        matching = await Database.agents.get_list(
            project_id=project_id,
            name=name,
            session=session,
        )
        if any(
            agent.id != current_agent_id and agent.status != enum.AgentStatus.ARCHIVED
            for agent in matching
        ):
            raise PmsError(
                422,
                "VALIDATION_ERROR",
                "Agent name must be unique within the project.",
                field_errors={
                    "name": [
                        {
                            "code": "NOT_UNIQUE",
                            "message": "An active agent with this name already exists.",
                        }
                    ]
                },
            )

    @staticmethod
    def _require_version(agent: pydantic.AgentDTO, expected_version: int) -> None:
        """Require an agent to match an optimistic concurrency version.

        Args:
            agent: Current persisted agent.
            expected_version: Version supplied by the caller.

        Raises:
            PmsError: If the versions differ.
        """
        if agent.version != expected_version:
            raise PmsError(
                409,
                "AGENT_VERSION_CONFLICT",
                "Agent version is stale.",
                details={"version": agent.version},
            )

    @classmethod
    async def _update_with_version(
        cls,
        session: AsyncSession,
        agent: pydantic.AgentDTO,
        data: pydantic.AgentUpdateFieldsDTO,
    ) -> pydantic.AgentDTO:
        """Update an agent using its current version as a write condition.

        Args:
            session: Active database session.
            agent: Current agent snapshot.
            data: Fields to persist, including the incremented version.

        Returns:
            The updated agent.

        Raises:
            PmsError: If a concurrent update changes the agent first.
        """
        updated = await Database.agents.update(
            id=agent.id,
            data=data,
            project_id=agent.project_id,
            version=agent.version,
            session=session,
        )
        if updated:
            return updated
        latest = await cls._get_agent(session, agent.project_id, agent.id)
        cls._require_version(latest, agent.version)
        raise PmsError(409, "AGENT_VERSION_CONFLICT", "Agent version is stale.")

    @classmethod
    async def create_coordinator(
        cls,
        session: AsyncSession,
        project_id: UUID,
        created_by: UUID,
    ) -> pydantic.AgentDTO:
        """Create the project's required coordinator if it is absent.

        Args:
            session: Active database session.
            project_id: Project receiving the coordinator.
            created_by: User recorded as the coordinator creator.

        Returns:
            The existing or newly created coordinator agent.
        """
        existing = await Database.agents.get(
            project_id=project_id,
            kind=enum.AgentKind.COORDINATOR,
            session=session,
        )
        if existing:
            return existing
        return await Database.agents.create(
            pydantic.AgentCreateDTO(
                project_id=project_id,
                kind=enum.AgentKind.COORDINATOR,
                name=COORDINATOR_NAME,
                description=COORDINATOR_DESCRIPTION,
                instructions=COORDINATOR_INSTRUCTIONS,
                model="qwen3:32b",
                memory_policy=enum.AgentMemoryPolicy.PROJECT,
                max_steps_per_run=50,
                approval_mode=enum.AgentApprovalMode.PROJECT,
                status=enum.AgentStatus.ACTIVE,
                system_tool_names=["task-management"],
                created_by=created_by,
            ),
            session=session,
            mode="json",
        )

    @classmethod
    async def list_agents(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> agent_api.AgentListResponse:
        """List project agents in stable UI order.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project whose agents are requested.
            actor: Request actor context.

        Returns:
            Agents ordered by kind, lifecycle status, name, and identifier.

        Raises:
            PmsError: If the actor cannot access the project.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(session, actor, workspace_slug, project_id)
            agents = await Database.agents.get_list(
                project_id=project_id,
                session=session,
            )
            agents.sort(
                key=lambda agent: (
                    agent.kind != enum.AgentKind.COORDINATOR,
                    agent.status == enum.AgentStatus.ARCHIVED,
                    agent.name.casefold(),
                    str(agent.id),
                )
            )
            return agent_api.AgentListResponse(
                data=[agent_api.Agent.model_validate(agent) for agent in agents]
            )

    @classmethod
    async def get_agent(
        cls,
        workspace_slug: str,
        project_id: UUID,
        agent_id: UUID,
        actor: pydantic.ActorDTO,
    ) -> agent_api.AgentResponse:
        """Retrieve a single project agent.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the agent.
            agent_id: Agent to retrieve.
            actor: Request actor context.

        Returns:
            The requested agent response.

        Raises:
            PmsError: If access is denied or the agent is missing.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(session, actor, workspace_slug, project_id)
            return cls._response(await cls._get_agent(session, project_id, agent_id))

    @classmethod
    async def create_agent(
        cls,
        workspace_slug: str,
        project_id: UUID,
        actor: pydantic.ActorDTO,
        data: agent_api.CreateAgentRequest,
    ) -> agent_api.AgentResponse:
        """Create a worker agent in a project.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project receiving the agent.
            actor: Request actor context.
            data: Validated agent configuration.

        Returns:
            The created agent response.

        Raises:
            PmsError: If access is denied or the name is already in use.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(
                session,
                actor,
                workspace_slug,
                project_id,
                "can_manage_agents",
            )
            await cls._require_unique_live_name(session, project_id, data.name)
            agent = await Database.agents.create(
                pydantic.AgentCreateDTO(
                    project_id=project_id,
                    kind=enum.AgentKind.WORKER,
                    status=enum.AgentStatus.ACTIVE,
                    system_tool_names=[],
                    created_by=actor.id,
                    **data.model_dump(),
                ),
                session=session,
                mode="json",
            )
            emit_event("agent_created", project_id=project_id, agent_id=agent.id)
            return cls._response(agent)

    @classmethod
    async def update_agent(
        cls,
        workspace_slug: str,
        project_id: UUID,
        agent_id: UUID,
        actor: pydantic.ActorDTO,
        data: agent_api.UpdateAgentRequest,
        expected_version: int,
    ) -> agent_api.AgentResponse:
        """Update mutable agent configuration under optimistic concurrency.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the agent.
            agent_id: Agent to update.
            actor: Request actor context.
            data: Validated partial configuration fields.
            expected_version: Version required before applying the update.

        Returns:
            The current or updated agent response.

        Raises:
            PmsError: If access is denied, the agent is archived, the name is
                duplicated, or the expected version is stale.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(
                session,
                actor,
                workspace_slug,
                project_id,
                "can_manage_agents",
            )
            current = await cls._get_agent(session, project_id, agent_id)
            cls._require_version(current, expected_version)
            if current.status == enum.AgentStatus.ARCHIVED:
                raise PmsError(409, "AGENT_ARCHIVED", "Archived agents cannot be changed.")
            values = data.model_dump(exclude_unset=True, exclude={"expected_version"})
            if not values:
                return cls._response(current)
            if "name" in values:
                await cls._require_unique_live_name(
                    session,
                    project_id,
                    values["name"],
                    current_agent_id=agent_id,
                )
            values["version"] = current.version + 1
            agent = await cls._update_with_version(
                session,
                current,
                pydantic.AgentUpdateFieldsDTO(**values),
            )
            emit_event("agent_updated", project_id=project_id, agent_id=agent.id)
            return cls._response(agent)

    @classmethod
    async def set_agent_enabled(
        cls,
        workspace_slug: str,
        project_id: UUID,
        agent_id: UUID,
        actor: pydantic.ActorDTO,
        enabled: bool,
        expected_version: int,
    ) -> agent_api.AgentResponse:
        """Enable or disable a worker agent under optimistic concurrency.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the agent.
            agent_id: Agent whose status is changed.
            actor: Request actor context.
            enabled: Whether the resulting status should be active.
            expected_version: Version required before applying the transition.

        Returns:
            The updated agent response.

        Raises:
            PmsError: If access is denied, the version is stale, the agent is
                archived, or disabling the coordinator is attempted.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(
                session,
                actor,
                workspace_slug,
                project_id,
                "can_manage_agents",
            )
            current = await cls._get_agent(session, project_id, agent_id)
            cls._require_version(current, expected_version)
            if current.kind == enum.AgentKind.COORDINATOR and not enabled:
                raise PmsError(
                    409,
                    "COORDINATOR_REQUIRED",
                    "The project coordinator cannot be disabled.",
                )
            if current.status == enum.AgentStatus.ARCHIVED:
                raise PmsError(
                    409,
                    "AGENT_ARCHIVED",
                    "Archived agents cannot be enabled or disabled.",
                )
            status = enum.AgentStatus.ACTIVE if enabled else enum.AgentStatus.DISABLED
            agent = await cls._update_with_version(
                session,
                current,
                pydantic.AgentUpdateFieldsDTO(
                    status=status,
                    version=current.version + 1,
                ),
            )
            emit_event(
                "agent_enabled" if enabled else "agent_disabled",
                project_id=project_id,
                agent_id=agent.id,
            )
            return cls._response(agent)

    @classmethod
    async def archive_agent(
        cls,
        workspace_slug: str,
        project_id: UUID,
        agent_id: UUID,
        actor: pydantic.ActorDTO,
        expected_version: int,
    ) -> agent_api.AgentResponse:
        """Archive a worker agent under optimistic concurrency.

        Args:
            workspace_slug: Workspace containing the project.
            project_id: Project expected to own the agent.
            agent_id: Agent to archive.
            actor: Request actor context.
            expected_version: Version required before applying the transition.

        Returns:
            The archived agent, or the unchanged response when already archived.

        Raises:
            PmsError: If access is denied, the version is stale, or the target
                is the required project coordinator.
        """
        async with Services.database.session() as session:
            await AccessManager.require_project(
                session,
                actor,
                workspace_slug,
                project_id,
                "can_manage_agents",
            )
            current = await cls._get_agent(session, project_id, agent_id)
            cls._require_version(current, expected_version)
            if current.kind == enum.AgentKind.COORDINATOR:
                raise PmsError(
                    409,
                    "COORDINATOR_REQUIRED",
                    "The project coordinator cannot be archived.",
                )
            if current.status == enum.AgentStatus.ARCHIVED:
                return cls._response(current)
            agent = await cls._update_with_version(
                session,
                current,
                pydantic.AgentUpdateFieldsDTO(
                    status=enum.AgentStatus.ARCHIVED,
                    version=current.version + 1,
                ),
            )
            emit_event("agent_archived", project_id=project_id, agent_id=agent.id)
            return cls._response(agent)
