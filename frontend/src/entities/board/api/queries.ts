import { computed, toValue, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { BoardFilters } from "../model/types";
import { useBoardApi } from "./port";

export const boardKeys = {
  all: (workspaceSlug: string, projectId: UUID) =>
    ["workspaces", workspaceSlug, "projects", projectId, "board"] as const,
  detail: (workspaceSlug: string, projectId: UUID, filters: BoardFilters) =>
    [...boardKeys.all(workspaceSlug, projectId), filters] as const,
};

export function useBoardQuery(
  workspaceSlug: MaybeRefOrGetter<string>,
  projectId: MaybeRefOrGetter<UUID | undefined>,
  filters: MaybeRefOrGetter<BoardFilters>,
) {
  const api = useBoardApi();
  return useQuery({
    queryKey: computed(() => boardKeys.detail(toValue(workspaceSlug), toValue(projectId) ?? "missing", toValue(filters))),
    queryFn: ({ signal }) => api.getBoard(toValue(workspaceSlug), toValue(projectId)!, toValue(filters), signal),
    enabled: computed(() => Boolean(toValue(projectId))),
    staleTime: 15_000,
    refetchOnWindowFocus: true,
  });
}
