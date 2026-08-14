import type { Agent } from "@/entities/agent";
import type { Epic } from "@/entities/epic";
import type { MemberSummary } from "@/entities/member";
import type { Project } from "@/entities/project";
import type { WorkItem } from "@/entities/work-item";
import type { WorkflowState } from "@/entities/workflow-state";
import type { UUID } from "@/shared/lib/domain-primitives";
import { permissionsForRole } from "@/entities/project";

export interface MockDatabase {
  schemaVersion: 2;
  boardVersions: Record<UUID, number>;
  projects: Project[];
  agents: Agent[];
  states: WorkflowState[];
  workItems: WorkItem[];
  epics: Epic[];
  members: MemberSummary[];
}

const STORAGE_KEY = "plane-inspired-mvp-db-v2";

const now = "2026-08-10T08:00:00.000Z";

function project(id: string, name: string, identifier: string, color: string, archived = false): Project {
  return {
    id,
    workspaceSlug: "demo",
    name,
    identifier,
    description:
      identifier === "WEB"
        ? "Новый кабинет клиента: от discovery до запуска первой публичной версии."
        : "Внутренний продукт для управления качеством и релизными проверками.",
    access: "workspace",
    role: "admin",
    color,
    archivedAt: archived ? "2026-07-01T10:00:00.000Z" : null,
    createdAt: "2026-06-02T10:00:00.000Z",
    updatedAt: now,
    version: 1,
    permissions: permissionsForRole("admin"),
  };
}

function coordinator(projectId: string, name = "Координатор проекта"): Agent {
  return {
    id: `agent-${projectId}-coordinator`,
    projectId,
    kind: "coordinator",
    name,
    description: "ИИ-менеджер проекта: анализирует состояние, строит план и делегирует работу ассистентам.",
    instructions: "Помогай команде достигать целей проекта, выявляй блокеры и риски, делегируй специализированные задачи подходящим ассистентам.",
    model: "qwen3:32b",
    memoryPolicy: "project",
    maxStepsPerRun: 50,
    approvalMode: "project",
    status: "active",
    systemToolNames: ["task-management"],
    createdAt: "2026-06-02T10:00:00.000Z",
    updatedAt: now,
    version: 1,
  };
}

function worker(id: string, projectId: string, name: string, description: string, instructions: string): Agent {
  return {
    id,
    projectId,
    kind: "worker",
    name,
    description,
    instructions,
    model: "qwen3:14b",
    memoryPolicy: "project",
    maxStepsPerRun: 25,
    approvalMode: "project",
    status: "active",
    systemToolNames: [],
    createdAt: "2026-08-01T09:00:00.000Z",
    updatedAt: now,
    version: 1,
  };
}

function statesFor(projectId: string, prefix: string): WorkflowState[] {
  return [
    { id: `${prefix}-backlog`, projectId, name: "Бэклог", color: "#94a3b8", group: "backlog", order: 0, isDefault: true, version: 1 },
    { id: `${prefix}-todo`, projectId, name: "К выполнению", color: "#60a5fa", group: "unstarted", order: 1, isDefault: false, version: 1 },
    { id: `${prefix}-progress`, projectId, name: "В работе", color: "#f59e0b", group: "started", order: 2, isDefault: false, version: 1 },
    { id: `${prefix}-done`, projectId, name: "Готово", color: "#22c55e", group: "completed", order: 3, isDefault: false, version: 1 },
  ];
}

function item(
  sequenceId: number,
  title: string,
  stateId: string,
  sortOrder: number,
  options: Partial<WorkItem> = {},
): WorkItem {
  return {
    id: `wi-web-${sequenceId}`,
    projectId: "project-web",
    sequenceId,
    identifier: `WEB-${sequenceId}`,
    title,
    descriptionHtml: "",
    stateId,
    priority: "none",
    assigneeIds: [],
    epicId: null,
    startDate: null,
    dueDate: null,
    sortOrder,
    createdAt: "2026-08-01T09:00:00.000Z",
    updatedAt: now,
    version: 1,
    ...options,
  };
}

