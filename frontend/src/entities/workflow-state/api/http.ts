import { apiClient } from "@/shared/api/api-client";
import { dataSchema, listSchema, voidSchema } from "@/shared/api/schema";
import { projectBase, queryString } from "@/shared/api/url";

import type { WorkflowStateApi } from "./port";
import { mapState, wireStateSchema } from "./wire";

export const httpWorkflowStateApi: WorkflowStateApi = {
  async listStates(workspaceSlug, projectId, signal) {
    const result = await apiClient.get(`${projectBase(workspaceSlug, projectId)}/states`, {
      schema: listSchema(wireStateSchema),
      signal,
    });
    return result.data.map(mapState);
  },
  async createState(workspaceSlug, projectId, input) {
    const result = await apiClient.post(`${projectBase(workspaceSlug, projectId)}/states`, input, {
      schema: dataSchema(wireStateSchema),
      idempotencyKey: crypto.randomUUID(),
    });
    return mapState(result.data);
  },
  async updateState(workspaceSlug, projectId, stateId, input, version) {
    const result = await apiClient.patch(
      `${projectBase(workspaceSlug, projectId)}/states/${stateId}`,
      { name: input.name, color: input.color, group: input.group, is_default: input.isDefault },
      { schema: dataSchema(wireStateSchema), version },
    );
    return mapState(result.data);
  },
  async reorderStates(workspaceSlug, projectId, orderedStateIds) {
    const result = await apiClient.post(
      `${projectBase(workspaceSlug, projectId)}/states/reorder`,
      { state_ids: orderedStateIds },
      { schema: listSchema(wireStateSchema), idempotencyKey: crypto.randomUUID() },
    );
    return result.data.map(mapState);
  },
  async deleteState(workspaceSlug, projectId, stateId, replacementStateId) {
    await apiClient.delete(
      `${projectBase(workspaceSlug, projectId)}/states/${stateId}${queryString({ replacement_state_id: replacementStateId })}`,
      { schema: voidSchema },
    );
  },
};
