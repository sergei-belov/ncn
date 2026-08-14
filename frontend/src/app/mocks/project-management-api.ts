import type { Agent, AgentApi } from "@/entities/agent";
import type {
  BoardApi,
  BoardColumn,
  BoardFilters,
  BoardPayload,
  MoveWorkItemInput,
  MoveWorkItemResult,
} from "@/entities/board";
import type { Epic, EpicApi } from "@/entities/epic";
import type { Project, ProjectApi } from "@/entities/project";
import type { Priority, WorkItem, WorkItemApi } from "@/entities/work-item";
import type { WorkflowState, WorkflowStateApi } from "@/entities/workflow-state";
import { ApiError } from "@/shared/api/api-error";
import type { UUID } from "@/shared/lib/domain-primitives";
import { createId } from "@/shared/lib/id";
import { permissionsForRole } from "@/entities/project";

import { readDatabase, writeDatabase, type MockDatabase } from "./database";

const latency = 120;

async function wait(signal?: AbortSignal): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const timer = window.setTimeout(resolve, latency + Math.floor(Math.random() * 80));
    signal?.addEventListener(
      "abort",
      () => {
        window.clearTimeout(timer);
        reject(new DOMException("Aborted", "AbortError"));
      },
      { once: true },
    );
  });
}

function notFound(entity: string): never {
  throw new ApiError({ status: 404, code: "NOT_FOUND", message: `${entity} не найден` });
}

function conflict(message = "Данные изменились в другой вкладке. Обновите страницу."): never {
  throw new ApiError({ status: 409, code: "VERSION_CONFLICT", message });
}

function requireProject(database: MockDatabase, workspaceSlug: string, projectId: UUID): Project {
  const project = database.projects.find((candidate) => candidate.id === projectId && candidate.workspaceSlug === workspaceSlug);
  return project ?? notFound("Проект");
}

function requireWorkItem(database: MockDatabase, projectId: UUID, workItemId: UUID): WorkItem {
  const workItem = database.workItems.find((candidate) => candidate.id === workItemId && candidate.projectId === projectId);
  return workItem ?? notFound("Карточка");
}

function requireEpic(database: MockDatabase, projectId: UUID, epicId: UUID): Epic {
  const epic = database.epics.find((candidate) => candidate.id === epicId && candidate.projectId === projectId);
  return epic ?? notFound("Эпик");
}

function requireState(database: MockDatabase, projectId: UUID, stateId: UUID): WorkflowState {
  const state = database.states.find((candidate) => candidate.id === stateId && candidate.projectId === projectId);
  return state ?? notFound("Состояние");
}

function requireAgent(database: MockDatabase, projectId: UUID, agentId: UUID): Agent {
  const agent = database.agents.find((candidate) => candidate.id === agentId && candidate.projectId === projectId);
  return agent ?? notFound("Ассистент");
}

function assertCanManageAgents(project: Project): void {
  if (!project.permissions.canManageAgents) {
    throw new ApiError({ status: 403, code: "FORBIDDEN", message: "Недостаточно прав для управления ассистентами" });
  }
  if (project.archivedAt) {
    throw new ApiError({ status: 409, code: "PROJECT_ARCHIVED", message: "Архивный проект доступен только для чтения" });
  }
}

function makeCoordinator(projectId: UUID, timestamp: string): Agent {
  return {
    id: createId("agent"),
    projectId,
    kind: "coordinator",
    name: "Координатор проекта",
    description: "ИИ-менеджер проекта: анализирует состояние, строит план и делегирует работу ассистентам.",
    instructions: "Помогай команде достигать целей проекта, выявляй блокеры и риски, делегируй специализированные задачи подходящим ассистентам.",
    model: "qwen3:32b",
    memoryPolicy: "project",
    maxStepsPerRun: 50,
    approvalMode: "project",
    status: "active",
    systemToolNames: ["task-management"],
    createdAt: timestamp,
    updatedAt: timestamp,
    version: 1,
  };
}

function assertVersion(actual: number, expected: number): void {
  if (actual !== expected) conflict();
}

