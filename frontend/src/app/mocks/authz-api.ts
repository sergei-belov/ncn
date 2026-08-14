import type {
  AuthzApi,
  AuthzSession,
  CursorPage,
  MembershipFilters,
  ProjectMembership,
  ServiceRestriction,
  WorkspaceMembership,
  WorkspaceRole,
} from "@/entities/authz";
import { serviceRoleFitsProjectRole } from "@/entities/authz";
import { ApiError } from "@/shared/api/api-error";
import type { UUID } from "@/shared/lib/domain-primitives";
import { createId } from "@/shared/lib/id";

import { readDatabase, writeDatabase, type MockDatabase } from "./database";

const latency = 100;

async function wait(signal?: AbortSignal): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const timer = window.setTimeout(resolve, latency + Math.floor(Math.random() * 60));
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

function fail(status: number, code: string, message: string, current?: unknown): never {
  throw new ApiError({ status, code, message, current });
}

function requireCurrentUser(database: MockDatabase) {
  const user = database.authzUsers.find((candidate) => candidate.id === database.currentUserId);
  if (!user) return fail(401, "IDENTITY_UNTRUSTED", "Не удалось подтвердить текущую сессию");
  if (!user.isActive) return fail(403, "USER_DISABLED", "Учётная запись отключена. Обратитесь в поддержку.");
  return user;
}

function requireTargetUser(database: MockDatabase, userId: UUID) {
  const user = database.authzUsers.find((candidate) => candidate.id === userId);
  if (!user) return fail(404, "USER_NOT_FOUND", "Пользователь не найден");
  if (!user.isActive) return fail(409, "USER_DISABLED", "Нельзя назначить доступ отключённому пользователю");
  return user;
}

function workspaceActorRole(database: MockDatabase, workspaceId: string): WorkspaceRole {
  const actor = requireCurrentUser(database);
  const role = database.workspaceMemberships.find(
    (membership) => membership.workspaceId === workspaceId && membership.userId === actor.id,
  )?.role;
  if (role !== "owner" && role !== "admin") {
    return fail(403, "ROLE_INSUFFICIENT", "Недостаточно прав для управления доступом workspace");
  }
  return role;
}

function projectActor(database: MockDatabase, projectId: UUID): ProjectMembership {
  const actor = requireCurrentUser(database);
  const membership = database.projectMemberships.find(
    (candidate) => candidate.projectId === projectId && candidate.userId === actor.id,
  );
  if (!membership || membership.role !== "admin") {
    return fail(403, "ROLE_INSUFFICIENT", "Недостаточно прав для управления доступом проекта");
  }
  return membership;
}

function requireWorkspaceMembership(
  database: MockDatabase,
  workspaceId: string,
  userId: UUID,
): WorkspaceMembership {
  return (
    database.workspaceMemberships.find(
      (membership) => membership.workspaceId === workspaceId && membership.userId === userId,
    ) ?? fail(404, "MEMBERSHIP_NOT_FOUND", "Доступ пользователя к workspace не найден")
  );
}

function requireProjectMembership(database: MockDatabase, projectId: UUID, userId: UUID): ProjectMembership {
  return (
    database.projectMemberships.find(
      (membership) => membership.projectId === projectId && membership.userId === userId,
    ) ?? fail(404, "MEMBERSHIP_NOT_FOUND", "Доступ пользователя к проекту не найден")
  );
}

function assertVersion(membership: { version: number }, expectedVersion: number): void {
  if (membership.version !== expectedVersion) {
    fail(409, "VERSION_CONFLICT", "Доступ уже изменился. Проверьте актуальные данные и повторите действие.", membership);
  }
}

function assertWorkspaceRoleAllowed(targetRole: WorkspaceRole): void {
  if (targetRole === "owner") {
    fail(409, "OWNER_TRANSFER_REQUIRED", "Передача владельца выполняется отдельной защищённой операцией");
  }
}

function assertOwnerCoverage(database: MockDatabase, workspaceId: string, membership: WorkspaceMembership): void {
  const owners = database.workspaceMemberships.filter(
    (candidate) => candidate.workspaceId === workspaceId && candidate.role === "owner",
  );
  if (membership.role === "owner" && owners.length === 1) {
    fail(409, "LAST_WORKSPACE_OWNER", "Сначала назначьте другого владельца workspace");
  }
}

