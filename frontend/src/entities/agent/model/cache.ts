import type { Agent, AgentStatus } from "./types";

export function withAgentStatus(agent: Agent, status: AgentStatus): Agent {
  return { ...agent, status };
}

export function replaceAgentInList(agents: Agent[] | undefined, updated: Agent): Agent[] | undefined {
  if (!agents) return undefined;
  return agents.map((agent) => (agent.id === updated.id ? updated : agent));
}