function now(): string {
  return new Date().toISOString();
}

function nextColor(index: number): string {
  return ["#6d5dfc", "#0ea5e9", "#f97316", "#16a34a", "#db2777"][index % 5] ?? "#6d5dfc";
}

function normalizeIdentifier(value: string): string {
  return value.trim().toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 10);
}

function recalculateEpics(database: MockDatabase, projectId: UUID): void {
  const completedStateIds = new Set(
    database.states.filter((state) => state.projectId === projectId && state.group === "completed").map((state) => state.id),
  );
  for (const epic of database.epics.filter((candidate) => candidate.projectId === projectId)) {
    epic.workItemIds = database.workItems.filter((workItem) => workItem.epicId === epic.id).map((workItem) => workItem.id);
    const completed = database.workItems.filter(
      (workItem) => epic.workItemIds.includes(workItem.id) && completedStateIds.has(workItem.stateId),
    ).length;
    const total = epic.workItemIds.length;
    epic.progress = { total, completed, percentage: total === 0 ? 0 : Math.round((completed / total) * 100) };
    epic.updatedAt = now();
  }
}

function orderedItems(database: MockDatabase, projectId: UUID, stateId: UUID): WorkItem[] {
  return database.workItems
    .filter((workItem) => workItem.projectId === projectId && workItem.stateId === stateId)
    .sort((a, b) => a.sortOrder - b.sortOrder || a.id.localeCompare(b.id));
}

function buildColumns(database: MockDatabase, projectId: UUID, visibleItems?: WorkItem[]): BoardColumn[] {
  const visibleIds = visibleItems ? new Set(visibleItems.map((item) => item.id)) : null;
  return database.states
    .filter((state) => state.projectId === projectId)
    .sort((a, b) => a.order - b.order)
    .map((state) => {
      const allIds = orderedItems(database, projectId, state.id).map((item) => item.id);
      const workItemIds = visibleIds ? allIds.filter((id) => visibleIds.has(id)) : allIds;
      return { stateId: state.id, workItemIds, totalCount: workItemIds.length, nextCursor: null };
    });
}

function applyBoardFilters(items: WorkItem[], filters: BoardFilters): WorkItem[] {
  const search = filters.search?.trim().toLocaleLowerCase("ru");
  const priorities = new Set<Priority>(filters.priorities ?? []);
  return items.filter((item) => {
    if (search && !`${item.identifier} ${item.title}`.toLocaleLowerCase("ru").includes(search)) return false;
    if (priorities.size > 0 && !priorities.has(item.priority)) return false;
    if (filters.epicId && item.epicId !== filters.epicId) return false;
    if (filters.assigneeId && !item.assigneeIds.includes(filters.assigneeId)) return false;
    return true;
  });
}

function resequence(items: WorkItem[]): void {
  items.forEach((item, index) => {
    item.sortOrder = (index + 1) * 1000;
  });
}

function insertMovedItem(database: MockDatabase, input: MoveWorkItemInput, workItem: WorkItem): void {
  const sourceItems = orderedItems(database, workItem.projectId, input.fromStateId).filter((item) => item.id !== workItem.id);
  const targetItems =
    input.fromStateId === input.toStateId
      ? sourceItems
      : orderedItems(database, workItem.projectId, input.toStateId).filter((item) => item.id !== workItem.id);

  let index = targetItems.length;
  if (input.beforeWorkItemId) {
    const beforeIndex = targetItems.findIndex((item) => item.id === input.beforeWorkItemId);
    if (beforeIndex >= 0) index = beforeIndex;
  } else if (input.afterWorkItemId) {
    const afterIndex = targetItems.findIndex((item) => item.id === input.afterWorkItemId);
    if (afterIndex >= 0) index = afterIndex + 1;
  }

  workItem.stateId = input.toStateId;
  targetItems.splice(index, 0, workItem);
  resequence(targetItems);
  if (input.fromStateId !== input.toStateId) resequence(sourceItems);
}

export type ProjectManagementApi = ProjectApi & BoardApi & WorkItemApi & EpicApi & WorkflowStateApi & AgentApi;

