import { computed, toValue, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";

import type { UUID } from "@/shared/lib/domain-primitives";

import { useAgentApi } from "./port";

export const agentKeys = {
  all: (workspaceSlug: string, projectId: UUID) => ["workspaces", workspaceSlug, "projects", projectId, "agents"] as const,
  list: (workspaceSlug: string, projectId: UUID) => [...agentKeys.all(workspaceSlug, projectId), "list"] as const,
  detail: (workspaceSlug: string, projectId: UUID, agentId: UUID) =>
    [...agentKeys.all(workspaceSlug, projectId), "detail", agentId] as const,
};

export function useAgentsQuery(
  workspaceSlug: MaybeRefOrGetter<string>,
  projectId: MaybeRefOrGetter<UUID>,
) {
  const api = useAgentApi();
  return useQuery({
    queryKey: computed(() => agentKeys.list(toValue(workspaceSlug), toValue(projectId))),
    queryFn: ({ signal }) => api.listAgents(toValue(workspaceSlug), toValue(projectId), signal),
    staleTime: 20_000,
  });
}

export function useAgentQuery(
  workspaceSlug: MaybeRefOrGetter<string>,
  projectId: MaybeRefOrGetter<UUID>,
  agentId: MaybeRefOrGetter<UUID | undefined>,
) {
  const api = useAgentApi();
  return useQuery({
    queryKey: computed(() => agentKeys.detail(toValue(workspaceSlug), toValue(projectId), toValue(agentId) ?? "missing")),
    queryFn: ({ signal }) => api.getAgent(toValue(workspaceSlug), toValue(projectId), toValue(agentId)!, signal),
    enabled: computed(() => Boolean(toValue(agentId))),
    staleTime: 20_000,
  });
}
