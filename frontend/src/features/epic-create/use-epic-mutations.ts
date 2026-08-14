import { toValue, type MaybeRefOrGetter } from "vue";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

import { boardKeys } from "@/entities/board";
import { epicKeys, useEpicApi, type CreateEpicInput, type Epic, type UpdateEpicInput } from "@/entities/epic";
import type { UUID } from "@/shared/lib/domain-primitives";

export function useEpicMutations(workspaceSlug: MaybeRefOrGetter<string>, projectId: MaybeRefOrGetter<UUID>) {
  const api = useEpicApi();
  const queryClient = useQueryClient();
  const invalidate = () =>
    Promise.all([
      queryClient.invalidateQueries({
        queryKey: epicKeys.all(toValue(workspaceSlug), toValue(projectId)),
      }),
      queryClient.invalidateQueries({
        queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)),
      }),
    ]);

  const create = useMutation({
    mutationFn: (input: CreateEpicInput) => api.createEpic(toValue(workspaceSlug), toValue(projectId), input),
    onSuccess: invalidate,
  });
  const update = useMutation({
    mutationFn: ({ epic, input }: { epic: Epic; input: UpdateEpicInput }) =>
      api.updateEpic(toValue(workspaceSlug), toValue(projectId), epic.id, input, epic.version),
    onSuccess: async (epic) => {
      queryClient.setQueriesData<Epic[]>(
        { queryKey: epicKeys.all(toValue(workspaceSlug), toValue(projectId)) },
        (current) => current?.map((item) => (item.id === epic.id ? epic : item)),
      );
      await invalidate();
    },
  });
  const remove = useMutation({
    mutationFn: (epic: Epic) => api.deleteEpic(toValue(workspaceSlug), toValue(projectId), epic.id, epic.version),
    onSuccess: async (_, epic) => {
      queryClient.setQueriesData<Epic[]>(
        { queryKey: epicKeys.all(toValue(workspaceSlug), toValue(projectId)) },
        (current) => current?.filter((item) => item.id !== epic.id),
      );
      await invalidate();
    },
  });
  const setWorkItems = useMutation({
    mutationFn: ({ epicId, workItemIds }: { epicId: UUID; workItemIds: UUID[] }) =>
      api.setEpicWorkItems(toValue(workspaceSlug), toValue(projectId), epicId, workItemIds),
    onSuccess: async (epic) => {
      queryClient.setQueriesData<Epic[]>(
        { queryKey: epicKeys.all(toValue(workspaceSlug), toValue(projectId)) },
        (current) => current?.map((item) => (item.id === epic.id ? epic : item)),
      );
      await invalidate();
    },
  });
  return { create, update, remove, setWorkItems };
}
