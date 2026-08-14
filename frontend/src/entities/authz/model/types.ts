import type { UUID } from "@/shared/lib/domain-primitives";

export type WorkspaceRole = "owner" | "admin" | "member";
export type ProjectAccessRole = "admin" | "member" | "viewer";
export type MembershipSource = "manual" | "bootstrap";

export interface AuthzUser {
  id: UUID;
  email: string;
  name: string;
  isActive: boolean;
}

export interface WorkspaceAccessSummary {
  workspaceId: string;
  role: WorkspaceRole;
}

export interface ProjectAccessSummary {
  workspaceId: string;
  projectId: UUID;
  role: ProjectAccessRole;
}

export interface AuthzSession {
  user: AuthzUser;
  workspaceAccess: WorkspaceAccessSummary[];
  projectAccess: ProjectAccessSummary[];
  policyVersion: string;
}

export interface WorkspaceMembership {
  id: UUID;
  workspaceId: string;
  userId: UUID;
  user: AuthzUser;
  role: WorkspaceRole;
  version: number;
}

export interface ServiceRestriction {
  id: UUID;
  projectUserId: UUID;
  serviceId: string;
  role: ProjectAccessRole;
  version: number;
}

export interface ProjectMembership {
  id: UUID;
  workspaceId: string;
  projectId: UUID;
  userId: UUID;
  user: AuthzUser;
  role: ProjectAccessRole;
  source: MembershipSource;
  version: number;
  serviceRestrictions: ServiceRestriction[];
}

export interface CursorPage<T> {
  items: T[];
  nextCursor: string | null;
}

export interface MembershipFilters {
  search?: string;
  cursor?: string;
  limit?: number;
}

export interface AddWorkspaceMembershipInput {
  userId: UUID;
  role: WorkspaceRole;
}

export interface UpdateWorkspaceMembershipInput {
  role: WorkspaceRole;
  expectedVersion: number;
}

export interface AddProjectMembershipInput {
  userId: UUID;
  role: ProjectAccessRole;
}

export interface UpdateProjectMembershipInput {
  role: ProjectAccessRole;
  expectedVersion: number;
}

export interface SetServiceRestrictionInput {
  role: ProjectAccessRole;
  expectedVersion: number | null;
}

export type AccessMembership = WorkspaceMembership | ProjectMembership;

export function isProjectMembership(membership: AccessMembership): membership is ProjectMembership {
  return "projectId" in membership;
}

export function workspaceRoleFor(session: AuthzSession | undefined, workspaceId: string): WorkspaceRole | undefined {
  return session?.workspaceAccess.find((access) => access.workspaceId === workspaceId)?.role;
}

export function projectRoleFor(
  session: AuthzSession | undefined,
  projectId: UUID,
): ProjectAccessRole | undefined {
  return session?.projectAccess.find((access) => access.projectId === projectId)?.role;
}

export function canManageWorkspaceAccess(role: WorkspaceRole | undefined): boolean {
  return role === "owner" || role === "admin";
}

export function canManageProjectAccess(role: ProjectAccessRole | undefined): boolean {
  return role === "admin";
}

const projectRoleRank: Record<ProjectAccessRole, number> = { viewer: 1, member: 2, admin: 3 };

export function serviceRoleFitsProjectRole(serviceRole: ProjectAccessRole, projectRole: ProjectAccessRole): boolean {
  return projectRoleRank[serviceRole] <= projectRoleRank[projectRole];
}

