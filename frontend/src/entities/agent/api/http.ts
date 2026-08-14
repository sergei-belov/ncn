import { apiClient } from "@/shared/api/api-client";
import { dataSchema, listSchema } from "@/shared/api/schema";
import { projectBase } from "@/shared/api/url";

import type { CreateAgentInput, UpdateAgentInput } from "../model/types";
import type { AgentApi } from "./port";
import { mapAgent, wireAgentSchema } from "./wire";

function agentsBase(workspaceSlug: string, projectId: string, agentId?: string): string {
  const root = `${projectBase(workspaceSlug, projectId)}/agents`;
  return agentId ? `${root}/${encodeURIComponent(agentId)}` : root;
}

function toWireInput(input: CreateAgentInput | UpdateAgentInput): Record<string, unknown> {
  return {
    ...(input.name === undefined ? {} : { name: input.name }),
    ...(input.description === undefined ? {} : { description: input.description }),
    ...(input.instructions === undefined ? {} : { instructions: input.instructions }),
    ...(input.model === undefined ? {} : { model: input.model }),
    ...(input.memoryPolicy === undefined ? {} : { memory_policy: input.memoryPolicy }),
    ...(input.maxStepsPerRun === undefined ? {} : { max_steps_per_run: input.maxStepsPerRun }),
    ...(input.approvalMode === undefined ? {} : { approval_mode: input.approvalMode }),
  };
}

export const httpAgentApi: AgentApi = {
  async listAgents(workspaceSlug, projectId, signal) {
    const result = await apiClient.get(agentsBase(workspaceSlug, projectId), {
      schema: listSchema(wireAgentSchema),
      signal,
    });
    return result.data.map(mapAgent);
  },
  async getAgent(workspaceSlug, projectId, agentId, signal) {
    const result = await apiClient.get(agentsBase(workspaceSlug, projectId, agentId), {
      schema: dataSchema(wireAgentSchema),
      signal,
    });
    return mapAgent(result.data);
  },
  async createAgent(workspaceSlug, projectId, input) {
    const result = await apiClient.post(agentsBase(workspaceSlug, projectId), toWireInput(input), {
      schema: dataSchema(wireAgentSchema),
      idempotencyKey: crypto.randomUUID(),
    });
    return mapAgent(result.data);
  },
  async updateAgent(workspaceSlug, projectId, agentId, input, version) {
    const result = await apiClient.patch(agentsBase(workspaceSlug, projectId, agentId), toWireInput(input), {
      schema: dataSchema(wireAgentSchema),
      version,
    });
    return mapAgent(result.data);
  },
  async setAgentEnabled(workspaceSlug, projectId, agentId, enabled, version) {
    const result = await apiClient.post(`${agentsBase(workspaceSlug, projectId, agentId)}/${enabled ? "enable" : "disable"}`, {}, {
      schema: dataSchema(wireAgentSchema),
      idempotencyKey: crypto.randomUUID(),
      version,
    });
    return mapAgent(result.data);
  },
  async archiveAgent(workspaceSlug, projectId, agentId, version) {
    const result = await apiClient.post(`${agentsBase(workspaceSlug, projectId, agentId)}/archive`, {}, {
      schema: dataSchema(wireAgentSchema),
      idempotencyKey: crypto.randomUUID(),
      version,
    });
    return mapAgent(result.data);
  },
};
