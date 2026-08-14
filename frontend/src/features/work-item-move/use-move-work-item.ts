import { toValue, type MaybeRefOrGetter } from "vue";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

import {
  boardKeys,
  commitWorkItemMove,
  moveWorkItemOptimistically,
  useBoardApi,
  type BoardPayload,
  type MoveCommand,
  type MoveWorkItemInput,
} from "@/entities/board";
import type { UUID } from "@/shared/lib/domain-primitives";

export type { MoveCommand } from "@/entities/board";

export function useMoveWorkItem(workspaceSlug: MaybeRefOrGetter<string>, projectId: MaybeRefOrGetter<UUID>) {
  const api = useBoardApi();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (command: MoveCommand) => {
      const queryKey = boardKeys.all(toValue(workspaceSlug), toValue(projectId));
      await queryClient.cancelQueries({ queryKey });
      const snapshots = queryClient.getQueriesData<BoardPayload>({ queryKey });
      const payload = snapshots.map(([, data]) => data).find((data) => data?.workItems.some((item) => item.id === command.workItemId));
      const workItem = payload?.workItems.find((item) => item.id === command.workItemId);
      if (!workItem) throw new Error("Карточка отсутствует в кэше доски");
      const input: MoveWorkItemInput = {
        ...command,
        entityVersion: workItem.version,
        boardVersion: payload.boardVersion,
        clientMutationId: crypto.randomUUID(),
      };
      queryClient.setQueriesData<BoardPayload>({ queryKey }, (current) =>
        current ? moveWorkItemOptimistically(current, command) : current,
      );
      try {
        const result = await api.moveWorkItem(toValue(workspaceSlug), toValue(projectId), input);
        queryClient.setQueriesData<BoardPayload>({ queryKey }, (current) =>
          current ? commitWorkItemMove(current, result) : current,
        );
        return result;
      } catch (error) {
        for (const [snapshotKey, snapshot] of snapshots) queryClient.setQueryData(snapshotKey, snapshot);
        throw error;
      } finally {
        await queryClient.invalidateQueries({ queryKey });
      }
    },
  });
}
