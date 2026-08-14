import { toValue, type MaybeRefOrGetter } from "vue";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

import {
  boardKeys,
  insertWorkItem,
  removeWorkItem,
  updateWorkItem,
  type BoardPayload,
} from "@/entities/board";
import { useWorkItemApi, type CreateWorkItemInput, type UpdateWorkItemInput, type WorkItem } from "@/entities/work-item";
import type { UUID } from "@/shared/lib/domain-primitives";

export function useCreateWorkItem(workspaceSlug: MaybeRefOrGetter<string>, projectId: MaybeRefOrGetter<UUID>) {
  const api = useWorkItemApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateWorkItemInput) => api.createWorkItem(toValue(workspaceSlug), toValue(projectId), input),
    onSuccess: async (workItem) => {
      queryClient.setQueriesData<BoardPayload>(
        { queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)) },
        (current) => (current ? insertWorkItem(current, workItem) : current),
      );
      await queryClient.invalidateQueries({
        queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)),
      });
    },
  });
}

export function useUpdateWorkItem(workspaceSlug: MaybeRefOrGetter<string>, projectId: MaybeRefOrGetter<UUID>) {
  const api = useWorkItemApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ workItem, input }: { workItem: WorkItem; input: UpdateWorkItemInput }) =>
      api.updateWorkItem(toValue(workspaceSlug), toValue(projectId), workItem.id, input, workItem.version),
    onSuccess: async (workItem) => {
      queryClient.setQueriesData<BoardPayload>(
        { queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)) },
        (current) => (current ? updateWorkItem(current, workItem) : current),
      );
      await queryClient.invalidateQueries({
        queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)),
      });
    },
  });
}

export function useDeleteWorkItem(workspaceSlug: MaybeRefOrGetter<string>, projectId: MaybeRefOrGetter<UUID>) {
  const api = useWorkItemApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (workItem: WorkItem) =>
      api.deleteWorkItem(toValue(workspaceSlug), toValue(projectId), workItem.id, workItem.version),
    onSuccess: async (_, workItem) => {
      queryClient.setQueriesData<BoardPayload>(
        { queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)) },
        (current) => (current ? removeWorkItem(current, workItem.id) : current),
      );
      await queryClient.invalidateQueries({
        queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)),
      });
    },
  });
}
