import type { ISODateTime, UUID } from "@/shared/lib/domain-primitives";

export type AgentKind = "coordinator" | "worker";
export type AgentStatus = "active" | "disabled" | "archived";
export type AgentMemoryPolicy = "project" | "session" | "none";
export type AgentApprovalMode = "project" | "always";

export interface Agent {
  id: UUID;
  projectId: UUID;
  kind: AgentKind;
  name: string;
  description: string;
  instructions: string;
  model: string;
  memoryPolicy: AgentMemoryPolicy;
  maxStepsPerRun: number;
  approvalMode: AgentApprovalMode;
  status: AgentStatus;
  systemToolNames: string[];
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
  version: number;
}

export interface CreateAgentInput {
  name: string;
  description: string;
  instructions: string;
  model: string;
  memoryPolicy: AgentMemoryPolicy;
  maxStepsPerRun: number;
  approvalMode: AgentApprovalMode;
}

export type UpdateAgentInput = Partial<CreateAgentInput>;
