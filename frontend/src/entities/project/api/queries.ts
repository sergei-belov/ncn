import { computed, toValue, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { ProjectFilters } from "../model/types";
import { useProjectApi } from "./port";

export const projectKeys = {
  all: (workspaceSlug: string) => ["workspaces", workspaceSlug, "projects"] as const,
  lists: (workspaceSlug: string) => [...projectKeys.all(workspaceSlug), "list"] as const,
  list: (workspaceSlug: string, filters: ProjectFilters) => [...projectKeys.lists(workspaceSlug), filters] as const,
  detail: (workspaceSlug: string, projectId: UUID) => [...projectKeys.all(workspaceSlug), "detail", projectId] as const,
};

export function useProjectsQuery(
  workspaceSlug: MaybeRefOrGetter<string>,
  filters: MaybeRefOrGetter<ProjectFilters>,
) {
  const api = useProjectApi();
  return useQuery({
    queryKey: computed(() => projectKeys.list(toValue(workspaceSlug), toValue(filters))),
    queryFn: ({ signal }) => api.listProjects(toValue(workspaceSlug), toValue(filters), signal),
    staleTime: 20_000,
  });
}

export function useProjectQuery(
  workspaceSlug: MaybeRefOrGetter<string>,
  projectId: MaybeRefOrGetter<UUID | undefined>,
) {
  const api = useProjectApi();
  return useQuery({
    queryKey: computed(() => projectKeys.detail(toValue(workspaceSlug), toValue(projectId) ?? "missing")),
    queryFn: ({ signal }) => api.getProject(toValue(workspaceSlug), toValue(projectId)!, signal),
    enabled: computed(() => Boolean(toValue(projectId))),
    staleTime: 20_000,
  });
}
