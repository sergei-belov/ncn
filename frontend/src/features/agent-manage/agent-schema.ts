import { z } from "zod";

import type { Agent, CreateAgentInput } from "@/entities/agent";

export const agentSchema = z.object({
  name: z.string().trim().min(2, "Введите не менее двух символов").max(80, "Максимум 80 символов"),
  description: z.string().trim().max(240, "Максимум 240 символов"),
  instructions: z.string().trim().min(20, "Опишите задачу ассистента подробнее").max(4000, "Максимум 4000 символов"),
  model: z.string().trim().min(1, "Выберите модель"),
  memoryPolicy: z.enum(["project", "session", "none"]),
  maxStepsPerRun: z.enum(["10", "25", "50"]),
  approvalMode: z.enum(["project", "always"]),
});

export type AgentFormValues = z.infer<typeof agentSchema>;

export const defaultAgentValues: AgentFormValues = {
  name: "",
  description: "",
  instructions: "",
  model: "qwen3:14b",
  memoryPolicy: "project",
  maxStepsPerRun: "25",
  approvalMode: "project",
};

export function valuesForAgent(agent: Agent): AgentFormValues {
  const allowedSteps = [10, 25, 50].includes(agent.maxStepsPerRun) ? String(agent.maxStepsPerRun) : "25";
  return {
    name: agent.name,
    description: agent.description,
    instructions: agent.instructions,
    model: agent.model,
    memoryPolicy: agent.memoryPolicy,
    maxStepsPerRun: allowedSteps as AgentFormValues["maxStepsPerRun"],
    approvalMode: agent.approvalMode,
  };
}

export function toAgentInput(values: AgentFormValues): CreateAgentInput {
  return {
    name: values.name,
    description: values.description,
    instructions: values.instructions,
    model: values.model,
    memoryPolicy: values.memoryPolicy,
    maxStepsPerRun: Number(values.maxStepsPerRun),
    approvalMode: values.approvalMode,
  };
}