function assertProjectAdminCoverage(database: MockDatabase, projectId: UUID, membership: ProjectMembership): void {
  const admins = database.projectMemberships.filter(
    (candidate) => candidate.projectId === projectId && candidate.role === "admin",
  );
  if (membership.role === "admin" && admins.length === 1) {
    fail(409, "LAST_PROJECT_ADMIN", "Сначала назначьте другого администратора проекта");
  }
}

function paginate<T extends { id: UUID; user: { name: string; email: string } }>(
  items: T[],
  filters: MembershipFilters,
): CursorPage<T> {
  const search = filters.search?.trim().toLocaleLowerCase("ru");
  const matched = items
    .filter((item) => !search || `${item.user.name} ${item.user.email} ${item.user.id}`.toLocaleLowerCase("ru").includes(search))
    .sort((left, right) => left.id.localeCompare(right.id));
  const offset = Number.parseInt(filters.cursor?.replace("offset:", "") ?? "0", 10);
  const safeOffset = Number.isFinite(offset) && offset >= 0 ? offset : 0;
  const limit = Math.min(Math.max(filters.limit ?? 50, 1), 100);
  const pageItems = matched.slice(safeOffset, safeOffset + limit);
  const nextOffset = safeOffset + pageItems.length;
  return {
    items: pageItems,
    nextCursor: nextOffset < matched.length ? `offset:${nextOffset}` : null,
  };
}

function session(database: MockDatabase): AuthzSession {
  const user = requireCurrentUser(database);
  return {
    user,
    workspaceAccess: database.workspaceMemberships
      .filter((membership) => membership.userId === user.id)
      .map((membership) => ({ workspaceId: membership.workspaceId, role: membership.role })),
    projectAccess: database.projectMemberships
      .filter((membership) => membership.userId === user.id)
      .map((membership) => ({
        workspaceId: membership.workspaceId,
        projectId: membership.projectId,
        role: membership.role,
      })),
    policyVersion: "demo-v1",
  };
}

