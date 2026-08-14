import { apiClient } from "@/shared/api/api-client";
import { dataSchema, listSchema, voidSchema } from "@/shared/api/schema";
import { projectBase, queryString } from "@/shared/api/url";

import type { EpicApi } from "./port";
import { mapEpic, wireEpicSchema } from "./wire";

export const httpEpicApi: EpicApi = {
  async listEpics(workspaceSlug, projectId, filters, signal) {
    const result = await apiClient.get(
      `${projectBase(workspaceSlug, projectId)}/epics${queryString({ search: filters.search })}`,
      { schema: listSchema(wireEpicSchema), signal },
    );
    return result.data.map(mapEpic);
  },
  async getEpic(workspaceSlug, projectId, epicId, signal) {
    const result = await apiClient.get(`${projectBase(workspaceSlug, projectId)}/epics/${epicId}`, {
      schema: dataSchema(wireEpicSchema),
      signal,
    });
    return mapEpic(result.data);
  },
  async createEpic(workspaceSlug, projectId, input) {
    const result = await apiClient.post(
      `${projectBase(workspaceSlug, projectId)}/epics`,
      {
        name: input.name,
        description: input.description,
        color: input.color,
        start_date: input.startDate,
        target_date: input.targetDate,
      },
      { schema: dataSchema(wireEpicSchema), idempotencyKey: crypto.randomUUID() },
    );
    return mapEpic(result.data);
  },
  async updateEpic(workspaceSlug, projectId, epicId, input, version) {
    const result = await apiClient.patch(
      `${projectBase(workspaceSlug, projectId)}/epics/${epicId}`,
      {
        name: input.name,
        description: input.description,
        color: input.color,
        start_date: input.startDate,
        target_date: input.targetDate,
      },
      { schema: dataSchema(wireEpicSchema), version },
    );
    return mapEpic(result.data);
  },
  async deleteEpic(workspaceSlug, projectId, epicId, version) {
    await apiClient.delete(`${projectBase(workspaceSlug, projectId)}/epics/${epicId}`, { schema: voidSchema, version });
  },
  async setEpicWorkItems(workspaceSlug, projectId, epicId, workItemIds) {
    const result = await apiClient.post(
      `${projectBase(workspaceSlug, projectId)}/epics/${epicId}/work-items/batch`,
      { work_item_ids: workItemIds },
      { schema: dataSchema(wireEpicSchema), idempotencyKey: crypto.randomUUID() },
    );
    return mapEpic(result.data);
  },
};
