import { computed, toValue, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";

import type { UUID } from "@/shared/lib/domain-primitives";

import { useWorkflowStateApi } from "./port";

export const workflowStateKeys = {
  all: (workspaceSlug: string, projectId: UUID) =>
    ["workspaces", workspaceSlug, "projects", projectId, "states"] as const,
};

export function useStatesQuery(workspaceSlug: MaybeRefOrGetter<string>, projectId: MaybeRefOrGetter<UUID | undefined>) {
  const api = useWorkflowStateApi();
  return useQuery({
    queryKey: computed(() => workflowStateKeys.all(toValue(workspaceSlug), toValue(projectId) ?? "missing")),
    queryFn: ({ signal }) => api.listStates(toValue(workspaceSlug), toValue(projectId)!, signal),
    enabled: computed(() => Boolean(toValue(projectId))),
    staleTime: 30_000,
  });
}
