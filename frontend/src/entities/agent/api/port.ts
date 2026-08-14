import { inject, type InjectionKey } from "vue";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { Agent, CreateAgentInput, UpdateAgentInput } from "../model/types";

export interface AgentApi {
  listAgents(workspaceSlug: string, projectId: UUID, signal?: AbortSignal): Promise<Agent[]>;
  getAgent(workspaceSlug: string, projectId: UUID, agentId: UUID, signal?: AbortSignal): Promise<Agent>;
  createAgent(workspaceSlug: string, projectId: UUID, input: CreateAgentInput): Promise<Agent>;
  updateAgent(
    workspaceSlug: string,
    projectId: UUID,
    agentId: UUID,
    input: UpdateAgentInput,
    version: number,
  ): Promise<Agent>;
  setAgentEnabled(
    workspaceSlug: string,
    projectId: UUID,
    agentId: UUID,
    enabled: boolean,
    version: number,
  ): Promise<Agent>;
  archiveAgent(workspaceSlug: string, projectId: UUID, agentId: UUID, version: number): Promise<Agent>;
}

export const agentApiKey: InjectionKey<AgentApi> = Symbol("agent-api");

export function useAgentApi(): AgentApi {
  const api = inject(agentApiKey);
  if (!api) throw new Error("Agent API provider is not installed");
  return api;
}
