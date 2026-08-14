import { computed, toValue, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { EpicFilters } from "../model/types";
import { useEpicApi } from "./port";

export const epicKeys = {
  all: (workspaceSlug: string, projectId: UUID) => ["workspaces", workspaceSlug, "projects", projectId, "epics"] as const,
  list: (workspaceSlug: string, projectId: UUID, filters: EpicFilters) =>
    [...epicKeys.all(workspaceSlug, projectId), "list", filters] as const,
};

export function useEpicsQuery(
  workspaceSlug: MaybeRefOrGetter<string>,
  projectId: MaybeRefOrGetter<UUID | undefined>,
  filters: MaybeRefOrGetter<EpicFilters>,
) {
  const api = useEpicApi();
  return useQuery({
    queryKey: computed(() => epicKeys.list(toValue(workspaceSlug), toValue(projectId) ?? "missing", toValue(filters))),
    queryFn: ({ signal }) => api.listEpics(toValue(workspaceSlug), toValue(projectId)!, toValue(filters), signal),
    enabled: computed(() => Boolean(toValue(projectId))),
    staleTime: 20_000,
  });
}
