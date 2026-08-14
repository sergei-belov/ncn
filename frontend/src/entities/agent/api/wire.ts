import { z } from "zod";

import type { Agent } from "../model/types";

export const wireAgentSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  kind: z.enum(["coordinator", "worker"]),
  name: z.string(),
  description: z.string().default(""),
  instructions: z.string(),
  model: z.string(),
  memory_policy: z.enum(["project", "session", "none"]),
  max_steps_per_run: z.number().int().positive(),
  approval_mode: z.enum(["project", "always"]),
  status: z.enum(["active", "disabled", "archived"]),
  system_tool_names: z.array(z.string()).default([]),
  created_at: z.string(),
  updated_at: z.string(),
  version: z.number().int().positive(),
});

export function mapAgent(value: z.infer<typeof wireAgentSchema>): Agent {
  return {
    id: value.id,
    projectId: value.project_id,
    kind: value.kind,
    name: value.name,
    description: value.description,
    instructions: value.instructions,
    model: value.model,
    memoryPolicy: value.memory_policy,
    maxStepsPerRun: value.max_steps_per_run,
    approvalMode: value.approval_mode,
    status: value.status,
    systemToolNames: value.system_tool_names,
    createdAt: value.created_at,
    updatedAt: value.updated_at,
    version: value.version,
  };
}
