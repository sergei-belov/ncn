import { apiClient } from "@/shared/api/api-client";
import { dataSchema, listSchema } from "@/shared/api/schema";
import { projectBase, queryString } from "@/shared/api/url";

import type { ProjectApi } from "./port";
import { mapProject, wireProjectSchema } from "./wire";

export const httpProjectApi: ProjectApi = {
  async listProjects(workspaceSlug, filters, signal) {
    const result = await apiClient.get(
      `${projectBase(workspaceSlug)}${queryString({ search: filters.search, archived: filters.archived })}`,
      { schema: listSchema(wireProjectSchema), signal },
    );
    return result.data.map(mapProject);
  },
  async getProject(workspaceSlug, projectId, signal) {
    const result = await apiClient.get(projectBase(workspaceSlug, projectId), {
      schema: dataSchema(wireProjectSchema),
      signal,
    });
    return mapProject(result.data);
  },
  async createProject(workspaceSlug, input) {
    const result = await apiClient.post(projectBase(workspaceSlug), input, {
      schema: dataSchema(wireProjectSchema),
      idempotencyKey: crypto.randomUUID(),
    });
    return mapProject(result.data);
  },
  async updateProject(workspaceSlug, projectId, input, version) {
    const result = await apiClient.patch(projectBase(workspaceSlug, projectId), input, {
      schema: dataSchema(wireProjectSchema),
      version,
    });
    return mapProject(result.data);
  },
  async archiveProject(workspaceSlug, projectId, version) {
    const result = await apiClient.post(`${projectBase(workspaceSlug, projectId)}/archive`, {}, {
      schema: dataSchema(wireProjectSchema),
      version,
      idempotencyKey: crypto.randomUUID(),
    });
    return mapProject(result.data);
  },
  async restoreProject(workspaceSlug, projectId, version) {
    const result = await apiClient.post(`${projectBase(workspaceSlug, projectId)}/restore`, {}, {
      schema: dataSchema(wireProjectSchema),
      version,
      idempotencyKey: crypto.randomUUID(),
    });
    return mapProject(result.data);
  },
};
