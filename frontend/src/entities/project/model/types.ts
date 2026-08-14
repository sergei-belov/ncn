import type { ISODateTime, UUID } from "@/shared/lib/domain-primitives";

export type ProjectRole = "admin" | "member" | "viewer";
export type ProjectAccess = "private" | "workspace";

export interface ProjectPermissions {
  canViewProject: boolean;
  canEditProject: boolean;
  canArchiveProject: boolean;
  canManageStates: boolean;
  canManageAgents: boolean;
  canCreateWorkItem: boolean;
  canEditWorkItem: boolean;
  canMoveWorkItem: boolean;
  canDeleteWorkItem: boolean;
  canCreateEpic: boolean;
  canEditEpic: boolean;
  canDeleteEpic: boolean;
}

export interface Project {
  id: UUID;
  workspaceSlug: string;
  name: string;
  identifier: string;
  description: string;
  access: ProjectAccess;
  role: ProjectRole;
  color: string;
  archivedAt: ISODateTime | null;
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
  version: number;
  permissions: ProjectPermissions;
}

export interface ProjectFilters {
  search?: string;
  archived?: boolean;
}

export interface CreateProjectInput {
  name: string;
  identifier: string;
  description?: string;
  access: ProjectAccess;
}

export interface UpdateProjectInput {
  name?: string;
  description?: string;
  access?: ProjectAccess;
}
