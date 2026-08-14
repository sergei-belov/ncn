import { toValue, type MaybeRefOrGetter } from "vue";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

import {
  projectKeys,
  useProjectApi,
  type CreateProjectInput,
  type Project,
  type UpdateProjectInput,
} from "@/entities/project";

export function useCreateProject(workspaceSlug: MaybeRefOrGetter<string>) {
  const api = useProjectApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateProjectInput) => api.createProject(toValue(workspaceSlug), input),
    onSuccess: async (project) => {
      queryClient.setQueryData(projectKeys.detail(toValue(workspaceSlug), project.id), project);
      await queryClient.invalidateQueries({ queryKey: projectKeys.all(toValue(workspaceSlug)) });
    },
  });
}

export function useUpdateProject(workspaceSlug: MaybeRefOrGetter<string>) {
  const api = useProjectApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ project, input }: { project: Project; input: UpdateProjectInput }) =>
      api.updateProject(toValue(workspaceSlug), project.id, input, project.version),
    onSuccess: async (project) => {
      queryClient.setQueryData(projectKeys.detail(toValue(workspaceSlug), project.id), project);
      await queryClient.invalidateQueries({ queryKey: projectKeys.all(toValue(workspaceSlug)) });
    },
  });
}

export function useArchiveProject(workspaceSlug: MaybeRefOrGetter<string>) {
  const api = useProjectApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ project, restore }: { project: Project; restore: boolean }) =>
      restore
        ? api.restoreProject(toValue(workspaceSlug), project.id, project.version)
        : api.archiveProject(toValue(workspaceSlug), project.id, project.version),
    onSuccess: async (project) => {
      queryClient.setQueryData(projectKeys.detail(toValue(workspaceSlug), project.id), project);
      await queryClient.invalidateQueries({ queryKey: projectKeys.all(toValue(workspaceSlug)) });
    },
  });
}
