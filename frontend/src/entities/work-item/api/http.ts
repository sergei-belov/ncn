import { apiClient } from "@/shared/api/api-client";
import { dataSchema, voidSchema } from "@/shared/api/schema";
import { projectBase } from "@/shared/api/url";

import type { WorkItemApi } from "./port";
import { mapWorkItem, wireWorkItemSchema } from "./wire";

export const httpWorkItemApi: WorkItemApi = {
  async getWorkItem(workspaceSlug, projectId, workItemId, signal) {
    const result = await apiClient.get(`${projectBase(workspaceSlug, projectId)}/work-items/${workItemId}`, {
      schema: dataSchema(wireWorkItemSchema),
      signal,
    });
    return mapWorkItem(result.data);
  },
  async createWorkItem(workspaceSlug, projectId, input) {
    const result = await apiClient.post(
      `${projectBase(workspaceSlug, projectId)}/work-items`,
      {
        title: input.title,
        state_id: input.stateId,
        priority: input.priority,
        description_html: input.descriptionHtml,
        assignee_ids: input.assigneeIds,
        epic_id: input.epicId,
        start_date: input.startDate,
        due_date: input.dueDate,
      },
      { schema: dataSchema(wireWorkItemSchema), idempotencyKey: crypto.randomUUID() },
    );
    return mapWorkItem(result.data);
  },
  async updateWorkItem(workspaceSlug, projectId, workItemId, input, version) {
    const result = await apiClient.patch(
      `${projectBase(workspaceSlug, projectId)}/work-items/${workItemId}`,
      {
        title: input.title,
        description_html: input.descriptionHtml,
        state_id: input.stateId,
        priority: input.priority,
        assignee_ids: input.assigneeIds,
        epic_id: input.epicId,
        start_date: input.startDate,
        due_date: input.dueDate,
      },
      { schema: dataSchema(wireWorkItemSchema), version },
    );
    return mapWorkItem(result.data);
  },
  async deleteWorkItem(workspaceSlug, projectId, workItemId, version) {
    await apiClient.delete(`${projectBase(workspaceSlug, projectId)}/work-items/${workItemId}`, {
      schema: voidSchema,
      version,
    });
  },
};
