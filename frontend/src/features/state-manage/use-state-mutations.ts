import { toValue, type MaybeRefOrGetter } from "vue";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

import { boardKeys } from "@/entities/board";
import {
  useWorkflowStateApi,
  workflowStateKeys,
  type CreateStateInput,
  type UpdateStateInput,
  type WorkflowState,
} from "@/entities/workflow-state";
import type { UUID } from "@/shared/lib/domain-primitives";

export function useStateMutations(workspaceSlug: MaybeRefOrGetter<string>, projectId: MaybeRefOrGetter<UUID>) {
  const api = useWorkflowStateApi();
  const queryClient = useQueryClient();
  const invalidate = () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: workflowStateKeys.all(toValue(workspaceSlug), toValue(projectId)) }),
      queryClient.invalidateQueries({ queryKey: boardKeys.all(toValue(workspaceSlug), toValue(projectId)) }),
    ]);

  const create = useMutation({
    mutationFn: (input: CreateStateInput) => api.createState(toValue(workspaceSlug), toValue(projectId), input),
    onSuccess: invalidate,
  });
  const update = useMutation({
    mutationFn: ({ state, input }: { state: WorkflowState; input: UpdateStateInput }) =>
      api.updateState(toValue(workspaceSlug), toValue(projectId), state.id, input, state.version),
    onSuccess: async (state) => {
      queryClient.setQueryData<WorkflowState[]>(
        workflowStateKeys.all(toValue(workspaceSlug), toValue(projectId)),
        (current) => current?.map((item) => (item.id === state.id ? state : item)),
      );
      await invalidate();
    },
  });
  const reorder = useMutation({
    mutationFn: (orderedIds: UUID[]) => api.reorderStates(toValue(workspaceSlug), toValue(projectId), orderedIds),
    onSuccess: async (states) => {
      queryClient.setQueryData(workflowStateKeys.all(toValue(workspaceSlug), toValue(projectId)), states);
      await invalidate();
    },
  });
  const remove = useMutation({
    mutationFn: ({ stateId, replacementStateId }: { stateId: UUID; replacementStateId: UUID }) =>
      api.deleteState(toValue(workspaceSlug), toValue(projectId), stateId, replacementStateId),
    onSuccess: async (_, variables) => {
      queryClient.setQueryData<WorkflowState[]>(
        workflowStateKeys.all(toValue(workspaceSlug), toValue(projectId)),
        (current) => current?.filter((state) => state.id !== variables.stateId),
      );
      await invalidate();
    },
  });
  return { create, update, reorder, remove };
}
