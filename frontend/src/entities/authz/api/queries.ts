import { computed, toValue, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { MembershipFilters } from "../model/types";
import { useAuthzApi } from "./port";

export const authzKeys = {
  all: ["authz"] as const,
  session: () => [...authzKeys.all, "session"] as const,
  workspaceMemberships: (workspaceId: string) => [...authzKeys.all, "workspaces", workspaceId, "members"] as const,
  workspaceMembershipList: (workspaceId: string, filters: MembershipFilters) =>
    [...authzKeys.workspaceMemberships(workspaceId), filters] as const,
  projectMemberships: (projectId: UUID) => [...authzKeys.all, "projects", projectId, "members"] as const,
  projectMembershipList: (projectId: UUID, filters: MembershipFilters) =>
    [...authzKeys.projectMemberships(projectId), filters] as const,
};

export function useAuthzSessionQuery() {
  const api = useAuthzApi();
  return useQuery({
    queryKey: authzKeys.session(),
    queryFn: ({ signal }) => api.resolveSession(signal),
    staleTime: 60_000,
    retry: (failureCount, error) => {
      const status = typeof error === "object" && error && "status" in error ? Number(error.status) : 0;
      return status === 503 && failureCount < 2;
    },
  });
}

export function useWorkspaceMembershipsQuery(
  workspaceId: MaybeRefOrGetter<string>,
  filters: MaybeRefOrGetter<MembershipFilters>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  const api = useAuthzApi();
  return useQuery({
    queryKey: computed(() => authzKeys.workspaceMembershipList(toValue(workspaceId), toValue(filters))),
    queryFn: ({ signal }) => api.listWorkspaceMemberships(toValue(workspaceId), toValue(filters), signal),
    enabled: computed(() => toValue(enabled)),
    staleTime: 15_000,
  });
}

export function useProjectMembershipsQuery(
  projectId: MaybeRefOrGetter<UUID>,
  filters: MaybeRefOrGetter<MembershipFilters>,
  enabled: MaybeRefOrGetter<boolean> = true,
) {
  const api = useAuthzApi();
  return useQuery({
    queryKey: computed(() => authzKeys.projectMembershipList(toValue(projectId), toValue(filters))),
    queryFn: ({ signal }) => api.listProjectMemberships(toValue(projectId), toValue(filters), signal),
    enabled: computed(() => toValue(enabled)),
    staleTime: 15_000,
  });
}