export function createSeedDatabase(): MockDatabase {
  const members: MemberSummary[] = [
    { id: "member-alex", displayName: "Алексей Смирнов", email: "alex@example.com", avatarUrl: null, initials: "АС", isActive: true },
    { id: "member-maria", displayName: "Мария Волкова", email: "maria@example.com", avatarUrl: null, initials: "МВ", isActive: true },
    { id: "member-ilya", displayName: "Илья Орлов", email: "ilya@example.com", avatarUrl: null, initials: "ИО", isActive: true },
    { id: "member-nina", displayName: "Нина Белова", email: "nina@example.com", avatarUrl: null, initials: "НБ", isActive: true },
  ];

  const epics: Epic[] = [
    {
      id: "epic-onboarding",
      projectId: "project-web",
      name: "Первый запуск пользователя",
      description: "Регистрация, onboarding и пустые состояния нового кабинета.",
      color: "#8b5cf6",
      startDate: "2026-08-01",
      targetDate: "2026-08-29",
      workItemIds: ["wi-web-1", "wi-web-2", "wi-web-4", "wi-web-8"],
      progress: { total: 4, completed: 1, percentage: 25 },
      createdAt: "2026-07-28T08:00:00.000Z",
      updatedAt: now,
      version: 1,
    },
    {
      id: "epic-billing",
      projectId: "project-web",
      name: "Подписка и биллинг",
      description: "Тарифы, checkout, документы и управление подпиской.",
      color: "#0ea5e9",
      startDate: "2026-08-12",
      targetDate: "2026-09-15",
      workItemIds: ["wi-web-5", "wi-web-6", "wi-web-10"],
      progress: { total: 3, completed: 0, percentage: 0 },
      createdAt: "2026-07-30T08:00:00.000Z",
      updatedAt: now,
      version: 1,
    },
    {
      id: "epic-design-system",
      projectId: "project-web",
      name: "Основа интерфейса",
      description: "Токены, компоненты и адаптивный shell.",
      color: "#f97316",
      startDate: "2026-07-20",
      targetDate: "2026-08-20",
      workItemIds: ["wi-web-3", "wi-web-7", "wi-web-9"],
      progress: { total: 3, completed: 1, percentage: 33 },
      createdAt: "2026-07-20T08:00:00.000Z",
      updatedAt: now,
      version: 1,
    },
  ];

  const workItems: WorkItem[] = [
    item(1, "Спроектировать onboarding wizard", "web-progress", 1000, {
      priority: "high",
      assigneeIds: ["member-maria"],
      epicId: "epic-onboarding",
      startDate: "2026-08-04",
      dueDate: "2026-08-15",
      descriptionHtml: "<p>Собрать короткий wizard из трёх шагов и предусмотреть пропуск необязательных полей.</p>",
    }),
    item(2, "Добавить вход по magic link", "web-todo", 1000, {
      priority: "urgent",
      assigneeIds: ["member-alex"],
      epicId: "epic-onboarding",
      dueDate: "2026-08-18",
    }),
    item(3, "Зафиксировать semantic color tokens", "web-done", 1000, {
      priority: "medium",
      assigneeIds: ["member-nina"],
      epicId: "epic-design-system",
    }),
    item(4, "Пустое состояние списка проектов", "web-done", 2000, {
      priority: "low",
      assigneeIds: ["member-nina"],
      epicId: "epic-onboarding",
    }),
    item(5, "Экран выбора тарифа", "web-backlog", 1000, {
      priority: "high",
      assigneeIds: ["member-maria"],
      epicId: "epic-billing",
      dueDate: "2026-09-01",
    }),
    item(6, "Интеграция checkout", "web-backlog", 2000, {
      priority: "medium",
      assigneeIds: ["member-alex"],
      epicId: "epic-billing",
    }),
    item(7, "Адаптивный project sidebar", "web-progress", 2000, {
      priority: "medium",
      assigneeIds: ["member-ilya"],
      epicId: "epic-design-system",
      dueDate: "2026-08-14",
    }),
    item(8, "Продуктовый checklist первого входа", "web-todo", 2000, {
      priority: "low",
      assigneeIds: ["member-maria"],
      epicId: "epic-onboarding",
    }),
    item(9, "Компонент уведомлений", "web-todo", 3000, {
      priority: "medium",
      assigneeIds: ["member-ilya"],
      epicId: "epic-design-system",
    }),
    item(10, "История платежных документов", "web-backlog", 3000, {
      priority: "none",
      epicId: "epic-billing",
    }),
    item(11, "Проверить keyboard navigation", "web-progress", 3000, {
      priority: "high",
      assigneeIds: ["member-nina"],
      dueDate: "2026-08-12",
    }),
    item(12, "Подготовить launch checklist", "web-todo", 4000, {
      priority: "medium",
      assigneeIds: ["member-alex", "member-maria"],
    }),
  ];

  return {
    schemaVersion: 2,
    boardVersions: { "project-web": 1, "project-ncn": 1, "project-archive": 1 },
    projects: [
      project("project-web", "Кабинет клиента", "WEB", "#6d5dfc"),
      project("project-ncn", "Quality AI", "QAI", "#0ea5e9"),
      project("project-archive", "Маркетинговый сайт 2025", "MKT", "#64748b", true),
    ],
    agents: [
      coordinator("project-web"),
      worker(
        "agent-web-risk",
        "project-web",
        "Аналитик рисков",
        "Следит за сроками, зависимостями и блокерами.",
        "Анализируй состояние проекта, выявляй риски по срокам и зависимостям, возвращай приоритизированные рекомендации координатору.",
      ),
      worker(
        "agent-web-docs",
        "project-web",
        "Редактор документации",
        "Готовит проектные документы и отчёты.",
        "Собирай факты из доступного контекста, готовь краткие структурированные документы и явно отмечай недостающие данные.",
      ),
      coordinator("project-ncn"),
      coordinator("project-archive"),
    ],
    states: [...statesFor("project-web", "web"), ...statesFor("project-ncn", "ncn"), ...statesFor("project-archive", "mkt")],
    workItems,
    epics,
    members,
  };
}

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function readDatabase(): MockDatabase {
  if (!canUseStorage()) return createSeedDatabase();
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    const seed = createSeedDatabase();
    writeDatabase(seed);
    return seed;
  }
  try {
    const database = JSON.parse(raw) as Partial<MockDatabase>;
    if (database.schemaVersion === 2 && Array.isArray(database.agents)) return database as MockDatabase;
    const seed = createSeedDatabase();
    writeDatabase(seed);
    return seed;
  } catch {
    const seed = createSeedDatabase();
    writeDatabase(seed);
    return seed;
  }
}

export function writeDatabase(database: MockDatabase): void {
  if (canUseStorage()) window.localStorage.setItem(STORAGE_KEY, JSON.stringify(database));
}

export function resetDatabase(): void {
  if (canUseStorage()) window.localStorage.removeItem(STORAGE_KEY);
}