export const mockAuthzApi: AuthzApi = {
  async resolveSession(signal) {
    await wait(signal);
    return session(readDatabase());
  },

  async getCurrentSession(signal) {
    await wait(signal);
    return session(readDatabase());
  },

  async listWorkspaceMemberships(workspaceId, filters, signal) {
    await wait(signal);
    const database = readDatabase();
    workspaceActorRole(database, workspaceId);
    return paginate(
      database.workspaceMemberships.filter((membership) => membership.workspaceId === workspaceId),
      filters,
    );
  },

  async addWorkspaceMembership(workspaceId, input) {
    await wait();
    const database = readDatabase();
    workspaceActorRole(database, workspaceId);
    assertWorkspaceRoleAllowed(input.role);
    const user = requireTargetUser(database, input.userId);
    if (
      database.workspaceMemberships.some(
        (membership) => membership.workspaceId === workspaceId && membership.userId === input.userId,
      )
    ) {
      fail(409, "MEMBERSHIP_EXISTS", "У пользователя уже есть доступ к workspace");
    }
    const membership: WorkspaceMembership = {
      id: createId("workspace-user"),
      workspaceId,
      userId: user.id,
      user,
      role: input.role,
      version: 1,
    };
    database.workspaceMemberships.push(membership);
    writeDatabase(database);
    return membership;
  },

  async updateWorkspaceMembership(workspaceId, userId, input) {
    await wait();
    const database = readDatabase();
    workspaceActorRole(database, workspaceId);
    const membership = requireWorkspaceMembership(database, workspaceId, userId);
    assertVersion(membership, input.expectedVersion);
    if (membership.role === "owner" && input.role !== "owner") assertOwnerCoverage(database, workspaceId, membership);
    if (membership.role === "owner") {
      fail(409, "OWNER_TRANSFER_REQUIRED", "Передача владельца выполняется отдельной защищённой операцией");
    }
    assertWorkspaceRoleAllowed(input.role);
    membership.role = input.role;
    membership.version += 1;
    writeDatabase(database);
    return membership;
  },

  async revokeWorkspaceMembership(workspaceId, userId, expectedVersion) {
    await wait();
    const database = readDatabase();
    workspaceActorRole(database, workspaceId);
    const membership = requireWorkspaceMembership(database, workspaceId, userId);
    assertVersion(membership, expectedVersion);
    assertOwnerCoverage(database, workspaceId, membership);
    if (membership.role === "owner") {
      fail(409, "OWNER_TRANSFER_REQUIRED", "Передача владельца выполняется отдельной защищённой операцией");
    }
    database.workspaceMemberships = database.workspaceMemberships.filter((candidate) => candidate.id !== membership.id);
    writeDatabase(database);
  },

  async listProjectMemberships(projectId, filters, signal) {
    await wait(signal);
    const database = readDatabase();
    projectActor(database, projectId);
    return paginate(
      database.projectMemberships.filter((membership) => membership.projectId === projectId),
      filters,
    );
  },

  async addProjectMembership(projectId, input) {
    await wait();
    const database = readDatabase();
    const actor = projectActor(database, projectId);
    const user = requireTargetUser(database, input.userId);
    if (
      database.projectMemberships.some(
        (membership) => membership.projectId === projectId && membership.userId === input.userId,
      )
    ) {
      fail(409, "MEMBERSHIP_EXISTS", "У пользователя уже есть доступ к проекту");
    }
    const membership: ProjectMembership = {
      id: createId("project-user"),
      workspaceId: actor.workspaceId,
      projectId,
      userId: user.id,
      user,
      role: input.role,
      source: "manual",
      version: 1,
      serviceRestrictions: [],
    };
    database.projectMemberships.push(membership);
    writeDatabase(database);
    return membership;
  },

  async updateProjectMembership(projectId, userId, input) {
    await wait();
    const database = readDatabase();
    projectActor(database, projectId);
    const membership = requireProjectMembership(database, projectId, userId);
    assertVersion(membership, input.expectedVersion);
    if (membership.role === "admin" && input.role !== "admin") assertProjectAdminCoverage(database, projectId, membership);
    if (membership.serviceRestrictions.some((restriction) => !serviceRoleFitsProjectRole(restriction.role, input.role))) {
      fail(
        409,
        "SERVICE_RESTRICTION_CONFLICT",
        "Сначала ослабьте несовместимые ограничения сервисов для новой роли",
      );
    }
    membership.role = input.role;
    membership.version += 1;
    writeDatabase(database);
    return membership;
  },

  async revokeProjectMembership(projectId, userId, expectedVersion) {
    await wait();
    const database = readDatabase();
    projectActor(database, projectId);
    const membership = requireProjectMembership(database, projectId, userId);
    assertVersion(membership, expectedVersion);
    assertProjectAdminCoverage(database, projectId, membership);
    database.projectMemberships = database.projectMemberships.filter((candidate) => candidate.id !== membership.id);
    writeDatabase(database);
  },

  async setServiceRestriction(projectId, userId, serviceId, input) {
    await wait();
    const database = readDatabase();
    projectActor(database, projectId);
    const membership = requireProjectMembership(database, projectId, userId);
    if (!serviceId.trim()) fail(400, "SERVICE_UNKNOWN", "Укажите идентификатор сервиса");
    if (!serviceRoleFitsProjectRole(input.role, membership.role)) {
      fail(422, "SERVICE_ROLE_ELEVATION", "Ограничение сервиса не может быть сильнее роли проекта");
    }
    const existing = membership.serviceRestrictions.find((restriction) => restriction.serviceId === serviceId);
    if (!existing) {
      if (input.expectedVersion !== null) fail(409, "VERSION_CONFLICT", "Ограничение сервиса уже изменилось");
      const restriction: ServiceRestriction = {
        id: createId("service-user"),
        projectUserId: membership.id,
        serviceId,
        role: input.role,
        version: 1,
      };
      membership.serviceRestrictions.push(restriction);
      writeDatabase(database);
      return restriction;
    }
    if (input.expectedVersion === null) {
      fail(409, "RESTRICTION_EXISTS", "Для этого сервиса уже задано ограничение", existing);
    }
    assertVersion(existing, input.expectedVersion);
    if (existing.role === input.role) return existing;
    existing.role = input.role;
    existing.version += 1;
    writeDatabase(database);
    return existing;
  },

  async removeServiceRestriction(projectId, userId, serviceId, expectedVersion) {
    await wait();
    const database = readDatabase();
    projectActor(database, projectId);
    const membership = requireProjectMembership(database, projectId, userId);
    const restriction = membership.serviceRestrictions.find((candidate) => candidate.serviceId === serviceId);
    if (!restriction) fail(404, "MEMBERSHIP_NOT_FOUND", "Ограничение сервиса не найдено");
    assertVersion(restriction, expectedVersion);
    membership.serviceRestrictions = membership.serviceRestrictions.filter((candidate) => candidate.id !== restriction.id);
    writeDatabase(database);
  },
};
