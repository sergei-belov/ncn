import { z } from "zod";

import type { WorkflowState } from "../model/types";

export const wireStateSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  name: z.string(),
  color: z.string(),
  group: z.enum(["backlog", "unstarted", "started", "completed", "cancelled"]),
  order: z.number(),
  is_default: z.boolean(),
  version: z.number(),
});

export function mapState(value: z.infer<typeof wireStateSchema>): WorkflowState {
  return {
    id: value.id,
    projectId: value.project_id,
    name: value.name,
    color: value.color,
    group: value.group,
    order: value.order,
    isDefault: value.is_default,
    version: value.version,
  };
}
