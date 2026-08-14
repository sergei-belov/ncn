import { inject, type InjectionKey } from "vue";

import type { UUID } from "@/shared/lib/domain-primitives";

import type {
  AddProjectMembershipInput,
  AddWorkspaceMembershipInput,
  AuthzSession,
  CursorPage,
  MembershipFilters,
  ProjectMembership,
  ServiceRestriction,
  SetServiceRestrictionInput,
  UpdateProjectMembershipInput,
  UpdateWorkspaceMembershipInput,
  WorkspaceMembership,
} from "../model/types";

export interface AuthzApi {
  resolveSession(signal?: AbortSignal): Promise<AuthzSession>;
  getCurrentSession(signal?: AbortSignal): Promise<AuthzSession>;
  listWorkspaceMemberships(
    workspaceId: string,
    filters: MembershipFilters,
    signal?: AbortSignal,
  ): Promise<CursorPage<WorkspaceMembership>>;
  addWorkspaceMembership(workspaceId: string, input: AddWorkspaceMembershipInput): Promise<WorkspaceMembership>;
  updateWorkspaceMembership(
    workspaceId: string,
    userId: UUID,
    input: UpdateWorkspaceMembershipInput,
  ): Promise<WorkspaceMembership>;
  revokeWorkspaceMembership(workspaceId: string, userId: UUID, expectedVersion: number): Promise<void>;
  listProjectMemberships(
    projectId: UUID,
    filters: MembershipFilters,
    signal?: AbortSignal,
  ): Promise<CursorPage<ProjectMembership>>;
  addProjectMembership(projectId: UUID, input: AddProjectMembershipInput): Promise<ProjectMembership>;
  updateProjectMembership(
    projectId: UUID,
    userId: UUID,
    input: UpdateProjectMembershipInput,
  ): Promise<ProjectMembership>;
  revokeProjectMembership(projectId: UUID, userId: UUID, expectedVersion: number): Promise<void>;
  setServiceRestriction(
    projectId: UUID,
    userId: UUID,
    serviceId: string,
    input: SetServiceRestrictionInput,
  ): Promise<ServiceRestriction>;
  removeServiceRestriction(
    projectId: UUID,
    userId: UUID,
    serviceId: string,
    expectedVersion: number,
  ): Promise<void>;
}

export const authzApiKey: InjectionKey<AuthzApi> = Symbol("authz-api");

export function useAuthzApi(): AuthzApi {
  const api = inject(authzApiKey);
  if (!api) throw new Error("Authz API provider is not installed");
  return api;
}

