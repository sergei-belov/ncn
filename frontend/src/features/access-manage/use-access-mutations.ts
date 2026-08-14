import { toValue, type MaybeRefOrGetter } from "vue";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

import {
  authzKeys,
  useAuthzApi,
  type ProjectAccessRole,
  type ProjectMembership,
  type ServiceRestriction,
  type WorkspaceMembership,
  type WorkspaceRole,
} from "@/entities/authz";
import type { UUID } from "@/shared/lib/domain-primitives";

export function useAccessMutations(
  workspaceId: MaybeRefOrGetter<string>,
  projectId: MaybeRefOrGetter<UUID | undefined>,
) {
  const api = useAuthzApi();
  const queryClient = useQueryClient();

  async function refreshWorkspace(): Promise<void> {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: authzKeys.workspaceMemberships(toValue(workspaceId)) }),
      queryClient.invalidateQueries({ queryKey: authzKeys.session() }),
    ]);
  }

  async function refreshProject(): Promise<void> {
    const id = toValue(projectId);
    if (!id) return;
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: authzKeys.projectMemberships(id) }),
      queryClient.invalidateQueries({ queryKey: authzKeys.session() }),
    ]);
  }

  const addWorkspace = useMutation({
    mutationFn: (input: { userId: UUID; role: WorkspaceRole }) =>
      api.addWorkspaceMembership(toValue(workspaceId), input),
    onSuccess: refreshWorkspace,
    onError: refreshWorkspace,
  });

  const updateWorkspace = useMutation({
    mutationFn: ({ membership, role }: { membership: WorkspaceMembership; role: WorkspaceRole }) =>
      api.updateWorkspaceMembership(toValue(workspaceId), membership.userId, {
        role,
        expectedVersion: membership.version,
      }),
    onSuccess: refreshWorkspace,
    onError: refreshWorkspace,
  });

  const revokeWorkspace = useMutation({
    mutationFn: (membership: WorkspaceMembership) =>
      api.revokeWorkspaceMembership(toValue(workspaceId), membership.userId, membership.version),
    onSuccess: refreshWorkspace,
    onError: refreshWorkspace,
  });

  const addProject = useMutation({
    mutationFn: (input: { userId: UUID; role: ProjectAccessRole }) => {
      const id = toValue(projectId);
      if (!id) throw new Error("Project scope is required");
      return api.addProjectMembership(id, input);
    },
    onSuccess: refreshProject,
    onError: refreshProject,
  });

  const updateProject = useMutation({
    mutationFn: ({ membership, role }: { membership: ProjectMembership; role: ProjectAccessRole }) => {
      const id = toValue(projectId);
      if (!id) throw new Error("Project scope is required");
      return api.updateProjectMembership(id, membership.userId, {
        role,
        expectedVersion: membership.version,
      });
    },
    onSuccess: refreshProject,
    onError: refreshProject,
  });

  const revokeProject = useMutation({
    mutationFn: (membership: ProjectMembership) => {
      const id = toValue(projectId);
      if (!id) throw new Error("Project scope is required");
      return api.revokeProjectMembership(id, membership.userId, membership.version);
    },
    onSuccess: refreshProject,
    onError: refreshProject,
  });

  const setServiceRestriction = useMutation({
    mutationFn: ({
      membership,
      serviceId,
      role,
      restriction,
    }: {
      membership: ProjectMembership;
      serviceId: string;
      role: ProjectAccessRole;
      restriction?: ServiceRestriction;
    }) => {
      const id = toValue(projectId);
      if (!id) throw new Error("Project scope is required");
      return api.setServiceRestriction(id, membership.userId, serviceId, {
        role,
        expectedVersion: restriction?.version ?? null,
      });
    },
    onSuccess: refreshProject,
    onError: refreshProject,
  });

  const removeServiceRestriction = useMutation({
    mutationFn: ({ membership, restriction }: { membership: ProjectMembership; restriction: ServiceRestriction }) => {
      const id = toValue(projectId);
      if (!id) throw new Error("Project scope is required");
      return api.removeServiceRestriction(
        id,
        membership.userId,
        restriction.serviceId,
        restriction.version,
      );
    },
    onSuccess: refreshProject,
    onError: refreshProject,
  });

  return {
    addWorkspace,
    updateWorkspace,
    revokeWorkspace,
    addProject,
    updateProject,
    revokeProject,
    setServiceRestriction,
    removeServiceRestriction,
  };
}

