import { z } from "zod";

import type { Epic } from "../model/types";

export const wireEpicSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  name: z.string(),
  description: z.string().default(""),
  color: z.string(),
  start_date: z.string().nullable(),
  target_date: z.string().nullable(),
  work_item_ids: z.array(z.string()),
  progress: z.object({ total: z.number(), completed: z.number(), percentage: z.number() }),
  created_at: z.string(),
  updated_at: z.string(),
  version: z.number(),
});

export function mapEpic(value: z.infer<typeof wireEpicSchema>): Epic {
  return {
    id: value.id,
    projectId: value.project_id,
    name: value.name,
    description: value.description,
    color: value.color,
    startDate: value.start_date,
    targetDate: value.target_date,
    workItemIds: value.work_item_ids,
    progress: value.progress,
    createdAt: value.created_at,
    updatedAt: value.updated_at,
    version: value.version,
  };
}
