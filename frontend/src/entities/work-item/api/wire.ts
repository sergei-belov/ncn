import { z } from "zod";

import type { WorkItem } from "../model/types";

export const wireWorkItemSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  sequence_id: z.number(),
  identifier: z.string(),
  title: z.string(),
  description_html: z.string().default(""),
  state_id: z.string(),
  priority: z.enum(["none", "low", "medium", "high", "urgent"]),
  assignee_ids: z.array(z.string()),
  epic_id: z.string().nullable(),
  start_date: z.string().nullable(),
  due_date: z.string().nullable(),
  sort_order: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
  version: z.number(),
});

export function mapWorkItem(value: z.infer<typeof wireWorkItemSchema>): WorkItem {
  return {
    id: value.id,
    projectId: value.project_id,
    sequenceId: value.sequence_id,
    identifier: value.identifier,
    title: value.title,
    descriptionHtml: value.description_html,
    stateId: value.state_id,
    priority: value.priority,
    assigneeIds: value.assignee_ids,
    epicId: value.epic_id,
    startDate: value.start_date,
    dueDate: value.due_date,
    sortOrder: value.sort_order,
    createdAt: value.created_at,
    updatedAt: value.updated_at,
    version: value.version,
  };
}