export const mockProjectManagementApi: ProjectManagementApi = {
  async listProjects(workspaceSlug, filters, signal) {
    await wait(signal);
    const database = readDatabase();
    const search = filters.search?.trim().toLocaleLowerCase("ru");
    return database.projects
      .filter((project) => project.workspaceSlug === workspaceSlug)
      .filter((project) => (filters.archived ? project.archivedAt !== null : project.archivedAt === null))
      .filter((project) => !search || `${project.name} ${project.identifier}`.toLocaleLowerCase("ru").includes(search))
      .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
  },

  async getProject(workspaceSlug, projectId, signal) {
    await wait(signal);
    return requireProject(readDatabase(), workspaceSlug, projectId);
  },

  async createProject(workspaceSlug, input) {
    await wait();
    const database = readDatabase();
    const identifier = normalizeIdentifier(input.identifier);
    if (database.projects.some((project) => project.workspaceSlug === workspaceSlug && project.identifier === identifier)) {
      throw new ApiError({
        status: 422,
        code: "VALIDATION_ERROR",
        message: "Исправьте поля формы",
        fieldErrors: { identifier: ["Такой идентификатор уже используется"] },
      });
    }
    const timestamp = now();
    const projectId = createId("project");
    const project: Project = {
      id: projectId,
      workspaceSlug,
      name: input.name.trim(),
      identifier,
      description: input.description?.trim() ?? "",
      access: input.access,
      role: "admin",
      color: nextColor(database.projects.length),
      archivedAt: null,
      createdAt: timestamp,
      updatedAt: timestamp,
      version: 1,
      permissions: permissionsForRole("admin"),
    };
    const definitions: Array<Pick<WorkflowState, "name" | "color" | "group">> = [
      { name: "Бэклог", color: "#94a3b8", group: "backlog" },
      { name: "К выполнению", color: "#60a5fa", group: "unstarted" },
      { name: "В работе", color: "#f59e0b", group: "started" },
      { name: "Готово", color: "#22c55e", group: "completed" },
    ];
    const states = definitions.map<WorkflowState>((definition, index) => ({
      id: createId("state"),
      projectId,
      ...definition,
      order: index,
      isDefault: index === 0,
      version: 1,
    }));
    database.projects.push(project);
    const creator = database.authzUsers.find((user) => user.id === database.currentUserId);
    if (!creator) {
      throw new ApiError({ status: 409, code: "USER_NOT_FOUND", message: "Текущий пользователь не найден" });
    }
    database.projectMemberships.push({
      id: createId("project-user"),
      workspaceId: workspaceSlug,
      projectId,
      userId: creator.id,
      user: creator,
      role: "admin",
      source: "bootstrap",
      version: 1,
      serviceRestrictions: [],
    });
    database.agents.push(makeCoordinator(projectId, timestamp));
    database.states.push(...states);
    database.boardVersions[projectId] = 1;
    writeDatabase(database);
    return project;
  },

  async updateProject(workspaceSlug, projectId, input, version) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    assertVersion(project.version, version);
    Object.assign(project, input, { updatedAt: now(), version: project.version + 1 });
    writeDatabase(database);
    return project;
  },

  async archiveProject(workspaceSlug, projectId, version) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    assertVersion(project.version, version);
    project.archivedAt = now();
    project.updatedAt = project.archivedAt;
    project.version += 1;
    writeDatabase(database);
    return project;
  },

  async restoreProject(workspaceSlug, projectId, version) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    assertVersion(project.version, version);
    project.archivedAt = null;
    project.updatedAt = now();
    project.version += 1;
    writeDatabase(database);
    return project;
  },

  async listAgents(workspaceSlug, projectId, signal) {
    await wait(signal);
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    return database.agents.filter((agent) => agent.projectId === projectId).sort((left, right) => {
      if (left.kind !== right.kind) return left.kind === "coordinator" ? -1 : 1;
      return left.name.localeCompare(right.name, "ru");
    });
  },

  async getAgent(workspaceSlug, projectId, agentId, signal) {
    await wait(signal);
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    return requireAgent(database, projectId, agentId);
  },

  async createAgent(workspaceSlug, projectId, input) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    assertCanManageAgents(project);
    const name = input.name.trim();
    if (database.agents.some((agent) => agent.projectId === projectId && agent.status !== "archived" && agent.name === name)) {
      throw new ApiError({
        status: 422,
        code: "VALIDATION_ERROR",
        message: "Исправьте поля формы",
        fieldErrors: { name: ["Ассистент с таким названием уже существует"] },
      });
    }
    const timestamp = now();
    const agent: Agent = {
      id: createId("agent"),
      projectId,
      kind: "worker",
      name,
      description: input.description.trim(),
      instructions: input.instructions.trim(),
      model: input.model,
      memoryPolicy: input.memoryPolicy,
      maxStepsPerRun: input.maxStepsPerRun,
      approvalMode: input.approvalMode,
      status: "active",
      systemToolNames: [],
      createdAt: timestamp,
      updatedAt: timestamp,
      version: 1,
    };
    database.agents.push(agent);
    writeDatabase(database);
    return agent;
  },

  async updateAgent(workspaceSlug, projectId, agentId, input, version) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    assertCanManageAgents(project);
    const agent = requireAgent(database, projectId, agentId);
    assertVersion(agent.version, version);
    if (agent.status === "archived") conflict("Архивного ассистента нельзя изменить");
    Object.assign(agent, input, {
      ...(input.name === undefined ? {} : { name: input.name.trim() }),
      ...(input.description === undefined ? {} : { description: input.description.trim() }),
      ...(input.instructions === undefined ? {} : { instructions: input.instructions.trim() }),
      updatedAt: now(),
      version: agent.version + 1,
    });
    writeDatabase(database);
    return agent;
  },

  async setAgentEnabled(workspaceSlug, projectId, agentId, enabled, version) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    assertCanManageAgents(project);
    const agent = requireAgent(database, projectId, agentId);
    assertVersion(agent.version, version);
    if (agent.kind === "coordinator" && !enabled) {
      throw new ApiError({ status: 409, code: "COORDINATOR_REQUIRED", message: "Координатора проекта нельзя отключить" });
    }
    if (agent.status === "archived") conflict("Архивного ассистента нельзя включить");
    agent.status = enabled ? "active" : "disabled";
    agent.updatedAt = now();
    agent.version += 1;
    writeDatabase(database);
    return agent;
  },

  async archiveAgent(workspaceSlug, projectId, agentId, version) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    assertCanManageAgents(project);
    const agent = requireAgent(database, projectId, agentId);
    assertVersion(agent.version, version);
    if (agent.kind === "coordinator") {
      throw new ApiError({ status: 409, code: "COORDINATOR_REQUIRED", message: "Координатора проекта нельзя архивировать" });
    }
    agent.status = "archived";
    agent.updatedAt = now();
    agent.version += 1;
    writeDatabase(database);
    return agent;
  },

  async getBoard(workspaceSlug, projectId, filters, signal) {
    await wait(signal);
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    recalculateEpics(database, projectId);
    const workItems = applyBoardFilters(
      database.workItems.filter((workItem) => workItem.projectId === projectId),
      filters,
    );
    const payload: BoardPayload = {
      project,
      states: database.states.filter((state) => state.projectId === projectId).sort((a, b) => a.order - b.order),
      workItems,
      epics: database.epics.filter((epic) => epic.projectId === projectId),
      members: database.members,
      columns: buildColumns(database, projectId, workItems),
      boardVersion: database.boardVersions[projectId] ?? 1,
    };
    writeDatabase(database);
    return payload;
  },

  async getWorkItem(workspaceSlug, projectId, workItemId, signal) {
    await wait(signal);
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    return requireWorkItem(database, projectId, workItemId);
  },

  async createWorkItem(workspaceSlug, projectId, input) {
    await wait();
    const database = readDatabase();
    const project = requireProject(database, workspaceSlug, projectId);
    requireState(database, projectId, input.stateId);
    if (input.epicId) requireEpic(database, projectId, input.epicId);
    const sequenceId =
      Math.max(0, ...database.workItems.filter((item) => item.projectId === projectId).map((item) => item.sequenceId)) + 1;
    const timestamp = now();
    const workItem: WorkItem = {
      id: createId("work-item"),
      projectId,
      sequenceId,
      identifier: `${project.identifier}-${sequenceId}`,
      title: input.title.trim(),
      descriptionHtml: input.descriptionHtml ?? "",
      stateId: input.stateId,
      priority: input.priority ?? "none",
      assigneeIds: input.assigneeIds ?? [],
      epicId: input.epicId ?? null,
      startDate: input.startDate ?? null,
      dueDate: input.dueDate ?? null,
      sortOrder: (orderedItems(database, projectId, input.stateId).length + 1) * 1000,
      createdAt: timestamp,
      updatedAt: timestamp,
      version: 1,
    };
    database.workItems.push(workItem);
    database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    recalculateEpics(database, projectId);
    writeDatabase(database);
    return workItem;
  },

  async updateWorkItem(workspaceSlug, projectId, workItemId, input, version) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const workItem = requireWorkItem(database, projectId, workItemId);
    assertVersion(workItem.version, version);
    if (input.stateId) requireState(database, projectId, input.stateId);
    if (input.epicId) requireEpic(database, projectId, input.epicId);
    const previousStateId = workItem.stateId;
    Object.assign(workItem, input, { updatedAt: now(), version: workItem.version + 1 });
    if (input.stateId && input.stateId !== previousStateId) {
      workItem.sortOrder = (orderedItems(database, projectId, input.stateId).length + 1) * 1000;
      database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    }
    recalculateEpics(database, projectId);
    writeDatabase(database);
    return workItem;
  },

  async moveWorkItem(workspaceSlug, projectId, input) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    requireState(database, projectId, input.toStateId);
    const workItem = requireWorkItem(database, projectId, input.workItemId);
    assertVersion(workItem.version, input.entityVersion);
    if ((database.boardVersions[projectId] ?? 1) !== input.boardVersion) {
      throw new ApiError({
        status: 409,
        code: "BOARD_VERSION_CONFLICT",
        message: "Порядок доски изменился. Доска будет обновлена.",
      });
    }
    insertMovedItem(database, input, workItem);
    workItem.updatedAt = now();
    workItem.version += 1;
    database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    recalculateEpics(database, projectId);
    writeDatabase(database);
    const result: MoveWorkItemResult = {
      workItem,
      columns: buildColumns(database, projectId),
      boardVersion: database.boardVersions[projectId] ?? 1,
    };
    return result;
  },

  async deleteWorkItem(workspaceSlug, projectId, workItemId, version) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const workItem = requireWorkItem(database, projectId, workItemId);
    assertVersion(workItem.version, version);
    database.workItems = database.workItems.filter((candidate) => candidate.id !== workItemId);
    database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    recalculateEpics(database, projectId);
    writeDatabase(database);
  },

  async listEpics(workspaceSlug, projectId, filters, signal) {
    await wait(signal);
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    recalculateEpics(database, projectId);
    const search = filters.search?.trim().toLocaleLowerCase("ru");
    writeDatabase(database);
    return database.epics
      .filter((epic) => epic.projectId === projectId)
      .filter((epic) => !search || epic.name.toLocaleLowerCase("ru").includes(search))
      .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
  },

  async getEpic(workspaceSlug, projectId, epicId, signal) {
    await wait(signal);
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    recalculateEpics(database, projectId);
    return requireEpic(database, projectId, epicId);
  },

  async createEpic(workspaceSlug, projectId, input) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const timestamp = now();
    const epic: Epic = {
      id: createId("epic"),
      projectId,
      name: input.name.trim(),
      description: input.description?.trim() ?? "",
      color: input.color ?? nextColor(database.epics.length),
      startDate: input.startDate ?? null,
      targetDate: input.targetDate ?? null,
      workItemIds: [],
      progress: { total: 0, completed: 0, percentage: 0 },
      createdAt: timestamp,
      updatedAt: timestamp,
      version: 1,
    };
    database.epics.push(epic);
    writeDatabase(database);
    return epic;
  },

  async updateEpic(workspaceSlug, projectId, epicId, input, version) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const epic = requireEpic(database, projectId, epicId);
    assertVersion(epic.version, version);
    Object.assign(epic, input, { updatedAt: now(), version: epic.version + 1 });
    writeDatabase(database);
    return epic;
  },

  async deleteEpic(workspaceSlug, projectId, epicId, version) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const epic = requireEpic(database, projectId, epicId);
    assertVersion(epic.version, version);
    for (const workItem of database.workItems.filter((item) => item.epicId === epicId)) workItem.epicId = null;
    database.epics = database.epics.filter((candidate) => candidate.id !== epicId);
    writeDatabase(database);
  },

  async setEpicWorkItems(workspaceSlug, projectId, epicId, workItemIds) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const epic = requireEpic(database, projectId, epicId);
    const selected = new Set(workItemIds);
    for (const workItem of database.workItems.filter((item) => item.projectId === projectId)) {
      if (selected.has(workItem.id)) workItem.epicId = epicId;
      else if (workItem.epicId === epicId) workItem.epicId = null;
    }
    recalculateEpics(database, projectId);
    epic.version += 1;
    writeDatabase(database);
    return epic;
  },

  async listStates(workspaceSlug, projectId, signal) {
    await wait(signal);
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    return database.states.filter((state) => state.projectId === projectId).sort((a, b) => a.order - b.order);
  },

  async createState(workspaceSlug, projectId, input) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const projectStates = database.states.filter((state) => state.projectId === projectId);
    const state: WorkflowState = {
      id: createId("state"),
      projectId,
      name: input.name.trim(),
      color: input.color,
      group: input.group,
      order: projectStates.length,
      isDefault: false,
      version: 1,
    };
    database.states.push(state);
    database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    writeDatabase(database);
    return state;
  },

  async updateState(workspaceSlug, projectId, stateId, input, version) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const state = requireState(database, projectId, stateId);
    assertVersion(state.version, version);
    if (input.isDefault) {
      for (const candidate of database.states.filter((item) => item.projectId === projectId)) candidate.isDefault = false;
    }
    Object.assign(state, input, { version: state.version + 1 });
    database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    writeDatabase(database);
    return state;
  },

  async reorderStates(workspaceSlug, projectId, orderedStateIds) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const states = database.states.filter((state) => state.projectId === projectId);
    if (states.length !== orderedStateIds.length || states.some((state) => !orderedStateIds.includes(state.id))) {
      throw new ApiError({ status: 422, code: "INVALID_STATE_ORDER", message: "Передан неполный порядок состояний" });
    }
    orderedStateIds.forEach((id, order) => {
      const state = states.find((candidate) => candidate.id === id);
      if (state) state.order = order;
    });
    database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    writeDatabase(database);
    return states.sort((a, b) => a.order - b.order);
  },

  async deleteState(workspaceSlug, projectId, stateId, replacementStateId) {
    await wait();
    const database = readDatabase();
    requireProject(database, workspaceSlug, projectId);
    const state = requireState(database, projectId, stateId);
    requireState(database, projectId, replacementStateId);
    if (state.isDefault) {
      throw new ApiError({
        status: 409,
        code: "DEFAULT_STATE_DELETE_FORBIDDEN",
        message: "Сначала назначьте другое состояние по умолчанию",
      });
    }
    const targetItems = orderedItems(database, projectId, replacementStateId);
    const movingItems = orderedItems(database, projectId, stateId);
    for (const workItem of movingItems) workItem.stateId = replacementStateId;
    resequence([...targetItems, ...movingItems]);
    database.states = database.states.filter((candidate) => candidate.id !== stateId);
    database.states
      .filter((candidate) => candidate.projectId === projectId)
      .sort((a, b) => a.order - b.order)
      .forEach((candidate, order) => {
        candidate.order = order;
      });
    database.boardVersions[projectId] = (database.boardVersions[projectId] ?? 1) + 1;
    recalculateEpics(database, projectId);
    writeDatabase(database);
  },
};
