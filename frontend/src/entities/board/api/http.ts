import { apiClient } from "@/shared/api/api-client";
import { projectBase, queryString } from "@/shared/api/url";

import type { BoardApi } from "./port";
import { mapBoard, wireBoardSchema } from "./wire";

export const httpBoardApi: BoardApi = {
  async getBoard(workspaceSlug, projectId, filters, signal) {
    const result = await apiClient.get(
      `${projectBase(workspaceSlug, projectId)}/board${queryString({
        search: filters.search,
        priority: filters.priorities,
        epic_id: filters.epicId,
        assignee_id: filters.assigneeId,
      })}`,
      { schema: wireBoardSchema, signal },
    );
    return mapBoard(result);
  },
  async moveWorkItem(workspaceSlug, projectId, input) {
    const result = await apiClient.post(
      `${projectBase(workspaceSlug, projectId)}/work-items/${input.workItemId}/move`,
      {
        from_state_id: input.fromStateId,
        to_state_id: input.toStateId,
        before_work_item_id: input.beforeWorkItemId,
        after_work_item_id: input.afterWorkItemId,
        board_version: input.boardVersion,
        client_mutation_id: input.clientMutationId,
      },
      { schema: wireBoardSchema, version: input.entityVersion, idempotencyKey: input.clientMutationId },
    );
    const board = mapBoard(result);
    const workItem = board.workItems.find((item) => item.id === input.workItemId);
    if (!workItem) throw new Error("Move response does not contain work item");
    return { workItem, columns: board.columns, boardVersion: board.boardVersion };
  },
};
