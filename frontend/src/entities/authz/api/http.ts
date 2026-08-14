import { apiClient } from "@/shared/api/api-client";
import { voidSchema } from "@/shared/api/schema";
import { queryString } from "@/shared/api/url";

import type { AuthzApi } from "./port";
import {
  mapAuthzSession,
  mapProjectMembership,
  mapProjectMembershipPage,
  mapServiceRestriction,
  mapWorkspaceMembership,
  mapWorkspaceMembershipPage,
  wireAuthzSessionSchema,
  wireProjectMembershipPageSchema,
  wireProjectMembershipSchema,
  wireServiceRestrictionResultSchema,
  wireWorkspaceMembershipPageSchema,
  wireWorkspaceMembershipSchema,
} from "./wire";

function workspaceMembersBase(workspaceId: string): string {
  return `/workspaces/${encodeURIComponent(workspaceId)}/members`;
}

function projectMembersBase(projectId: string): string {
  return `/projects/${encodeURIComponent(projectId)}/members`;
}

export const httpAuthzApi: AuthzApi = {
  async resolveSession(signal) {
    return mapAuthzSession(
      await apiClient.post("/auth/session/resolve", {}, { schema: wireAuthzSessionSchema, signal }),
    );
  },
  async getCurrentSession(signal) {
    return mapAuthzSession(await apiClient.get("/auth/me", { schema: wireAuthzSessionSchema, signal }));
  },
  async listWorkspaceMemberships(workspaceId, filters, signal) {
    const result = await apiClient.get(
      `${workspaceMembersBase(workspaceId)}${queryString({ search: filters.search, cursor: filters.cursor, limit: filters.limit?.toString() })}`,
      { schema: wireWorkspaceMembershipPageSchema, signal },
    );
    return mapWorkspaceMembershipPage(result);
  },
  async addWorkspaceMembership(workspaceId, input) {
    const result = await apiClient.post(
      workspaceMembersBase(workspaceId),
      { user_id: input.userId, role: input.role },
      { schema: wireWorkspaceMembershipSchema },
    );
    return mapWorkspaceMembership(result);
  },
  async updateWorkspaceMembership(workspaceId, userId, input) {
    const result = await apiClient.patch(
      `${workspaceMembersBase(workspaceId)}/${encodeURIComponent(userId)}`,
      { role: input.role, expected_version: input.expectedVersion },
      { schema: wireWorkspaceMembershipSchema },
    );
    return mapWorkspaceMembership(result);
  },
  async revokeWorkspaceMembership(workspaceId, userId, expectedVersion) {
    await apiClient.post(
      `${workspaceMembersBase(workspaceId)}/${encodeURIComponent(userId)}/revoke`,
      { expected_version: expectedVersion },
      { schema: voidSchema },
    );
  },
  async listProjectMemberships(projectId, filters, signal) {
    const result = await apiClient.get(
      `${projectMembersBase(projectId)}${queryString({ search: filters.search, cursor: filters.cursor, limit: filters.limit?.toString() })}`,
      { schema: wireProjectMembershipPageSchema, signal },
    );
    return mapProjectMembershipPage(result);
  },
  async addProjectMembership(projectId, input) {
    const result = await apiClient.post(
      projectMembersBase(projectId),
      { user_id: input.userId, role: input.role },
      { schema: wireProjectMembershipSchema },
    );
    return mapProjectMembership(result);
  },
  async updateProjectMembership(projectId, userId, input) {
    const result = await apiClient.patch(
      `${projectMembersBase(projectId)}/${encodeURIComponent(userId)}`,
      { role: input.role, expected_version: input.expectedVersion },
      { schema: wireProjectMembershipSchema },
    );
    return mapProjectMembership(result);
  },
  async revokeProjectMembership(projectId, userId, expectedVersion) {
    await apiClient.post(
      `${projectMembersBase(projectId)}/${encodeURIComponent(userId)}/revoke`,
      { expected_version: expectedVersion },
      { schema: voidSchema },
    );
  },
  async setServiceRestriction(projectId, userId, serviceId, input) {
    const result = await apiClient.put(
      `${projectMembersBase(projectId)}/${encodeURIComponent(userId)}/services/${encodeURIComponent(serviceId)}`,
      { role: input.role, expected_version: input.expectedVersion },
      { schema: wireServiceRestrictionResultSchema },
    );
    return mapServiceRestriction(result);
  },
  async removeServiceRestriction(projectId, userId, serviceId, expectedVersion) {
    await apiClient.delete(
      `${projectMembersBase(projectId)}/${encodeURIComponent(userId)}/services/${encodeURIComponent(serviceId)}`,
      { schema: voidSchema, body: { expected_version: expectedVersion } },
    );
  },
};
